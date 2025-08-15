"""
Test script for icon generation functionality
Run this to verify that icon generation works correctly
"""

import os
import json
from datetime import datetime

try:
    from icon_generator import PieceIconGenerator
    print("✓ Icon generator imported successfully")
except ImportError as e:
    print(f"✗ Failed to import icon generator: {e}")
    print("Make sure PIL/Pillow is installed: pip install Pillow")
    exit(1)

def test_icon_generation():
    """Test basic icon generation functionality"""
    
    # Test pattern (simple L-shape)
    test_pattern = [
        [1, 0, 0],
        [2, 3, 4],
        [0, 0, 0]
    ]
    
    test_piece = {
        'pattern_array': test_pattern,
        'stat_type': 'hp',
        'id': 'test_piece_hp'
    }
    
    print("\n=== Testing Icon Generation ===")
    
    # Test different sizes
    sizes = [32, 64, 128]
    colors = ['hp', 'attack', 'defense', 'speed']
    
    test_dir = "test_icons"
    os.makedirs(test_dir, exist_ok=True)
    
    for size in sizes:
        for color in colors:
            try:
                generator = PieceIconGenerator(size)
                test_piece['stat_type'] = color
                test_piece['id'] = f'test_{color}_{size}px'
                
                icon_path = os.path.join(test_dir, f"test_{color}_{size}px.webp")
                icon = generator.generate_icon(test_piece, icon_path)
                
                # Check if file was created
                if os.path.exists(icon_path):
                    file_size = os.path.getsize(icon_path)
                    print(f"✓ Generated {color} icon ({size}px): {file_size} bytes")
                else:
                    print(f"✗ Failed to create {color} icon ({size}px)")
                    
            except Exception as e:
                print(f"✗ Error generating {color} icon ({size}px): {e}")
    
    print(f"\nTest icons saved in: {os.path.abspath(test_dir)}")

def test_daily_content_integration():
    """Test integration with daily content format"""
    
    print("\n=== Testing Daily Content Integration ===")
    
    # Sample daily content structure
    sample_daily_data = {
        "date": "2025-01-01",
        "shop_pieces": [
            {
                "pattern": "+2..3...",
                "pattern_array": [
                    [1, 2, 0, 0, 3, 0, 0, 0]
                ],
                "blocks": 3,
                "stats": {"hp": 1500, "att": 0, "def": 0, "spd": 0},
                "stat_type": "hp",
                "price": 150,
                "rarity": "common",
                "id": "test_piece_001",
                "size_category": "small"
            },
            {
                "pattern": "+.2\n3.4",
                "pattern_array": [
                    [1, 0, 2],
                    [3, 0, 4]
                ],
                "blocks": 4,
                "stats": {"hp": 0, "att": 800, "def": 0, "spd": 0},
                "stat_type": "attack",
                "price": 80,
                "rarity": "common",
                "id": "test_piece_002",
                "size_category": "small"
            }
        ]
    }
    
    try:
        generator = PieceIconGenerator(64)
        test_dir = "test_daily_icons"
        generated_files = generator.generate_icons_for_daily_content(sample_daily_data, test_dir)
        
        print(f"✓ Generated {len(generated_files)} icons for daily content")
        for file_path in generated_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"  - {os.path.basename(file_path)}: {file_size} bytes")
            else:
                print(f"  ✗ Missing: {os.path.basename(file_path)}")
                
    except Exception as e:
        print(f"✗ Error in daily content integration: {e}")

def test_url_generation():
    """Test URL generation for web integration"""
    
    print("\n=== Testing URL Generation ===")
    
    try:
        generator = PieceIconGenerator()
        
        test_cases = [
            ("piece_20250101_001", "2025-01-01"),
            ("unique_piece_20250115_143052", "2025-01-15")
        ]
        
        for piece_id, date_str in test_cases:
            url = generator.get_icon_url(piece_id, date_str)
            print(f"✓ URL for {piece_id}: {url}")
            
    except Exception as e:
        print(f"✗ Error in URL generation: {e}")

if __name__ == "__main__":
    print("Icon Generation Test Suite")
    print("=" * 40)
    
    test_icon_generation()
    test_daily_content_integration()
    test_url_generation()
    
    print("\n" + "=" * 40)
    print("Test completed!")
    print("\nTo run this test:")
    print("1. Ensure PIL/Pillow is installed: pip install Pillow")
    print("2. Run: python test_icon_generation.py")
    print("3. Check the generated test_icons/ and test_daily_icons/ folders")