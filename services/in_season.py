"""
In-Season Analysis Service
Provides real-time insights, matchup analysis, and current season trends
"""

from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
import statistics
from datetime import datetime
from services.espn_dashboard import ESPNDashboardService
from services.ai_service import AIService
from config.team_map import TEAM_ID_MAP, TEAM_TO_OWNER_MAP


class InSeasonService:
    """Service for analyzing current season trends and matchups"""
    
    def __init__(self):
        self.espn_service = ESPNDashboardService()
        self.ai_service = AIService()
        self._cached_current_data = None
        
    def _get_current_season_data(self) -> Dict[str, Any]:
        """Get current season data with caching"""
        if self._cached_current_data is None:
            current_season = self.espn_service.config["CURRENT_SEASON"]
            self._cached_current_data = self.espn_service.get_season_data(current_season)
        return self._cached_current_data
    

    
    def get_recent_performances(self, weeks_back: int = 3) -> Dict[str, Any]:
        """Analyze recent team performances over the last N weeks"""
        season_data = self._get_current_season_data()
        matchups = season_data.get("matchups", [])
        
        if not matchups:
            return {"error": "No matchup data available"}
            
        # Find the most recent weeks with data
        weeks_with_data = sorted([m["week"] for m in matchups if m.get("teams")])
        recent_weeks = weeks_with_data[-weeks_back:] if len(weeks_with_data) >= weeks_back else weeks_with_data
        
        team_performances = defaultdict(lambda: {
            "recent_scores": [],
            "owner": "Unknown", 
            "avg_recent": 0,
            "trend": "stable",
            "best_week": {"week": 0, "score": 0},
            "worst_week": {"week": 0, "score": 0}
        })
        
        # Analyze recent matchups
        for matchup in matchups:
            if matchup["week"] in recent_weeks:
                for team in matchup.get("teams", []):
                    team_id = team["id"]
                    score = team["score"]
                    owner = team.get("owner", "Unknown")
                    
                    perf = team_performances[team_id]
                    perf["owner"] = owner
                    perf["recent_scores"].append({
                        "week": matchup["week"],
                        "score": score
                    })
                    
                    # Track best and worst performances
                    if score > perf["best_week"]["score"]:
                        perf["best_week"] = {"week": matchup["week"], "score": score}
                    if perf["worst_week"]["score"] == 0 or score < perf["worst_week"]["score"]:
                        perf["worst_week"] = {"week": matchup["week"], "score": score}
        
        # Calculate trends and insights
        performance_insights = []
        for team_id, perf in team_performances.items():
            if len(perf["recent_scores"]) >= 1:  # Changed from 2 to 1 to show data with fewer games
                scores = [s["score"] for s in perf["recent_scores"]]
                perf["avg_recent"] = round(statistics.mean(scores), 2)
                
                # Calculate trend (simple: comparing first half to second half of recent games)
                if len(scores) >= 2:
                    mid_point = len(scores) // 2
                    if mid_point > 0:
                        early_avg = statistics.mean(scores[:mid_point])
                        late_avg = statistics.mean(scores[mid_point:])
                        
                        if late_avg > early_avg * 1.1:  # 10% improvement
                            perf["trend"] = "hot"
                        elif late_avg < early_avg * 0.9:  # 10% decline
                            perf["trend"] = "cold"
                        else:
                            perf["trend"] = "stable"
                else:
                    # With only 1 game, check if it's above or below league average estimate
                    if scores[0] > 110:  # Rough estimate for good performance
                        perf["trend"] = "hot"
                    elif scores[0] < 90:
                        perf["trend"] = "cold"
                    else:
                        perf["trend"] = "stable"
                
                performance_insights.append({
                    "team_id": team_id,
                    "owner": perf["owner"],
                    "avg_recent": perf["avg_recent"],
                    "trend": perf["trend"],
                    "best_week": perf["best_week"],
                    "worst_week": perf["worst_week"],
                    "recent_scores": perf["recent_scores"]
                })
        
        # Sort by recent average
        performance_insights.sort(key=lambda x: x["avg_recent"], reverse=True)
        
        return {
            "weeks_analyzed": recent_weeks,
            "performances": performance_insights,
            "league_avg_recent": round(statistics.mean([p["avg_recent"] for p in performance_insights]), 2) if performance_insights else 0
        }
    
    def get_matchup_previews(self) -> Dict[str, Any]:
        """Get insights for upcoming matchups"""
        season_data = self._get_current_season_data()
        current_season = self.espn_service.config["CURRENT_SEASON"]
        
        # For now, we'll analyze recent head-to-head trends
        # This could be enhanced with roster analysis, player news, etc.
        
        matchups = season_data.get("matchups", [])
        if not matchups:
            return {"error": "No matchup data available"}
            
        # Find current week
        weeks_with_data = [m["week"] for m in matchups if m.get("teams")]
        current_week = max(weeks_with_data) if weeks_with_data else 1
        next_week = current_week + 1
        
        # Get recent form for predictions
        recent_perf = self.get_recent_performances(weeks_back=4)
        
        previews = []
        insights = [
            "🔥 This team is on fire lately!",
            "📈 Strong upward trend in recent weeks",
            "⚡ Explosive potential - could break out big",
            "🎯 Consistent performer, expect steady production",
            "❄️ Cold streak might continue",
            "📉 Struggling recently, due for a bounce-back?",
            "🎲 Unpredictable team - could go either way",
            "⭐ Star players heating up at the right time"
        ]
        
        if recent_perf.get("performances"):
            # Create mock matchup previews based on recent performance
            perfs = recent_perf["performances"]
            
            for i in range(0, len(perfs) - 1, 2):
                if i + 1 < len(perfs):
                    team1 = perfs[i]
                    team2 = perfs[i + 1]
                    
                    # Determine favorite based on recent form
                    favorite = team1 if team1["avg_recent"] > team2["avg_recent"] else team2
                    underdog = team2 if favorite == team1 else team1
                    
                    preview = {
                        "team1": {
                            "owner": team1["owner"],
                            "recent_avg": team1["avg_recent"],
                            "trend": team1["trend"],
                            "insight": self._get_team_insight(team1)
                        },
                        "team2": {
                            "owner": team2["owner"],
                            "recent_avg": team2["avg_recent"],
                            "trend": team2["trend"],
                            "insight": self._get_team_insight(team2)
                        },
                        "prediction": {
                            "favorite": favorite["owner"],
                            "confidence": "High" if abs(team1["avg_recent"] - team2["avg_recent"]) > 20 else "Medium",
                            "key_factor": self._get_matchup_factor(team1, team2)
                        }
                    }
                    previews.append(preview)
        
        return {
            "current_week": current_week,
            "next_week": next_week,
            "matchup_previews": previews[:4],  # Limit to 4 previews
            "analysis_note": f"Analysis based on last 4 weeks of performance data"
        }
    
    def get_ai_analysis(self) -> Dict[str, Any]:
        """Get AI-powered trash talk and weekly recap"""
        try:
            season_data = self._get_current_season_data()
            ai_status = self.ai_service.get_status()

            # Check if we have sufficient data for AI analysis
            if not season_data.get("matchups") or len(season_data.get("matchups", [])) == 0:
                return {
                    "status": "waiting_for_data",
                    "message": "🤖 The AI Trash-Talker is warming up! Weekly roasts and matchup previews will be available once the season begins.",
                    "features": [
                        "🔥 Weekly recap roast sessions",
                        "💀 Shame corner for disappointing teams", 
                        "👑 Props for dominant performances",
                        "🎯 Upcoming matchup trash talk",
                        "📊 AI-powered storylines and rivalries"
                    ],
                    "ai_status": ai_status
                }

            # Check if AI service is available
            if not ai_status["ai_available"]:
                return {
                    "status": "ai_unavailable",
                    "message": "No AI service available. Configure OPENAI_API_KEY or ANTHROPIC_API_KEY for cloud AI.",
                    "ai_status": ai_status,
                    "setup_instructions": ai_status["setup_instructions"]
                }

            # AI is ready and we have data - generate trash talk!
            insights = self.ai_service.analyze_league_data(season_data)

            return {
                "status": "ready",
                "ai_status": ai_status,
                "insights": insights,
                "content_type": "trash_talk",
                "description": "AI-generated weekly roasts, props, and matchup previews"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"AI trash-talker is having technical difficulties: {str(e)}"
            }
    

    
    def get_weekly_highlights(self) -> Dict[str, Any]:
        """Get notable performances and storylines from recent weeks"""
        recent_perf = self.get_recent_performances(weeks_back=2)
        
        if not recent_perf.get("performances"):
            return {"error": "No recent performance data"}
            
        performances = recent_perf["performances"]
        league_avg = recent_perf["league_avg_recent"]
        
        highlights = []
        
        # Find notable performances
        for perf in performances:
            recent_scores = [s["score"] for s in perf["recent_scores"]]
            max_score = max(recent_scores)
            min_score = min(recent_scores)
            
            # High scorer highlight
            if max_score > league_avg * 1.3:  # 30% above average
                highlights.append({
                    "type": "explosion",
                    "owner": perf["owner"],
                    "title": f"🚀 {perf['owner']} Exploded for {max_score:.1f} Points!",
                    "description": f"Massive week {perf['best_week']['week']} performance, {(max_score - league_avg):.1f} points above league average",
                    "impact": "high"
                })
            
            # Struggle highlight
            if min_score < league_avg * 0.7:  # 30% below average
                highlights.append({
                    "type": "struggle",
                    "owner": perf["owner"],
                    "title": f"😰 {perf['owner']} Had a Rough Week",
                    "description": f"Only managed {min_score:.1f} points in week {perf['worst_week']['week']}, {(league_avg - min_score):.1f} below average",
                    "impact": "low"
                })
            
            # Hot streak
            if perf["trend"] == "hot":
                highlights.append({
                    "type": "hot_streak",
                    "owner": perf["owner"],
                    "title": f"🔥 {perf['owner']} is Heating Up!",
                    "description": f"Trending upward with {perf['avg_recent']:.1f} points per game recently",
                    "impact": "medium"
                })
        
        # Sort by impact and limit
        impact_order = {"high": 3, "medium": 2, "low": 1}
        highlights.sort(key=lambda x: impact_order.get(x["impact"], 0), reverse=True)
        
        return {
            "highlights": highlights[:6],  # Top 6 highlights
            "league_context": {
                "avg_recent": league_avg,
                "weeks_analyzed": recent_perf.get("weeks_analyzed", [])
            }
        }
    
    def _get_team_insight(self, team_perf: Dict[str, Any]) -> str:
        """Generate insight text for a team based on their performance"""
        trend = team_perf["trend"]
        avg = team_perf["avg_recent"]
        
        if trend == "hot" and avg > 120:
            return "🔥 Red hot and putting up big numbers - scary matchup"
        elif trend == "hot":
            return "📈 Trending up at the right time"
        elif trend == "cold" and avg < 90:
            return "❄️ In a cold spell - could be due for a bounce-back"
        elif trend == "cold":
            return "📉 Cooling off recently, looking to rebound"
        elif avg > 130:
            return "⚡ Consistent high-end production"
        elif avg > 110:
            return "🎯 Solid and reliable option"
        else:
            return "🎲 Unpredictable - could surprise either way"
    
    def _get_matchup_factor(self, team1: Dict[str, Any], team2: Dict[str, Any]) -> str:
        """Determine the key factor in a matchup"""
        trend1, trend2 = team1["trend"], team2["trend"]
        
        if trend1 == "hot" and trend2 == "cold":
            return f"{team1['owner']}'s hot streak vs {team2['owner']}'s struggles"
        elif trend1 == "cold" and trend2 == "hot":
            return f"{team2['owner']}'s momentum vs {team1['owner']}'s cold spell"
        elif abs(team1["avg_recent"] - team2["avg_recent"]) > 25:
            higher = team1 if team1["avg_recent"] > team2["avg_recent"] else team2
            return f"{higher['owner']}'s superior recent form"
        else:
            return "Both teams evenly matched - could go either way"
    
    def get_in_season_dashboard(self) -> Dict[str, Any]:
        """Get complete in-season analysis dashboard"""
        try:
            recent_performances = self.get_recent_performances()
            matchup_previews = self.get_matchup_previews()
            weekly_highlights = self.get_weekly_highlights()
            ai_analysis = self.get_ai_analysis()
            
            return {
                "recent_performances": recent_performances,
                "matchup_previews": matchup_previews,
                "weekly_highlights": weekly_highlights,
                "ai_analysis": ai_analysis,
                "current_season": self.espn_service.config["CURRENT_SEASON"],
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {
                "error": f"Failed to load in-season analysis: {str(e)}",
                "current_season": self.espn_service.config.get("CURRENT_SEASON", "Unknown")
            }
