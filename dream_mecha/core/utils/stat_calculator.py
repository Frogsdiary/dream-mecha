"""
Stat Calculator - Core stat calculation engine

Protected stat calculation system with overflow protection and validation.
"""

from typing import Dict, List, Optional, Any
import math


class StatCalculator:
    """Protected stat calculation engine with overflow protection"""
    
    # System limits
    MAX_TOTAL_HP = 100_000_000_000  # 100 billion
    MAX_PIECE_SIZE = 144  # 12x12 blocks
    MAX_STAT_VALUE = 100_000_000_000  # 100 billion per stat
    
    def __init__(self):
        self.calculation_history: List[Dict] = []
    
    def calculate_grid_stats(self, grid_data: Dict[str, Any]) -> Dict[str, int]:
        """Calculate total stats from grid with protection"""
        try:
            # Step 1: Calculate base piece stats
            base_stats = self._calculate_base_stats(grid_data)
            
            # Step 2: Apply glyph effects
            enhanced_stats = self._apply_glyph_effects(base_stats, grid_data)
            
            # Step 3: Apply final validation
            final_stats = self._validate_final_stats(enhanced_stats)
            
            # Log calculation
            self._log_calculation(grid_data, base_stats, enhanced_stats, final_stats)
            
            return final_stats
            
        except Exception as e:
            # Fallback to safe values
            return self._get_safe_stats()
    
    def _calculate_base_stats(self, grid_data: Dict[str, Any]) -> Dict[str, int]:
        """Calculate base stats from pieces only"""
        total_stats = {'hp': 0, 'attack': 0, 'defense': 0, 'speed': 0}
        
        pieces = grid_data.get('pieces', {})
        for piece_id, piece_data in pieces.items():
            if piece_data.get('piece_type') == 'stat':
                stats = piece_data.get('stats', {})
                for stat_name, value in stats.items():
                    if stat_name in total_stats:
                        total_stats[stat_name] += value
        
        return total_stats
    
    def _apply_glyph_effects(self, base_stats: Dict[str, int], grid_data: Dict[str, Any]) -> Dict[str, int]:
        """Apply glyph enhancement effects"""
        enhanced_stats = base_stats.copy()
        glyphs = grid_data.get('glyphs', {})
        
        for glyph_id, glyph_data in glyphs.items():
            if glyph_data.get('piece_type') == 'glyph':
                affected_pieces = self._get_pieces_in_glyph_area(glyph_id, grid_data)
                glyph_effect = self._calculate_glyph_effect(glyph_data, affected_pieces)
                
                # Apply glyph effect to enhanced stats
                for stat_name, effect_multiplier in glyph_effect.items():
                    if stat_name in enhanced_stats:
                        enhanced_stats[stat_name] = int(enhanced_stats[stat_name] * effect_multiplier)
        
        return enhanced_stats
    
    def _get_pieces_in_glyph_area(self, glyph_id: str, grid_data: Dict[str, Any]) -> List[Dict]:
        """Get pieces affected by a glyph"""
        # Simplified implementation - would need full grid position logic
        affected_pieces = []
        pieces = grid_data.get('pieces', {})
        
        # For now, return all stat pieces (simplified)
        for piece_id, piece_data in pieces.items():
            if piece_data.get('piece_type') == 'stat':
                affected_pieces.append(piece_data)
        
        return affected_pieces
    
    def _calculate_glyph_effect(self, glyph_data: Dict, affected_pieces: List[Dict]) -> Dict[str, float]:
        """Calculate glyph enhancement effect"""
        # Simplified glyph effects
        glyph_type = glyph_data.get('glyph_type', 'enhance')
        
        if glyph_type == 'enhance':
            return {'hp': 1.2, 'attack': 1.2, 'defense': 1.2, 'speed': 1.2}
        elif glyph_type == 'focus':
            return {'hp': 1.5, 'attack': 1.0, 'defense': 1.0, 'speed': 1.0}
        elif glyph_type == 'agility':
            return {'hp': 1.0, 'attack': 1.0, 'defense': 1.0, 'speed': 1.5}
        else:
            return {'hp': 1.0, 'attack': 1.0, 'defense': 1.0, 'speed': 1.0}
    
    def _validate_final_stats(self, stats: Dict[str, int]) -> Dict[str, int]:
        """Validate and cap final stats"""
        validated_stats = {}
        
        for stat_name, value in stats.items():
            # Apply individual stat cap
            capped_value = min(value, self.MAX_STAT_VALUE)
            
            # Ensure non-negative
            capped_value = max(0, capped_value)
            
            validated_stats[stat_name] = capped_value
        
        # Apply total HP cap
        if validated_stats.get('hp', 0) > self.MAX_TOTAL_HP:
            validated_stats['hp'] = self.MAX_TOTAL_HP
        
        return validated_stats
    
    def _get_safe_stats(self) -> Dict[str, int]:
        """Return safe fallback stats"""
        return {'hp': 100, 'attack': 10, 'defense': 5, 'speed': 10}
    
    def _log_calculation(self, grid_data: Dict, base_stats: Dict, enhanced_stats: Dict, final_stats: Dict):
        """Log calculation for debugging"""
        log_entry = {
            'timestamp': self._get_timestamp(),
            'grid_pieces': len(grid_data.get('pieces', {})),
            'grid_glyphs': len(grid_data.get('glyphs', {})),
            'base_stats': base_stats,
            'enhanced_stats': enhanced_stats,
            'final_stats': final_stats
        }
        
        self.calculation_history.append(log_entry)
        
        # Keep only recent history
        if len(self.calculation_history) > 100:
            self.calculation_history = self.calculation_history[-100:]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_piece_stats(self, piece_data: Dict[str, Any]) -> bool:
        """Validate piece stats before adding to system"""
        try:
            stats = piece_data.get('stats', {})
            shape = piece_data.get('shape', [])
            
            # Check piece size
            block_count = sum(sum(row) for row in shape)
            if block_count > self.MAX_PIECE_SIZE:
                return False
            
            # Check individual stats
            for stat_name, value in stats.items():
                if not isinstance(value, int) or value < 0 or value > self.MAX_STAT_VALUE:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def calculate_piece_power(self, piece_data: Dict[str, Any]) -> int:
        """Calculate total power of a piece"""
        try:
            stats = piece_data.get('stats', {})
            total_power = sum(stats.values())
            return min(total_power, self.MAX_STAT_VALUE * 4)  # 400 billion max per piece
        except Exception:
            return 0
    
    def get_calculation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent calculation history"""
        return self.calculation_history[-limit:] 