"""
Analytics Service
Calculates various statistics and analytics for the ESPN Fantasy Football dashboard
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import statistics
from datetime import datetime
from services.espn_dashboard import ESPNDashboardService

class AnalyticsService:
    """Service for calculating league analytics and statistics"""
    
    def __init__(self):
        self.espn_service = ESPNDashboardService()
        self._cached_historical_data = None
    
    def _get_historical_data(self) -> List[Dict[str, Any]]:
        """Get historical data with caching"""
        if self._cached_historical_data is None:
            self._cached_historical_data = self.espn_service.get_historical_data()
        return self._cached_historical_data
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the main dashboard"""
        historical_data = self._get_historical_data()
        current_season = self.espn_service.get_current_season()
        
        # Calculate summary stats
        total_seasons = len(historical_data)
        total_games = sum(len(season.get("matchups", [])) for season in historical_data)
        
        # Get all-time highest and lowest scores
        all_scores = []
        for season in historical_data:
            for matchup in season.get("matchups", []):
                for team in matchup.get("teams", []):
                    if team.get("score", 0) > 0:  # Only valid scores
                        all_scores.append(team["score"])
        
        highest_score = max(all_scores) if all_scores else 0
        lowest_score = min(all_scores) if all_scores else 0
        avg_score = statistics.mean(all_scores) if all_scores else 0
        
        # Get champions
        champions = self.get_champions_history()
        most_championships = max(
            (owner["championships"] for owner in champions.get("by_owner", [])),
            default=0
        )
        
        return {
            "total_seasons": total_seasons,
            "total_games": total_games,
            "highest_score_ever": round(highest_score, 2),
            "lowest_score_ever": round(lowest_score, 2),
            "average_score": round(avg_score, 2),
            "most_championships": most_championships,
            "current_season_teams": len(current_season.get("standings", [])),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_champions_history(self) -> Dict[str, Any]:
        """Get championship history and statistics"""
        historical_data = self._get_historical_data()
        
        champions_by_season = []
        runner_ups_by_season = []
        championship_counts = Counter()
        runner_up_counts = Counter()
        
        for season_data in historical_data:
            season = season_data["season"]
            champion = season_data.get("champion")
            runner_up = season_data.get("runner_up")
            
            if champion:
                champion_info = {
                    "season": season,
                    "team_name": champion["name"],
                    "owner": champion["owner"],
                    "record": champion.get("record", {}),
                }
                champions_by_season.append(champion_info)
                championship_counts[champion["owner"]] += 1
            
            if runner_up:
                runner_up_info = {
                    "season": season,
                    "team_name": runner_up["name"],
                    "owner": runner_up["owner"],
                    "record": runner_up.get("record", {}),
                }
                runner_ups_by_season.append(runner_up_info)
                runner_up_counts[runner_up["owner"]] += 1
        
        # Create owner summary
        all_owners = set(championship_counts.keys()) | set(runner_up_counts.keys())
        by_owner = []
        
        for owner in all_owners:
            owner_stats = {
                "owner": owner,
                "championships": championship_counts.get(owner, 0),
                "runner_ups": runner_up_counts.get(owner, 0),
                "championship_seasons": [
                    champ["season"] for champ in champions_by_season 
                    if champ["owner"] == owner
                ],
                "runner_up_seasons": [
                    ru["season"] for ru in runner_ups_by_season 
                    if ru["owner"] == owner
                ]
            }
            owner_stats["total_finals"] = owner_stats["championships"] + owner_stats["runner_ups"]
            by_owner.append(owner_stats)
        
        # Sort by championships, then runner-ups
        by_owner.sort(key=lambda x: (x["championships"], x["runner_ups"]), reverse=True)
        
        return {
            "by_season": champions_by_season,
            "runner_ups_by_season": runner_ups_by_season,
            "by_owner": by_owner,
            "total_seasons": len(champions_by_season)
        }
    
    def get_scoring_stats(self) -> Dict[str, Any]:
        """Get scoring statistics and records"""
        historical_data = self._get_historical_data()
        
        # Collect all scores with context
        all_scores = []
        weekly_scores = defaultdict(list)  # by week number
        season_totals = defaultdict(lambda: defaultdict(float))  # by season, by team
        
        for season_data in historical_data:
            season = season_data["season"]
            
            for matchup in season_data.get("matchups", []):
                week = matchup.get("week", 0)
                is_playoff = matchup.get("playoff", False)
                
                for team in matchup.get("teams", []):
                    score = team.get("score", 0)
                    if score > 0:  # Valid score
                        score_record = {
                            "score": score,
                            "team_name": team.get("name", "Unknown"),
                            "team_id": team.get("id"),
                            "season": season,
                            "week": week,
                            "is_playoff": is_playoff
                        }
                        all_scores.append(score_record)
                        weekly_scores[week].append(score_record)
                        season_totals[season][team.get("id", 0)] += round(score, 2)
        
        if not all_scores:
            return {"error": "No scoring data available"}
        
        # Sort scores
        all_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Highest and lowest scores
        highest_scores = all_scores[:10]  # Top 10
        lowest_scores = sorted(all_scores, key=lambda x: x["score"])[:10]  # Bottom 10
        
        # Weekly averages
        weekly_averages = {}
        for week, scores in weekly_scores.items():
            if scores:
                weekly_averages[week] = {
                    "average": statistics.mean(score["score"] for score in scores),
                    "count": len(scores)
                }
        
        # Season scoring leaders
        season_leaders = []
        for season, team_totals in season_totals.items():
            if team_totals:
                top_scorer_id = max(team_totals.keys(), key=lambda x: team_totals[x])
                top_score = team_totals[top_scorer_id]
                
                # Find team name
                team_name = "Unknown"
                for season_data in historical_data:
                    if season_data["season"] == season:
                        for team in season_data.get("teams", []):
                            if team.get("id") == top_scorer_id:
                                team_name = team.get("name", "Unknown")
                                break
                
                season_leaders.append({
                    "season": season,
                    "team_name": team_name,
                    "total_points": round(top_score, 2),
                    "team_id": top_scorer_id
                })
        
        season_leaders.sort(key=lambda x: x["season"], reverse=True)
        
        # Overall statistics
        scores_only = [score["score"] for score in all_scores]
        
        return {
            "highest_scores": [{**score, "score": round(score["score"], 2)} for score in highest_scores],
            "lowest_scores": [{**score, "score": round(score["score"], 2)} for score in lowest_scores],
            "season_leaders": season_leaders,
            "weekly_averages": {
                week: {**avg, "average": round(avg["average"], 2)} 
                for week, avg in weekly_averages.items()
            },
            "overall_stats": {
                "total_games": len(all_scores),
                "average_score": round(statistics.mean(scores_only), 2),
                "median_score": round(statistics.median(scores_only), 2),
                "std_dev": round(statistics.stdev(scores_only), 2) if len(scores_only) > 1 else 0,
                "score_range": round(max(scores_only) - min(scores_only), 2)
            }
        }
    
    def get_season_stats(self) -> Dict[str, Any]:
        """Get season-by-season statistics"""
        historical_data = self._get_historical_data()
        
        season_stats = []
        
        for season_data in historical_data:
            season = season_data["season"]
            teams = season_data.get("teams", [])
            matchups = season_data.get("matchups", [])
            
            if not teams or not matchups:
                continue
            
            # Calculate season statistics
            season_scores = []
            team_records = {}
            
            for matchup in matchups:
                for team in matchup.get("teams", []):
                    score = team.get("score", 0)
                    if score > 0:
                        season_scores.append(score)
            
            # Get team records
            for team in teams:
                team_id = team.get("id")
                record = team.get("record", {})
                team_records[team_id] = {
                    "name": team.get("name", "Unknown"),
                    "wins": record.get("wins", 0),
                    "losses": record.get("losses", 0),
                    "points_for": record.get("pointsFor", 0),
                    "points_against": record.get("pointsAgainst", 0),
                }
            
            # Find best and worst records
            best_record = max(team_records.values(), key=lambda x: x["wins"]) if team_records else None
            worst_record = min(team_records.values(), key=lambda x: x["wins"]) if team_records else None
            
            # Highest and lowest scoring teams
            highest_scoring = max(team_records.values(), key=lambda x: x["points_for"]) if team_records else None
            lowest_scoring = min(team_records.values(), key=lambda x: x["points_for"]) if team_records else None
            
            stats = {
                "season": season,
                "total_teams": len(teams),
                "total_games": len([m for m in matchups if not m.get("playoff", False)]),
                "playoff_games": len([m for m in matchups if m.get("playoff", False)]),
                "average_score": round(statistics.mean(season_scores), 2) if season_scores else 0,
                "highest_score": round(max(season_scores), 2) if season_scores else 0,
                "lowest_score": round(min(season_scores), 2) if season_scores else 0,
                "best_record": best_record,
                "worst_record": worst_record,
                "highest_scoring_team": highest_scoring,
                "lowest_scoring_team": lowest_scoring,
                "champion": season_data.get("champion"),
                "runner_up": season_data.get("runner_up")
            }
            
            season_stats.append(stats)
        
        season_stats.sort(key=lambda x: x["season"], reverse=True)
        
        return {
            "seasons": season_stats,
            "total_seasons": len(season_stats)
        }
    
    def get_all_time_stats(self) -> Dict[str, Any]:
        """Get all-time statistics across all seasons"""
        historical_data = self._get_historical_data()
        
        # Aggregate all-time records
        owner_stats = defaultdict(lambda: {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "ties": 0,
            "points_for": 0,
            "points_against": 0,
            "seasons_played": 0,
            "playoff_appearances": 0,
            "championships": 0,
            "runner_ups": 0,
            "seasons": [],
            "championship_years": [],
            "runner_up_years": []
        })
        
        all_time_scores = []
        
        for season_data in historical_data:
            season = season_data["season"]
            
            for team in season_data.get("teams", []):
                owner = team.get("owner", "Unknown")
                record = team.get("record", {})
                
                stats = owner_stats[owner]
                stats["seasons_played"] += 1
                stats["wins"] += record.get("wins", 0)
                stats["losses"] += record.get("losses", 0)
                stats["ties"] += record.get("ties", 0)
                stats["points_for"] += round(record.get("pointsFor", 0), 2)
                stats["points_against"] += round(record.get("pointsAgainst", 0), 2)
                stats["games_played"] += (record.get("wins", 0) + record.get("losses", 0) + record.get("ties", 0))
                stats["seasons"].append(season)
                
                # Check for playoff appearance (could be determined by playoff seed or final rank)
                if team.get("playoff_seed", 0) > 0 or team.get("final_rank", 99) <= 6:  # Assuming top 6 make playoffs
                    stats["playoff_appearances"] += 1
                
                # Championships and runner-ups
                if season_data.get("champion") and season_data["champion"]["owner"] == owner:
                    stats["championships"] += 1
                    stats["championship_years"].append(season)
                if season_data.get("runner_up") and season_data["runner_up"]["owner"] == owner:
                    stats["runner_ups"] += 1
                    stats["runner_up_years"].append(season)
            
            # Collect all scores
            for matchup in season_data.get("matchups", []):
                for team in matchup.get("teams", []):
                    score = team.get("score", 0)
                    if score > 0:
                        all_time_scores.append(score)
        
        # Calculate derived stats for each owner
        all_time_leaders = []
        for owner, stats in owner_stats.items():
            if stats["games_played"] > 0:
                win_pct = stats["wins"] / stats["games_played"]
                avg_points_for = stats["points_for"] / stats["seasons_played"] if stats["seasons_played"] > 0 else 0
                avg_points_against = stats["points_against"] / stats["seasons_played"] if stats["seasons_played"] > 0 else 0
                
                leader_stats = {
                    "owner": owner,
                    "win_percentage": round(win_pct, 3),
                    "avg_points_per_season": round(avg_points_for, 2),
                    "avg_points_against_per_season": round(avg_points_against, 2),
                    "playoff_percentage": round(stats["playoff_appearances"] / stats["seasons_played"], 3) if stats["seasons_played"] > 0 else 0,
                    **stats
                }
                all_time_leaders.append(leader_stats)
        
        # Sort by various metrics
        leaders_by_wins = sorted(all_time_leaders, key=lambda x: x["wins"], reverse=True)
        leaders_by_win_pct = sorted(all_time_leaders, key=lambda x: x["win_percentage"], reverse=True)
        leaders_by_points = sorted(all_time_leaders, key=lambda x: x["points_for"], reverse=True)
        
        # Sort championships with tiebreaker: most championships first, then most recent championship year
        leaders_by_championships = sorted(
            all_time_leaders, 
            key=lambda x: (
                x["championships"], 
                max(x["championship_years"]) if x["championship_years"] else 0
            ), 
            reverse=True
        )
        
        return {
            "all_time_records": all_time_leaders,
            "leaders": {
                "most_wins": leaders_by_wins[:5],
                "highest_win_percentage": leaders_by_win_pct[:5],
                "most_points": leaders_by_points[:5],
                "most_championships": leaders_by_championships[:5]
            },
            "league_totals": {
                "total_games": sum(owner["games_played"] for owner in all_time_leaders),
                "total_points": sum(owner["points_for"] for owner in all_time_leaders),
                "average_score_all_time": round(statistics.mean(all_time_scores), 2) if all_time_scores else 0,
                "total_seasons": len(historical_data)
            }
        }
    
    def get_head_to_head_stats(self) -> Dict[str, Any]:
        """Get head-to-head matchup statistics"""
        historical_data = self._get_historical_data()
        
        # Track head-to-head records
        h2h_records = defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0, "points_for": 0, "points_against": 0, "games": 0}))
        
        for season_data in historical_data:
            for matchup in season_data.get("matchups", []):
                teams = matchup.get("teams", [])
                if len(teams) == 2:
                    team1, team2 = teams[0], teams[1]
                    score1, score2 = team1.get("score", 0), team2.get("score", 0)
                    
                    if score1 > 0 and score2 > 0:  # Valid matchup
                        name1, name2 = team1.get("name", "Unknown"), team2.get("name", "Unknown")
                        
                        # Update records
                        h2h_records[name1][name2]["games"] += 1
                        h2h_records[name2][name1]["games"] += 1
                        
                        h2h_records[name1][name2]["points_for"] += round(score1, 2)
                        h2h_records[name1][name2]["points_against"] += round(score2, 2)
                        h2h_records[name2][name1]["points_for"] += round(score2, 2)
                        h2h_records[name2][name1]["points_against"] += round(score1, 2)
                        
                        if score1 > score2:
                            h2h_records[name1][name2]["wins"] += 1
                            h2h_records[name2][name1]["losses"] += 1
                        else:
                            h2h_records[name2][name1]["wins"] += 1
                            h2h_records[name1][name2]["losses"] += 1
        
        # Convert to list format with win percentages
        matchup_results = []
        processed_pairs = set()
        
        for team1, opponents in h2h_records.items():
            for team2, record in opponents.items():
                if team1 != team2:
                    pair = tuple(sorted([team1, team2]))
                    if pair not in processed_pairs:
                        processed_pairs.add(pair)
                        
                        # Get both directions
                        record1 = h2h_records[team1][team2]
                        record2 = h2h_records[team2][team1]
                        
                        total_games = record1["games"]
                        if total_games > 0:
                            matchup_data = {
                                "team1": team1,
                                "team2": team2,
                                "team1_wins": record1["wins"],
                                "team2_wins": record2["wins"],
                                "total_games": total_games,
                                "team1_points": round(record1["points_for"], 2),
                                "team2_points": round(record2["points_for"], 2),
                                "team1_avg": round(record1["points_for"] / total_games, 2),
                                "team2_avg": round(record2["points_for"] / total_games, 2),
                            }
                            
                            # Determine series leader
                            if record1["wins"] > record2["wins"]:
                                matchup_data["series_leader"] = team1
                            elif record2["wins"] > record1["wins"]:
                                matchup_data["series_leader"] = team2
                            else:
                                matchup_data["series_leader"] = "Tied"
                            
                            matchup_results.append(matchup_data)
        
        # Sort by total games (most played matchups first)
        matchup_results.sort(key=lambda x: x["total_games"], reverse=True)
        
        return {
            "head_to_head": matchup_results,
            "total_matchups": len(matchup_results)
        }
    

    
    def clear_cache(self):
        """Clear cached data"""
        self._cached_historical_data = None
