"""
Game Manager - Overall game coordination

Manages the daily cycle, combat resolution, and game state.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from core.systems.mecha_system import MechaSystem, Mecha
from core.systems.combat_system import CombatSystem
from core.systems.shop_system import ShopSystem
from core.systems.grid_system import GridSystem
from core.managers.fortress_manager import FortressManager


class GameManager:
    """Main game coordinator"""
    
    def __init__(self):
        self.mecha_system = MechaSystem()
        self.combat_system = CombatSystem()
        self.shop_system = ShopSystem()
        self.fortress_manager = FortressManager()
        self.voidstate = 0
        self.daily_cycle = 1
        self.last_reset = datetime.now()
        self.game_state = 'preparing'  # preparing, launching, combat, resolved
        
    def start_daily_cycle(self):
        """Start a new daily cycle"""
        # Reset game state
        self.game_state = 'preparing'
        self.mecha_system.reset_daily_state()
        self.combat_system.reset_combat()
        
        # Generate new shop
        player_count = len(self.mecha_system.mechas)
        self.shop_system.generate_daily_shop(self.voidstate, player_count)
        
        # Update cycle
        self.daily_cycle += 1
        self.last_reset = datetime.now()
        
        return {
            'cycle': self.daily_cycle,
            'voidstate': self.voidstate,
            'shop_pieces': len(self.shop_system.daily_inventory)
        }
    
    def launch_mecha(self, player_id: str) -> bool:
        """Launch a player's mecha for combat"""
        mecha = self.mecha_system.get_mecha(player_id)
        if not mecha:
            return False
        
        if self.game_state != 'preparing':
            return False
        
        return self.combat_system.add_mecha(mecha)
    
    def resolve_combat(self) -> Dict[str, Any]:
        """Resolve the current combat round"""
        if self.game_state != 'preparing':
            return {'success': False, 'message': 'Combat not ready'}
        
        self.game_state = 'combat'
        
        # Calculate total player power for enemy scaling
        total_power = sum(m.stats.hp + m.stats.attack + m.stats.defense + m.stats.speed 
                         for m in self.mecha_system.mechas.values())
        
        # Generate enemies
        self.combat_system.generate_enemies(self.voidstate, total_power)
        
        # Resolve combat
        result = self.combat_system.resolve_combat()
        
        # Check if fortress should be attacked
        launched_count = len(self.combat_system.launched_mechas)
        all_mechs_defeated = result.get('all_mechs_defeated', False)
        
        if self.fortress_manager.check_fortress_condition(launched_count, all_mechs_defeated):
            # Calculate total enemy power for fortress attack
            enemy_power = sum(enemy.attack for enemy in result.get('enemies', []))
            fortress_result = self.fortress_manager.fortress_under_attack(
                enemy_power=enemy_power,
                no_mechs_launched=(launched_count == 0)
            )
            result['fortress_attack'] = fortress_result
        
        # Update voidstate
        self.voidstate = result.get('voidstate_change', self.voidstate)
        
        # Distribute rewards
        self._distribute_rewards(result.get('zoltan_rewards', {}))
        
        self.game_state = 'resolved'
        return result
    
    def _distribute_rewards(self, rewards: Dict[str, int]):
        """Distribute Zoltan rewards to players"""
        for player_id, amount in rewards.items():
            mecha = self.mecha_system.get_mecha(player_id)
            if mecha:
                mecha.zoltans += amount
    
    def get_game_status(self) -> Dict[str, Any]:
        """Get current game status"""
        launched_count = len(self.combat_system.launched_mechas)
        total_players = len(self.mecha_system.mechas)
        
        return {
            'game_state': self.game_state,
            'daily_cycle': self.daily_cycle,
            'voidstate': self.voidstate,
            'launched_mechas': launched_count,
            'total_players': total_players,
            'shop_pieces': len(self.shop_system.daily_inventory),
            'player_trades': len(self.shop_system.player_trades)
        }
    
    def should_reset_daily(self) -> bool:
        """Check if daily cycle should reset"""
        now = datetime.now()
        return (now - self.last_reset).days >= 1
    
    def get_launched_mechas_info(self) -> List[Dict[str, Any]]:
        """Get information about launched mechas"""
        info = []
        for mecha in self.combat_system.launched_mechas:
            info.append({
                'player_id': mecha.player_id,
                'name': mecha.name,
                'hp': mecha.stats.hp,
                'max_hp': mecha.stats.max_hp,
                'attack': mecha.stats.attack,
                'defense': mecha.stats.defense,
                'speed': mecha.stats.speed,
                'state': mecha.state.value
            })
        return info 