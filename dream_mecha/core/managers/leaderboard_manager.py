#!/usr/bin/env python3
"""
Leaderboard Manager - Pilot scoring and rankings

Simple, effective pilot scoring system.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from core.managers.combat_history_manager import combat_history_manager


@dataclass
class PilotScore:
    """Pilot score breakdown"""
    player_id: str
    username: str
    total_points: int
    
    # Simple scoring categories
    combat_points: int      # Enemies defeated + flawless victories
    progression_points: int # Voidstate + zoltan earnings
    mecha_points: int      # Total stats + board efficiency


class LeaderboardManager:
    """Manages pilot scoring and leaderboard rankings"""
    
    def __init__(self):
        self.leaderboard_file = "database/leaderboard.json"
        self.ensure_leaderboard_directory()
    
    def ensure_leaderboard_directory(self):
        """Create database directory if it doesn't exist"""
        os.makedirs("database", exist_ok=True)
    
    def calculate_pilot_score(self, player_id: str, combat_stats: Dict[str, Any], 
                            mecha_stats: Dict[str, int], board_size: int, 
                            pieces_equipped: int) -> PilotScore:
        """Calculate simple pilot score"""
        
        # Get combat statistics
        total_enemies_defeated = combat_stats.get('total_enemies_defeated', 0)
        flawless_victories = combat_stats.get('flawless_victories', 0)
        total_zoltan_earned = combat_stats.get('total_zoltan_earned', 0)
        highest_voidstate = combat_stats.get('highest_voidstate', 0)
        
        # Calculate mecha stats
        total_stats = sum(mecha_stats.values())
        board_efficiency = pieces_equipped / max(board_size, 1)  # Pieces vs board size ratio
        
        # === SIMPLE SCORING ===
        # Combat points: Enemies defeated (100 each) + Flawless victories (500 each)
        combat_points = (total_enemies_defeated * 100) + (flawless_victories * 500)
        
        # Progression points: Voidstate (300 per level) + Zoltan (1 per 100)
        progression_points = (highest_voidstate * 300) + (total_zoltan_earned // 100)
        
        # Mecha points: Total stats (10 each) + Board efficiency (1000 max)
        mecha_points = (total_stats * 10) + int(board_efficiency * 1000)
        
        # Total score
        total_points = combat_points + progression_points + mecha_points
        
        return PilotScore(
            player_id=player_id,
            username=combat_stats.get('username', 'Unknown'),
            total_points=total_points,
            combat_points=combat_points,
            progression_points=progression_points,
            mecha_points=mecha_points
        )
    
    def update_player_score(self, player_id: str, username: str, 
                           mecha_stats: Dict[str, int], board_size: int, 
                           pieces_equipped: int) -> PilotScore:
        """Update player score and save to leaderboard"""
        
        # Get combat statistics
        combat_stats = combat_history_manager.get_player_combat_stats(player_id)
        combat_stats['username'] = username
        
        # Calculate score
        pilot_score = self.calculate_pilot_score(player_id, combat_stats, 
                                               mecha_stats, board_size, pieces_equipped)
        
        # Save to leaderboard
        self.save_pilot_score(pilot_score)
        
        return pilot_score
    
    def save_pilot_score(self, pilot_score: PilotScore):
        """Save pilot score to leaderboard"""
        try:
            # Load existing leaderboard
            leaderboard = self.load_leaderboard()
            
            # Update player score
            leaderboard[pilot_score.player_id] = {
                'username': pilot_score.username,
                'total_points': pilot_score.total_points,
                'last_updated': datetime.now().isoformat(),
                'score_breakdown': {
                    'combat_points': pilot_score.combat_points,
                    'progression_points': pilot_score.progression_points,
                    'mecha_points': pilot_score.mecha_points
                }
            }
            
            # Save updated leaderboard
            with open(self.leaderboard_file, 'w') as f:
                json.dump(leaderboard, f, indent=2)
            
            print(f"🏆 Updated leaderboard score for {pilot_score.username}: {pilot_score.total_points} points")
            
        except Exception as e:
            print(f"⚠️ Error saving pilot score: {e}")
    
    def load_leaderboard(self) -> Dict[str, Any]:
        """Load current leaderboard"""
        try:
            if not os.path.exists(self.leaderboard_file):
                return {}
            
            with open(self.leaderboard_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"⚠️ Error loading leaderboard: {e}")
            return {}
    
    def get_leaderboard_rankings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top pilot rankings"""
        leaderboard = self.load_leaderboard()
        
        # Convert to list and sort by total points
        rankings = []
        for player_id, data in leaderboard.items():
            rankings.append({
                'player_id': player_id,
                'username': data['username'],
                'total_points': data['total_points'],
                'last_updated': data['last_updated'],
                'score_breakdown': data.get('score_breakdown', {})
            })
        
        # Sort by total points (descending)
        rankings.sort(key=lambda x: x['total_points'], reverse=True)
        
        # Add rank numbers
        for i, ranking in enumerate(rankings):
            ranking['rank'] = i + 1
        
        return rankings[:limit]
    
    def get_player_ranking(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get specific player's ranking"""
        rankings = self.get_leaderboard_rankings(limit=1000)  # Get all rankings
        
        for ranking in rankings:
            if ranking['player_id'] == player_id:
                return ranking
        
        return None
    
    def get_leaderboard_summary(self) -> Dict[str, Any]:
        """Get leaderboard summary statistics"""
        rankings = self.get_leaderboard_rankings(limit=1000)
        
        if not rankings:
            return {
                'total_pilots': 0,
                'average_score': 0,
                'highest_score': 0,
                'top_pilot': None
            }
        
        total_pilots = len(rankings)
        total_score = sum(r['total_points'] for r in rankings)
        average_score = total_score / total_pilots
        highest_score = max(r['total_points'] for r in rankings)
        top_pilot = rankings[0] if rankings else None
        
        return {
            'total_pilots': total_pilots,
            'average_score': int(average_score),
            'highest_score': highest_score,
            'top_pilot': top_pilot,
            'score_distribution': {
                'elite': len([r for r in rankings if r['total_points'] >= 10000]),
                'veteran': len([r for r in rankings if 5000 <= r['total_points'] < 10000]),
                'experienced': len([r for r in rankings if 2000 <= r['total_points'] < 5000]),
                'novice': len([r for r in rankings if r['total_points'] < 2000])
            }
        }


# Global instance
leaderboard_manager = LeaderboardManager() 