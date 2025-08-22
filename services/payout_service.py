"""
Payout Service
Calculates league payouts based on performance and structure
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict
import statistics
from services.espn_dashboard import ESPNDashboardService
from config.team_map import TEAM_ID_MAP, TEAM_TO_OWNER_MAP

class PayoutService:
    """Service for calculating league payouts"""
    
    # League payout structure
    PAYOUT_STRUCTURE = {
        "champion": 300,           # League Champion: $300
        "runner_up": 150,          # Runner-Up: $150
        "third_place": 70,         # 3rd Place: $70
        "fourth_place": 50,        # 4th Place: $50
        "weekly_high": 10,         # Weekly High Score: $10
        "most_points_regular": 40  # Most Points in Regular Season: $40
    }
    
    def __init__(self):
        self.espn_service = ESPNDashboardService()
        self._cached_historical_data = None
    
    def _get_historical_data(self) -> List[Dict[str, Any]]:
        """Get historical data with caching"""
        if self._cached_historical_data is None:
            self._cached_historical_data = self.espn_service.get_historical_data()
        return self._cached_historical_data
    
    def _get_owner_name(self, team_data: Dict[str, Any]) -> str:
        """Map team data to owner name using our team mapping system"""
        # First try to get owner from the processed data
        if isinstance(team_data, dict) and "owner" in team_data:
            owner = team_data["owner"]
            if owner and owner != "Unknown":
                return owner
        
        # Fallback: try to map using team ID
        team_id = team_data.get("id") if isinstance(team_data, dict) else None
        if team_id:
            team_key = TEAM_ID_MAP.get(team_id)
            if team_key:
                return TEAM_TO_OWNER_MAP.get(team_key, f"Team {team_id}")
        
        # Last resort - log the issue for debugging
        print(f"Warning: Could not map team data to owner: {team_data}")
        return f"Team {team_id}" if team_id else "Unknown Team"
    
    def calculate_season_payouts(self, season: int) -> Dict[str, Any]:
        """Calculate payouts for a specific season"""
        historical_data = self._get_historical_data()
        season_data = None
        
        # Find the specific season data
        for data in historical_data:
            if data["season"] == season:
                season_data = data
                break
        
        if not season_data:
            return {"error": f"No data found for season {season}"}
        
        payouts = defaultdict(float)
        payout_details = defaultdict(list)
        
        # 1. Championship Payouts (1st, 2nd, 3rd, 4th place)
        champion = season_data.get("champion")
        runner_up = season_data.get("runner_up")
        
        if champion:
            owner = self._get_owner_name(champion)
            payouts[owner] += self.PAYOUT_STRUCTURE["champion"]
            payout_details[owner].append({
                "type": "Champion",
                "amount": self.PAYOUT_STRUCTURE["champion"],
                "description": f"{season} League Champion"
            })
        
        if runner_up:
            owner = self._get_owner_name(runner_up)
            payouts[owner] += self.PAYOUT_STRUCTURE["runner_up"]
            payout_details[owner].append({
                "type": "Runner-Up",
                "amount": self.PAYOUT_STRUCTURE["runner_up"],
                "description": f"{season} Runner-Up"
            })
        
        # Get final standings for 3rd and 4th place
        teams = season_data.get("teams", [])
        if teams:
            # Sort by final rank or playoff seed
            sorted_teams = sorted(teams, key=lambda x: x.get("final_rank", x.get("playoff_seed", 99)))
            
            if len(sorted_teams) >= 3:
                third_place = sorted_teams[2]
                owner = self._get_owner_name(third_place)
                payouts[owner] += self.PAYOUT_STRUCTURE["third_place"]
                payout_details[owner].append({
                    "type": "3rd Place",
                    "amount": self.PAYOUT_STRUCTURE["third_place"],
                    "description": f"{season} 3rd Place"
                })
            
            if len(sorted_teams) >= 4:
                fourth_place = sorted_teams[3]
                owner = self._get_owner_name(fourth_place)
                payouts[owner] += self.PAYOUT_STRUCTURE["fourth_place"]
                payout_details[owner].append({
                    "type": "4th Place",
                    "amount": self.PAYOUT_STRUCTURE["fourth_place"],
                    "description": f"{season} 4th Place"
                })
        
        # 2. Most Points in Regular Season
        regular_season_totals = defaultdict(float)
        regular_season_games = defaultdict(int)
        
        for matchup in season_data.get("matchups", []):
            # Skip playoff games
            if matchup.get("playoff", False):
                continue
                
            for team in matchup.get("teams", []):
                owner = self._get_owner_name(team)
                score = team.get("score", 0)
                if score > 0:
                    regular_season_totals[owner] += round(score, 2)
                    regular_season_games[owner] += 1
        
        if regular_season_totals:
            top_scorer = max(regular_season_totals.keys(), key=lambda x: regular_season_totals[x])
            top_score = regular_season_totals[top_scorer]
            payouts[top_scorer] += self.PAYOUT_STRUCTURE["most_points_regular"]
            payout_details[top_scorer].append({
                "type": "Most Points (Regular)",
                "amount": self.PAYOUT_STRUCTURE["most_points_regular"],
                "description": f"{season} Most Points in Regular Season ({top_score:.2f} pts)"
            })
        
        # 3. Weekly High Scores
        weekly_highs = {}
        weekly_high_details = defaultdict(int)
        
        for matchup in season_data.get("matchups", []):
            week = matchup.get("week", 0)
            if week <= 0:
                continue
                
            week_scores = []
            for team in matchup.get("teams", []):
                score = team.get("score", 0)
                owner = self._get_owner_name(team)
                if score > 0:
                    week_scores.append({"owner": owner, "score": score})
            
            if week_scores:
                # Find highest score for this week
                if week not in weekly_highs:
                    weekly_highs[week] = {"owner": None, "score": 0}
                
                for score_data in week_scores:
                    if score_data["score"] > weekly_highs[week]["score"]:
                        weekly_highs[week] = score_data
        
        # Award weekly high score payouts
        for week, winner in weekly_highs.items():
            if winner["owner"]:
                owner = winner["owner"]
                payouts[owner] += self.PAYOUT_STRUCTURE["weekly_high"]
                weekly_high_details[owner] += 1
        
        # Add weekly high details to payout details
        for owner, count in weekly_high_details.items():
            total_weekly = count * self.PAYOUT_STRUCTURE["weekly_high"]
            payout_details[owner].append({
                "type": "Weekly High Scores",
                "amount": total_weekly,
                "description": f"{count} Weekly High Scores × ${self.PAYOUT_STRUCTURE['weekly_high']}"
            })
        
        # Calculate total payout for the season
        total_season_payout = sum(payouts.values())
        
        # Convert to list format for easier display
        payout_list = []
        for owner, total in payouts.items():
            payout_list.append({
                "owner": owner,
                "total_payout": round(total, 2),
                "details": payout_details[owner]
            })
        
        # Sort by total payout descending
        payout_list.sort(key=lambda x: x["total_payout"], reverse=True)
        
        return {
            "season": season,
            "payouts": payout_list,
            "season_total": round(total_season_payout, 2),
            "weekly_highs": weekly_highs,
            "regular_season_leader": {
                "owner": top_scorer if regular_season_totals else "Unknown",
                "points": round(top_score, 2) if regular_season_totals else 0
            } if regular_season_totals else None
        }
    
    def get_all_season_payouts(self) -> Dict[str, Any]:
        """Get payouts for all completed seasons (excludes current season)"""
        historical_data = self._get_historical_data()
        current_season = self.espn_service.config["CURRENT_SEASON"]
        all_payouts = []
        
        for season_data in historical_data:
            season = season_data["season"]
            
            # Skip current season - payouts only for completed seasons
            if season >= current_season:
                continue
                
            season_payouts = self.calculate_season_payouts(season)
            if "error" not in season_payouts:
                all_payouts.append(season_payouts)
        
        # Sort by season descending (most recent first)
        all_payouts.sort(key=lambda x: x["season"], reverse=True)
        
        return {
            "seasons": all_payouts,
            "total_seasons": len(all_payouts),
            "excluded_current_season": current_season
        }
    
    def get_cumulative_payouts(self) -> Dict[str, Any]:
        """Get cumulative payouts across all seasons"""
        all_season_payouts = self.get_all_season_payouts()
        cumulative_payouts = defaultdict(lambda: {
            "total_earnings": 0,
            "championships": 0,
            "runner_ups": 0,
            "third_places": 0,
            "fourth_places": 0,
            "weekly_highs": 0,
            "most_points_regular": 0,
            "seasons_participated": 0,
            "earnings_by_season": {}
        })
        
        total_league_payouts = 0
        
        for season_data in all_season_payouts["seasons"]:
            season = season_data["season"]
            total_league_payouts += season_data["season_total"]
            
            for payout in season_data["payouts"]:
                owner = payout["owner"]
                total_payout = payout["total_payout"]
                
                if total_payout > 0:
                    cumulative_payouts[owner]["total_earnings"] += total_payout
                    cumulative_payouts[owner]["seasons_participated"] += 1
                    cumulative_payouts[owner]["earnings_by_season"][season] = total_payout
                    
                    # Count achievement types
                    for detail in payout["details"]:
                        if detail["type"] == "Champion":
                            cumulative_payouts[owner]["championships"] += 1
                        elif detail["type"] == "Runner-Up":
                            cumulative_payouts[owner]["runner_ups"] += 1
                        elif detail["type"] == "3rd Place":
                            cumulative_payouts[owner]["third_places"] += 1
                        elif detail["type"] == "4th Place":
                            cumulative_payouts[owner]["fourth_places"] += 1
                        elif detail["type"] == "Weekly High Scores":
                            # Extract count from description
                            desc = detail["description"]
                            count = int(desc.split()[0]) if desc.split()[0].isdigit() else 0
                            cumulative_payouts[owner]["weekly_highs"] += count
                        elif detail["type"] == "Most Points (Regular)":
                            cumulative_payouts[owner]["most_points_regular"] += 1
        
        # Convert to list and sort by total earnings
        cumulative_list = []
        for owner, stats in cumulative_payouts.items():
            stats["owner"] = owner
            stats["total_earnings"] = round(stats["total_earnings"], 2)
            stats["avg_earnings_per_season"] = round(
                stats["total_earnings"] / max(1, stats["seasons_participated"]), 2
            )
            cumulative_list.append(stats)
        
        cumulative_list.sort(key=lambda x: x["total_earnings"], reverse=True)
        
        return {
            "cumulative_payouts": cumulative_list,
            "total_league_payouts": round(total_league_payouts, 2),
            "payout_structure": self.PAYOUT_STRUCTURE,
            "total_owners": len(cumulative_list)
        }
    
    def get_payout_summary(self) -> Dict[str, Any]:
        """Get a summary of payout information for completed seasons"""
        all_seasons = self.get_all_season_payouts()
        cumulative = self.get_cumulative_payouts()
        
        # Calculate some interesting stats
        total_weekly_payouts = 0
        total_weeks = 0
        
        for season_data in all_seasons["seasons"]:
            weekly_highs = season_data.get("weekly_highs", {})
            total_weeks += len(weekly_highs)
            total_weekly_payouts += len(weekly_highs) * self.PAYOUT_STRUCTURE["weekly_high"]
        
        return {
            "total_seasons": all_seasons["total_seasons"],
            "total_payouts": cumulative["total_league_payouts"],
            "total_weekly_payouts": total_weekly_payouts,
            "total_weeks": total_weeks,
            "avg_payout_per_season": round(
                cumulative["total_league_payouts"] / max(1, all_seasons["total_seasons"]), 2
            ),
            "payout_structure": self.PAYOUT_STRUCTURE,
            "excluded_current_season": all_seasons.get("excluded_current_season"),
            "completed_seasons_only": True
        }
