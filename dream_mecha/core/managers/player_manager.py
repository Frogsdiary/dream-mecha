"""
Player Manager - Player data and progression

Manages player accounts, progression, and data persistence.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from core.systems.mecha_system import Mecha
from core.systems.grid_system import GridSystem


class PlayerManager:
    """Manages player data and progression"""
    
    def __init__(self):
        self.players: Dict[str, 'Player'] = {}
        self.player_data_file = 'player_data.json'
        self.load_player_data()
    
    def create_player(self, player_id: str, username: str) -> 'Player':
        """Create a new player account"""
        if player_id in self.players:
            raise ValueError(f"Player {player_id} already exists")
        
        player = Player(player_id, username)
        self.players[player_id] = player
        self.save_player_data()
        return player
    
    def get_player(self, player_id: str) -> Optional['Player']:
        """Get player by ID"""
        return self.players.get(player_id)
    
    def get_all_players(self) -> List['Player']:
        """Get all players"""
        return list(self.players.values())
    
    def get_active_players(self, days: int = 7) -> List['Player']:
        """Get players active in the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [p for p in self.players.values() if p.last_active > cutoff_date]
    
    def update_player_activity(self, player_id: str):
        """Update player's last activity timestamp"""
        player = self.get_player(player_id)
        if player:
            player.last_active = datetime.now()
            self.save_player_data()
    
    def get_player_stats(self, player_id: str) -> Dict[str, Any]:
        """Get comprehensive player statistics"""
        player = self.get_player(player_id)
        if not player:
            return {}
        
        return {
            'player_id': player.player_id,
            'username': player.username,
            'join_date': player.join_date.isoformat(),
            'last_active': player.last_active.isoformat(),
            'days_played': player.days_played,
            'total_zoltans_earned': player.total_zoltans_earned,
            'pieces_collected': len(player.piece_library),
            'combat_participation': player.combat_participation,
            'mecha_stats': player.mecha.stats.__dict__ if player.mecha else None
        }
    
    def save_player_data(self):
        """Save all player data to file"""
        data = {}
        for player_id, player in self.players.items():
            data[player_id] = player.to_dict()
        
        try:
            with open(self.player_data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving player data: {e}")
    
    def load_player_data(self):
        """Load player data from file"""
        try:
            with open(self.player_data_file, 'r') as f:
                data = json.load(f)
            
            for player_id, player_data in data.items():
                player = Player.from_dict(player_data)
                self.players[player_id] = player
        except FileNotFoundError:
            # No existing data, start fresh
            pass
        except Exception as e:
            print(f"Error loading player data: {e}")


class Player:
    """Individual player account"""
    
    def __init__(self, player_id: str, username: str):
        self.player_id = player_id
        self.username = username
        self.join_date = datetime.now()
        self.last_active = datetime.now()
        self.days_played = 0
        self.total_zoltans_earned = 0
        self.combat_participation = 0
        self.mecha: Optional[Mecha] = None
        self.piece_library: List[Dict] = []
        self.grid_system = GridSystem()
    
    def create_mecha(self, name: str = None) -> Mecha:
        """Create a mecha for this player"""
        if self.mecha:
            raise ValueError("Player already has a mecha")
        
        from ..systems.mecha_system import Mecha
        self.mecha = Mecha(self.player_id, name or f"{self.username}'s Mecha")
        return self.mecha
    
    def add_piece_to_library(self, piece_data: Dict):
        """Add a piece to player's library"""
        self.piece_library.append(piece_data)
    
    def earn_zoltans(self, amount: int):
        """Add Zoltans to player's total"""
        self.total_zoltans_earned += amount
        if self.mecha:
            self.mecha.zoltans += amount
    
    def increment_days_played(self):
        """Increment days played counter"""
        self.days_played += 1
    
    def increment_combat_participation(self):
        """Increment combat participation counter"""
        self.combat_participation += 1
    
    def get_repair_discount(self) -> float:
        """Calculate repair discount based on inactivity"""
        days_inactive = (datetime.now() - self.last_active).days
        if days_inactive >= 7:
            return 0.5  # 50% discount
        elif days_inactive >= 3:
            return 0.25  # 25% discount
        else:
            return 0.0  # No discount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for serialization"""
        return {
            'player_id': self.player_id,
            'username': self.username,
            'join_date': self.join_date.isoformat(),
            'last_active': self.last_active.isoformat(),
            'days_played': self.days_played,
            'total_zoltans_earned': self.total_zoltans_earned,
            'combat_participation': self.combat_participation,
            'piece_library': self.piece_library,
            'grid_data': self.grid_system.to_json() if self.grid_system else None,
            'mecha_data': self.mecha.to_dict() if self.mecha else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create player from dictionary"""
        player = cls(data['player_id'], data['username'])
        player.join_date = datetime.fromisoformat(data['join_date'])
        player.last_active = datetime.fromisoformat(data['last_active'])
        player.days_played = data['days_played']
        player.total_zoltans_earned = data['total_zoltans_earned']
        player.combat_participation = data['combat_participation']
        player.piece_library = data.get('piece_library', [])
        
        # Load grid data
        if data.get('grid_data'):
            player.grid_system.from_json(data['grid_data'])
        
        # Load mecha data
        if data.get('mecha_data'):
            from core.systems.mecha_system import Mecha
            player.mecha = Mecha.from_dict(data['mecha_data'])
        
        return player 