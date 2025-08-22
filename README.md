# ESPN Fantasy Football Dashboard

A comprehensive Flask-based dashboard for analyzing your ESPN Fantasy Football league with beautiful visualizations, historical data, and fun statistics.

![Dashboard Preview](https://img.shields.io/badge/Status-Ready_to_Deploy-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

## 🏈 Features

### 📊 Dashboard Pages
- **Main Dashboard**: Current season overview, quick stats, and standings
- **Champions Hall**: Championship history and winner statistics
- **League Statistics**: Scoring records, season analysis, and all-time leaders
- **Head-to-Head**: Complete matchup history between all teams
- **Trends Analysis**: League evolution, scoring trends, and competitiveness

### 📈 Analytics
- **Championship Tracking**: Winners, runners-up, and title counts by owner
- **Scoring Records**: Highest/lowest scores, season leaders, weekly averages
- **All-Time Statistics**: Career records, win percentages, playoff appearances
- **Head-to-Head Analysis**: Complete matchup records between teams
- **League Trends**: Scoring evolution, parity analysis, competitiveness tracking

### 🎨 UI Features
- **Modern Design**: Clean, responsive Bootstrap 5 interface
- **Interactive Charts**: Beautiful Chart.js visualizations
- **Mobile Friendly**: Fully responsive design for all devices
- **Real-time Updates**: Refresh data with a single click
- **Error Handling**: Graceful error handling with helpful messages

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <your-repo>
cd espn-api-integration
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with your ESPN league details:

```env
# ESPN League Configuration
LEAGUE_ID=your_league_id_here
ESPN_SWID=your_swid_here
ESPN_S2=your_espn_s2_here

# Season Configuration
CURRENT_SEASON=2024
START_SEASON=2020

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=False
PORT=5000
ENVIRONMENT=production
```

### 3. Get ESPN Credentials

#### Find Your League ID
1. Go to your ESPN Fantasy Football league page
2. Look at the URL: `https://fantasy.espn.com/football/league?leagueId=XXXXXX`
3. The number after `leagueId=` is your LEAGUE_ID

#### Get SWID and ESPN_S2 (for private leagues)
1. Log into ESPN Fantasy Football in your browser
2. Open Developer Tools (F12) → Network tab
3. Refresh the page and look for requests to `fantasy.espn.com`
4. Find the `SWID` and `espn_s2` cookie values in request headers

### 4. Test Your Setup
```bash
python test_setup.py
```

### 5. Run Locally
```bash
python app.py
```

Visit `http://localhost:5000` to see your dashboard!

## ☁️ Deploy to Railway

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Deploy
```bash
railway login
railway init
railway up
```

### 3. Set Environment Variables
In your Railway dashboard, add all the environment variables from your `.env` file.

## 🛠️ Project Structure

```
espn-api-integration/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── railway.json          # Railway deployment config
├── Procfile              # Process file for deployment
├── test_setup.py         # Setup verification script
├── config_guide.md       # Detailed configuration guide
├── README.md             # This file
├── services/
│   ├── espn.py           # Original ESPN API service
│   ├── espn_dashboard.py # Enhanced ESPN service for dashboard
│   └── analytics.py      # Analytics and statistics service
├── config/
│   └── team_map.py       # Team ID mapping
├── templates/
│   ├── base.html         # Base template
│   ├── dashboard.html    # Main dashboard
│   ├── champions.html    # Champions page
│   ├── stats.html        # Statistics page
│   ├── matchups.html     # Head-to-head page
│   ├── trends.html       # Trends analysis
│   └── error.html        # Error page
└── static/
    ├── css/
    │   └── dashboard.css  # Custom styles
    └── js/               # JavaScript files (if any)
```

## 🎯 API Endpoints

- `GET /` - Main dashboard
- `GET /champions` - Championship history
- `GET /stats` - League statistics
- `GET /matchups` - Head-to-head analysis
- `GET /trends` - League trends
- `GET /api/stats/<type>` - JSON API for statistics
- `GET /api/refresh` - Refresh league data

## 🔧 Configuration Options

### Environment Variables
- `LEAGUE_ID` - Your ESPN league ID
- `ESPN_SWID` - ESPN authentication cookie
- `ESPN_S2` - ESPN authentication cookie
- `CURRENT_SEASON` - Current fantasy season year
- `START_SEASON` - First year of league (for historical data)
- `SECRET_KEY` - Flask secret key
- `FLASK_DEBUG` - Debug mode (True/False)
- `PORT` - Server port (default: 5000)
- `ENVIRONMENT` - Environment (development/production)

### Team Mapping
Edit `config/team_map.py` to map ESPN team IDs to friendly names:

```python
TEAM_ID_MAP = {
    1: "team_nickname_1",
    2: "team_nickname_2",
    # ... etc
}
```

## 📊 Analytics Explained

### Scoring Statistics
- **Highest/Lowest Scores**: All-time records with game details
- **Season Leaders**: Top scoring teams by season
- **Weekly Averages**: Scoring trends by week number
- **Overall Stats**: League-wide scoring statistics

### Championship Analysis
- **Champions by Season**: Complete championship history
- **Runner-ups**: Second place finishers by year
- **Owner Records**: Championship counts and finals appearances

### Head-to-Head Records
- **Complete Matchup History**: Win-loss records between all teams
- **Scoring Averages**: Average points scored in matchups
- **Series Leaders**: Who dominates each rivalry

### League Trends
- **Scoring Evolution**: How league scoring has changed over time
- **Parity Analysis**: Measuring league competitiveness
- **Season Comparisons**: Year-over-year league statistics

## 🎨 Customization

### Styling
- Edit `static/css/dashboard.css` for custom styles
- Modify Bootstrap classes in templates
- Add custom JavaScript in template script blocks

### Adding New Analytics
1. Add new methods to `services/analytics.py`
2. Create new routes in `app.py`
3. Build corresponding templates
4. Update navigation in `templates/base.html`

### Extending ESPN Data
- Modify `services/espn_dashboard.py` to fetch additional data
- Update analytics service to process new data types
- Create visualizations for new data

## 🐛 Troubleshooting

### Common Issues

#### "No data available"
- Check ESPN credentials (SWID, ESPN_S2, LEAGUE_ID)
- Verify season dates are correct
- Ensure league has sufficient historical data

#### Authentication errors
- ESPN cookies expire periodically - get fresh ones
- Make sure you're logged into ESPN in the same browser
- Check that your league allows API access

#### Slow loading
- Large leagues with many seasons may take time to load
- Consider implementing caching for production use
- Reduce START_SEASON to limit historical data

#### Deployment issues
- Verify all environment variables are set in Railway
- Check Railway logs for specific error messages
- Ensure requirements.txt includes all dependencies

### Getting Help
1. Run `python test_setup.py` to diagnose issues
2. Check the detailed `config_guide.md`
3. Review Railway/deployment logs
4. Verify ESPN API access in browser developer tools

## 🔮 Future Enhancements

### Potential Features
- **Player Analysis**: Individual player performance tracking
- **Trade History**: Analysis of league trades over time
- **Waiver Wire**: Pickup and drop analysis
- **Playoff Predictor**: Playoff odds calculator
- **Draft Analysis**: Draft performance evaluation
- **Mobile App**: Native mobile application
- **Email Reports**: Automated weekly/seasonal reports
- **Data Export**: CSV/Excel export functionality

### Technical Improvements
- **Database Integration**: Store data for faster access
- **Caching**: Redis/Memcached for performance
- **Background Jobs**: Automated data updates
- **User Authentication**: Multi-league support
- **API Rate Limiting**: Prevent ESPN API abuse
- **Unit Tests**: Comprehensive test suite

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgments

- ESPN for providing the Fantasy Football API
- Flask community for the excellent web framework
- Bootstrap for the responsive UI components
- Chart.js for beautiful data visualizations

---

**Enjoy analyzing your fantasy football league! 🏆**
