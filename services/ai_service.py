"""
AI Service
Integrates with cloud AI services for production-ready league analysis and insights
Supports multiple AI providers with fallback options
"""

import requests
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import AI SDKs with graceful fallbacks
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True  
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AIService:
    """Service for AI-powered analysis using cloud AI providers"""
    
    def __init__(self):
        # AI Provider Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY") 
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        # Default model preferences (in order of preference)
        self.model_preferences = [
            {"provider": "openai", "model": "gpt-4o-mini", "requires_key": True},
            {"provider": "anthropic", "model": "claude-3-haiku-20240307", "requires_key": True},
            {"provider": "ollama", "model": "llama3.2", "requires_key": False},
        ]
        
    def get_available_provider(self) -> Optional[Dict[str, Any]]:
        """Get the first available AI provider based on preferences"""
        for provider_config in self.model_preferences:
            if self._is_provider_available(provider_config):
                return provider_config
        return None
    
    def _is_provider_available(self, provider_config: Dict[str, Any]) -> bool:
        """Check if a specific AI provider is available"""
        provider = provider_config["provider"]
        requires_key = provider_config["requires_key"]
        
        if provider == "openai" and requires_key:
            return bool(self.openai_api_key) and OPENAI_AVAILABLE
        elif provider == "anthropic" and requires_key:
            return bool(self.anthropic_api_key) and ANTHROPIC_AVAILABLE
        elif provider == "ollama":
            try:
                response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
                return response.status_code == 200
            except Exception:
                return False
        return False
    
    def is_available(self) -> bool:
        """Check if any AI provider is available"""
        return self.get_available_provider() is not None
    
    def analyze_league_data(self, season_data: Dict[str, Any], question: str = None) -> Dict[str, Any]:
        """Analyze league data using AI and return insights"""
        
        provider = self.get_available_provider()
        if not provider:
            return {
                "status": "unavailable",
                "message": "No AI service available. Configure OPENAI_API_KEY or ANTHROPIC_API_KEY for cloud AI.",
                "suggestion": "Add an AI API key to your environment variables for hosted deployment."
            }
        
        # Prepare league data summary for AI analysis
        data_summary = self._prepare_data_summary(season_data)
        
        if question:
            # Answer specific question about the league
            return self._answer_question(data_summary, question, provider)
        else:
            # Generate general insights
            return self._generate_insights(data_summary, provider)
    
    def analyze_what_could_have_scored(self, team_data: Dict[str, Any], week: int) -> Dict[str, Any]:
        """Analyze what a team could have scored with optimal lineup"""
        
        if not self.is_available():
            return {
                "status": "unavailable",
                "message": "AI analysis requires Ollama to be running"
            }
        
        # This would require roster/lineup data from ESPN API
        # For now, return a structured response
        return {
            "status": "needs_roster_data",
            "message": "Optimal lineup analysis requires player roster data from ESPN API",
            "week": week,
            "team": team_data.get("owner", "Unknown")
        }
    
    def _prepare_data_summary(self, season_data: Dict[str, Any]) -> str:
        """Prepare a text summary of league data for AI analysis with historical context"""
        
        summary_parts = []
        
        # Basic season info
        season = season_data.get("season", "Unknown")
        summary_parts.append(f"Fantasy Football League - {season} Season")
        
        # Team information with performance context
        teams = season_data.get("teams", [])
        if teams:
            summary_parts.append(f"\\nCurrent Season Teams ({len(teams)} total):")
            for team in teams[:10]:  # Limit to prevent token overflow
                owner = team.get("owner", "Unknown")
                record = team.get("record", {})
                wins = record.get("wins", 0)
                losses = record.get("losses", 0)
                points = record.get("pointsFor", 0)
                
                # Add performance context
                if points > 0:
                    avg_points = points / max(wins + losses, 1)
                    performance_note = ""
                    if avg_points > 120:
                        performance_note = " (high scorer)"
                    elif avg_points < 80:
                        performance_note = " (struggling offense)"
                    summary_parts.append(f"- {owner}: {wins}-{losses} record, {points:.1f} points{performance_note}")
                else:
                    summary_parts.append(f"- {owner}: {wins}-{losses} record, {points:.1f} points")
        
        # Recent matchups with context
        matchups = season_data.get("matchups", [])
        if matchups:
            recent_matchups = [m for m in matchups if m.get("teams")][-8:]  # Last 8 matchups for more context
            summary_parts.append(f"\\nRecent Matchups (Last {len(recent_matchups)} games):")
            
            # Track head-to-head history
            head_to_head = {}
            blowouts = []
            close_games = []
            
            for matchup in recent_matchups:
                week = matchup.get("week", 0)
                teams = matchup.get("teams", [])
                if len(teams) >= 2:
                    team1 = teams[0]
                    team2 = teams[1]
                    score1 = team1.get('score', 0)
                    score2 = team2.get('score', 0)
                    
                    owner1 = team1.get('owner', 'Team1')
                    owner2 = team2.get('owner', 'Team2')
                    
                    # Track head-to-head
                    matchup_key = tuple(sorted([owner1, owner2]))
                    if matchup_key not in head_to_head:
                        head_to_head[matchup_key] = []
                    head_to_head[matchup_key].append((week, score1, score2, owner1, owner2))
                    
                    # Identify interesting games
                    score_diff = abs(score1 - score2)
                    if score_diff > 50:
                        winner = owner1 if score1 > score2 else owner2
                        loser = owner2 if score1 > score2 else owner1
                        blowouts.append(f"Week {week}: {winner} demolished {loser} ({max(score1, score2):.1f} - {min(score1, score2):.1f})")
                    elif score_diff < 10:
                        close_games.append(f"Week {week}: {owner1} vs {owner2} nail-biter ({score1:.1f} - {score2:.1f})")
                    
                    summary_parts.append(
                        f"Week {week}: {owner1} ({score1:.1f}) vs {owner2} ({score2:.1f})"
                    )
            
            # Add historical context sections
            if blowouts:
                summary_parts.append(f"\\nNotable Blowouts:")
                for blowout in blowouts[-3:]:  # Last 3 blowouts
                    summary_parts.append(f"- {blowout}")
            
            if close_games:
                summary_parts.append(f"\\nThrilling Close Games:")
                for close_game in close_games[-3:]:  # Last 3 close games
                    summary_parts.append(f"- {close_game}")
            
            # Add recurring matchup context
            recurring_matchups = [(k, v) for k, v in head_to_head.items() if len(v) > 1]
            if recurring_matchups:
                summary_parts.append(f"\\nRecurring Rivalries:")
                for (owner1, owner2), games in recurring_matchups:
                    wins1 = sum(1 for g in games if (g[3] == owner1 and g[1] > g[2]) or (g[3] == owner2 and g[2] > g[1] and g[4] == owner1))
                    wins2 = len(games) - wins1
                    summary_parts.append(f"- {owner1} vs {owner2}: {wins1}-{wins2} series record over {len(games)} recent games")
        
        # Add league context
        if teams:
            total_points = sum(team.get("record", {}).get("pointsFor", 0) for team in teams)
            avg_league_points = total_points / len(teams) if teams else 0
            summary_parts.append(f"\\nLeague Context:")
            summary_parts.append(f"- Average team score: {avg_league_points:.1f} points")
            
            # Find highest and lowest scorers
            sorted_teams = sorted(teams, key=lambda t: t.get("record", {}).get("pointsFor", 0), reverse=True)
            if len(sorted_teams) >= 2:
                highest = sorted_teams[0].get("owner", "Unknown")
                lowest = sorted_teams[-1].get("owner", "Unknown")
                summary_parts.append(f"- Highest scorer: {highest}")
                summary_parts.append(f"- Needs offensive help: {lowest}")
        
        return "\\n".join(summary_parts)
    
    def _answer_question(self, data_summary: str, question: str, provider: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to answer a specific question about the league"""
        
        prompt = f"""You are an expert fantasy football analyst. Based on the following league data, please answer this question: "{question}"

League Data:
{data_summary}

Please provide a detailed analysis that includes:
1. Direct answer to the question
2. Supporting data/evidence
3. Any relevant insights or trends
4. Recommendations if applicable

Keep the response conversational and engaging, as if talking to league members."""

        try:
            response = self._call_ai_provider(prompt, provider)
            return {
                "status": "success",
                "question": question,
                "answer": response,
                "provider": provider["provider"],
                "model": provider["model"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI analysis failed: {str(e)}"
            }
    
    def _generate_insights(self, data_summary: str, provider: Dict[str, Any]) -> Dict[str, Any]:
        """Generate entertaining trash talk and matchup analysis"""
        
        prompt = f"""You are the league's official AI trash-talker and hype man! Your personality is sassy, witty, and entertaining - like a sports radio shock jock meets fantasy football expert. 

Your job is to create SPICY weekly content that gets everyone fired up. Use the historical context and rivalries provided to make your trash talk more personal and entertaining.

League Data with Historical Context:
{data_summary}

Write an entertaining weekly analysis with these sections:

🔥 **WEEK RECAP ROAST SESSION**
- Call out teams that choked or got lucky
- Reference past performances and patterns ("Remember when...")
- Create callbacks to previous matchups and seasons
- Celebrate dominant performances (but keep them humble)

💀 **SHAME CORNER** 
- Roast the biggest disappointments with historical context
- Mock teams who are repeating past mistakes
- Reference their previous struggles or embarrassing losses
- Point out if they're falling into old bad habits

👑 **PROPS WHERE DUE**
- Give credit to standout performers 
- Compare current success to their historical performance
- Acknowledge improvement from past struggles
- Highlight if they're breaking personal records or patterns

🎯 **UPCOMING MATCHUP TRASH TALK**
- Reference head-to-head history between upcoming opponents
- Bring up past grudges, revenge games, or dominant streaks
- Predict based on historical matchup patterns
- Create storylines around recurring rivalries

Use the provided blowouts, close games, and recurring rivalries data to make your commentary more engaging. Reference specific past games and scores when trash talking. Keep it fun, competitive, and engaging. Use emojis and personality. Be witty but not mean-spirited. Maximum 450 words. Think ESPN SportsCenter highlights meets fantasy football banter with a memory!"""

        try:
            response = self._call_ai_provider(prompt, provider)
            return {
                "status": "success",
                "insights": response,
                "provider": provider["provider"],
                "model": provider["model"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI analysis failed: {str(e)}"
            }
    
    def _call_ai_provider(self, prompt: str, provider: Dict[str, Any]) -> str:
        """Make API call to the specified AI provider"""
        
        provider_name = provider["provider"]
        model = provider["model"]
        
        if provider_name == "openai":
            return self._call_openai(prompt, model)
        elif provider_name == "anthropic":
            return self._call_anthropic(prompt, model)
        elif provider_name == "ollama":
            return self._call_ollama(prompt, model)
        else:
            raise Exception(f"Unsupported AI provider: {provider_name}")
    
    def _call_openai(self, prompt: str, model: str) -> str:
        """Make API call to OpenAI using SDK"""
        
        if not OPENAI_AVAILABLE:
            raise Exception("OpenAI package not installed")
        
        try:
            # Create client with minimal configuration
            client = openai.OpenAI(
                api_key=self.openai_api_key,
                timeout=60.0
            )
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert fantasy football analyst. Provide detailed, engaging analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _call_anthropic(self, prompt: str, model: str) -> str:
        """Make API call to Anthropic Claude using SDK"""
        
        if not ANTHROPIC_AVAILABLE:
            raise Exception("Anthropic package not installed")
            
        client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        
        try:
            response = client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"You are an expert fantasy football analyst. {prompt}"
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def _call_ollama(self, prompt: str, model: str) -> str:
        """Make API call to Ollama (for local development)"""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            f"{self.ollama_host}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response generated")
        else:
            raise Exception(f"Ollama API error: {response.status_code}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get AI service status and capabilities"""
        
        available_provider = self.get_available_provider()
        is_available = available_provider is not None
        
        # Check status of each provider
        provider_status = {}
        for config in self.model_preferences:
            provider_status[config["provider"]] = {
                "available": self._is_provider_available(config),
                "model": config["model"],
                "requires_key": config["requires_key"]
            }
        
        return {
            "ai_available": is_available,
            "active_provider": available_provider,
            "provider_status": provider_status,
            "capabilities": [
                "League data analysis and insights",
                "Question answering about team performance", 
                "Trend identification and predictions",
                "Historical performance analysis",
                "Natural language conversation about league"
            ] if is_available else [],
            "setup_instructions": [
                "For hosted deployment (recommended):",
                "1. Set OPENAI_API_KEY environment variable with your OpenAI API key",
                "2. Or set ANTHROPIC_API_KEY for Claude AI",
                "3. Get API keys from https://platform.openai.com or https://console.anthropic.com",
                "",
                "For local development:",
                "1. Install Ollama: https://ollama.ai", 
                "2. Run 'ollama pull llama3.2' to download the model",
                "3. Run 'ollama serve' to start the service"
            ] if not is_available else []
        }
