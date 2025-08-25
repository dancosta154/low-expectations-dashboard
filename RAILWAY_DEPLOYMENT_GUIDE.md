# Railway Deployment Guide

This guide covers everything needed to deploy the Low Expectations League Dashboard to Railway with automatic ESPN credential refresh.

## 🚀 Required Environment Variables

### Core ESPN Configuration
```bash
# Required for ESPN API access
LEAGUE_ID=your_league_id_here
ESPN_SWID=your_swid_cookie_here
ESPN_S2=your_espn_s2_cookie_here

# Required for automatic credential refresh
ESPN_EMAIL=your_espn_email@example.com
ESPN_PASSWORD=your_espn_password_here
```

### Season Configuration
```bash
# League season settings
CURRENT_SEASON=2025
START_SEASON=2022
```

### Flask Configuration
```bash
# Flask app settings
SECRET_KEY=your-secret-key-here-make-it-long-and-random
FLASK_DEBUG=False
PORT=8080
ENVIRONMENT=production
```

### Optional AI Services
```bash
# AI analysis features (optional)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
OLLAMA_HOST=http://localhost:11434
```

## 📋 Railway Setup Steps

### 1. Deploy to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 2. Set Environment Variables in Railway Dashboard

Go to your Railway project dashboard and add these environment variables:

#### **Required Variables:**
- `LEAGUE_ID` - Your ESPN league ID
- `ESPN_SWID` - ESPN authentication cookie
- `ESPN_S2` - ESPN authentication cookie  
- `ESPN_EMAIL` - Your ESPN account email
- `ESPN_PASSWORD` - Your ESPN account password
- `CURRENT_SEASON` - Current fantasy season (e.g., 2025)
- `START_SEASON` - First year of league data (e.g., 2022)
- `SECRET_KEY` - Flask secret key (generate a random one)

#### **Optional Variables:**
- `OPENAI_API_KEY` - For AI analysis features
- `ANTHROPIC_API_KEY` - For AI analysis features
- `OLLAMA_HOST` - For local AI analysis

### 3. Automatic Credential Refresh Setup

The deployment includes automatic ESPN credential refresh. Railway will need to install Chrome for the Selenium-based refresh script.

#### **Add Buildpack for Chrome:**
In your Railway project settings, add this buildpack:
```
https://github.com/heroku/heroku-buildpack-google-chrome
```

#### **Add Chrome Dependencies:**
Railway will automatically install Chrome dependencies, but you may need to add these to your `requirements.txt`:
```
selenium==4.18.1
```

### 4. Cron Job Setup (Optional)

To enable automatic credential refresh, you can set up a Railway cron job:

#### **Method 1: Railway Cron (Recommended)**
In your Railway dashboard:
1. Go to "Cron Jobs" section
2. Add a new cron job:
   - **Command**: `python auto_refresh_cron.py`
   - **Schedule**: `0 6 * * *` (runs daily at 6 AM)

#### **Method 2: Manual Refresh**
You can manually refresh credentials by running:
```bash
railway run python refresh_espn_credentials.py
```

## 🔧 Deployment Configuration Files

### railway.json
```json
{
    "$schema": "https://railway.app/railway.schema.json",
    "build": {
        "builder": "NIXPACKS"
    },
    "deploy": {
        "startCommand": "gunicorn --bind 0.0.0.0:$PORT app:app",
        "healthcheckPath": "/",
        "healthcheckTimeout": 100,
        "restartPolicyType": "ON_FAILURE",
        "restartPolicyMaxRetries": 10
    },
    "environments": {
        "production": {
            "variables": {
                "ENVIRONMENT": "production",
                "FLASK_DEBUG": "False"
            }
        }
    }
}
```

### Procfile
```
web: gunicorn --bind 0.0.0.0:$PORT app:app
```

## 🧪 Testing Your Deployment

### 1. Check Environment Variables
```bash
railway run python test_setup.py
```

### 2. Test ESPN Connection
```bash
railway run python simple_payout_test.py
```

### 3. Test Credential Refresh
```bash
railway run python refresh_espn_credentials.py
```

## 🔍 Troubleshooting

### Common Issues:

#### **"Missing environment variables"**
- Ensure all required variables are set in Railway dashboard
- Check variable names match exactly (case-sensitive)

#### **"Chrome driver not found"**
- Railway automatically installs Chrome
- If issues persist, the credential refresh will fall back to manual mode

#### **"ESPN API connection failed"**
- Check that `ESPN_SWID` and `ESPN_S2` are current
- Run credential refresh: `railway run python refresh_espn_credentials.py`

#### **"Port binding error"**
- Railway automatically sets the `PORT` environment variable
- The app uses `gunicorn --bind 0.0.0.0:$PORT app:app`

### **Getting Fresh ESPN Credentials:**

1. **Manual Method:**
   ```bash
   railway run python refresh_espn_credentials.py
   ```

2. **Automatic Method:**
   - Set up Railway cron job to run daily
   - Script will automatically refresh when credentials expire

## 📊 Monitoring

### **Railway Logs:**
```bash
railway logs
```

### **Health Check:**
Your app includes a health check endpoint at `/` that Railway uses to monitor the deployment.

### **Credential Refresh Logs:**
The auto-refresh script logs to both console and `espn_refresh.log` file.

## 🔐 Security Notes

1. **Never commit credentials** to your repository
2. **Use Railway's environment variables** for all sensitive data
3. **Generate a strong SECRET_KEY** for production
4. **Regularly rotate ESPN credentials** using the refresh script

## 🎯 Post-Deployment Checklist

- [ ] All environment variables set in Railway
- [ ] App deploys successfully
- [ ] ESPN API connection working
- [ ] Payout calculations working correctly
- [ ] Automatic credential refresh configured (optional)
- [ ] Health checks passing
- [ ] Custom domain configured (if needed)

## 📞 Support

If you encounter issues:
1. Check Railway logs: `railway logs`
2. Test locally with same environment variables
3. Verify ESPN credentials are current
4. Check the `test_setup.py` output for configuration issues
