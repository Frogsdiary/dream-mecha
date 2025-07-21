"""
Grid System - Upgrade grid management and piece placement

Handles the 8x8 to 18x18 grid system for stat pieces and glyphs.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json


@dataclass
class GridPiece:
    """Represents a piece on the grid"""
    piece_id: str
    piece_type: str  # 'stat', 'glyph'
    shape: List[List[bool]]  # 2D array of boolean values
    stats: Dict[str, int]  # HP, Attack, Defense, Speed
    position: Tuple[int, int]  # Top-left corner position
    rotation: int = 0  # 0, 90, 180, 270 degrees


class GridSystem:
    """Manages upgrade grids for mechas"""
    
    def __init__(self, initial_size: int = 8):
        self.max_size = 18
        self.current_size = min(initial_size, self.max_size)
        self.grid: List[List[Optional[str]]] = [[None for _ in range(self.current_size)] for _ in range(self.current_size)]
        self.pieces: Dict[str, GridPiece] = {}
        self.glyphs: Dict[str, GridPiece] = {}
    
    def can_place_piece(self, piece: GridPiece, position: Tuple[int, int]) -> bool:
        """Check if a piece can be placed at the given position"""
        x, y = position
        shape = piece.shape
        
        # Check if piece fits within grid bounds
        if x + len(shape[0]) > self.current_size or y + len(shape) > self.current_size:
            return False
        
        # Check if position is occupied
        for dy, row in enumerate(shape):
            for dx, cell in enumerate(row):
                if cell and self.grid[y + dy][x + dx] is not None:
                    return False
        
        return True
    
    def place_piece(self, piece: GridPiece, position: Tuple[int, int]) -> bool:
        """Place a piece on the grid"""
        if not self.can_place_piece(piece, position):
            return False
        
        x, y = position
        shape = piece.shape
        
        # Place the piece
        for dy, row in enumerate(shape):
            for dx, cell in enumerate(row):
                if cell:
                    self.grid[y + dy][x + dx] = piece.piece_id
        
        # Store piece data
        piece.position = position
        if piece.piece_type == 'glyph':
            self.glyphs[piece.piece_id] = piece
        else:
            self.pieces[piece.piece_id] = piece
        
        return True
    
    def remove_piece(self, piece_id: str) -> bool:
        """Remove a piece from the grid"""
        piece = self.pieces.get(piece_id) or self.glyphs.get(piece_id)
        if not piece:
            return False
        
        x, y = piece.position
        shape = piece.shape
        
        # Remove from grid
        for dy, row in enumerate(shape):
            for dx, cell in enumerate(row):
                if cell and self.grid[y + dy][x + dx] == piece_id:
                    self.grid[y + dy][x + dx] = None
        
        # Remove from storage
        if piece_id in self.pieces:
            del self.pieces[piece_id]
        if piece_id in self.glyphs:
            del self.glyphs[piece_id]
        
        return True
    
    def rotate_piece(self, piece_id: str) -> bool:
        """Rotate a piece 90 degrees clockwise"""
        piece = self.pieces.get(piece_id) or self.glyphs.get(piece_id)
        if not piece:
            return False
        
        # Remove piece temporarily
        self.remove_piece(piece_id)
        
        # Rotate shape
        old_shape = piece.shape
        rows, cols = len(old_shape), len(old_shape[0])
        new_shape = [[False for _ in range(rows)] for _ in range(cols)]
        
        for y in range(rows):
            for x in range(cols):
                new_shape[x][rows - 1 - y] = old_shape[y][x]
        
        piece.shape = new_shape
        piece.rotation = (piece.rotation + 90) % 360
        
        # Try to place back
        if self.can_place_piece(piece, piece.position):
            self.place_piece(piece, piece.position)
            return True
        else:
            # If can't place, revert rotation
            piece.shape = old_shape
            piece.rotation = (piece.rotation - 90) % 360
            self.place_piece(piece, piece.position)
            return False
    
    def expand_grid(self, direction: str) -> bool:
        """Expand grid by 1 in specified direction"""
        if self.current_size >= self.max_size:
            return False
        
        new_size = self.current_size + 1
        new_grid = [[None for _ in range(new_size)] for _ in range(new_size)]
        
        # Copy existing grid
        for y in range(self.current_size):
            for x in range(self.current_size):
                new_grid[y][x] = self.grid[y][x]
        
        self.grid = new_grid
        self.current_size = new_size
        return True
    
    def calculate_stats(self) -> Dict[str, int]:
        """Calculate total stats from all pieces on grid"""
        total_stats = {'hp': 0, 'attack': 0, 'defense': 0, 'speed': 0}
        
        # Calculate base stats from pieces
        for piece in self.pieces.values():
            for stat, value in piece.stats.items():
                total_stats[stat] += value
        
        # Apply glyph effects
        for glyph in self.glyphs.values():
            affected_pieces = self.get_pieces_in_glyph_area(glyph)
            for piece in affected_pieces:
                # Apply glyph enhancement (implementation depends on glyph type)
                pass
        
        return total_stats
    
    def get_pieces_in_glyph_area(self, glyph: GridPiece) -> List[GridPiece]:
        """Get all pieces within a glyph's area of effect"""
        affected_pieces = []
        glyph_x, glyph_y = glyph.position
        glyph_shape = glyph.shape
        
        for piece in self.pieces.values():
            piece_x, piece_y = piece.position
            piece_shape = piece.shape
            
            # Check if piece overlaps with glyph area
            if self.shapes_overlap(glyph_x, glyph_y, glyph_shape, piece_x, piece_y, piece_shape):
                affected_pieces.append(piece)
        
        return affected_pieces
    
    def shapes_overlap(self, x1: int, y1: int, shape1: List[List[bool]], 
                      x2: int, y2: int, shape2: List[List[bool]]) -> bool:
        """Check if two shapes overlap"""
        # Simple overlap detection - can be optimized
        for dy1, row1 in enumerate(shape1):
            for dx1, cell1 in enumerate(row1):
                if not cell1:
                    continue
                
                pos1_x, pos1_y = x1 + dx1, y1 + dy1
                
                for dy2, row2 in enumerate(shape2):
                    for dx2, cell2 in enumerate(row2):
                        if not cell2:
                            continue
                        
                        pos2_x, pos2_y = x2 + dx2, y2 + dy2
                        
                        if pos1_x == pos2_x and pos1_y == pos2_y:
                            return True
        
        return False
    
    def to_json(self) -> str:
        """Serialize grid to JSON"""
        data = {
            'current_size': self.current_size,
            'grid': self.grid,
            'pieces': {pid: {
                'piece_type': p.piece_type,
                'shape': p.shape,
                'stats': p.stats,
                'position': p.position,
                'rotation': p.rotation
            } for pid, p in self.pieces.items()},
            'glyphs': {gid: {
                'piece_type': g.piece_type,
                'shape': g.shape,
                'stats': g.stats,
                'position': g.position,
                'rotation': g.rotation
            } for gid, g in self.glyphs.items()}
        }
        return json.dumps(data)
    
    def from_json(self, json_str: str):
        """Deserialize grid from JSON"""
        data = json.loads(json_str)
        self.current_size = data['current_size']
        self.grid = data['grid']
        
        self.pieces.clear()
        self.glyphs.clear()
        
        for pid, p_data in data['pieces'].items():
            piece = GridPiece(
                piece_id=pid,
                piece_type=p_data['piece_type'],
                shape=p_data['shape'],
                stats=p_data['stats'],
                position=tuple(p_data['position']),
                rotation=p_data['rotation']
            )
            self.pieces[pid] = piece
        
        for gid, g_data in data['glyphs'].items():
            glyph = GridPiece(
                piece_id=gid,
                piece_type=g_data['piece_type'],
                shape=g_data['shape'],
                stats=g_data['stats'],
                position=tuple(g_data['position']),
                rotation=g_data['rotation']
            )
            self.glyphs[gid] = glyph 