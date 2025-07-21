"""
Dream Mecha - Turn-based daily puzzle RPG game system

A cooperative mecha combat game where players manage upgrade grids
and fight void enemies through Discord integration and web UI.
"""

__version__ = "0.1.0"
__author__ = "Dream Mecha Development Team"

# Core imports
from core.systems.mecha_system import MechaSystem
from core.systems.grid_system import GridSystem
from core.systems.combat_system import CombatSystem
from core.systems.shop_system import ShopSystem

# Managers
from core.managers.game_manager import GameManager
from core.managers.player_manager import PlayerManager
from core.managers.voidstate_manager import VoidstateManager

# Utilities
from core.utils.stat_calculator import StatCalculator
from core.utils.piece_generator import PieceGenerator

__all__ = [
    # Systems
    'MechaSystem',
    'GridSystem', 
    'CombatSystem',
    'ShopSystem',
    
    # Managers
    'GameManager',
    'PlayerManager',
    'VoidstateManager',
    
    # Utilities
    'StatCalculator',
    'PieceGenerator',
] 