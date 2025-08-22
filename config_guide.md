# ESPN Fantasy Football Dashboard Configuration Guide

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# ESPN League Configuration
LEAGUE_ID=your_league_id_here
ESPN_SWID=your_swid_here
ESPN_S2=your_espn_s2_here

# Season Configuration
CURRENT_SEASON=2024
START_SEASON=2020

# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_DEBUG=False

# Server Configuration
PORT=5000

# Environment
ENVIRONMENT=production
```

## Getting ESPN API Credentials

### 1. Finding Your League ID
- Go to your ESPN Fantasy Football league page
- Look at the URL: `https://fantasy.espn.com/football/league?leagueId=XXXXXX`
- The number after `leagueId=` is your LEAGUE_ID

### 2. Getting SWID and ESPN_S2
These are authentication cookies needed for private leagues:

#### Method 1: Browser Developer Tools
1. Log into ESPN Fantasy Football in your browser
2. Open Developer Tools (F12)
3. Go to the Network tab
4. Refresh the page
5. Look for any request to `fantasy.espn.com`
6. In the request headers, find:
   - `SWID` cookie value
   - `espn_s2` cookie value

#### Method 2: Browser Console
1. Log into ESPN Fantasy Football
2. Open Browser Console (F12)
3. Type: `document.cookie`
4. Look for SWID and espn_s2 values in the output

### 3. Season Configuration
- `CURRENT_SEASON`: The current fantasy season year
- `START_SEASON`: The first year your league started (for historical data)

## Railway Deployment

### 1. Prepare for Railway
1. Create a Railway account at railway.app
2. Install Railway CLI: `npm install -g @railway/cli`
3. Login: `railway login`

### 2. Deploy
```bash
# Initialize Railway project
railway init

# Add environment variables in Railway dashboard
# Deploy
railway up
```

### 3. Environment Variables in Railway
Set these in your Railway project dashboard:
- LEAGUE_ID
- ESPN_SWID
- ESPN_S2
- CURRENT_SEASON
- START_SEASON
- SECRET_KEY
- ENVIRONMENT=production

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create `.env` file with the configuration above.

### 3. Run Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Troubleshooting

### Authentication Issues
- Make sure SWID and ESPN_S2 are current (they can expire)
- Ensure your league is accessible with these credentials
- Check that LEAGUE_ID is correct

### No Data Issues
- Verify season dates are correct
- Check if the league has sufficient historical data
- Ensure API endpoints are responding

### Performance Issues
- Consider implementing caching for large leagues
- Reduce the number of seasons if API calls are slow
- Check Railway resource limits

## Features Included

### Dashboard Pages
- **Main Dashboard**: Overview and current season standings
- **Champions**: Championship history and hall of fame
- **Statistics**: Scoring records, season stats, all-time leaders
- **Head-to-Head**: Matchup analysis between teams
- **Trends**: League evolution and competitiveness analysis

### Analytics
- Championship tracking
- Scoring records (highest/lowest scores)
- All-time statistics
- Head-to-head records
- League trends and parity analysis
- Season-by-season breakdowns

### Visualizations
- Championship charts
- Scoring trend graphs
- Interactive statistics tables
- Responsive dashboard cards
