# Dream Mecha System Audit

## 🏗️ System Architecture Overview

### Core Components
1. **Discord Bot** (`bot/main.py`) - Main game interface
2. **Web UI** (`web_ui/`) - Grid management interface  
3. **Game Managers** (`core/managers/`) - Data persistence
4. **Game Systems** (`core/systems/`) - Game mechanics
5. **Fortress System** - Global defense entity
6. **Testing System** - Debug and verification tools

---

## 🤖 Discord Bot System

### **Current Status: ❌ BROKEN**
- **Issue**: Bot is sending messages to `#general` instead of `#dream-mecha-beta`
- **Root Cause**: Bot is not running with updated code
- **Fix Needed**: Restart bot with new commands

### **Bot Commands Available:**
```
!help                    - Show all commands
!test health            - Test system health  
!test fortress          - Test fortress damage
!test enemies           - Test enemy generation
!test webui             - Test web UI connection
!test export            - Test data export
!test all               - Run all tests
!debug all              - Comprehensive debug
!debug status           - Show system status
!debug reset            - Reset fortress HP
!launch                 - Launch mecha for combat
!status                 - Check mecha status
```

### **Daily Cycle Process (6 AM):**
1. **Generate New Shop** - Creates daily pieces
2. **Announce Daily Boss** - Posts enemy info to Discord
3. **Check Fortress Status** - Monitors fortress health
4. **Test Fortress Attack** - Simulates damage for testing
5. **Reset Player Status** - Resets mechas to ready state

### **Channel Targeting Logic:**
```python
# CORRECT (in updated code):
for channel_name in ['dream-mecha-beta']:
    channel = discord.utils.get(guild.text_channels, name=channel_name)

# PROBLEM: Old code might have fallback to general
```

---

## 🏰 Fortress System

### **Fortress Entity:**
- **HP**: 100,000,000,000 (100 billion)
- **Damage System**: Takes damage when no mechs launch
- **Attack Formula**: `enemy_power × 1000`
- **Status Tracking**: Days under attack, total damage

### **Fortress Attack Conditions:**
- No players launch mechas
- All launched mechas are defeated
- Daily cycle triggers attack simulation

### **Manual Trigger Commands:**
```python
# Discord Commands:
!debug reset            # Reset fortress to full HP
!test fortress          # Test damage system

# Direct API:
fortress_manager.fortress_under_attack(enemy_power=50000, no_mechs_launched=True)
```

---

## ⚔️ Combat System

### **Combat Flow:**
1. **Launch Phase** - Players use `!launch`
2. **Enemy Generation** - Based on voidstate and player power
3. **Combat Resolution** - Automated turn-based combat
4. **Results Distribution** - Zoltans, experience, voidstate changes

### **Enemy Generation:**
```python
# Base enemy count scales with voidstate
base_count = 1 + (voidstate // 10)
enemy_count = min(base_count, 10)  # Cap at 10 enemies

# Enemy stats scale with:
# - Voidstate level
# - Total player power
# - Random factors
```

### **Manual Combat Trigger:**
```python
# Force combat resolution:
game_manager.resolve_combat()

# Force enemy generation:
enemies = combat_system.generate_enemies(voidstate=5, player_power=10000)
```

---

## 🎮 Game Managers

### **PlayerManager:**
- **Players**: Individual player accounts
- **Mechas**: Player's combat units
- **Data**: Zoltans, pieces, grid layouts
- **Persistence**: JSON file storage

### **VoidstateManager:**
- **Voidstate**: 0-100 scale (enemy difficulty)
- **Events**: Special void events when activity is low
- **Scaling**: Enemy power increases with voidstate

### **GameManager:**
- **Daily Cycles**: 24-hour game cycles
- **Combat Coordination**: Manages combat resolution
- **Shop Generation**: Daily piece generation
- **State Management**: Game state transitions

### **FortressManager:**
- **Fortress HP**: 100 billion health points
- **Damage Tracking**: Total damage, days under attack
- **Attack Logic**: When no mechs defend
- **Persistence**: Fortress data saved to JSON

---

## 🌐 Web UI System

### **Components:**
- **Flask App** (`web_ui/app.py`) - Main web server
- **Templates** (`web_ui/templates/`) - HTML pages
- **Static Files** (`web_ui/static/`) - CSS, JS, images
- **API Endpoints** - Data exchange with Discord bot

