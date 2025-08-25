#!/usr/bin/env python3
"""
Test script to show how 2024 payouts are calculated
"""

import os
from dotenv import load_dotenv
from services.payout_service import PayoutService
from services.espn_dashboard import ESPNDashboardService

# Load environment variables
load_dotenv()

def test_2024_payouts():
    """Test and display 2024 payout calculations"""
    
    print("🏈 Low Expectations League - 2024 Payout Analysis")
    print("=" * 60)
    
    # Initialize services
    espn_service = ESPNDashboardService()
    payout_service = PayoutService()
    
    # Get 2024 season data
    print("\n📊 Fetching 2024 season data from ESPN...")
    season_2024 = espn_service.get_season_data(2024)
    
    if "error" in season_2024:
        print(f"❌ Error fetching 2024 data: {season_2024['error']}")
        return
    
    print(f"✅ Successfully retrieved 2024 data")
    print(f"   Teams: {len(season_2024.get('teams', []))}")
    print(f"   Matchups: {len(season_2024.get('matchups', []))}")
    
    # Show payout structure
    print(f"\n💰 Payout Structure:")
    for payout_type, amount in payout_service.PAYOUT_STRUCTURE.items():
        print(f"   {payout_type.replace('_', ' ').title()}: ${amount}")
    
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
    
    # Show raw data structure for debugging
    print(f"\n🔍 Raw Data Structure (first few items):")
    print(f"   Teams in 2024:")
    for team in season_2024.get('teams', [])[:3]:  # Show first 3 teams
        print(f"     ID: {team.get('id')}, Name: {team.get('name')}, Owner: {team.get('owner')}, Final Rank: {team.get('final_rank')}")
    
    print(f"\n   Sample Matchups (first 2):")
    for matchup in season_2024.get('matchups', [])[:2]:
        print(f"     Week {matchup.get('week')}, Playoff: {matchup.get('playoff')}")
        for team in matchup.get('teams', []):
            print(f"       {team.get('owner')}: {team.get('score')} pts")

if __name__ == "__main__":
    test_2024_payouts()
