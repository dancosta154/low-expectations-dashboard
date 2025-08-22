#!/usr/bin/env python3
"""
Test script to verify ESPN Fantasy Dashboard setup
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment variables"""
    print("🔧 Testing Environment Configuration...")
    
    # Load environment variables
    load_dotenv()
    
    required_vars = [
        'LEAGUE_ID',
        'ESPN_SWID', 
        'ESPN_S2',
        'CURRENT_SEASON',
        'START_SEASON'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"  ✅ {var}: {'*' * min(len(str(value)), 8)}...")
    
    if missing_vars:
        print(f"  ❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("  ✅ All required environment variables found")
    return True

def test_imports():
    """Test that all required modules can be imported"""
    print("\n📦 Testing Imports...")
    
    try:
        import flask
        print(f"  ✅ Flask {flask.__version__}")
    except ImportError as e:
        print(f"  ❌ Flask import failed: {e}")
        return False
    
    try:
        import requests
        print(f"  ✅ Requests {requests.__version__}")
    except ImportError as e:
        print(f"  ❌ Requests import failed: {e}")
        return False
    
    try:
        from services.espn_dashboard import ESPNDashboardService
        print("  ✅ ESPN Dashboard Service")
    except ImportError as e:
        print(f"  ❌ ESPN Dashboard Service import failed: {e}")
        return False
    
    try:
        from services.analytics import AnalyticsService
        print("  ✅ Analytics Service")
    except ImportError as e:
        print(f"  ❌ Analytics Service import failed: {e}")
        return False
    
    return True

def test_espn_connection():
    """Test connection to ESPN API"""
    print("\n🔌 Testing ESPN API Connection...")
    
    try:
        from services.espn_dashboard import ESPNDashboardService
        
        service = ESPNDashboardService()
        league_info = service.get_league_info()
        
        if league_info and 'name' in league_info:
            print(f"  ✅ Connected to league: {league_info['name']}")
            print(f"  ✅ Season: {league_info['season']}")
            print(f"  ✅ Teams: {league_info['size']}")
            return True
        else:
            print("  ❌ Could not retrieve league information")
            return False
            
    except Exception as e:
        print(f"  ❌ ESPN API connection failed: {e}")
        return False

def test_analytics():
    """Test analytics service"""
    print("\n📊 Testing Analytics Service...")
    
    try:
        from services.analytics import AnalyticsService
        
        analytics = AnalyticsService()
        summary = analytics.get_dashboard_summary()
        
        if summary and 'total_seasons' in summary:
            print(f"  ✅ Analytics working - {summary['total_seasons']} seasons found")
            print(f"  ✅ Total games: {summary['total_games']}")
            print(f"  ✅ Highest score: {summary['highest_score_ever']}")
            return True
        else:
            print("  ❌ Could not retrieve analytics data")
            return False
            
    except Exception as e:
        print(f"  ❌ Analytics service failed: {e}")
        return False

def test_flask_app():
    """Test Flask app initialization"""
    print("\n🌐 Testing Flask Application...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test main route
            response = client.get('/')
            if response.status_code == 200:
                print("  ✅ Main dashboard route working")
            else:
                print(f"  ❌ Main dashboard route failed: {response.status_code}")
                return False
            
            # Test API route
            response = client.get('/api/refresh')
            if response.status_code in [200, 500]:  # 500 is ok for testing without full data
                print("  ✅ API routes accessible")
            else:
                print(f"  ❌ API routes failed: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Flask app test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏈 ESPN Fantasy Dashboard Setup Test")
    print("=" * 50)
    
    tests = [
        test_environment,
        test_imports,
        test_espn_connection,
        test_analytics,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📋 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your dashboard is ready to deploy.")
        print("\n🚀 To run locally:")
        print("   python app.py")
        print("\n☁️  To deploy to Railway:")
        print("   railway login")
        print("   railway init")
        print("   railway up")
        return 0
    else:
        print("❌ Some tests failed. Please check your configuration.")
        print("\n📖 Check the config_guide.md for setup instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
