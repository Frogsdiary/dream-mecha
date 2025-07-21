"""
Voidstate Manager - Enemy scaling and void events

Manages the voidstate system and enemy difficulty scaling.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random


class VoidstateManager:
    """Manages voidstate and enemy scaling"""
    
    def __init__(self):
        self.voidstate = 0
        self.max_voidstate = 100
        self.last_void_event = None
        self.void_event_cooldown = timedelta(hours=12)
        self.player_activity_threshold = 3  # Minimum players for normal voidstate
    
    def get_voidstate(self) -> int:
        """Get current voidstate level"""
        return self.voidstate
    
    def increase_voidstate(self, amount: int = 1):
        """Increase voidstate level"""
        self.voidstate = min(self.max_voidstate, self.voidstate + amount)
    
    def decrease_voidstate(self, amount: int = 1):
        """Decrease voidstate level"""
        self.voidstate = max(0, self.voidstate - amount)
    
    def reset_voidstate(self):
        """Reset voidstate to 0"""
        self.voidstate = 0
    
    def should_trigger_void_event(self, active_players: int) -> bool:
        """Check if a void event should be triggered"""
        now = datetime.now()
        
        # Check cooldown
        if (self.last_void_event and 
            now - self.last_void_event < self.void_event_cooldown):
            return False
        
        # Trigger if low activity and high voidstate
        if (active_players < self.player_activity_threshold and 
            self.voidstate > 10):
            return True
        
        # Random chance based on voidstate
        if self.voidstate > 20 and random.random() < 0.1:
            return True
        
        return False
    
    def trigger_void_event(self) -> Dict[str, Any]:
        """Trigger a void event and return event details"""
        self.last_void_event = datetime.now()
        
        # Generate event type
        event_types = [
            'void_surge',
            'crystal_convergence', 
            'crimson_void',
            'shadow_storm',
            'void_awakening'
        ]
        
        event_type = random.choice(event_types)
        
        # Calculate event bonuses
        zoltan_bonus = self.voidstate * 50
        enemy_count_bonus = self.voidstate // 5
        
        return {
            'event_type': event_type,
            'voidstate': self.voidstate,
            'zoltan_bonus': zoltan_bonus,
            'enemy_count_bonus': enemy_count_bonus,
            'duration_hours': 24,
            'description': self._get_event_description(event_type)
        }
    
    def _get_event_description(self, event_type: str) -> str:
        """Get description for void event type"""
        descriptions = {
            'void_surge': "The void surges with renewed intensity, sending waves of corrupted energy across the dreamspace.",
            'crystal_convergence': "Crystal formations emerge from the void, their geometric patterns pulsing with alien energy.",
            'crimson_void': "The void takes on a crimson hue as ancient blood magic seeps through the dimensional barriers.",
            'shadow_storm': "Shadows coalesce into living storms, their dark tendrils reaching for any light they can extinguish.",
            'void_awakening': "Something ancient stirs in the depths of the void, its consciousness slowly emerging into reality."
        }
        return descriptions.get(event_type, "The void grows restless...")
    
    def calculate_enemy_scaling(self, base_enemies: int, total_player_power: int) -> Dict[str, Any]:
        """Calculate enemy scaling based on voidstate and player power"""
        # Enemy count scaling
        enemy_count = base_enemies + (self.voidstate // 10)
        
        # Enemy stat scaling
        power_factor = max(0.5, min(3.0, total_player_power / 10000))
        voidstate_multiplier = 1 + (self.voidstate * 0.1)
        
        # HP scaling
        base_hp = 100 * power_factor * voidstate_multiplier
        
        # Attack scaling
        base_attack = 20 * power_factor * voidstate_multiplier
        
        # Defense scaling
        base_defense = 10 * power_factor * voidstate_multiplier
        
        return {
            'enemy_count': enemy_count,
            'base_hp': int(base_hp),
            'base_attack': int(base_attack),
            'base_defense': int(base_defense),
            'power_factor': power_factor,
            'voidstate_multiplier': voidstate_multiplier
        }
    
    def get_voidstate_info(self) -> Dict[str, Any]:
        """Get comprehensive voidstate information"""
        return {
            'current_voidstate': self.voidstate,
            'max_voidstate': self.max_voidstate,
            'voidstate_percentage': (self.voidstate / self.max_voidstate) * 100,
            'last_void_event': self.last_void_event.isoformat() if self.last_void_event else None,
            'next_event_available': self._can_trigger_event(),
            'scaling_factor': 1 + (self.voidstate * 0.1)
        }
    
    def _can_trigger_event(self) -> bool:
        """Check if void event can be triggered"""
        if not self.last_void_event:
            return True
        
        return datetime.now() - self.last_void_event >= self.void_event_cooldown 