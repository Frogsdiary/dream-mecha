# Dream Mecha - Game Rules & Implementation Guide

*This document is designed to help AI assistants understand and implement the Dream Mecha game system*

## Core Concept
Each player pilots and manages their own Dream Mecha, navigating the dreamspace to fight enemies from the void in a turn-based daily puzzle RPG format.

**IMPLEMENTATION NOTES**: 
- Discord bot handles announcements and social features
- Web UI handles grid management and shop interface
- All player data stored in database with proper backup systems

## Mecha Stats System
Dream Mechas have four core stats:
- **HP** (Health Points)
- **Att** (Attack)
- **Def** (Defense) - Uses scaling formula: `Damage Reduction = Defense / (Defense + Enemy_Attack)`
- **Spd** (Speed) - Determines attack order within launched mechas

**IMPLEMENTATION**: 
- Store stats as integers in database
- Defense calculation: 
  - `damage_reduction = player_defense / (player_defense + enemy_attack)`
  - `actual_damage = enemy_attack * (1 - damage_reduction)`
- Speed determines attack order within launched mechas (not launch order)

## Upgrade Grid System
- **Base Grid**: 8x8 squares (64 total squares)
- **Maximum Grid**: 18x18 squares (324 total squares)
- **Grid Expansion**: Players can expand their grid using "Grid Expansion" consumable items
  - Items allow expansion by 1 square in any direction adjacent to current grid
  - Expansion continues until maximum 18x18 size is reached
  - Grid Expansion items drop for each player after major boss defeats
- **Stat Pieces**: Generated via blockmaker tool following blockmaker rules
- **Piece Sizes**: Can range from 1 block up to 80+ blocks (generated fresh daily)
- **Scaling**: Exponential stat increases per block size reaching billions for large pieces
  - 1 block piece = ~100 HP
  - 10 block piece = ~100,000 HP 
  - 20 block piece = ~10,000,000 HP
  - 80 block piece = ~10,000,000,000 HP (10 billion)
  - Total mecha HP can reach 100 billion range through optimal grid stacking
- **Piece Management**: 
  - Players can rotate pieces when placing
  - Pieces can be removed and reorganized anytime
  - Each player maintains a personal piece library
  - Shop limit: Players can only purchase 1 piece per day for fairness
- **Glyphs**: Legendary enhancement patterns that modify stats within their boundaries
  - Glyphs affect only regular stat pieces placed inside their shape
  - Glyphs cannot be placed inside other glyphs
  - Multiple glyphs of the same type can create multiplicative effects
  - Different glyph types may have varying enhancement effects
- **Grid Puzzle**: Core gameplay involves optimizing piece placement for maximum stat efficiency

**IMPLEMENTATION NOTES**:
- Grid stored as 2D array: `grid[x][y] = piece_id` or `null`
- Grid expansion: Track current_grid_size, allow expansion when consumable used
- Piece library: Array of piece objects `{id, shape, stats, type}`
- Stat calculation: Loop through grid, sum base stats, apply glyph multipliers
- Web UI: Drag-and-drop interface with rotation buttons
- Piece shapes: Store as 2D arrays of boolean values
- Save/Load: Serialize grid state as JSON

## Voidstate & Enemy System
- **Voidstate**: Monitored by AI/Bot system
- **Dynamic Scaling**: Voidstate increases enemy quantity and difficulty
- **Enemy Scaling Options**:
  - Enemy damage scales with average player power (survivability)
  - Enemy HP scales with total launched mecha power (clear speed)
  - More enemies spawn rather than making individual enemies tankier
- **Escalation**: As enemies are defeated, void sends larger armies
- **Discord Integration**: Server stats/functions can influence voidstate
- **Major Void Events**: When Discord activity is low AND fewer players launch:
  - "Void Surge" with special boss enemies
  - Higher Zoltan rewards to incentivize participation  
  - Unique pieces only available during void events
- **Tanking System**: High-HP mechas naturally draw more enemy attacks (enemies prioritize highest HP targets)

**IMPLEMENTATION NOTES**:
- Voidstate: Single integer value stored globally
- Enemy generation: `num_enemies = base_count + (voidstate * multiplier)`
- Enemy stats: `enemy_hp = base_hp * total_player_power_factor`
- Target selection: Sort launched mechas by HP descending, enemies attack in that order
- Void events: Trigger when `active_players < threshold AND voidstate > threshold`

