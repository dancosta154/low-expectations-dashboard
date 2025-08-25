#!/usr/bin/env python3
"""
ESPN Credentials Auto-Refresh Script
Automatically refreshes ESPN cookies when they expire
"""

import os
import time
import requests
import json
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

class ESPNCredentialRefresher:
    """Automated ESPN credential refresher"""
    
    def __init__(self):
        load_dotenv()
        self.league_id = os.getenv('LEAGUE_ID')
        self.espn_email = os.getenv('ESPN_EMAIL')
        self.espn_password = os.getenv('ESPN_PASSWORD')
        self.env_file = '.env'
        
        # Check if we have the required credentials
        if not all([self.league_id, self.espn_email, self.espn_password]):
            print("❌ Missing required environment variables:")
            print("   - LEAGUE_ID")
            print("   - ESPN_EMAIL") 
            print("   - ESPN_PASSWORD")
            print("\nPlease add these to your .env file for automatic refresh.")
            return
        
        self.driver = None
    
    def setup_driver(self):
        """Setup headless Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            print("Make sure Chrome is installed and chromedriver is in your PATH")
            return False
    
    def login_to_espn(self):
        """Login to ESPN and get fresh cookies"""
        try:
            print("🔐 Logging into ESPN...")
            
            # Go to ESPN login page
            self.driver.get("https://www.espn.com/login")
            
            # Wait for login form and enter credentials
            wait = WebDriverWait(self.driver, 10)
            
            # Find and fill email field
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            email_field.clear()
            email_field.send_keys(self.espn_email)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(self.espn_password)
            
            # Submit login form
            password_field.submit()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "login" not in self.driver.current_url.lower():
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login failed - check credentials")
                return False
                
        except TimeoutException:
            print("❌ Login timeout - ESPN page structure may have changed")
            return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_fantasy_cookies(self):
        """Navigate to fantasy football and extract cookies"""
        try:
            print("🏈 Accessing Fantasy Football...")
            
            # Go to fantasy football league
            league_url = f"https://fantasy.espn.com/football/league?leagueId={self.league_id}"
            self.driver.get(league_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Extract cookies
            cookies = self.driver.get_cookies()
            swid_cookie = None
            espn_s2_cookie = None
            
            for cookie in cookies:
                if cookie['name'] == 'SWID':
                    swid_cookie = cookie['value']
                elif cookie['name'] == 'espn_s2':
                    espn_s2_cookie = cookie['value']
            
            if swid_cookie and espn_s2_cookie:
                print("✅ Found ESPN cookies!")
                return {
                    'SWID': swid_cookie,
                    'espn_s2': espn_s2_cookie
                }
            else:
                print("❌ Could not find required cookies")
                return None
                
        except Exception as e:
            print(f"❌ Error accessing fantasy football: {e}")
            return None
    
    def update_env_file(self, cookies):
        """Update .env file with new cookies"""
        try:
            print("📝 Updating .env file...")
            
            # Read current .env file
            with open(self.env_file, 'r') as f:
                env_content = f.read()
            
            # Update SWID
            swid_pattern = r'ESPN_SWID=.*'
            env_content = re.sub(swid_pattern, f'ESPN_SWID={cookies["SWID"]}', env_content)
            
            # Update ESPN_S2
            s2_pattern = r'ESPN_S2=.*'
            env_content = re.sub(s2_pattern, f'ESPN_S2={cookies["espn_s2"]}', env_content)
            
            # Add timestamp
            timestamp_pattern = r'ESPN_CREDENTIALS_UPDATED=.*'
            if 'ESPN_CREDENTIALS_UPDATED=' in env_content:
                env_content = re.sub(timestamp_pattern, f'ESPN_CREDENTIALS_UPDATED={datetime.now().isoformat()}', env_content)
            else:
                env_content += f'\nESPN_CREDENTIALS_UPDATED={datetime.now().isoformat()}\n'
            
            # Write updated .env file
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            
            print("✅ .env file updated successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error updating .env file: {e}")
            return False
    
    def test_credentials(self):
        """Test if the new credentials work"""
        try:
            print("🧪 Testing new credentials...")
            
            # Import and test ESPN service
            from services.espn_dashboard import ESPNDashboardService
            
            espn_service = ESPNDashboardService()
            league_info = espn_service.get_league_info()
            
            if league_info and league_info.get('name'):
                print(f"✅ Credentials working! League: {league_info['name']}")
                return True
            else:
                print("❌ Credentials test failed")
                return False
                
        except Exception as e:
            print(f"❌ Credentials test error: {e}")
            return False
    
    def refresh_credentials(self):
        """Main method to refresh credentials"""
        print("🔄 Starting ESPN credential refresh...")
        
        if not self.setup_driver():
            return False
        
        try:
            # Login to ESPN
            if not self.login_to_espn():
                return False
            
            # Get fantasy cookies
            cookies = self.get_fantasy_cookies()
            if not cookies:
                return False
            
            # Update .env file
            if not self.update_env_file(cookies):
                return False
            
            # Test new credentials
            if not self.test_credentials():
                return False
            
            print("🎉 Credential refresh completed successfully!")
            return True
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def check_credentials_expired(self):
        """Check if credentials are expired by testing API call"""
        try:
            from services.espn_dashboard import ESPNDashboardService
            
            espn_service = ESPNDashboardService()
            league_info = espn_service.get_league_info()
            
            # If we get a valid response, credentials are working
            return not (league_info and league_info.get('name'))
            
        except Exception:
            # Any exception means credentials are likely expired
            return True

def main():
    """Main function for manual refresh"""
    refresher = ESPNCredentialRefresher()
    
    if not all([refresher.league_id, refresher.espn_email, refresher.espn_password]):
        print("\n📋 SETUP INSTRUCTIONS:")
        print("1. Add these to your .env file:")
        print("   ESPN_EMAIL=your_espn_email@example.com")
        print("   ESPN_PASSWORD=your_espn_password")
        print("2. Install selenium: pip install selenium")
        print("3. Install Chrome and chromedriver")
        print("4. Run this script again")
        return
    
    # Check if credentials are expired
    if refresher.check_credentials_expired():
        print("🔍 Credentials appear to be expired, refreshing...")
        refresher.refresh_credentials()
    else:
        print("✅ Credentials are still working!")

if __name__ == "__main__":
    main()
