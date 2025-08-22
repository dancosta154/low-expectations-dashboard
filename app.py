"""
ESPN Fantasy Football Dashboard
A Flask application for analyzing and displaying ESPN Fantasy Football league data
"""

from flask import Flask, render_template, jsonify, request
import os
from dotenv import load_dotenv
from services.analytics import AnalyticsService
from services.espn_dashboard import ESPNDashboardService
from services.payout_service import PayoutService
from services.in_season import InSeasonService
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
espn_service = ESPNDashboardService()
analytics_service = AnalyticsService()
payout_service = PayoutService()
in_season_service = InSeasonService()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        # Get current season overview
        current_season = espn_service.get_current_season()
        league_info = espn_service.get_league_info()
        
        # Get quick stats for dashboard cards
        quick_stats = analytics_service.get_dashboard_summary()
        
        return render_template('dashboard.html', 
                             current_season=current_season,
                             league_info=league_info,
                             quick_stats=quick_stats)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/champions')
def champions():
    """League champions page"""
    try:
        champions_data = analytics_service.get_champions_history()
        return render_template('champions.html', champions=champions_data)
    except Exception as e:
        logger.error(f"Error loading champions: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/stats')
def stats():
    """League statistics page"""
    try:
        # Get various statistics
        scoring_stats = analytics_service.get_scoring_stats()
        season_stats = analytics_service.get_season_stats()
        all_time_stats = analytics_service.get_all_time_stats()
        
        return render_template('stats.html', 
                             scoring_stats=scoring_stats,
                             season_stats=season_stats,
                             all_time_stats=all_time_stats)
    except Exception as e:
        logger.error(f"Error loading stats: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/matchups')
def matchups():
    """Head-to-head matchup analysis"""
    try:
        matchup_data = analytics_service.get_head_to_head_stats()
        return render_template('matchups.html', matchups=matchup_data)
    except Exception as e:
        logger.error(f"Error loading matchups: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/payouts')
def payouts():
    """League payout tracking and analysis"""
    try:
        all_season_payouts = payout_service.get_all_season_payouts()
        cumulative_payouts = payout_service.get_cumulative_payouts()
        payout_summary = payout_service.get_payout_summary()

        return render_template('payouts.html',
                             season_payouts=all_season_payouts,
                             cumulative_payouts=cumulative_payouts,
                             summary=payout_summary)
    except Exception as e:
        logger.error(f"Error loading payouts: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/in-season')
def in_season():
    """In-season analysis and matchup insights"""
    try:
        analysis = in_season_service.get_in_season_dashboard()
        
        return render_template('in_season.html', analysis=analysis)
    except Exception as e:
        logger.error(f"Error loading in-season analysis: {e}")
        return render_template('error.html', error=str(e)), 500





@app.route('/api/stats/<stat_type>')
def api_stats(stat_type):
    """API endpoint for retrieving specific stats"""
    try:
        if stat_type == 'scoring':
            data = analytics_service.get_scoring_stats()
        elif stat_type == 'champions':
            data = analytics_service.get_champions_history()

        elif stat_type == 'matchups':
            data = analytics_service.get_head_to_head_stats()
        elif stat_type == 'payouts':
            data = payout_service.get_cumulative_payouts()
        elif stat_type == 'in_season':
            data = in_season_service.get_in_season_dashboard()
        else:
            return jsonify({'error': 'Invalid stat type'}), 400
            
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in API endpoint {stat_type}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh')
def api_refresh():
    """Refresh league data"""
    try:
        espn_service.refresh_data()
        return jsonify({'success': True, 'message': 'Data refreshed successfully'})
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == '__main__':
    # Development server
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