## Currency & Economy
- **Zoltans**: Primary currency earned by defeating enemies
- **Uses**: 
  - Recharge HP: `cost = (max_hp - current_hp) * hp_cost_multiplier`
  - Purchase upgrade pieces from daily shop
  - Repair downed mechas: `cost = max_hp * repair_percentage * discount_multiplier`
- **Trading**: 
  - Sell pieces back to shop for 50% value
  - Trade pieces between players at negotiated prices
  - Player trade pieces visible in shop
- **Repair Discounts**: Players inactive for X days receive progressive discounts to help catch up
- **Pricing Formula**: `piece_cost = base_cost * (block_count ^ scaling_factor)`
- **Example Economy Scaling**:
  - 1 block: 100 Zoltans
  - 10 blocks: 50,000 Zoltans  
  - 20 blocks: 500,000 Zoltans
  - 80 blocks: 50,000,000+ Zoltans

**IMPLEMENTATION NOTES**:
- Zoltans: Integer value per player in database
- HP recharge: `cost = (max_hp - current_hp) * hp_cost_multiplier`
- Repair cost: `cost = max_hp * repair_percentage * discount_multiplier`
- Trading: Simple marketplace table with seller_id, piece_id, asking_price

## Daily Shop System
- **AI Generated**: Bot creates stat pieces based on current game state
- **Shop Inventory**: 6-8 pieces per day with guaranteed size distribution
  - 2-3 small pieces (1-2 blocks) for new players
  - 2-3 medium pieces (3-5 blocks) for established players
  - 1-2 large pieces (6+ blocks) for advanced players
- **Blockmaker Integration**: AI uses blockmaker tool to generate unique piece shapes daily
- **Monster Generation**: AI creates enemies based on voidstate and seasonal themes
- **Player Trading**: Shop displays pieces available for trade between players
- **Purchase Limits**: Each player can buy maximum 1 piece per day from shop

**IMPLEMENTATION NOTES**:
- Daily reset: Cron job or scheduled task runs at midnight
- Shop inventory: Generate 6-8 pieces with guaranteed size distribution
- Piece generation: Call blockmaker API/function with random parameters
- Shop display: Web UI shows pieces with stats, prices, and preview images
- Purchase limits: Track daily_purchases_count per player, reset daily

## Combat System
- **Launch Order**: Mechas attack in order of "launch" (final ready button) - determines participation
- **Attack Order**: Speed stat determines actual attack sequence within launched mechas
- **No Recall**: Cannot recall mecha after launch until next day's results
- **Enemy Retaliation**: If enemy survives, attacks launched mechas (prioritizes highest HP targets)
- **Downed State**: Mecha at 0 HP requires Zoltan payment to repair before next launch
- **Launch Requirement**: Mecha needs minimum 50% max HP to launch

**IMPLEMENTATION NOTES**:
- Launch phase: Players press "Launch" button, adds them to combat queue
- Combat resolution: Automated process runs after launch window closes
- Attack sequence: Sort by speed stat, then process attacks in order
- Damage calculation: Use defense formula, apply to target's current HP
- Combat log: Generate text description of battle for Discord announcement
- Results: Update player HP, distribute Zoltans, update voidstate

## Daily Cycle System
- **24-Hour Cycles**: Following successful NYT/Wordle model for maximum community engagement
- **Cycle Structure**:
  1. Shop refresh with new AI-generated pieces (daily reset)
  2. Player preparation phase (upgrading, strategizing)
  3. Launch window for combat participation
  4. Automated combat resolution
  5. Results distribution and community discussion
  6. Repair/recovery phase before next cycle

## Platform Integration
- **Discord Integration**: Core game runs through Discord bot
- **Bot Functions**: Announcements, social features, commands, links to web UI
- **UI Elements**: Grid and shop interfaces via web UI (accessible from Discord)
- **Access Method**: Players click Discord bot links to open web UI for grid management
- **Modular Design**: Self-contained "Dream Mecha" module
- **Implementation Notes**: 
  - Start with Discord bot framework for community features
  - Simple web UI for grid management and shop interface
  - Consider standalone app integration for future versions
