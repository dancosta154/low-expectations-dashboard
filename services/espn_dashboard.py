"""
ESPN Dashboard Service
Extended ESPN API service for dashboard analytics and historical data
"""

from typing import Dict, List, Any, Optional
import requests
from datetime import datetime
import os
from config.team_map import TEAM_ID_MAP, OWNER_UUID_MAP, TEAM_TO_OWNER_MAP

class ESPNDashboardService:
    """Enhanced ESPN service for dashboard analytics"""
    
    def __init__(self):
        self.api_hosts = [
            "https://lm-api-reads.fantasy.espn.com",
            "https://fantasy.espn.com",
        ]
        self.api_path = "/apis/v3/games/ffl/seasons/{season}/segments/0/leagues/{league}"
        
        # Load configuration from environment
        self.config = {
            "LEAGUE_ID": os.getenv("LEAGUE_ID"),
            "ESPN_SWID": os.getenv("ESPN_SWID"),
            "ESPN_S2": os.getenv("ESPN_S2"),
            "CURRENT_SEASON": int(os.getenv("CURRENT_SEASON", datetime.now().year)),
            "START_SEASON": int(os.getenv("START_SEASON", 2022)),  # League start year
        }
        
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration"""
        required = ["LEAGUE_ID", "ESPN_SWID", "ESPN_S2"]
        missing = [key for key in required if not self.config.get(key)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    def _get_cookies(self) -> Dict[str, str]:
        """Get authentication cookies"""
        return {
            "SWID": self.config["ESPN_SWID"],
            "espn_s2": self.config["ESPN_S2"]
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        league_id = self.config["LEAGUE_ID"]
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": f"https://fantasy.espn.com/football/league?leagueId={league_id}",
            "Origin": "https://fantasy.espn.com",
            "x-fantasy-platform": "kona",
            "x-fantasy-source": "kona",
            "Connection": "keep-alive",
        }
    
    def _make_request(self, season: int, params: Dict[str, str] = None) -> Dict:
        """Make authenticated request to ESPN API"""
        if params is None:
            params = {}
            
        last_error = None
        
        for host in self.api_hosts:
            url = host + self.api_path.format(
                season=season, 
                league=self.config["LEAGUE_ID"]
            )
            
            try:
                response = requests.get(
                    url,
                    params=params,
                    cookies=self._get_cookies(),
                    headers=self._get_headers(),
                    timeout=30,
                    allow_redirects=False
                )
                
                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        return response.json()
                
                last_error = f"HTTP {response.status_code} from {url}"
                
            except Exception as e:
                last_error = f"Request failed for {url}: {str(e)}"
                continue
        
        raise Exception(f"All API hosts failed. Last error: {last_error}")
    
    def get_league_info(self) -> Dict[str, Any]:
        """Get basic league information"""
        current_season = self.config["CURRENT_SEASON"]
        
        try:
            data = self._make_request(current_season, {"view": "mSettings"})
            settings = data.get("settings", {})
            
            return {
                "name": settings.get("name", "Fantasy League"),
                "season": current_season,
                "size": settings.get("size", 10),
                "scoring_type": settings.get("scoringSettings", {}).get("scoringType", "STANDARD"),
                "playoff_teams": settings.get("scheduleSettings", {}).get("playoffTeamCount", 4),
                "regular_season_matchups": settings.get("scheduleSettings", {}).get("matchupPeriodCount", 14),
            }
        except Exception as e:
            # Return default info if API fails
            return {
                "name": "Fantasy League",
                "season": current_season,
                "size": 10,
                "scoring_type": "STANDARD",
                "playoff_teams": 4,
                "regular_season_matchups": 14,
            }
    
    def get_current_season(self) -> Dict[str, Any]:
        """Get current season standings and basic info"""
        current_season = self.config["CURRENT_SEASON"]
        
        try:
            data = self._make_request(current_season, {"view": "mTeam"})
            teams = data.get("teams", [])
            
            standings = []
            for team in teams:
                team_id = team.get("id")
                team_info = {
                    "id": team_id,
                    "name": self._get_team_name(team),
                    "owner": self._map_team_to_owner(team_id),  # Use proper team mapping
                    "wins": team.get("record", {}).get("overall", {}).get("wins", 0),
                    "losses": team.get("record", {}).get("overall", {}).get("losses", 0),
                    "ties": team.get("record", {}).get("overall", {}).get("ties", 0),
                    "points_for": team.get("record", {}).get("overall", {}).get("pointsFor", 0),
                    "points_against": team.get("record", {}).get("overall", {}).get("pointsAgainst", 0),
                    "playoff_seed": team.get("playoffSeed", 0),
                }
                team_info["win_percentage"] = round(
                    team_info["wins"] / max(1, team_info["wins"] + team_info["losses"])
                    if team_info["wins"] + team_info["losses"] > 0 else 0, 2
                )
                standings.append(team_info)
            
            # Sort by playoff seed (or wins if no playoff seed)
            standings.sort(key=lambda x: (x["playoff_seed"] or 999, -x["wins"], -x["points_for"]))
            
            return {
                "season": current_season,
                "standings": standings,
                "total_teams": len(standings)
            }
            
        except Exception as e:
            return {
                "season": current_season,
                "standings": [],
                "total_teams": 0,
                "error": str(e)
            }
    
    def get_season_data(self, season: int) -> Dict[str, Any]:
        """Get comprehensive data for a specific season"""
        try:
            # Get multiple views of data
            team_data = self._make_request(season, {"view": "mTeam"})
            matchup_data = self._make_request(season, {"view": "mMatchup"})
            
            teams = team_data.get("teams", [])
            schedule = matchup_data.get("schedule", [])
            
            season_info = {
                "season": season,
                "teams": [],
                "matchups": [],
                "champion": None,
                "runner_up": None,
            }
            
            # Process teams
            for team in teams:
                team_id = team.get("id")
                team_info = {
                    "id": team_id,
                    "name": self._get_team_name(team),
                    "owner": self._map_team_to_owner(team_id),  # Use proper team mapping
                    "record": team.get("record", {}).get("overall", {}),
                    "playoff_seed": team.get("playoffSeed", 0),
                    "final_rank": team.get("rankCalculatedFinal", 0),
                }
                season_info["teams"].append(team_info)
            
            # Process matchups
            for matchup in schedule:
                if matchup.get("matchupPeriodId", 0) > 0:  # Valid matchup
                    matchup_info = {
                        "week": matchup.get("matchupPeriodId"),
                        "playoff": matchup.get("playoffTierType") == "WINNERS_BRACKET",
                        "teams": []
                    }
                    
                    for team in matchup.get("away", {}).get("teamId"), matchup.get("home", {}).get("teamId"):
                        if team:
                            team_data = next((t for t in teams if t.get("id") == team), {})
                            matchup_info["teams"].append({
                                "id": team,
                                "name": self._get_team_name(team_data),
                                "owner": self._map_team_to_owner(team),  # Add owner mapping
                                "score": matchup.get("away", {}).get("totalPoints", 0) if team == matchup.get("away", {}).get("teamId") else matchup.get("home", {}).get("totalPoints", 0)
                            })
                    
                    season_info["matchups"].append(matchup_info)
            
            # Find champion (rank 1) and runner-up (rank 2)
            sorted_teams = sorted(season_info["teams"], key=lambda x: x["final_rank"] or 999)
            if sorted_teams:
                season_info["champion"] = sorted_teams[0] if sorted_teams[0]["final_rank"] == 1 else None
                season_info["runner_up"] = sorted_teams[1] if len(sorted_teams) > 1 and sorted_teams[1]["final_rank"] == 2 else None
            
            return season_info
            
        except Exception as e:
            return {
                "season": season,
                "teams": [],
                "matchups": [],
                "champion": None,
                "runner_up": None,
                "error": str(e)
            }
    
    def get_historical_data(self) -> List[Dict[str, Any]]:
        """Get data for all seasons"""
        start_season = self.config["START_SEASON"]
        current_season = self.config["CURRENT_SEASON"]
        
        historical_data = []
        
        for season in range(start_season, current_season + 1):
            season_data = self.get_season_data(season)
            historical_data.append(season_data)
        
        return historical_data
    
    def _get_team_name(self, team_data: Dict) -> str:
        """Extract team name from team data"""
        if isinstance(team_data, dict):
            # Try different name fields
            name = (
                team_data.get("name") or
                f"{team_data.get('location', '')} {team_data.get('nickname', '')}".strip() or
                f"Team {team_data.get('id', 'Unknown')}"
            )
            return name
        return "Unknown Team"
    
    def _get_owner_name(self, owner_data: Any) -> str:
        """Map ESPN owner UUID/ID to readable owner name"""
        if isinstance(owner_data, str):
            # Check if it's a UUID string we can map
            mapped_name = OWNER_UUID_MAP.get(owner_data)
            if mapped_name:
                return mapped_name
            # If it starts with '{' it's likely a UUID we haven't mapped yet
            if owner_data.startswith('{') and owner_data.endswith('}'):
                return f"Owner {owner_data[:8]}..."  # Show partial UUID as fallback
            return owner_data
        elif isinstance(owner_data, dict):
            # Sometimes ESPN returns owner as an object
            return owner_data.get("displayName", owner_data.get("firstName", "Unknown"))
        else:
            return "Unknown Owner"
    
    def _map_team_to_owner(self, team_id: int) -> str:
        """Map team ID to owner name using our team mapping"""
        team_key = TEAM_ID_MAP.get(team_id)
        if team_key:
            return TEAM_TO_OWNER_MAP.get(team_key, "Unknown Owner")
        return "Unknown Owner"
    
    def refresh_data(self):
        """Refresh cached data (placeholder for future caching implementation)"""
        # This could clear any cached data and force fresh API calls
        pass
    
    def get_team_mapping(self) -> Dict[int, str]:
        """Get the team ID mapping"""
        return TEAM_ID_MAP
