# Dream Mecha - Turn-based Daily Puzzle RPG

A cooperative mecha combat game where players manage upgrade grids and fight void enemies through Discord integration and web UI.

## Overview

Dream Mecha is a turn-based daily puzzle RPG where players:
- **Pilot individual mechas** with unique stat configurations
- **Manage upgrade grids** (8x8 to 18x18) with stat pieces
- **Fight cooperative battles** against void enemies
- **Earn currency** to purchase new pieces from the daily shop
- **Optimize grid layouts** for maximum stat efficiency

## Core Systems

### Mecha System
- **Four core stats**: HP, Attack, Defense, Speed
- **Defense formula**: `Damage Reduction = Defense / (Defense + Enemy_Attack)`
- **Launch requirements**: Minimum 50% HP to participate in combat
- **State management**: Ready, Launched, Downed, Repairing

### Grid System
- **Base grid**: 8x8 squares (64 total)
- **Maximum grid**: 18x18 squares (324 total)
- **Grid expansion**: Consumable items allow 1-square expansion
- **Piece placement**: Drag-and-drop with rotation support
- **Glyph system**: Legendary enhancement patterns

### Combat System
- **Turn-based combat**: Speed determines attack order
- **Cooperative battles**: All players fight the same enemies
- **Enemy scaling**: Based on voidstate and total player power
- **Reward distribution**: Zoltans based on participation and success

### Shop System
- **Daily inventory**: 6-8 AI-generated pieces
- **Size distribution**: Small (1-2), Medium (3-5), Large (6+) blocks
- **Purchase limits**: 1 piece per player per day
- **Player trading**: Marketplace for piece exchange

### Voidstate System
- **Dynamic scaling**: Enemy difficulty increases with voidstate
- **Void events**: Special events when activity is low
- **Self-correcting**: Rewards increase to incentivize participation

## Architecture

```
dream_mecha/
├── core/
│   ├── systems/           # Core game systems
│   │   ├── mecha_system.py
│   │   ├── grid_system.py
│   │   ├── combat_system.py
│   │   └── shop_system.py
│   ├── managers/          # Game coordination
│   │   ├── game_manager.py
│   │   ├── player_manager.py
│   │   └── voidstate_manager.py
│   └── utils/             # Helper utilities
│       ├── stat_calculator.py
│       └── piece_generator.py
├── gui/                   # Desktop GUI (future)
├── web_ui/                # Web interface for grid management
├── database/              # Data persistence
├── docs/                  # Documentation
│   └── GAME_RULES.md      # Comprehensive game rules
└── tests/                 # Test suite
```

## Key Features

### Stat Calculation Engine
- **Protected system**: Overflow protection and validation
- **Modular design**: New features add layers without breaking core logic
- **Hard caps**: Maximum HP (100 billion), piece size (144 blocks)
- **Calculation logging**: Debug and audit trail

### Piece Generation
- **Blockmaker integration**: Uses adjacency rules for shape generation
- **AI patterns**: Complex shapes with exponential stat scaling
- **Daily variety**: Fresh pieces generated each day
- **Balance protection**: Validation before shop generation

### Player Progression
- **Starter kit**: Free pieces and currency for new players
- **Catch-up mechanics**: Repair discounts for inactive players
- **Community features**: Trading, leaderboards, shared goals
- **Data persistence**: Complete save/load system

## Implementation Status

### Phase 1: Core Systems ✅
- [x] Mecha system with stats and state management
- [x] Grid system with piece placement and expansion
- [x] Combat system with turn-based resolution
- [x] Shop system with daily inventory
- [x] Stat calculation engine with protection
- [x] Piece generation with blockmaker algorithms

### Phase 2: Integration (In Progress)
- [ ] Discord bot integration
- [ ] Web UI for grid management
- [ ] Database persistence
- [ ] Player authentication

### Phase 3: Advanced Features (Planned)
- [ ] Glyph system implementation
- [ ] Community fortress system
- [ ] AI-generated events and storylines
- [ ] Mobile optimization

## Technical Requirements

### Core Dependencies
- **Python 3.10+**: Core game logic
- **Discord.py**: Bot integration
- **Flask/FastAPI**: Web UI backend
- **SQLite/PostgreSQL**: Data persistence
- **React/Vue**: Web UI frontend

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd dream_mecha

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start development server
python -m dream_mecha.web_ui.app
```

## Game Rules

See `docs/GAME_RULES.md` for comprehensive game rules and implementation guidelines.

## Contributing

1. **Follow the rules**: All implementations must follow the game rules document
2. **Protect core systems**: Never modify core stat calculation logic
3. **Add layers**: New features should add calculation layers, not replace existing ones
4. **Test thoroughly**: All changes must pass the test suite
5. **Document changes**: Update relevant documentation

## License

MIT License - See LICENSE file for details.

## Support

For questions about implementation or game mechanics, refer to:
- `docs/GAME_RULES.md` - Comprehensive game rules
- `tests/` - Test suite for examples
- Core system files for implementation details 