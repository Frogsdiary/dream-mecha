# Dream Mecha - Railway Deployment Guide

## **Step 1: Discord Bot Setup**

### Create Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name it "Dream Mecha"
4. Go to "Bot" section
5. Click "Add Bot"
6. Copy the **Bot Token** (you'll need this for Railway)

### Bot Permissions
Enable these permissions:
- Send Messages
- Embed Links
- Use Slash Commands
- Read Message History
- Add Reactions

### Invite Bot to Server
1. Go to "OAuth2" → "URL Generator"
2. Select "bot" scope
3. Select the permissions above
4. Copy the generated URL
5. Open URL in browser to invite bot to your server

## **Step 2: Railway Deployment**

### Connect Repository
1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Select the `dream_mecha` repository

### Environment Variables
Add these environment variables in Railway:

```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
WEB_UI_URL=https://your-web-service-url.railway.app
NODE_ENV=production
```

### Deploy Bot Service
1. Railway will detect the Python project
2. Set the start command: `python -m dream_mecha.bot.main`
3. Deploy the service

### Deploy Web UI Service (Optional)
1. Create a second service for the web UI
2. Set start command: `python dream_mecha/web_ui/app.py`
3. Set environment variable: `PORT=3000`

## **Step 3: Testing**

### Bot Commands
Once deployed, test these commands in Discord:
- `!help` - Show available commands
- `!status` - Check your mecha status
- `!launch` - Launch your mecha for combat

### Web UI Access
- Visit your web UI URL to access grid management
- Test grid drag-and-drop functionality
- Verify shop integration

## **Step 4: Monitoring**

### Railway Dashboard
- Monitor service logs in Railway dashboard
- Check resource usage
- Set up alerts for downtime

### Discord Bot Status
- Bot should show "Dream Mecha | !help" as status
- Check bot is responding to commands
- Verify daily cycle announcements

## **Troubleshooting**

### Common Issues
1. **Bot not responding**: Check DISCORD_BOT_TOKEN is correct
2. **Import errors**: Ensure all dependencies in requirements.txt
3. **Database errors**: Check file permissions for player_data.json
4. **Web UI not loading**: Verify WEB_UI_URL environment variable

### Logs
- Check Railway service logs for errors
- Bot logs will show startup and daily cycle info
- Web UI logs will show API requests

## **Next Steps**

### After Deployment
1. Test all bot commands
2. Verify web UI functionality
3. Set up daily cycle timing
4. Configure server-specific settings

### Scaling
- Monitor player count and resource usage
- Upgrade Railway plan if needed
- Consider database migration for larger player base

## **Security Notes**

- Never commit DISCORD_BOT_TOKEN to git
- Use environment variables for all secrets
- Regularly rotate bot tokens
- Monitor for unusual activity

## **Support**

If you encounter issues:
1. Check Railway logs first
2. Verify environment variables
3. Test locally before deploying
4. Check Discord bot permissions 