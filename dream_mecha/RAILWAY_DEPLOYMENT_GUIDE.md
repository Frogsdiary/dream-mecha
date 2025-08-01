# Dream Mecha - Complete Railway Deployment Guide

## **Overview**

This guide will walk you through deploying your Dream Mecha project to Railway for public hosting. The project consists of two main services:
1. **Discord Bot** - Handles game logic, daily cycles, and player interactions
2. **Web UI** - Provides grid management interface for players

## **Prerequisites**

### **1. Discord Bot Setup**
- [ ] Create Discord Application at [Discord Developer Portal](https://discord.com/developers/applications)
- [ ] Generate Bot Token
- [ ] Set up bot permissions
- [ ] Invite bot to your server

### **2. Railway Account**
- [ ] Sign up at [Railway.app](https://railway.app)
- [ ] Connect your GitHub account
- [ ] Verify your account (if required)

### **3. Repository Preparation**
- [ ] Ensure all code is committed to GitHub
- [ ] Verify requirements.txt is up to date
- [ ] Check runtime.txt specifies Python 3.10.11

## **Step 1: Discord Bot Configuration**

### **Create Discord Application**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name: `Dream Mecha`
4. Go to "Bot" section → "Add Bot"
5. Copy the **Bot Token** (keep this secure!)

### **Configure Bot Permissions**
Enable these permissions:
- ✅ Send Messages
- ✅ Embed Links
- ✅ Use Slash Commands
- ✅ Read Message History
- ✅ Add Reactions
- ✅ Manage Messages (for cleanup)

### **Generate Invite Link**
1. Go to "OAuth2" → "URL Generator"
2. Select "bot" scope
3. Select permissions above
4. Copy generated URL
5. Open URL to invite bot to your server

## **Step 2: Railway Project Setup**

### **Create New Project**
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect GitHub account (if not already connected)
5. Select your `dream_mecha` repository

### **Configure Environment Variables**
Add these variables in Railway project settings:

```bash
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Web UI Configuration  
WEB_UI_URL=https://your-web-service-url.railway.app
FLASK_ENV=production

# Database Configuration
DATABASE_URL=file://./database/
PLAYER_DATA_FILE=player_data.json

# Game Configuration
VOIDSTATE=1
DAILY_RESET_HOUR=0
DAILY_RESET_MINUTE=0

# Security
NODE_ENV=production
```

## **Step 3: Deploy Discord Bot Service**

### **Configure Bot Service**
1. In Railway dashboard, click "New Service"
2. Select "GitHub Repo"
3. Choose your `dream_mecha` repository
4. Set service name: `dream-mecha-bot`

### **Set Start Command**
```bash
python main.py
```

### **Configure Environment**
- **Port**: Leave empty (bot doesn't need port)
- **Health Check**: Disable (bot doesn't serve HTTP)

### **Deploy Bot**
1. Click "Deploy" button
2. Wait for build to complete
3. Check logs for successful startup
4. Verify bot appears online in Discord

## **Step 4: Deploy Web UI Service**

### **Create Web UI Service**
1. In same Railway project, click "New Service"
2. Select "GitHub Repo"
3. Choose your `dream_mecha` repository
4. Set service name: `dream-mecha-web`

### **Configure Web UI**
1. **Start Command**: `python web_ui/railway_app.py`
2. **Port**: `3000` (Railway will auto-assign)
3. **Health Check**: Enable with path `/health`

### **Set Web UI Environment Variables**
```bash
FLASK_ENV=production
WEB_UI_URL=https://your-web-service-url.railway.app
DATABASE_URL=file://./database/
```

### **Deploy Web UI**
1. Click "Deploy" button
2. Wait for build to complete
3. Copy the generated URL (e.g., `https://dream-mecha-web-production.up.railway.app`)
4. Update `WEB_UI_URL` in bot service with this URL

## **Step 5: Link Services**

### **Update Bot Configuration**
1. Go back to bot service
2. Add environment variable:
   ```bash
   WEB_UI_URL=https://your-web-service-url.railway.app
   ```
3. Redeploy bot service

### **Test Integration**
1. In Discord, run `!help` command
2. Check that web UI links work
3. Test grid management functionality

## **Step 6: Database Setup**

### **Persistent Storage**
Railway provides ephemeral storage by default. For production:

1. **Option A: Use Railway Volumes**
   - Add volume service to project
   - Mount to `/app/database`
   - Update database paths in code

2. **Option B: Use External Database**
   - Set up PostgreSQL on Railway
   - Update DATABASE_URL environment variable
   - Modify code to use PostgreSQL

### **Backup Strategy**
- Set up automated backups
- Store backups in Railway volumes or external storage
- Test restore procedures

## **Step 7: Testing & Verification**

### **Bot Commands Test**
Test these commands in Discord:
```bash
!help          # Show available commands
!status        # Check mecha status  
!launch        # Launch mecha for combat
!shop          # Show current shop
!grid          # Open grid management
!voidstate     # Show current voidstate
```

### **Web UI Test**
1. Visit your web UI URL
2. Test grid drag-and-drop
3. Verify shop integration
4. Check API endpoints

### **Daily Cycle Test**
1. Wait for daily reset (or trigger manually)
2. Verify shop refresh
3. Check boss announcements
4. Test combat resolution

## **Step 8: Monitoring & Maintenance**

### **Railway Dashboard Monitoring**
- **Logs**: Monitor service logs for errors
- **Metrics**: Track CPU, memory, and network usage
- **Deployments**: Monitor deployment status
- **Alerts**: Set up alerts for downtime

### **Discord Bot Monitoring**
- **Status**: Bot should show "Dream Mecha | !help"
- **Commands**: Verify all commands respond correctly
- **Daily Cycles**: Check daily announcements work
- **Error Handling**: Monitor for command errors

### **Web UI Monitoring**
- **Health Check**: Verify `/health` endpoint responds
- **API Endpoints**: Test all API routes
- **Performance**: Monitor response times
- **Errors**: Check for 404/500 errors

## **Step 9: Production Optimization**

### **Performance Tuning**
1. **Database Optimization**
   - Index frequently queried fields
   - Optimize queries for large datasets
   - Consider caching for read-heavy operations

2. **Web UI Optimization**
   - Enable gzip compression
   - Minify CSS/JS files
   - Use CDN for static assets

3. **Bot Optimization**
   - Implement command cooldowns
   - Cache frequently accessed data
   - Optimize daily cycle processing

### **Security Hardening**
1. **Environment Variables**
   - Never commit secrets to git
   - Use Railway's secret management
   - Rotate tokens regularly

2. **Input Validation**
   - Validate all user inputs
   - Sanitize data before processing
   - Implement rate limiting

3. **Error Handling**
   - Log all errors appropriately
   - Don't expose sensitive info in errors
   - Implement graceful degradation

## **Step 10: Scaling Considerations**

### **Player Growth**
- Monitor player count and resource usage
- Upgrade Railway plan as needed
- Consider database migration for larger datasets

### **Feature Scaling**
- Implement pagination for large lists
- Use caching for expensive operations
- Consider microservices architecture

### **Cost Optimization**
- Monitor Railway usage and costs
- Optimize resource allocation
- Consider reserved instances for predictable loads

## **Troubleshooting Common Issues**

### **Bot Not Responding**
```bash
# Check logs
railway logs

# Verify token
echo $DISCORD_BOT_TOKEN

# Test locally
python main.py
```

### **Web UI Not Loading**
```bash
# Check service status
railway status

# Verify port configuration
railway variables

# Test health endpoint
curl https://your-url.railway.app/health
```

### **Database Issues**
```bash
# Check file permissions
ls -la database/

# Verify data integrity
python -c "import json; json.load(open('database/player_data.json'))"

# Test database operations
python -c "from core.managers.player_manager import PlayerManager; pm = PlayerManager()"
```

### **Import Errors**
```bash
# Check requirements
pip list

# Verify Python version
python --version

# Test imports
python -c "import discord; import flask; print('OK')"
```

## **Next Steps After Deployment**

### **Immediate Actions**
1. ✅ Test all bot commands
2. ✅ Verify web UI functionality  
3. ✅ Set up monitoring and alerts
4. ✅ Create backup procedures
5. ✅ Document deployment process

### **Future Enhancements**
1. **Analytics**: Track player engagement and game metrics
2. **Automation**: Set up CI/CD pipeline for deployments
3. **Monitoring**: Implement comprehensive logging and alerting
4. **Backup**: Set up automated database backups
5. **Scaling**: Plan for increased player load

## **Support Resources**

### **Railway Documentation**
- [Railway Docs](https://docs.railway.app/)
- [Deployment Guide](https://docs.railway.app/deploy/deployments)
- [Environment Variables](https://docs.railway.app/deploy/environment-variables)

### **Discord.py Documentation**
- [Discord.py Docs](https://discordpy.readthedocs.io/)
- [Bot Examples](https://github.com/Rapptz/discord.py/tree/master/examples)

### **Flask Documentation**
- [Flask Docs](https://flask.palletsprojects.com/)
- [Production Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)

## **Security Checklist**

- [ ] DISCORD_BOT_TOKEN is in environment variables
- [ ] No secrets committed to git repository
- [ ] Web UI has proper input validation
- [ ] Database access is properly secured
- [ ] Error messages don't expose sensitive information
- [ ] Regular security updates applied
- [ ] Monitoring for unusual activity

---

**Congratulations!** Your Dream Mecha project is now deployed and accessible to players worldwide! 🎉

Remember to monitor your deployment regularly and keep your dependencies updated for security and performance. 