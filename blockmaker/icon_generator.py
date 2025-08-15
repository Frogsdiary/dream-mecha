"""
Icon Generator for Dream Mecha Game Pieces
Generates small WebP icons with transparent backgrounds and stat-based colors
"""

import os
from PIL import Image, ImageDraw
from typing import List, Tuple, Dict, Any

class PieceIconGenerator:
    """Generate small icons for Dream Mecha game pieces"""
    
    # Stat colors from Dream Mecha CSS
    STAT_COLORS = {
        'hp': (68, 255, 68),        # #44ff44 - Green
        'attack': (255, 68, 68),    # #ff4444 - Red  
        'defense': (255, 136, 0),   # #ff8800 - Orange
        'speed': (255, 255, 68)     # #ffff44 - Yellow
    }
    
    def __init__(self, icon_size: int = 64):
        """
        Initialize the icon generator
        
        Args:
            icon_size: Size of the output icon in pixels (square)
        """
        self.icon_size = icon_size
        self.cell_size = max(2, icon_size // 16)  # Minimum 2px per cell, scale based on icon size
        self.border_width = max(1, icon_size // 32)  # Minimum 1px border
        
    def generate_icon(self, piece_data: Dict[str, Any], output_path: str = None) -> Image.Image:
        """
        Generate an icon for a game piece
        
        Args:
            piece_data: Dictionary containing piece information with pattern_array and stat_type
            output_path: Optional path to save the icon (will save as WebP)
            
        Returns:
            PIL Image object of the generated icon
        """
        pattern_array = piece_data.get('pattern_array', [])
        stat_type = piece_data.get('stat_type', 'hp')
        piece_id = piece_data.get('id', 'unknown')
        
        if not pattern_array:
            raise ValueError(f"No pattern_array found in piece data for {piece_id}")
            
        # Get stat color
        color = self.STAT_COLORS.get(stat_type.lower(), self.STAT_COLORS['hp'])
        
        # Create the icon
        icon = self._create_icon_from_pattern(pattern_array, color)
        
        # Save if path provided
        if output_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save as WebP for smallest file size with good quality
            icon.save(output_path, 'WEBP', quality=85, method=6)
            
        return icon
    
    def _create_icon_from_pattern(self, pattern_array: List[List[int]], color: Tuple[int, int, int]) -> Image.Image:
        """
        Create an icon image from a pattern array
        
        Args:
            pattern_array: 2D array representing the piece pattern
            color: RGB color tuple for the piece
            
        Returns:
            PIL Image with transparent background
        """
        # Find the bounding box of the pattern
        filled_positions = []
        for row_idx, row in enumerate(pattern_array):
            for col_idx, cell in enumerate(row):
                if cell > 0:  # Non-zero means filled
                    filled_positions.append((row_idx, col_idx))
        
        if not filled_positions:
            # Empty pattern, create a single pixel
            filled_positions = [(0, 0)]
        
        # Calculate bounds
        min_row = min(pos[0] for pos in filled_positions)
        max_row = max(pos[0] for pos in filled_positions)
        min_col = min(pos[1] for pos in filled_positions)
        max_col = max(pos[1] for pos in filled_positions)
        
        pattern_width = max_col - min_col + 1
        pattern_height = max_row - min_row + 1
        
        # Calculate scaling to fit within icon size with padding
        padding = self.icon_size // 8  # 12.5% padding on each side
        available_size = self.icon_size - (2 * padding)
        
        # Scale to fit while maintaining aspect ratio
        scale_factor = min(available_size / pattern_width, available_size / pattern_height)
        cell_size = max(1, int(scale_factor))
        
        # Calculate actual pattern size after scaling
        scaled_width = pattern_width * cell_size
        scaled_height = pattern_height * cell_size
        
        # Center the pattern in the icon
        offset_x = (self.icon_size - scaled_width) // 2
        offset_y = (self.icon_size - scaled_height) // 2
        
        # Create image with transparent background
        icon = Image.new('RGBA', (self.icon_size, self.icon_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Draw the pattern
        for row_idx, col_idx in filled_positions:
            # Normalize position relative to bounding box
            norm_row = row_idx - min_row
            norm_col = col_idx - min_col
            
            # Calculate pixel position
            x = offset_x + (norm_col * cell_size)
            y = offset_y + (norm_row * cell_size)
            
            # Draw filled rectangle with border for definition
            # Main color fill
            draw.rectangle(
                [x, y, x + cell_size - 1, y + cell_size - 1],
                fill=(*color, 255)  # Full opacity
            )
            
            # Subtle border for definition (darker version of the color)
            border_color = tuple(max(0, c - 40) for c in color)
            if cell_size > 2:  # Only add border if cell is large enough
                draw.rectangle(
                    [x, y, x + cell_size - 1, y + cell_size - 1],
                    outline=(*border_color, 255),
                    width=1
                )
        
        return icon
    
    def generate_icons_for_daily_content(self, daily_data: Dict[str, Any], output_dir: str) -> List[str]:
        """
        Generate icons for all pieces in daily content
        
        Args:
            daily_data: Daily content dictionary with shop_pieces
            output_dir: Directory to save icons
            
        Returns:
            List of generated icon file paths
        """
        generated_files = []
        
        shop_pieces = daily_data.get('shop_pieces', [])
        if not shop_pieces:
            return generated_files
        
        # Create subdirectory for icons
        icons_dir = os.path.join(output_dir, 'icons')
        os.makedirs(icons_dir, exist_ok=True)
        
        for piece in shop_pieces:
            piece_id = piece.get('id', 'unknown')
            
            # Generate filename
            icon_filename = f"{piece_id}.webp"
            icon_path = os.path.join(icons_dir, icon_filename)
            
            try:
                # Generate the icon
                self.generate_icon(piece, icon_path)
                generated_files.append(icon_path)
                
            except Exception as e:
                print(f"Error generating icon for {piece_id}: {e}")
                continue
        
        return generated_files
    
    def get_icon_url(self, piece_id: str, date_str: str) -> str:
        """
        Get the URL path for an icon
        
        Args:
            piece_id: ID of the piece
            date_str: Date string (YYYY-MM-DD format)
            
        Returns:
            URL path to the icon
        """
        return f"/static/daily/{date_str}/icons/{piece_id}.webp"

def generate_piece_icon(pattern_array: List[List[int]], stat_type: str, 
                       output_path: str = None, size: int = 64) -> Image.Image:
    """
    Convenience function to generate a single piece icon
    
    Args:
        pattern_array: 2D array representing the piece pattern  
        stat_type: Type of stat ('hp', 'attack', 'defense', 'speed')
        output_path: Optional path to save the icon
        size: Icon size in pixels
        
    Returns:
        PIL Image object
    """
    generator = PieceIconGenerator(size)
    piece_data = {
        'pattern_array': pattern_array,
        'stat_type': stat_type,
        'id': 'single_piece'
    }
    return generator.generate_icon(piece_data, output_path)

if __name__ == "__main__":
    # Test the icon generator
    test_pattern = [
        [1, 0, 0, 0],
        [2, 3, 0, 0], 
        [0, 4, 5, 0],
        [0, 0, 0, 0]
    ]
    
    test_piece = {
        'pattern_array': test_pattern,
        'stat_type': 'hp',
        'id': 'test_piece'
    }
    
    generator = PieceIconGenerator(64)
    icon = generator.generate_icon(test_piece, 'test_icon.webp')
    print("Test icon generated successfully!")