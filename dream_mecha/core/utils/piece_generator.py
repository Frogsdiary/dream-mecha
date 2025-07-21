"""
Piece Generator - AI-generated piece creation

Generates stat pieces using blockmaker algorithms and AI patterns.
"""

from typing import Dict, List, Optional, Any, Tuple
import random
import math


class PieceGenerator:
    """Generates pieces using blockmaker algorithms and AI patterns"""
    
    def __init__(self):
        self.generation_history: List[Dict] = []
        self.piece_templates: Dict[str, List[List[bool]]] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize basic piece templates"""
        self.piece_templates = {
            'small': [
                [[True]],  # 1 block
                [[True, True]],  # 2 blocks horizontal
                [[True], [True]],  # 2 blocks vertical
                [[True, True], [True, False]],  # L shape
            ],
            'medium': [
                [[True, True, True]],  # 3 blocks horizontal
                [[True], [True], [True]],  # 3 blocks vertical
                [[True, True], [True, True]],  # 2x2 square
                [[True, True, True], [False, True, False]],  # T shape
            ],
            'large': [
                [[True, True, True, True]],  # 4 blocks horizontal
                [[True], [True], [True], [True]],  # 4 blocks vertical
                [[True, True, True], [True, True, True]],  # 2x3 rectangle
                [[True, True, True], [True, False, True], [True, True, True]],  # Hollow square
            ]
        }
    
    def generate_piece(self, target_blocks: int, voidstate: int, piece_type: str = 'stat') -> Dict[str, Any]:
        """Generate a piece with specified parameters"""
        try:
            # Generate shape
            shape = self._generate_shape(target_blocks)
            
            # Calculate stats
            stats = self._calculate_stats(target_blocks, voidstate, shape)
            
            # Create piece data
            piece = {
                'piece_id': f"piece_{random.randint(10000, 99999)}",
                'name': self._generate_piece_name(target_blocks, voidstate),
                'shape': shape,
                'stats': stats,
                'piece_type': piece_type,
                'block_count': target_blocks,
                'voidstate_level': voidstate
            }
            
            # Log generation
            self._log_generation(piece)
            
            return piece
            
        except Exception as e:
            # Fallback to simple piece
            return self._generate_fallback_piece(target_blocks)
    
    def _generate_shape(self, target_blocks: int) -> List[List[bool]]:
        """Generate shape for piece using blockmaker-like algorithms"""
        if target_blocks <= 4:
            return self._generate_simple_shape(target_blocks)
        else:
            return self._generate_complex_shape(target_blocks)
    
    def _generate_simple_shape(self, blocks: int) -> List[List[bool]]:
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
    
    def _generate_complex_shape(self, blocks: int) -> List[List[bool]]:
        """Generate complex shapes for larger pieces"""
        # Calculate grid size needed
        grid_size = int(math.ceil(math.sqrt(blocks)))
        
        # Create empty grid
        grid = [[False for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Fill grid using adjacency rules (like blockmaker)
        placed_blocks = 0
        start_x, start_y = grid_size // 2, grid_size // 2
        
        # Place first block in center
        grid[start_y][start_x] = True
        placed_blocks += 1
        
        # Place remaining blocks adjacent to existing ones
        while placed_blocks < blocks:
            # Find all valid positions adjacent to existing blocks
            valid_positions = []
            for y in range(grid_size):
                for x in range(grid_size):
                    if not grid[y][x] and self._has_adjacent_block(grid, x, y):
                        valid_positions.append((x, y))
            
            if not valid_positions:
                # If no valid positions, place randomly
                empty_positions = []
                for y in range(grid_size):
                    for x in range(grid_size):
                        if not grid[y][x]:
                            empty_positions.append((x, y))
                
                if empty_positions:
                    x, y = random.choice(empty_positions)
                    grid[y][x] = True
                    placed_blocks += 1
                else:
                    break
            else:
                # Place in valid position
                x, y = random.choice(valid_positions)
                grid[y][x] = True
                placed_blocks += 1
        
        return grid
    
    def _has_adjacent_block(self, grid: List[List[bool]], x: int, y: int) -> bool:
        """Check if position has adjacent blocks"""
        grid_size = len(grid)
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                if grid[ny][nx]:
                    return True
        
        return False
    
    def _calculate_stats(self, blocks: int, voidstate: int, shape: List[List[bool]]) -> Dict[str, int]:
        """Calculate stats for piece based on blocks and voidstate"""
        # Exponential scaling as per rules
        base_multiplier = 100 * (blocks ** 2)
        voidstate_bonus = 1 + (voidstate * 0.1)
        
        # Calculate total power
        total_power = int(base_multiplier * voidstate_bonus)
        
        # Distribute power across stats based on shape characteristics
        shape_factor = self._calculate_shape_factor(shape)
        
        # Stat distribution
        hp_ratio = 0.4 + (shape_factor * 0.2)
        attack_ratio = 0.3 + (shape_factor * 0.1)
        defense_ratio = 0.2 + (shape_factor * 0.1)
        speed_ratio = 0.1 + (shape_factor * 0.1)
        
        # Normalize ratios
        total_ratio = hp_ratio + attack_ratio + defense_ratio + speed_ratio
        hp_ratio /= total_ratio
        attack_ratio /= total_ratio
        defense_ratio /= total_ratio
        speed_ratio /= total_ratio
        
        stats = {
            'hp': int(total_power * hp_ratio),
            'attack': int(total_power * attack_ratio),
            'defense': int(total_power * defense_ratio),
            'speed': int(total_power * speed_ratio)
        }
        
        return stats
    
    def _calculate_shape_factor(self, shape: List[List[bool]]) -> float:
        """Calculate shape complexity factor"""
        if not shape:
            return 0.0
        
        rows, cols = len(shape), len(shape[0])
        
        # Count filled cells
        filled_cells = sum(sum(row) for row in shape)
        
        # Calculate compactness (how close to square)
        total_cells = rows * cols
        compactness = filled_cells / total_cells if total_cells > 0 else 0
        
        # Calculate perimeter (more perimeter = more complex)
        perimeter = self._calculate_perimeter(shape)
        perimeter_factor = perimeter / (filled_cells * 4) if filled_cells > 0 else 0
        
        # Combine factors
        shape_factor = (compactness + perimeter_factor) / 2
        return min(1.0, max(0.0, shape_factor))
    
    def _calculate_perimeter(self, shape: List[List[bool]]) -> int:
        """Calculate perimeter of shape"""
        if not shape:
            return 0
        
        rows, cols = len(shape), len(shape[0])
        perimeter = 0
        
        for y in range(rows):
            for x in range(cols):
                if shape[y][x]:
                    # Check each direction
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if (nx < 0 or nx >= cols or ny < 0 or ny >= rows or 
                            not shape[ny][nx]):
                            perimeter += 1
        
        return perimeter
    
    def _generate_piece_name(self, blocks: int, voidstate: int) -> str:
        """Generate name for piece"""
        prefixes = ['Void', 'Crystal', 'Shadow', 'Ethereal', 'Corrupted']
        suffixes = ['Fragment', 'Shard', 'Core', 'Essence', 'Matrix']
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        return f"{prefix} {suffix} {blocks}"
    
    def _generate_fallback_piece(self, blocks: int) -> Dict[str, Any]:
        """Generate simple fallback piece"""
        return {
            'piece_id': f"fallback_{random.randint(1000, 9999)}",
            'name': f"Basic Fragment {blocks}",
            'shape': [[True] * blocks],
            'stats': {
                'hp': blocks * 100,
                'attack': blocks * 10,
                'defense': blocks * 5,
                'speed': blocks * 5
            },
            'piece_type': 'stat',
            'block_count': blocks,
            'voidstate_level': 0
        }
    
    def _log_generation(self, piece: Dict[str, Any]):
        """Log piece generation"""
        log_entry = {
            'timestamp': self._get_timestamp(),
            'piece_id': piece['piece_id'],
            'block_count': piece['block_count'],
            'voidstate_level': piece['voidstate_level'],
            'total_stats': sum(piece['stats'].values())
        }
        
        self.generation_history.append(log_entry)
        
        # Keep only recent history
        if len(self.generation_history) > 100:
            self.generation_history = self.generation_history[-100:]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def generate_daily_shop_pieces(self, voidstate: int, player_count: int) -> List[Dict[str, Any]]:
        """Generate pieces for daily shop"""
        pieces = []
        
        # Generate small pieces (1-2 blocks)
        small_count = random.randint(2, 3)
        for _ in range(small_count):
            blocks = random.randint(1, 2)
            piece = self.generate_piece(blocks, voidstate)
            pieces.append(piece)
        
        # Generate medium pieces (3-5 blocks)
        medium_count = random.randint(2, 3)
        for _ in range(medium_count):
            blocks = random.randint(3, 5)
            piece = self.generate_piece(blocks, voidstate)
            pieces.append(piece)
        
        # Generate large pieces (6+ blocks)
        large_count = random.randint(1, 2)
        for _ in range(large_count):
            blocks = random.randint(6, min(12, 6 + voidstate // 5))
            piece = self.generate_piece(blocks, voidstate)
            pieces.append(piece)
        
        return pieces
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about piece generation"""
        if not self.generation_history:
            return {'total_generated': 0}
        
        total_generated = len(self.generation_history)
        avg_blocks = sum(log['block_count'] for log in self.generation_history) / total_generated
        avg_stats = sum(log['total_stats'] for log in self.generation_history) / total_generated
        
        return {
            'total_generated': total_generated,
            'average_blocks': avg_blocks,
            'average_total_stats': avg_stats,
            'recent_generations': self.generation_history[-10:]
        } 