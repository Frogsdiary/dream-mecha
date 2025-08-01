# Dream Mecha Debug & Testing Guide

## 🔧 Quick Testing Commands

### Discord Bot Commands
Once the bot is running, use these commands in Discord:

```
!help                    - Show all available commands
!test health            - Test system health
!test fortress          - Test fortress damage system
!test enemies           - Test enemy generation
!test webui             - Test web UI connection
!test export            - Test data export
!test all               - Run all tests
!debug all              - Comprehensive debug (includes 5M damage test)
!debug status           - Show current system status
!debug reset            - Reset fortress to full HP
```

### Standalone Testing
Run the test script without the bot:

```bash
cd dream_mecha
python test_bot_system.py
```

## 🧪 Testing System Components

### 1. System Health Test
- ✅ Player count verification
- ✅ Fortress HP status
- ✅ Voidstate tracking
- ✅ Data persistence
- ✅ Bot connectivity

### 2. Fortress Damage Test
- ✅ Initial HP recording
- ✅ Damage application
- ✅ HP percentage calculation
- ✅ Data saving verification
- ✅ Attack simulation

### 3. Enemy Generation Test
- ✅ Enemy count generation
- ✅ Attack power calculation
- ✅ Defense calculation
- ✅ HP calculation
- ✅ Voidstate scaling

### 4. Web UI Connection Test
- ✅ URL accessibility
- ✅ Response time measurement
- ✅ Status code verification
- ✅ Timeout handling

### 5. Data Export Test
- ✅ System state capture
- ✅ JSON serialization
- ✅ Timestamp recording
- ✅ Data integrity

## 🚨 Troubleshooting

### Bot Not Responding
1. Check if bot is online: `!health`
2. Verify bot permissions in Discord
3. Check console for error messages
4. Ensure `DISCORD_TOKEN` is set correctly

### Fortress Issues
1. Run `!debug reset` to restore fortress HP
2. Check fortress data file: `database/fortress_data.json`
3. Verify fortress manager initialization
4. Test damage calculation manually

### Web UI Issues
1. Check if Flask app is running
2. Verify `WEB_UI_URL` environment variable
3. Test connectivity: `!test webui`
4. Check firewall/network settings

### Data Persistence Issues
1. Check file permissions in `database/` directory
2. Verify JSON file format
3. Test manual save/load operations
4. Check disk space

## 📊 Debug Output Examples

### Successful System Health
```
🔧 DEBUG: System Health
✅ Players: 5
✅ Fortress HP: 99,999,000,000
✅ Voidstate: 3
✅ Data persistence: Working
✅ Bot status: Online
```

### Fortress Damage Test
```
🔧 DEBUG: Fortress Damage Test
🔴 Initial HP: 100,000,000,000
⚔️ Damage Applied: 1,000,000
🟢 Final HP: 99,999,000,000
📊 HP Percentage: 99.9%
💾 Saved: True
```

### Enemy Generation Test
```
🔧 DEBUG: Enemy Generation Test
👹 Enemies Generated: 8
⚔️ Total Attack Power: 45,000
🛡️ Total Defense: 12,000
💀 Total HP: 180,000
🌌 Voidstate: 3
```

## 🔍 Environment Variables

Make sure these are set correctly:

```bash
DISCORD_TOKEN=your_discord_bot_token
WEB_UI_URL=http://localhost:3000
DEBUG_MODE=true
FLASK_ENV=development
```

## 📁 Important Files

### Data Files
- `database/players/` - Player data
- `database/fortress_data.json` - Fortress status
- `database/voidstate.json` - Voidstate tracking

### Log Files
- Check console output for error messages
- Bot logs will show in terminal/console
- Test reports saved as JSON files

## 🎯 Testing Checklist

Before deploying or making changes:

- [ ] Run `python test_bot_system.py`
- [ ] Test all Discord commands: `!test all`
- [ ] Verify fortress damage system
- [ ] Check web UI connectivity
- [ ] Test data persistence
- [ ] Verify enemy generation
- [ ] Check Discord channel permissions
- [ ] Test bot startup/shutdown

## 🚀 Quick Start Testing

1. **Start the bot:**
   ```bash
   cd dream_mecha
   python bot/main.py
   ```

2. **Run standalone tests:**
   ```bash
   python test_bot_system.py
   ```

3. **Test Discord commands:**
   ```
   !debug all
   ```

4. **Check results:**
   - Look for ✅ success messages
   - Check Discord channel for debug embeds
   - Review test report JSON files

## 🔧 Advanced Debugging

### Manual Fortress Testing
```python
from core.managers.fortress_manager import FortressManager

fm = FortressManager()
status = fm.get_fortress_status()
print(f"HP: {status['current_hp']:,}")
```

### Manual Enemy Testing
```python
from core.managers.game_manager import GameManager

gm = GameManager()
enemies = gm.combat_system.generate_enemies(voidstate=3, player_power=10000)
print(f"Enemies: {len(enemies['enemies'])}")
```

### Data Export Testing
```python
import json
from datetime import datetime

data = {
    'timestamp': datetime.now().isoformat(),
    'test': 'manual_export'
}
with open('debug_export.json', 'w') as f:
    json.dump(data, f, indent=2)
```

## 📞 Support

If tests are failing:

1. Check console error messages
2. Verify environment variables
3. Test individual components
4. Check file permissions
5. Review the test report JSON

The testing system will help identify exactly where issues occur! 🎯 