"""
Mecha System - Core mecha management and stats

Handles individual mecha stats, upgrades, and state management.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, date


class MechaState(Enum):
    """Mecha operational states"""
    READY = "ready"
    LAUNCHED = "launched"
    DOWNED = "downed"
    REPAIRING = "repairing"


@dataclass
class MechaStats:
    """Core mecha statistics"""
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 5
    speed: int = 10
    
    def is_launchable(self) -> bool:
        """Check if mecha meets launch requirements"""
        return self.hp >= (self.max_hp * 0.5) and self.hp > 0
    
    def take_damage(self, damage: int) -> int:
        """Apply damage with defense calculation"""
        damage_reduction = self.defense / (self.defense + damage)
        actual_damage = int(damage * (1 - damage_reduction))
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal mecha up to max HP"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp


class MechaSystem:
    """Manages individual mecha instances"""
    
    def __init__(self):
        self.mechas: Dict[str, 'Mecha'] = {}
    
    def create_mecha(self, player_id: str, name: Optional[str] = None) -> 'Mecha':
        """Create a new mecha for a player"""
        if player_id in self.mechas:
            raise ValueError(f"Player {player_id} already has a mecha")
        
        mecha_name = name if name else f"Mecha-{player_id[:8]}"
        mecha = Mecha(player_id, mecha_name)
        self.mechas[player_id] = mecha
        return mecha
    
    def get_mecha(self, player_id: str) -> Optional['Mecha']:
        """Get player's mecha"""
        return self.mechas.get(player_id)
    
    def get_launched_mechas(self) -> List['Mecha']:
        """Get all currently launched mechas"""
        return [m for m in self.mechas.values() if m.state == MechaState.LAUNCHED]
    
    def reset_daily_state(self):
        """Reset all mechas to ready state for new day"""
        for mecha in self.mechas.values():
            if mecha.state == MechaState.LAUNCHED:
                mecha.state = MechaState.READY


class Mecha:
    """Individual mecha instance"""
    
    def __init__(self, player_id: str, name: str):
        self.player_id = player_id
        self.name = name
        self.stats = MechaStats()
        self.state = MechaState.READY
        self.grid_size = 8  # Base 8x8 grid
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.piece_library: List[Dict] = []
        self.zoltans = 5000  # Starting currency (reduced from 50000)
        
        # Daily healing and launch tracking
        self.last_daily_heal = date.today()
        self.launches_today = 0
        self.max_launches_per_day = 3
        
    def check_daily_reset(self):
        """Check if daily reset should happen and perform it"""
        today = date.today()
        if self.last_daily_heal < today:
            # Daily reset: heal to full and reset launches
            self.stats.hp = self.stats.max_hp
            self.state = MechaState.READY  # Reset from DOWNED state
            self.launches_today = 0
            self.last_daily_heal = today
            print(f"🌅 Daily reset for {self.name}: HP restored, {self.max_launches_per_day} launches available")
    
    def can_launch(self) -> bool:
        """Check if mecha can launch (health + launch limit)"""
        self.check_daily_reset()  # Auto-check daily reset
        return (self.stats.hp > 0 and 
                self.state != MechaState.DOWNED and 
                self.launches_today < self.max_launches_per_day)
    
    def launch(self) -> bool:
        """Launch mecha for combat"""
        if not self.can_launch():
            return False
        
        self.launches_today += 1
        self.state = MechaState.LAUNCHED
        print(f"🚀 {self.name} launched! ({self.launches_today}/{self.max_launches_per_day} launches used today)")
        return True
    
    def take_damage(self, damage: int) -> int:
        """Take damage and update state"""
        actual_damage = self.stats.take_damage(damage)
        
        if self.stats.hp <= 0:
            self.state = MechaState.DOWNED
        
        return actual_damage
    
    def repair(self, cost: int) -> bool:
        """Repair downed mecha"""
        if self.state != MechaState.DOWNED:
            return False
        
        if self.zoltans < cost:
            return False
        
        self.zoltans -= cost
        self.stats.hp = self.stats.max_hp
        self.state = MechaState.READY
        return True
    
    def expand_grid(self) -> bool:
        """Expand grid by 1 in any direction"""
        if self.grid_size >= 18:
            return False
        
        # Implementation for grid expansion
        # This would add rows/columns to the grid
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert mecha to dictionary for serialization"""
        return {
            'player_id': self.player_id,
            'name': self.name,
            'stats': {
                'hp': self.stats.hp,
                'max_hp': self.stats.max_hp,
                'attack': self.stats.attack,
                'defense': self.stats.defense,
                'speed': self.stats.speed
            },
            'state': self.state.value,
            'grid_size': self.grid_size,
            'grid': self.grid,
            'piece_library': self.piece_library,
            'zoltans': self.zoltans,
            'last_daily_heal': self.last_daily_heal.isoformat(),
            'launches_today': self.launches_today,
            'max_launches_per_day': self.max_launches_per_day
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mecha':
        """Create mecha from dictionary"""
        mecha = cls(data['player_id'], data['name'])
        mecha.stats.hp = data['stats']['hp']
        mecha.stats.max_hp = data['stats']['max_hp']
        mecha.stats.attack = data['stats']['attack']
        mecha.stats.defense = data['stats']['defense']
        mecha.stats.speed = data['stats']['speed']
        mecha.state = MechaState(data['state'])
        mecha.grid_size = data['grid_size']
        mecha.grid = data['grid']
        mecha.piece_library = data['piece_library']
        mecha.zoltans = data['zoltans']
        
        # Handle daily healing fields (with defaults for backwards compatibility)
        if 'last_daily_heal' in data:
            from datetime import datetime
            mecha.last_daily_heal = datetime.fromisoformat(data['last_daily_heal']).date()
        if 'launches_today' in data:
            mecha.launches_today = data['launches_today']
        if 'max_launches_per_day' in data:
            mecha.max_launches_per_day = data['max_launches_per_day']
        
        return mecha 