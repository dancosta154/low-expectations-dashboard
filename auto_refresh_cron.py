#!/usr/bin/env python3
"""
Automated ESPN Credential Refresh Cron Job
Runs automatically to keep credentials fresh
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from refresh_espn_credentials import ESPNCredentialRefresher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('espn_refresh.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Main cron job function"""
    load_dotenv()
    
    logging.info("🔄 Starting automated ESPN credential check...")
    
    try:
        refresher = ESPNCredentialRefresher()
        
        # Check if we have the required setup
        if not all([refresher.league_id, refresher.espn_email, refresher.espn_password]):
            logging.error("❌ Missing required environment variables for auto-refresh")
            logging.error("Please add ESPN_EMAIL and ESPN_PASSWORD to your .env file")
            return False
        
        # Check if credentials are expired
        if refresher.check_credentials_expired():
            logging.info("🔍 Credentials expired, starting refresh...")
            
            success = refresher.refresh_credentials()
            
            if success:
                logging.info("✅ Credential refresh completed successfully!")
                return True
            else:
                logging.error("❌ Credential refresh failed!")
                return False
        else:
            logging.info("✅ Credentials are still working!")
            return True
            
    except Exception as e:
        logging.error(f"❌ Unexpected error in auto-refresh: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
