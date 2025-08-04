"""
Headless Blockmaker - Railway-compatible piece generation

This module provides headless versions of blockmaker algorithms
that can run on Railway's headless Linux environment without GUI dependencies.
"""

import random
import math
from typing import Dict, List, Any, Optional
from datetime import datetime, date


class HeadlessBlockmaker:
    """Headless version of blockmaker algorithms for Railway deployment"""
    
    def __init__(self):
        self.generation_history = []
    
    def generate_daily_content(self, player_count: int, voidstate: int, gen_date: date = None) -> Dict[str, Any]:
        """
        Generate daily content for Railway deployment
        
        Args:
            player_count: Number of active players
            voidstate: Current voidstate level
            gen_date: Generation date (defaults to today)
            
        Returns:
            Dictionary containing generated pieces and metadata
        """
        if gen_date is None:
            gen_date = date.today()
        
        try:
            # Generate daily pieces
            pieces = self.generate_daily_pieces(player_count, voidstate, gen_date)
            
            # Create response
            daily_content = {
                "generation_date": gen_date.isoformat(),
                "player_count": player_count,
                "voidstate": voidstate,
                "pieces": pieces,
                "generation_metadata": {
                    "total_pieces": len(pieces),
                    "estimated_player_power": self.estimate_player_power(player_count),
                    "generation_timestamp": datetime.now().isoformat()
                }
            }
            
            return daily_content
            
        except Exception as e:
            return {
                "error": f"Headless generation failed: {str(e)}",
                "generation_date": gen_date.isoformat(),
                "player_count": player_count,
                "voidstate": voidstate,
                "pieces": [],
                "fallback_used": True
            }
    
    def generate_daily_pieces(self, player_count: int, voidstate: int, gen_date: date) -> List[Dict[str, Any]]:
        """Generate daily shop pieces"""
        pieces = []
        
        # Generate 6-8 pieces with guaranteed size distribution
        total_pieces = random.randint(6, 8)
        
        # Small pieces (1-2 blocks) for new players
        small_count = random.randint(2, 3)
        for _ in range(small_count):
            piece = self.generate_piece(1, 2, voidstate)
            pieces.append(piece)
        
        # Medium pieces (3-5 blocks) for established players
        medium_count = random.randint(2, 3)
        for _ in range(medium_count):
            piece = self.generate_piece(3, 5, voidstate)
            pieces.append(piece)
        
        # Large pieces (6+ blocks) for advanced players
        large_count = total_pieces - small_count - medium_count
        for _ in range(large_count):
            piece = self.generate_piece(6, 12, voidstate)
            pieces.append(piece)
        
        return pieces
    
    def generate_piece(self, min_blocks: int, max_blocks: int, voidstate: int) -> Dict[str, Any]:
        """Generate a single piece using current blockmaker algorithms"""
        block_count = random.randint(min_blocks, max_blocks)
        
        # Generate shape using current blockmaker algorithms
        shape = self.generate_shape(block_count)
        
        # Calculate stats using current blockmaker algorithms - ONLY random algorithm
        stats = self.calculate_proper_piece_stats(block_count, "random", "random")
        
        # Calculate price using current blockmaker algorithms
        price = self.calculate_proper_piece_price(block_count, stats)
        
        # Create piece data
        piece = {
            "piece_id": f"headless_piece_{random.randint(10000, 99999)}",
            "name": f"Void Fragment {block_count}",
            "shape": shape,
            "stats": {
                "hp": stats.get("hp", 0),
                "attack": stats.get("att", 0),
                "defense": stats.get("def", 0),
                "speed": stats.get("spd", 0)
            },
            "price": price,
            "piece_type": "stat",
            "block_count": block_count,
            "voidstate_level": voidstate
        }
        
        return piece
    
    def generate_single_piece(self, block_count: int, stat_type: str = "random") -> Dict[str, Any]:
        """Generate a single piece for shop system compatibility"""
        # Generate shape using current blockmaker algorithms
        shape = self.generate_shape(block_count)
        
        # Calculate stats using current blockmaker algorithms - ONLY random algorithm
        stats = self.calculate_proper_piece_stats(block_count, stat_type, "random")
        
        # Calculate price using current blockmaker algorithms
        price = self.calculate_proper_piece_price(block_count, stats)
        
        # Create piece data
        piece = {
            "piece_id": f"headless_piece_{random.randint(10000, 99999)}",
            "name": f"Void Fragment {block_count}",
            "shape": shape,
            "stats": {
                "hp": stats.get("hp", 0),
                "attack": stats.get("att", 0),
                "defense": stats.get("def", 0),
                "speed": stats.get("spd", 0)
            },
            "price": price,
            "piece_type": "stat",
            "block_count": block_count
        }
        
        return piece
    
    def generate_shape(self, block_count: int) -> List[List[bool]]:
        """Generate shape using current blockmaker algorithms"""
        if block_count <= 4:
            return self.generate_simple_shape(block_count)
        else:
            return self.generate_complex_shape(block_count)
    
    def generate_simple_shape(self, blocks: int) -> List[List[bool]]:
        """Generate simple shapes for small pieces"""
        if blocks == 1:
            return [[True]]
        elif blocks == 2:
            return random.choice([
                [[True, True]],
                [[True], [True]]
            ])
        elif blocks == 3:
            return random.choice([
                [[True, True, True]],
                [[True], [True], [True]],
                [[True, True], [True, False]]
            ])
        else:  # 4 blocks
            return random.choice([
                [[True, True, True, True]],
                [[True], [True], [True], [True]],
                [[True, True], [True, True]]
            ])
    
    def generate_complex_shape(self, blocks: int) -> List[List[bool]]:
        """Generate complex shapes for larger pieces"""
        # Use simpler algorithms for reliability
        if blocks <= 6:
            # Use predefined shapes for reliability
            shapes = [
                [[True, True, True], [True, True, True]],  # 2x3
                [[True, True, True, True], [True, True, True, True]],  # 2x4
                [[True, True, True], [True, True, True], [True, True, True]],  # 3x3
            ]
            return random.choice(shapes)
        else:
            # For larger pieces, use a simple expanding algorithm
            max_size = min(6, blocks)  # Cap at 6x6 for reliability
            shape = [[False for _ in range(max_size)] for _ in range(max_size)]
            
            # Place blocks in a simple pattern
            blocks_placed = 0
            for row in range(max_size):
                for col in range(max_size):
                    if blocks_placed < blocks:
                        shape[row][col] = True
                        blocks_placed += 1
                    else:
                        break
                if blocks_placed >= blocks:
                    break
            
            return shape
    
    def count_blocks(self, shape: List[List[bool]]) -> int:
        """Count the number of True blocks in a shape"""
        return sum(sum(row) for row in shape)
    
    def expand_shape(self, shape: List[List[bool]]) -> List[List[bool]]:
        """Expand a shape by adding blocks"""
        # Find valid positions to add blocks
        valid_positions = []
        
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if not shape[row][col]:  # Empty position
                    # Check if adjacent to existing block
                    if self.has_adjacent_block(shape, row, col):
                        valid_positions.append((row, col))
        
        if valid_positions:
            # Add a block at random valid position
            row, col = random.choice(valid_positions)
            shape[row][col] = True
        
        return shape
    
    def has_adjacent_block(self, shape: List[List[bool]], row: int, col: int) -> bool:
        """Check if position has adjacent blocks"""
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < len(shape) and 
                0 <= new_col < len(shape[new_row]) and
                shape[new_row][new_col]):
                return True
        return False
    
    def trim_shape(self, shape: List[List[bool]]) -> List[List[bool]]:
        """Remove blocks from shape to reduce count"""
        # Find all True positions
        true_positions = []
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    true_positions.append((row, col))
        
        if true_positions:
            # Remove a random block
            row, col = random.choice(true_positions)
            shape[row][col] = False
        
        return shape
    
    def calculate_proper_piece_stats(self, block_count: int, stat_type: str, algorithm: str) -> Dict[str, int]:
        """Calculate stats using proper game rules exponential scaling"""
        # Game rules: exponential scaling ~100 HP per block base, exponentially increasing
        base_hp = 100
        scaling_factor = 1.6  # Game rules scaling factor
        total_stat_power = int(base_hp * (block_count ** scaling_factor))
        
        # Each piece gives ONLY ONE stat (use the specified stat_type)
        stat_types = ["hp", "attack", "defense", "speed"]
        
        # Use the specified stat_type, or random if "random"
        if stat_type == "random":
            chosen_stat = random.choice(stat_types)
        else:
            # Map stat_type to the correct stat name
            stat_mapping = {
                "hp": "hp",
                "attack": "attack", 
                "defense": "defense",
                "speed": "speed"
            }
            chosen_stat = stat_mapping.get(stat_type, "hp")  # Default to hp if invalid
        
        # All power goes to the chosen stat
        base_stats = {
            "hp": 0,
            "attack": 0,
            "defense": 0,
            "speed": 0
        }
        base_stats[chosen_stat] = total_stat_power
        
        # Add variance (±15%)
        variance = 0.15
        base_value = base_stats[chosen_stat]
        min_value = int(base_value * (1 - variance))
        max_value = int(base_value * (1 + variance))
        base_stats[chosen_stat] = random.randint(min_value, max_value)
        
        # Convert to expected format
        return {
            "hp": base_stats["hp"],
            "att": base_stats["attack"],
            "def": base_stats["defense"],
            "spd": base_stats["speed"]
        }
    
    def calculate_proper_piece_price(self, block_count: int, stats: Dict[str, int]) -> int:
        """Calculate piece price using game rules exponential scaling"""
        # Game rules: base_cost * (block_count ^ scaling_factor)
        base_cost = 100
        scaling_factor = 1.8
        block_price = int(base_cost * (block_count ** scaling_factor))
        
        # Add stat bonus (30% of total stats value)
        total_stats = stats["hp"] + stats["att"] + stats["def"] + stats["spd"]
        stat_bonus = int(total_stats * 0.3)
        
        final_price = block_price + stat_bonus
        
        # Add price variance (±10%)
        variance = 0.1
        min_price = int(final_price * (1 - variance))
        max_price = int(final_price * (1 + variance))
        
        return random.randint(min_price, max_price)
    
    def estimate_player_power(self, player_count: int) -> Dict[str, int]:
        """Estimate average player power for enemy scaling"""
        # For first day, use generic values that 4 people could handle
        return {
            "avg_hp": 50000,
            "avg_att": 8000,
            "avg_def": 3000,
            "avg_spd": 2000
        }


# Global instance for Railway to use
headless_blockmaker = HeadlessBlockmaker()


def generate_daily_content(player_count: int, voidstate: int, gen_date: date = None) -> Dict[str, Any]:
    """
    Railway-compatible function to generate daily content
    
    This is the main function Railway should call for daily shop generation.
    """
    return headless_blockmaker.generate_daily_content(player_count, voidstate, gen_date)


def generate_single_piece(block_count: int, stat_type: str = "random") -> Dict[str, Any]:
    """
    Railway-compatible function to generate a single piece
    
    This is the function the shop system uses for piece generation.
    """
    return headless_blockmaker.generate_single_piece(block_count, stat_type) 