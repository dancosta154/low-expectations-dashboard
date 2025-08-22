# Railway AI Setup Guide

## AI Integration for Production Deployment

Your dashboard now supports cloud-based AI providers that work perfectly with Railway hosting.

### Environment Variables for Railway

Add these environment variables in your Railway project settings:

#### Required for ESPN API
```
LEAGUE_ID=your_espn_league_id
ESPN_SWID=your_espn_swid
ESPN_S2=your_espn_s2
START_SEASON=2022
CURRENT_SEASON=2025
```

#### AI Provider (Choose One)

**Option 1: OpenAI (Recommended)**
```
OPENAI_API_KEY=sk-your-openai-api-key
```
- Get your API key: https://platform.openai.com/api-keys
- Uses GPT-4o-mini (fast and cost-effective)
- ~$0.15 per 1M input tokens

**Option 2: Anthropic Claude**
```
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key  
```
- Get your API key: https://console.anthropic.com
- Uses Claude-3-haiku (fast and efficient)
- ~$0.25 per 1M input tokens

### AI Provider Priority

The system automatically uses providers in this order:
1. **OpenAI** (if `OPENAI_API_KEY` is set)
2. **Anthropic** (if `ANTHROPIC_API_KEY` is set)  
3. **Ollama** (local development only)

### Cost Estimation

For a typical fantasy league:
- **Per AI question**: ~$0.001 - $0.005 (1/10th to 1/2 cent)
- **Monthly usage**: $1-5 for active league
- **Season total**: $5-20 depending on usage

### Features Enabled

With AI configured, your dashboard will have:
- ✅ Natural language questions about your league
- ✅ Automatic insights generation  
- ✅ "What could have scored" analysis
- ✅ Trend identification and predictions
- ✅ Historical performance analysis

### Local Development

For local development, you can also run Ollama:
```bash
# Install Ollama
brew install ollama  # macOS
# or visit https://ollama.ai

# Download model
ollama pull llama3.2

# Start service  
ollama serve
```

Set `OLLAMA_HOST=http://localhost:11434` for local Ollama.

### Troubleshooting

1. **AI not working**: Check environment variables are set correctly
2. **API errors**: Verify API keys have sufficient credits
3. **Timeout errors**: AI responses can take 10-30 seconds for complex analysis

### Security

- API keys are stored securely in Railway environment variables
- Never commit API keys to code
- Monitor API usage in provider dashboards
