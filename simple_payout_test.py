#!/usr/bin/env python3
"""
Simple test to show 2024 payout calculations
"""

import os
import sys
from email import parser

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

def test_2024_payouts():
    """Test 2024 payout calculations"""
    
    print("🏈 Low Expectations League - 2024 Payout Analysis")
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
    
    # Show payout structure
    print(f"\n💰 Payout Structure:")
    for payout_type, amount in payout_service.PAYOUT_STRUCTURE.items():
        print(f"   {payout_type.replace('_', ' ').title()}: ${amount}")
    
    # Get 2024 season data
    print(f"\n📊 Fetching 2024 season data...")
    season_2024 = espn_service.get_season_data(2024)
    
    if "error" in season_2024:
        print(f"❌ Error: {season_2024['error']}")
        return
    
    print(f"✅ Successfully retrieved 2024 data")
    print(f"   Teams: {len(season_2024.get('teams', []))}")
    print(f"   Matchups: {len(season_2024.get('matchups', []))}")
    
    # Calculate payouts
    print(f"\n🧮 Calculating 2024 payouts...")
    payouts_2024 = payout_service.calculate_season_payouts(2024)
    
    if "error" in payouts_2024:
        print(f"❌ Error calculating payouts: {payouts_2024['error']}")
        return
    
    # Display results
    print(f"\n🏆 2024 Payout Results:")
    print(f"   Total Season Payout: ${payouts_2024['season_total']}")
    print(f"   Number of Winners: {len(payouts_2024['payouts'])}")
    
    print(f"\n📋 Detailed Payouts:")
    for i, payout in enumerate(payouts_2024['payouts'], 1):
        print(f"\n{i}. {payout['owner']}: ${payout['total_payout']}")
        for detail in payout['details']:
            print(f"   • {detail['type']}: ${detail['amount']} - {detail['description']}")
    
    # Show regular season leader
    if payouts_2024.get('regular_season_leader'):
        leader = payouts_2024['regular_season_leader']
        print(f"\n🔥 Regular Season Points Leader:")
        print(f"   {leader['owner']}: {leader['points']} points")
    
    # Show weekly high scores
    print(f"\n📈 Weekly High Scores:")
    weekly_highs = payouts_2024.get('weekly_highs', {})
    for week, winner in sorted(weekly_highs.items()):
        if winner['owner']:
            print(f"   Week {week}: {winner['owner']} ({winner['score']} pts)")

if __name__ == "__main__":
    test_2024_payouts()