### **Key Endpoints:**
```
/api/player/grid          # Get player's grid
/api/player/shop          # Get shop items
/api/player/combat        # Initiate combat
/api/fortress/status      # Get fortress status
/api/auth/status          # Check authentication
```

### **Layout System:**
- **Drag & Drop**: Move UI containers
- **Resize**: Adjust container sizes
- **Snap to Grid**: Dot matrix alignment
- **Persistence**: Save layouts per player

---

## 🔄 Daily Cycle Process

### **6 AM Daily Cycle:**
1. **Shop Refresh** - Generate new daily pieces
2. **Enemy Generation** - Create void enemies based on voidstate
3. **Discord Announcement** - Post daily boss info
4. **Fortress Check** - Monitor fortress status
5. **Player Reset** - Reset all mechas to ready state

### **Combat Resolution:**
1. **Launch Window** - Players launch mechas
2. **Enemy Spawn** - Generate enemies based on voidstate
3. **Turn-based Combat** - Mechas vs enemies
4. **Reward Distribution** - Zoltans and experience
5. **Voidstate Update** - Adjust difficulty based on results

### **Fortress Attack Logic:**
```python
# Conditions for fortress attack:
if no_players_launched or all_mechs_defeated:
    enemy_power = sum(enemy.attack for enemy in enemies)
    fortress_damage = enemy_power * 1000
    fortress.take_damage(fortress_damage)
```

---

## 🧪 Testing & Debug System

### **Standalone Tests:**
```bash
python test_bot_system.py    # Run all system tests
python verify_bot_commands.py # Check bot status
```

### **Discord Debug Commands:**
```
!test all              # Run all tests
!debug all             # Comprehensive debug
!debug status          # System status
!debug reset           # Reset fortress
```

### **Test Categories:**
1. **System Health** - All managers working
2. **Fortress Damage** - Damage calculation
3. **Enemy Generation** - Enemy creation
4. **Player System** - Player management
5. **Data Persistence** - Save/load functionality
6. **Web UI Integration** - Flask connectivity

---

## 🚨 Current Issues & Solutions

### **Issue 1: Discord Bot Not Updated**
**Problem**: Bot still using old code, sending to wrong channels
**Solution**: 
```bash
# Stop current bot (Ctrl+C)
# Start updated bot:
python bot/main.py
```

### **Issue 2: Manual Trigger Commands**
**Problem**: Need manual void attack and combat triggers
**Solution**: Use Discord commands:
```
!debug all              # Triggers comprehensive tests
!test fortress          # Tests fortress damage
!test enemies           # Tests enemy generation
```

### **Issue 3: Channel Targeting**
**Problem**: Messages going to #general instead of #dream-mecha-beta
**Root Cause**: Bot not restarted with updated code
**Fix**: Restart bot with new channel targeting logic

---

## 🎯 Manual Trigger Commands

### **Force Void Attack:**
```python
# In Discord:
!debug all              # Triggers fortress attack test

# Direct API:
fortress_manager.fortress_under_attack(enemy_power=50000, no_mechs_launched=True)
```

### **Force Combat:**
```python
# In Discord:
!launch                 # Launch your mecha
!test enemies           # Generate enemies

# Direct API:
game_manager.resolve_combat()
combat_system.generate_enemies(voidstate=5, player_power=10000)
```

### **Reset Systems:**
```python
# In Discord:
!debug reset            # Reset fortress to full HP

# Direct API:
fortress_manager.fortress.current_hp = fortress_manager.fortress.max_hp
```

---

## 📊 System Status Check

### **Quick Health Check:**
```bash
# 1. Test all systems:
python test_bot_system.py

# 2. Check bot status:
python verify_bot_commands.py

# 3. Test Discord commands:
!debug status
!test all
```

### **Expected Results:**
- ✅ All 6 tests pass
- ✅ Bot responds to commands
- ✅ Messages go to #dream-mecha-beta
- ✅ Fortress system working
- ✅ Combat system functional

---

## 🔧 Next Steps

1. **Restart Bot**: Stop current bot and start with updated code
2. **Test Commands**: Use `!help` and `!debug status` in Discord
3. **Verify Channel**: Ensure messages go to #dream-mecha-beta
4. **Test Manual Triggers**: Use `!debug all` for comprehensive testing
5. **Monitor Daily Cycle**: Check 6 AM announcements

The system is designed to be fully functional once the bot is restarted with the updated code! 🎯 