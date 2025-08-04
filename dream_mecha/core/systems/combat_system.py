"""
Combat System - Turn-based combat resolution

Handles mecha vs enemy combat, damage calculation, and battle results.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CombatState(Enum):
    """Combat phase states"""
    PREPARING = "preparing"
    LAUNCHING = "launching"
    COMBAT = "combat"
    RESOLVED = "resolved"


@dataclass
class Enemy:
    """Enemy entity for combat"""
    name: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    voidstate_level: int


@dataclass
class CombatResult:
    """Result of a combat round"""
    mecha_id: str
    damage_dealt: int
    damage_taken: int
    enemy_destroyed: bool
    mecha_downed: bool


class CombatSystem:
    """Manages turn-based combat between mechas and enemies"""
    
    def __init__(self):
        self.state = CombatState.PREPARING
        self.launched_mechas: List['Mecha'] = []
        self.enemies: List[Enemy] = []
        self.combat_log: List[str] = []
        self.voidstate = 0
    
    def add_mecha(self, mecha: 'Mecha') -> bool:
        """Add mecha to combat queue"""
        if mecha.state.value != 'ready':
            return False
        
        if mecha in self.launched_mechas:
            return False
        
        self.launched_mechas.append(mecha)
        from core.systems.mecha_system import MechaState
        mecha.state = MechaState.LAUNCHED
        return True
    
    def generate_enemies(self, voidstate: int, player_power: int) -> List[Enemy]:
        """Generate enemies based on voidstate and player power"""
        self.voidstate = voidstate
        self.enemies.clear()
        
        # Base enemy count scales with voidstate
        base_count = 1 + (voidstate // 10)
        enemy_count = min(base_count, 10)  # Cap at 10 enemies
        
        for i in range(enemy_count):
            enemy = self._create_enemy(i, voidstate, player_power)
            self.enemies.append(enemy)
        
        return self.enemies
    
    def _create_enemy(self, index: int, voidstate: int, player_power: int) -> Enemy:
        """Create a single enemy with scaled stats"""
        # Enemy stats scale with voidstate and player power
        base_hp = 100 * (1 + voidstate * 0.1)
        base_attack = 20 * (1 + voidstate * 0.05)
        base_defense = 10 * (1 + voidstate * 0.03)
        
        # Adjust based on total player power
        power_factor = max(0.5, min(2.0, player_power / 10000))
        
        enemy = Enemy(
            name=f"Void Drone {index + 1}",
            hp=int(base_hp * power_factor),
            max_hp=int(base_hp * power_factor),
            attack=int(base_attack * power_factor),
            defense=int(base_defense * power_factor),
            speed=10 + (voidstate * 2),
            voidstate_level=voidstate
        )
        
        return enemy
    
    def resolve_combat(self) -> Dict[str, any]:
        """Resolve the entire combat round"""
        if not self.launched_mechas or not self.enemies:
            return {'success': False, 'message': 'No combatants'}
        
        self.state = CombatState.COMBAT
        self.combat_log.clear()
        
        # Sort mechas by speed for attack order
        mechas_by_speed = sorted(self.launched_mechas, key=lambda m: m.stats.speed, reverse=True)
        
        # Mecha attack phase
        for mecha in mechas_by_speed:
            if mecha.stats.hp <= 0:
                continue
            
            # Find target enemy (highest HP first)
            target_enemy = max(self.enemies, key=lambda e: e.hp) if self.enemies else None
            if not target_enemy:
                break
            
            # Calculate damage
            damage = self._calculate_damage(mecha.stats.attack, target_enemy.defense)
            target_enemy.hp = max(0, target_enemy.hp - damage)
            
            self.combat_log.append(f"{mecha.name} attacks {target_enemy.name} for {damage} damage")
            
            # Check if enemy destroyed
            if target_enemy.hp <= 0:
                self.enemies.remove(target_enemy)
                self.combat_log.append(f"{target_enemy.name} destroyed!")
        
        # Enemy retaliation phase
        for enemy in self.enemies[:]:  # Copy list to avoid modification during iteration
            if enemy.hp <= 0:
                continue
            
            # Target highest HP mecha
            target_mecha = max(mechas_by_speed, key=lambda m: m.stats.hp) if mechas_by_speed else None
            if not target_mecha or target_mecha.stats.hp <= 0:
                continue
            
            # Calculate damage
            damage = self._calculate_damage(enemy.attack, target_mecha.stats.defense)
            actual_damage = target_mecha.take_damage(damage)
            
            self.combat_log.append(f"{enemy.name} attacks {target_mecha.name} for {actual_damage} damage")
            
            # Check if mecha downed
            if target_mecha.stats.hp <= 0:
                self.combat_log.append(f"{target_mecha.name} has been downed!")
        
        # Calculate rewards
        zoltan_rewards = self._calculate_rewards()
        
        # Update voidstate
        if self.enemies:
            self.voidstate += 1  # Enemies survived, voidstate increases
        else:
            self.voidstate = max(0, self.voidstate - 1)  # All enemies defeated
        
        self.state = CombatState.RESOLVED
        
        # Store last combat result for web UI
        self.last_combat_result = {
            'success': True,
            'enemies_remaining': len(self.enemies),
            'mechas_downed': len([m for m in mechas_by_speed if m.stats.hp <= 0]),
            'zoltan_rewards': zoltan_rewards,
            'voidstate_change': self.voidstate,
            'combat_log': self.combat_log.copy(),
            'total_enemies': len(self.enemies) + len([e for e in self.enemies if e.hp <= 0]),
            'enemies_defeated': len([e for e in self.enemies if e.hp <= 0])
        }
        
        # Save combat records for each participating player
        try:
            from core.managers.combat_history_manager import combat_history_manager
            from core.managers.leaderboard_manager import leaderboard_manager
            
            for mecha in mechas_by_speed:
                if hasattr(mecha, 'player_id') and mecha.player_id:
                    # Get player info
                    from core.managers.player_manager import player_manager
                    player = player_manager.get_player(mecha.player_id)
                    if player:
                        # Create combat record
                        mecha_stats = {
                            'hp': mecha.stats.hp,
                            'attack': mecha.stats.attack,
                            'defense': mecha.stats.defense,
                            'speed': mecha.stats.speed
                        }
                        
                        # Get board info (if available)
                        board_size = 18  # Default grid size
                        pieces_equipped = len(player.piece_library) if player.piece_library else 0
                        
                        # Create and save combat record
                        combat_record = combat_history_manager.create_combat_record_from_result(
                            player_id=mecha.player_id,
                            username=player.username,
                            combat_result=self.last_combat_result,
                            mecha_stats=mecha_stats,
                            board_size=board_size,
                            pieces_equipped=pieces_equipped
                        )
                        combat_history_manager.save_combat_record(combat_record)
                        
                        # Update leaderboard score
                        leaderboard_manager.update_player_score(
                            player_id=mecha.player_id,
                            username=player.username,
                            mecha_stats=mecha_stats,
                            board_size=board_size,
                            pieces_equipped=pieces_equipped
                        )
                        
        except Exception as e:
            print(f"⚠️ Error saving combat records: {e}")
        
        return self.last_combat_result
    
    def _calculate_damage(self, attack: int, defense: int) -> int:
        """Calculate damage using defense formula"""
        if defense <= 0:
            return attack
        
        damage_reduction = defense / (defense + attack)
        actual_damage = int(attack * (1 - damage_reduction))
        return max(1, actual_damage)  # Minimum 1 damage
    
    def _calculate_rewards(self) -> Dict[str, int]:
        """Calculate Zoltan rewards for each player"""
        rewards = {}
        
        # Base reward for participation (increased significantly)
        base_reward = 500
        
        # Bonus for enemy defeats (increased)
        enemies_defeated = len([e for e in self.enemies if e.hp <= 0])
        defeat_bonus = enemies_defeated * 200
        
        # Voidstate bonus with exponential scaling
        voidstate_multiplier = 1 + (self.voidstate * 0.2)  # 20% increase per voidstate
        voidstate_bonus = int(self.voidstate * 100 * voidstate_multiplier)
        
        # Victory bonus (if all enemies defeated)
        victory_bonus = 1000 if enemies_defeated == len(self.enemies) else 0
        
        total_reward = base_reward + defeat_bonus + voidstate_bonus + victory_bonus
        
        for mecha in self.launched_mechas:
            if mecha.stats.hp > 0:  # Only reward surviving mechas
                rewards[mecha.player_id] = total_reward
            else:
                rewards[mecha.player_id] = total_reward // 2  # Half reward for downed mechas
        
        return rewards
    
    def reset_combat(self):
        """Reset combat system for new round"""
        self.state = CombatState.PREPARING
        self.launched_mechas.clear()
        self.enemies.clear()
        self.combat_log.clear()
    
    def initiate_combat(self, player_id: str, enemy_id: str = None) -> Dict[str, any]:
        """Initiate combat for a player"""
        try:
            # Find player's mecha
            player_mecha = None
            for mecha in self.launched_mechas:
                if hasattr(mecha, 'player_id') and mecha.player_id == player_id:
                    player_mecha = mecha
                    break
            
            if not player_mecha:
                return {'success': False, 'error': 'Mecha not launched'}
            
            # If no enemies, generate them
            if not self.enemies:
                # Generate enemies based on current voidstate
                self.generate_enemies(voidstate=self.voidstate, player_power=1000)
            
            # Resolve combat
            result = self.resolve_combat()
            
            # Update player rewards
            if player_id in result.get('zoltan_rewards', {}):
                reward = result['zoltan_rewards'][player_id]
                # This would need to be connected to player manager
                result['player_reward'] = reward
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_combat_status(self) -> Dict[str, any]:
        """Get current combat status"""
        return {
            'state': self.state.value,
            'enemies_remaining': len(self.enemies),
            'mechas_launched': len(self.launched_mechas),
            'voidstate': self.voidstate,
            'combat_log': self.combat_log[-10:]  # Last 10 log entries
        } 