- **Grid Management**:
  - Save/Load grid configurations (store as simple JSON data)
  - Undo last piece placement (keep previous grid state in memory)
  - Implementation: Basic state management, avoid complex UI previews
- **User Interface Priorities**:
  - Focus on core functionality first
  - Add advanced features only after core is stable
  - Keep all implementations simple and Discord-bot friendly
- **No Players Launch Scenario**:
  - Lore: "The void grows restless..."
  - Voidstate automatically increases
  - Next day's enemies become stronger but drop more Zoltans
  - Self-correcting system that rewards eventual participation
- **Implementation**: Simple counter - if launch_count = 0, increment voidstate++
- **Other Edge Cases**:
  - Minimum 1 enemy always spawns regardless of voidstate
  - Combat resolution has fallback logic for unusual scenarios
- **Community Fortress System**:
  - Shared fortress that all players contribute pieces to
  - Fights mega-bosses and special void events
  - Players donate pieces or Zoltans to fortress upgrades
  - Fortress success provides server-wide bonuses
- **Implementation**: Single shared grid + simple contribution tracking
- **Social Elements**:
  - Community goals and challenges
  - Shared victory celebrations
  - Optional: Basic leaderboards for contribution tracking
- **AI-Generated Content**: Use advanced AI to create seasonal events and story arcs
- **Event Types**:
  - Themed void invasions ("Crimson Void", "Crystal Convergence", etc.)
  - Special piece types matching event themes
  - Limited-time glyph releases
  - Community-wide challenges
- **Implementation**: AI generates event descriptions, enemy types, and themed pieces
- **Rotation**: Events change monthly/seasonally to maintain engagement
- **Starter Kit for New Players**:
  - Free 5-10 block piece upon first join
  - Starting Zoltan bonus (suggest 5,000-10,000 Zoltans)
  - Access to "Newcomer Shop" with discounted small pieces for first 7 days
- **Catch-Up Mechanics**:
  - Repair discounts for inactive players (already implemented)
  - Newcomer shop prices: 50% off regular shop prices for first week
  - Community mentoring bonus: Experienced players get small Zoltan reward for helping newbies
- **Simple Implementation**: Track "days_played" and "last_active" per player for automated bonuses

## System Safeguards & Balance Protection
- **Critical: Grid System Integrity**:
  - Grid stat calculation system must be bulletproof and never break
  - **Modular Stat Calculation Engine**: Core grid math protected with layered calculation system
  - All future features (abilities, items, equipment) must integrate without breaking core grid logic
  - New features add calculation layers without touching foundational grid system
  - Stat calculation engine designed to handle any future additions safely
- **Hard Caps**: 
  - Maximum total HP per mecha: 100 billion absolute ceiling
  - Maximum individual piece size: 12x12 blocks (144 blocks max)
  - Maximum stat value per piece: 100 billion per stat with overflow protection
- **Calculation Order**:
  1. Base piece stats calculated first
  2. Glyph effects applied to pieces within boundaries
  3. Multiple glyph bonuses calculated with clear precedence rules
  4. Final totals verified against system limits
- **Glyph Interaction Rules**:
  - Glyphs only affect regular stat pieces, not other glyphs
  - Same-type glyphs can stack multiplicatively (with limits)
  - Different glyph types provide different enhancement types
  - Clear "no glyph-in-glyph" placement rule
- **AI Generation Safeguards**:
  - Piece validation ensures shapes can fit on maximum grid size
  - Stat calculations verified before shop generation
  - Price scaling automatically adjusts based on calculated power
  - Overflow protection prevents system-breaking values
- **Data Backup & Security**:
  - Complete player save data stored for every player
  - Backup system enables restoration during major game updates
  - Version control for save data compatibility

**IMPLEMENTATION NOTES FOR AI DEVELOPERS**:
- Always validate stat calculations against max caps before saving
- Use try-catch blocks around all stat calculations
- Implement stat calculation as pure functions (no side effects)
- Create unit tests for edge cases like maximum piece sizes
- Store calculation results and inputs for debugging
- Never modify core grid calculation logic - only add new layers 