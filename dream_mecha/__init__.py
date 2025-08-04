"""
Dream Mecha - Turn-based daily puzzle RPG game system

A cooperative mecha combat game where players manage upgrade grids
and fight void enemies through Discord integration and web UI.
"""

__version__ = "0.3.5"
__author__ = "Dream Mecha Development Team"

# Core imports
from dream_mecha.core.systems.mecha_system import MechaSystem
from dream_mecha.core.systems.grid_system import GridSystem
from dream_mecha.core.systems.combat_system import CombatSystem
from dream_mecha.core.systems.shop_system import ShopSystem

# Managers
from dream_mecha.core.managers.game_manager import GameManager
from dream_mecha.core.managers.player_manager import PlayerManager
from dream_mecha.core.managers.voidstate_manager import VoidstateManager

# Utilities
from dream_mecha.core.utils.stat_calculator import StatCalculator
from dream_mecha.core.utils.piece_generator import PieceGenerator

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