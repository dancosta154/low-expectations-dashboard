# 🔄 Automated ESPN Credential Refresh Setup

This guide will help you set up automatic refresh of ESPN credentials so your dashboard runs all year without manual intervention.

## 📋 Prerequisites

1. **Chrome Browser** installed on your system
2. **ChromeDriver** installed and in your PATH
3. **ESPN Account** with access to your fantasy league

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
# Install selenium for browser automation
pip install selenium==4.18.1

# Or update all requirements
pip install -r requirements.txt
```

### 2. Install ChromeDriver

**macOS (using Homebrew):**
```bash
brew install chromedriver
```

**Linux:**
```bash
# Download from https://chromedriver.chromium.org/
# Add to PATH or place in /usr/local/bin/
```

**Windows:**
- Download from https://chromedriver.chromium.org/
- Add to PATH or place in same directory as script

### 3. Add ESPN Login Credentials

Add these to your `.env` file:

```bash
# ESPN Login Credentials (for auto-refresh)
ESPN_EMAIL=your_espn_email@example.com
ESPN_PASSWORD=your_espn_password
```

**⚠️ Security Note:** Store your password securely. Consider using environment variables or a password manager.

### 4. Test the Auto-Refresh

```bash
# Test manual refresh
python refresh_espn_credentials.py

# Test automated cron job
python auto_refresh_cron.py
```

## 🤖 Automated Setup Options

### Option 1: Cron Job (Recommended)

Add to your crontab to run every 6 hours:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path to your project)
0 */6 * * * cd /path/to/low-expectations-dashboard && /path/to/venv/bin/python auto_refresh_cron.py
```

### Option 2: Systemd Timer (Linux)

Create `/etc/systemd/system/espn-refresh.service`:
```ini
[Unit]
Description=ESPN Credential Refresh
After=network.target

[Service]
Type=oneshot
User=your_username
WorkingDirectory=/path/to/low-expectations-dashboard
ExecStart=/path/to/venv/bin/python auto_refresh_cron.py
```

Create `/etc/systemd/system/espn-refresh.timer`:
```ini
[Unit]
Description=Run ESPN refresh every 6 hours

[Timer]
OnCalendar=*-*-* 00/6:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable espn-refresh.timer
sudo systemctl start espn-refresh.timer
```

### Option 3: Railway Cron Job

If deploying on Railway, add this to your `railway.json`:

```json
{
  "crons": [
    {
      "command": "python auto_refresh_cron.py",
      "schedule": "0 */6 * * *"
    }
  ]
}
```

## 📊 Monitoring

The script creates a log file `espn_refresh.log` with detailed information about each refresh attempt.

### Check Logs:
```bash
# View recent logs
tail -f espn_refresh.log

# Check last refresh
grep "Credential refresh completed" espn_refresh.log | tail -1
```

### Manual Refresh:
```bash
# Force refresh (even if credentials are working)
python refresh_espn_credentials.py
```

## 🔧 Troubleshooting

### Common Issues:

1. **ChromeDriver not found:**
   - Install ChromeDriver and add to PATH
   - Or specify path in script

2. **Login fails:**
   - Check ESPN_EMAIL and ESPN_PASSWORD
   - ESPN may have changed login page structure
   - Try manual login first

3. **Cookies not found:**
   - ESPN may have changed cookie names
   - Check browser developer tools for current cookie names

4. **Permission denied:**
   - Check file permissions on .env file
   - Ensure script has write access

### Debug Mode:

Run with verbose logging:
```bash
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from refresh_espn_credentials import ESPNCredentialRefresher
refresher = ESPNCredentialRefresher()
refresher.refresh_credentials()
"
```

## 🎯 Benefits

- ✅ **Zero maintenance** - runs automatically
- ✅ **Always fresh credentials** - no more expired cookies
- ✅ **Reliable dashboard** - works all season long
- ✅ **Detailed logging** - track when refreshes happen
- ✅ **Safe fallback** - only refreshes when needed

## 🔒 Security Considerations

- Store ESPN password securely
- Use environment variables when possible
- Rotate passwords regularly
- Monitor logs for unusual activity
- Consider using ESPN API tokens if available

Your dashboard will now automatically refresh ESPN credentials every 6 hours, ensuring it stays running all season long! 🏈✨
