"""
Fortress Manager - Manages the global fortress entity
The fortress is humanity's last defense with 100 billion HP
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional


class Fortress:
    """Global fortress entity that protects humanity"""
    
    def __init__(self):
        self.max_hp: int = 100_000_000_000  # 100 billion HP
        self.current_hp: int = 100_000_000_000
        self.last_attack_date: Optional[str] = None
        self.total_damage_taken: int = 0
        self.days_under_attack: int = 0
        
    def take_damage(self, damage: int) -> Dict[str, Any]:
        """Apply damage to fortress and return result info"""
        if self.current_hp <= 0:
            return {
                'success': False,
                'message': 'Fortress has already fallen',
                'current_hp': 0,
                'damage_dealt': 0
            }
        
        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage
        self.total_damage_taken += actual_damage
        
        # Update attack tracking
        today = date.today().isoformat()
        if self.last_attack_date != today:
            self.days_under_attack += 1
            self.last_attack_date = today
        
        return {
            'success': True,
            'damage_dealt': actual_damage,
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'hp_percentage': (self.current_hp / self.max_hp) * 100,
            'fortress_fallen': self.current_hp <= 0
        }
    
    def repair(self, amount: int) -> int:
        """Repair fortress HP (for future mechanics)"""
        if self.current_hp >= self.max_hp:
            return 0
        
        actual_repair = min(amount, self.max_hp - self.current_hp)
        self.current_hp += actual_repair
        return actual_repair
    
    def get_status(self) -> Dict[str, Any]:
        """Get current fortress status"""
        return {
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'hp_percentage': (self.current_hp / self.max_hp) * 100,
            'total_damage_taken': self.total_damage_taken,
            'days_under_attack': self.days_under_attack,
            'last_attack_date': self.last_attack_date,
            'is_active': self.current_hp > 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert fortress to dictionary for saving"""
        return {
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'total_damage_taken': self.total_damage_taken,
            'days_under_attack': self.days_under_attack,
            'last_attack_date': self.last_attack_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Fortress':
        """Create fortress from dictionary data"""
        fortress = cls()
        fortress.current_hp = data.get('current_hp', 100_000_000_000)
        fortress.max_hp = data.get('max_hp', 100_000_000_000)
        fortress.total_damage_taken = data.get('total_damage_taken', 0)
        fortress.days_under_attack = data.get('days_under_attack', 0)
        fortress.last_attack_date = data.get('last_attack_date')
        return fortress


class FortressManager:
    """Manages the global fortress system"""
    
    def __init__(self, data_dir: str = "database"):
        self.data_dir = Path(data_dir)
        self.fortress_file = self.data_dir / "fortress_data.json"
        self.fortress = self.load_fortress()
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
    
    def load_fortress(self) -> Fortress:
        """Load fortress data from file"""
        try:
            if self.fortress_file.exists():
                with open(self.fortress_file, 'r') as f:
                    data = json.load(f)
                    return Fortress.from_dict(data)
        except Exception as e:
            print(f"⚠️ Error loading fortress data: {e}")
        
        # Create new fortress if loading failed
        return Fortress()
    
    def save_fortress(self) -> bool:
        """Save fortress data to file"""
        try:
            with open(self.fortress_file, 'w') as f:
                json.dump(self.fortress.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ Error saving fortress data: {e}")
            return False
    
    def fortress_under_attack(self, enemy_power: int, no_mechs_launched: bool = True) -> Dict[str, Any]:
        """
        Process fortress attack when no mechs are launched or all mechs are defeated
        
        Args:
            enemy_power: Total attack power of void enemies
            no_mechs_launched: True if no players launched mechs
        
        Returns:
            Attack result information
        """
        if not no_mechs_launched:
            return {
                'attack_occurred': False,
                'message': 'Mechs are defending - fortress is safe'
            }
        
        # Calculate fortress damage (void enemies attack directly)
        fortress_damage = enemy_power * 1000  # Amplified damage when hitting fortress directly
        
        result = self.fortress.take_damage(fortress_damage)
        
        # Save fortress state
        self.save_fortress()
        
        return {
            'attack_occurred': True,
            'enemy_power': enemy_power,
            'fortress_damage': fortress_damage,
            'fortress_result': result,
            'message': f"🚨 FORTRESS UNDER ATTACK! Void enemies dealt {fortress_damage:,} damage!"
        }
    
    def get_fortress_status(self) -> Dict[str, Any]:
        """Get current fortress status for UI"""
        return self.fortress.get_status()
    
    def check_fortress_condition(self, players_launched: int, all_mechs_defeated: bool) -> bool:
        """
        Check if fortress should be attacked today
        
        Args:
            players_launched: Number of players who launched mechs
            all_mechs_defeated: True if all player mechs were reduced to 0 HP
        
        Returns:
            True if fortress should be attacked
        """
        return players_launched == 0 or all_mechs_defeated 