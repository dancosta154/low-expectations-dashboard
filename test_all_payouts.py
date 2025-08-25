#!/usr/bin/env python3
"""
Test script to show updated payouts for all years with new 4th place amount ($40)
"""

import os
import sys

# Add current directory to path for imports
sys.path.append('.')

# Try to load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not available, using system environment variables")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

try:
    from services.payout_service import PayoutService
    from services.espn_dashboard import ESPNDashboardService
    print("✅ Successfully imported services")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_all_payouts():
    """Test updated payout calculations for all years"""
    
    print("🏈 Low Expectations League - Updated Payout Analysis")
    print("=" * 60)
    print("📊 4th Place payout changed from $50 to $40")
    print("=" * 60)
    
    # Check environment variables
    required_vars = ['LEAGUE_ID', 'ESPN_SWID', 'ESPN_S2']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these environment variables or create a .env file")
        return
    
    print("✅ Environment variables configured")
    
    # Initialize services
    espn_service = ESPNDashboardService()
    payout_service = PayoutService()
    
    # Show updated payout structure
    print(f"\n💰 Updated Payout Structure:")
    for payout_type, amount in payout_service.PAYOUT_STRUCTURE.items():
        print(f"   {payout_type.replace('_', ' ').title()}: ${amount}")
    
    # Get all season payouts
    print(f"\n📊 Fetching all season data...")
    all_season_payouts = payout_service.get_all_season_payouts()
    
    if not all_season_payouts.get('seasons'):
        print("❌ No season data available")
        return
    
    print(f"✅ Found {len(all_season_payouts['seasons'])} seasons")
    
    # Display results for each season
    print(f"\n🏆 Updated Payout Results by Season:")
    print("=" * 60)
    
    total_league_payouts = 0
    
    for season_data in all_season_payouts['seasons']:
        season = season_data['season']
        season_total = season_data['season_total']
        total_league_payouts += season_total
        
        print(f"\n📅 {season} Season:")
        print(f"   Total Payout: ${season_total}")
        print(f"   Winners: {len(season_data['payouts'])}")
        
        # Show detailed payouts for this season
        for i, payout in enumerate(season_data['payouts'], 1):
            print(f"   {i}. {payout['owner']}: ${payout['total_payout']}")
            for detail in payout['details']:
                print(f"      • {detail['type']}: ${detail['amount']} - {detail['description']}")
    
    # Show cumulative results
    print(f"\n📈 Cumulative Results:")
    print("=" * 60)
    print(f"Total League Payouts: ${total_league_payouts}")
    print(f"Total Seasons: {len(all_season_payouts['seasons'])}")
    print(f"Average per Season: ${total_league_payouts / len(all_season_payouts['seasons']):.2f}")
    
    # Show impact of the change
    print(f"\n💡 Impact of 4th Place Change:")
    print("=" * 60)
    print("4th Place payout reduced from $50 to $40")
    print("This saves $10 per season for 4th place finishers")
    print("Total savings across all seasons: $10 × number of seasons")

if __name__ == "__main__":
    test_all_payouts()
