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
        """Add mecha to combat queue with daily limits"""
        if not mecha.can_launch():
            return False
        
        if mecha in self.launched_mechas:
            return False
        
        # Use the mecha's launch method which handles daily limits
        if mecha.launch():
            self.launched_mechas.append(mecha)
            return True
        
        return False
    
    def generate_enemies(self, voidstate: int, player_power: int) -> List[Enemy]:
        """Generate enemies based on voidstate and player power"""
        self.voidstate = voidstate
        self.enemies.clear()
        
        # Cap enemies at 5 for better combat readability
        base_count = 1 + (voidstate // 15)  # Slower enemy count scaling
        enemy_count = min(base_count, 5)  # Cap at 5 enemies
        
        for i in range(enemy_count):
            enemy = self._create_enemy(i, voidstate, player_power)
            self.enemies.append(enemy)
        
        return self.enemies
    
    def _create_enemy(self, index: int, voidstate: int, player_power: int) -> Enemy:
        """Create a single enemy with scaled stats and modifiers"""
        # Base enemy stats with linear scaling
        base_hp = 100 * (1 + voidstate * 0.1)
        base_attack = 20 * (1 + voidstate * 0.05)
        base_defense = 10 * (1 + voidstate * 0.03)
        
        # Every 10 voidstate levels, add modifiers for variety
        hp_modifier = 1.0
        attack_modifier = 1.0
        defense_modifier = 1.0
        speed_modifier = 1.0
        
        if voidstate >= 10:
            hp_modifier += 0.5 * (voidstate // 10)  # +50% HP every 10 levels
        if voidstate >= 20:
            attack_modifier += 0.5 * ((voidstate - 10) // 10)  # +50% Attack starting at 20
        if voidstate >= 30:
            defense_modifier += 0.5 * ((voidstate - 20) // 10)  # +50% Defense starting at 30
        if voidstate >= 40:
            speed_modifier += 0.25 * ((voidstate - 30) // 10)  # +25% Speed starting at 40
        
        # Adjust based on total player power
        power_factor = max(0.5, min(2.0, player_power / 10000))
        
        enemy = Enemy(
            name=f"Void Drone {index + 1}",
            hp=int(base_hp * power_factor * hp_modifier),
            max_hp=int(base_hp * power_factor * hp_modifier),
            attack=int(base_attack * power_factor * attack_modifier),
            defense=int(base_defense * power_factor * defense_modifier),
            speed=int((10 + (voidstate * 2)) * speed_modifier),
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
            
            # Calculate damage with glancing blow mechanic
            damage = self._calculate_damage(
                mecha.stats.attack, 
                target_enemy.defense, 
                mecha.stats.speed, 
                target_enemy.speed
            )
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
            
            # Calculate damage with glancing blow mechanic
            damage = self._calculate_damage(
                enemy.attack, 
                target_mecha.stats.defense, 
                enemy.speed, 
                target_mecha.stats.speed
            )
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
    
    def _calculate_damage(self, attack: int, defense: int, attacker_speed: int = 0, defender_speed: int = 0) -> int:
        """Calculate damage using improved defense formula with glancing blow mechanic"""
        if defense <= 0:
            return attack
        
        # New formula: damage = attack * (1 - defense/(defense + 100 + attack*0.5))
        # This ensures attack always matters while defense still provides value
        denominator = defense + 100 + (attack * 0.5)
        damage_reduction = defense / denominator
        actual_damage = int(attack * (1 - damage_reduction))
        
        # Glancing blow mechanic: if defender is faster, reduce damage by 25%
        if defender_speed > attacker_speed and defender_speed > 0:
            actual_damage = int(actual_damage * 0.75)
            
        return max(1, actual_damage)  # Minimum 1 damage
    
    def _calculate_rewards(self) -> Dict[str, int]:
        """Calculate Zoltan rewards for each player"""
        rewards = {}
        
        # Minimum reward to prevent death spiral - ALWAYS at least 500 Zoltans
        minimum_reward = 500
        
        # Base reward for participation
        base_reward = 500
        
        # Bonus for enemy defeats
        enemies_defeated = len([e for e in self.enemies if e.hp <= 0])
        defeat_bonus = enemies_defeated * 200
        
        # Voidstate bonus - LINEAR scaling instead of exponential
        voidstate_bonus = self.voidstate * 150  # Linear: 150 per voidstate level
        
        # Victory bonus (if all enemies defeated)
        victory_bonus = 1000 if enemies_defeated == len(self.enemies) else 0
        
        total_reward = base_reward + defeat_bonus + voidstate_bonus + victory_bonus
        
        for mecha in self.launched_mechas:
            player_reward = total_reward if mecha.stats.hp > 0 else max(minimum_reward, total_reward // 2)
            rewards[mecha.player_id] = player_reward
        
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