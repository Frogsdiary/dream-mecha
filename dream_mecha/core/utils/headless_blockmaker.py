"""
Headless Blockmaker - Railway-compatible piece generation

This module provides headless versions of blockmaker algorithms
that can run on Railway's headless Linux environment without GUI dependencies.
"""

import random
import math
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, date

# Try to import icon generation, but continue without it if not available
try:
    from PIL import Image, ImageDraw
    ICON_GENERATION_AVAILABLE = True
except ImportError:
    ICON_GENERATION_AVAILABLE = False
    print("Warning: PIL/Pillow not available. Icon generation disabled.")


class HeadlessIconGenerator:
    """Headless icon generation for railway deployment"""
    
    # Stat colors from Dream Mecha CSS
    STAT_COLORS = {
        'hp': (68, 255, 68),        # #44ff44 - Green
        'attack': (255, 68, 68),    # #ff4444 - Red  
        'defense': (255, 136, 0),   # #ff8800 - Orange
        'speed': (255, 255, 68)     # #ffff44 - Yellow
    }
    
    def __init__(self, icon_size: int = 64):
        self.icon_size = icon_size
        self.cell_size = max(2, icon_size // 16)
        self.border_width = max(1, icon_size // 32)
    
    def generate_icon_from_shape(self, shape: List[List[bool]], stat_type: str, piece_id: str, output_dir: str) -> Optional[str]:
        """Generate icon from shape array"""
        if not ICON_GENERATION_AVAILABLE:
            return None
            
        try:
            # Get stat color
            color = self.STAT_COLORS.get(stat_type.lower(), self.STAT_COLORS['hp'])
            
            # Convert shape to filled positions
            filled_positions = []
            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        filled_positions.append((row_idx, col_idx))
            
            if not filled_positions:
                return None
                
            # Create icon
            icon = self._create_icon_from_positions(filled_positions, color)
            
            # Save icon
            os.makedirs(output_dir, exist_ok=True)
            icon_path = os.path.join(output_dir, f"{piece_id}.webp")
            icon.save(icon_path, 'WEBP', quality=85, method=6)
            
            # Return web-compatible path
            return self.to_web_path(icon_path)
            
        except Exception as e:
            print(f"Icon generation failed for {piece_id}: {e}")
            return None
    
    def _create_icon_from_positions(self, filled_positions: List[tuple], color: tuple):
        """Create icon from list of filled positions"""
        if not filled_positions:
            filled_positions = [(0, 0)]
        
        # Calculate bounds
        min_row = min(pos[0] for pos in filled_positions)
        max_row = max(pos[0] for pos in filled_positions)
        min_col = min(pos[1] for pos in filled_positions)
        max_col = max(pos[1] for pos in filled_positions)
        
        pattern_width = max_col - min_col + 1
        pattern_height = max_row - min_row + 1
        
        # Calculate scaling
        padding = self.icon_size // 8
        available_size = self.icon_size - (2 * padding)
        scale_factor = min(available_size / pattern_width, available_size / pattern_height)
        cell_size = max(1, int(scale_factor))
        
        # Calculate actual pattern size
        scaled_width = pattern_width * cell_size
        scaled_height = pattern_height * cell_size
        
        # Center the pattern
        offset_x = (self.icon_size - scaled_width) // 2
        offset_y = (self.icon_size - scaled_height) // 2
        
        # Create image
        icon = Image.new('RGBA', (self.icon_size, self.icon_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Draw the pattern
        for row_idx, col_idx in filled_positions:
            norm_row = row_idx - min_row
            norm_col = col_idx - min_col
            
            x = offset_x + (norm_col * cell_size)
            y = offset_y + (norm_row * cell_size)
            
            # Draw filled rectangle
            draw.rectangle(
                [x, y, x + cell_size - 1, y + cell_size - 1],
                fill=(*color, 255)
            )
            
            # Add border for definition
            if cell_size > 2:
                border_color = tuple(max(0, c - 40) for c in color)
                draw.rectangle(
                    [x, y, x + cell_size - 1, y + cell_size - 1],
                    outline=(*border_color, 255),
                    width=1
                )
        
        return icon
    
    def to_web_path(self, file_path: str) -> str:
        """Convert file system path to web-compatible path"""
        try:
            # Normalize path separators
            normalized = file_path.replace('\\', '/')
            
            # Find web_ui directory in path
            if 'web_ui' in normalized:
                web_ui_index = normalized.find('web_ui')
                # Return path relative to web_ui as /static/...
                relative_path = normalized[web_ui_index + len('web_ui'):]
                if relative_path.startswith('/'):
                    relative_path = relative_path[1:]
                return '/static/' + relative_path
            
            # Look for static directory
            if 'static' in normalized:
                static_index = normalized.find('static')
                return '/' + normalized[static_index:]
            
            # Fallback: assume it's a daily icon path
            if 'daily' in normalized:
                daily_index = normalized.find('daily')
                return '/static/' + normalized[daily_index:]
            
            # Final fallback
            return normalized
            
        except Exception as e:
            print(f"Path conversion failed: {e}")
            return file_path


class HeadlessBlockmaker:
    """Headless version of blockmaker algorithms for Railway deployment"""
    
    def __init__(self):
        self.generation_history = []
        self.icon_generator = HeadlessIconGenerator() if ICON_GENERATION_AVAILABLE else None
    
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
            
            # Generate icons for pieces
            icons_generated = 0
            if self.icon_generator:
                icons_dir = os.path.join("web_ui", "static", "daily", gen_date.isoformat(), "icons")
                for piece in pieces:
                    try:
                        # Determine stat type from stats
                        stat_type = self.get_primary_stat_type(piece["stats"])
                        icon_path = self.icon_generator.generate_icon_from_shape(
                            piece["shape"], 
                            stat_type, 
                            piece["piece_id"], 
                            icons_dir
                        )
                        if icon_path:
                            piece["icon_path"] = icon_path
                            icons_generated += 1
                    except Exception as e:
                        print(f"Failed to generate icon for {piece['piece_id']}: {e}")
            
            # Create response
            daily_content = {
                "generation_date": gen_date.isoformat(),
                "player_count": player_count,
                "voidstate": voidstate,
                "pieces": pieces,
                "generation_metadata": {
                    "total_pieces": len(pieces),
                    "icons_generated": icons_generated,
                    "icon_generation_available": self.icon_generator is not None,
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
    
    def get_primary_stat_type(self, stats: Dict[str, int]) -> str:
        """Determine which stat type has the highest value"""
        stat_mapping = {
            "hp": "hp",
            "attack": "attack", 
            "defense": "defense",
            "speed": "speed"
        }
        
        max_value = 0
        primary_stat = "hp"  # default
        
        for stat_name, value in stats.items():
            if value > max_value:
                max_value = value
                primary_stat = stat_mapping.get(stat_name, "hp")
        
        return primary_stat
    
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