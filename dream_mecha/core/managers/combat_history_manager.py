#!/usr/bin/env python3
"""
Combat History Manager - Track battle records

Simple, efficient combat tracking for leaderboards.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class CombatRecord:
    """Individual combat record for a player"""
    player_id: str
    username: str
    battle_id: str
    timestamp: str
    
    # Core combat data
    enemies_defeated: int
    total_enemies: int
    damage_dealt: int
    damage_taken: int
    zoltan_earned: int
    voidstate_level: int
    
    # Simple performance metrics
    flawless_victory: bool  # No damage taken
    mecha_survived: bool   # Mecha still alive
    
    # Mecha stats at time of battle
    mecha_stats: Dict[str, int]
    board_size: int
    pieces_equipped: int


class CombatHistoryManager:
    """Manages combat history and statistics"""
    
    def __init__(self):
        self.history_file = "database/combat_history.json"
        self.ensure_history_directory()
    
    def ensure_history_directory(self):
        """Create database directory if it doesn't exist"""
        os.makedirs("database", exist_ok=True)
    
    def save_combat_record(self, record: CombatRecord):
        """Save a combat record to single file"""
        try:
            # Load existing records
            all_records = self.load_all_combat_records()
            all_records.append(asdict(record))
            
            # Save updated records
            with open(self.history_file, 'w') as f:
                json.dump({
                    'last_updated': datetime.now().isoformat(),
                    'total_records': len(all_records),
                    'records': all_records
                }, f, indent=2)
            
            print(f"💾 Saved combat record for {record.username}")
            
        except Exception as e:
            print(f"⚠️ Error saving combat record: {e}")
    
    def load_all_combat_records(self) -> List[Dict]:
        """Load all combat records from single file"""
        try:
            if not os.path.exists(self.history_file):
                return []
            
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                return data.get('records', [])
                
        except Exception as e:
            print(f"⚠️ Error loading combat records: {e}")
            return []
    
    def get_player_combat_stats(self, player_id: str) -> Dict[str, Any]:
        """Get combat statistics for a specific player"""
        all_records = self.load_all_combat_records()
        player_records = [r for r in all_records if r['player_id'] == player_id]
        
        if not player_records:
            return {
                'total_battles': 0,
                'total_enemies_defeated': 0,
                'total_damage_dealt': 0,
                'total_damage_taken': 0,
                'total_zoltan_earned': 0,
                'flawless_victories': 0,
                'survival_count': 0,
                'highest_voidstate': 0,
                'average_voidstate': 0
            }
        
        # Calculate basic statistics
        total_battles = len(player_records)
        total_enemies_defeated = sum(r['enemies_defeated'] for r in player_records)
        total_damage_dealt = sum(r['damage_dealt'] for r in player_records)
        total_damage_taken = sum(r['damage_taken'] for r in player_records)
        total_zoltan_earned = sum(r['zoltan_earned'] for r in player_records)
        
        flawless_victories = sum(1 for r in player_records if r['flawless_victory'])
        survival_count = sum(1 for r in player_records if r['mecha_survived'])
        
        voidstate_levels = [r['voidstate_level'] for r in player_records]
        average_voidstate = sum(voidstate_levels) / len(voidstate_levels) if voidstate_levels else 0
        highest_voidstate = max(voidstate_levels) if voidstate_levels else 0
        
        return {
            'total_battles': total_battles,
            'total_enemies_defeated': total_enemies_defeated,
            'total_damage_dealt': total_damage_dealt,
            'total_damage_taken': total_damage_taken,
            'total_zoltan_earned': total_zoltan_earned,
            'flawless_victories': flawless_victories,
            'survival_count': survival_count,
            'highest_voidstate': highest_voidstate,
            'average_voidstate': average_voidstate,
            'average_enemies_per_battle': total_enemies_defeated / total_battles if total_battles > 0 else 0,
            'damage_efficiency': total_damage_dealt / max(total_damage_taken, 1),
            'flawless_rate': flawless_victories / total_battles if total_battles > 0 else 0
        }
    
    def get_all_combat_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get combat statistics for all players"""
        all_records = self.load_all_combat_records()
        all_stats = {}
        
        # Group records by player
        player_records = {}
        for record in all_records:
            player_id = record['player_id']
            if player_id not in player_records:
                player_records[player_id] = []
            player_records[player_id].append(record)
        
        # Calculate stats for each player
        for player_id, records in player_records.items():
            stats = self._calculate_stats_from_records(records)
            all_stats[player_id] = stats
        
        return all_stats
    
    def _calculate_stats_from_records(self, records: List[Dict]) -> Dict[str, Any]:
        """Calculate stats from a list of records"""
        if not records:
            return {
                'total_battles': 0,
                'total_enemies_defeated': 0,
                'total_damage_dealt': 0,
                'total_damage_taken': 0,
                'total_zoltan_earned': 0,
                'flawless_victories': 0,
                'survival_count': 0,
                'highest_voidstate': 0,
                'average_voidstate': 0
            }
        
        total_battles = len(records)
        total_enemies_defeated = sum(r['enemies_defeated'] for r in records)
        total_damage_dealt = sum(r['damage_dealt'] for r in records)
        total_damage_taken = sum(r['damage_taken'] for r in records)
        total_zoltan_earned = sum(r['zoltan_earned'] for r in records)
        
        flawless_victories = sum(1 for r in records if r['flawless_victory'])
        survival_count = sum(1 for r in records if r['mecha_survived'])
        
        voidstate_levels = [r['voidstate_level'] for r in records]
        average_voidstate = sum(voidstate_levels) / len(voidstate_levels) if voidstate_levels else 0
        highest_voidstate = max(voidstate_levels) if voidstate_levels else 0
        
        return {
            'total_battles': total_battles,
            'total_enemies_defeated': total_enemies_defeated,
            'total_damage_dealt': total_damage_dealt,
            'total_damage_taken': total_damage_taken,
            'total_zoltan_earned': total_zoltan_earned,
            'flawless_victories': flawless_victories,
            'survival_count': survival_count,
            'highest_voidstate': highest_voidstate,
            'average_voidstate': average_voidstate,
            'average_enemies_per_battle': total_enemies_defeated / total_battles if total_battles > 0 else 0,
            'damage_efficiency': total_damage_dealt / max(total_damage_taken, 1),
            'flawless_rate': flawless_victories / total_battles if total_battles > 0 else 0
        }
    
    def create_combat_record_from_result(self, player_id: str, username: str, 
                                       combat_result: Dict[str, Any], 
                                       mecha_stats: Dict[str, int],
                                       board_size: int, pieces_equipped: int) -> CombatRecord:
        """Create a combat record from combat system result"""
        
        # Generate unique battle ID
        battle_id = f"battle_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{player_id}"
        
        # Extract data from combat result
        enemies_defeated = combat_result.get('enemies_defeated', 0)
        total_enemies = combat_result.get('total_enemies', 0)
        zoltan_rewards = combat_result.get('zoltan_rewards', {})
        zoltan_earned = zoltan_rewards.get(player_id, 0)
        
        # Calculate simple performance metrics
        damage_taken = mecha_stats.get('hp', 0) - combat_result.get('mecha_hp_end', mecha_stats.get('hp', 0))
        damage_dealt = combat_result.get('damage_dealt', 0)
        
        # Simple bonuses (no fake metrics)
        flawless_victory = damage_taken == 0 and enemies_defeated > 0
        mecha_survived = combat_result.get('mecha_hp_end', 0) > 0
        
        record = CombatRecord(
            player_id=player_id,
            username=username,
            battle_id=battle_id,
            timestamp=datetime.now().isoformat(),
            enemies_defeated=enemies_defeated,
            total_enemies=total_enemies,
            damage_dealt=damage_dealt,
            damage_taken=damage_taken,
            zoltan_earned=zoltan_earned,
            voidstate_level=combat_result.get('voidstate_change', 0),
            flawless_victory=flawless_victory,
            mecha_survived=mecha_survived,
            mecha_stats=mecha_stats,
            board_size=board_size,
            pieces_equipped=pieces_equipped
        )
        
        return record


# Global instance
combat_history_manager = CombatHistoryManager() 