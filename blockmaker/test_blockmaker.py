#!/usr/bin/env python3
"""
Test script for Blockmaker module
Tests the core functionality without GUI
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from blockmaker.blockmaker_window import BlockmakerGrid

# Create QApplication for testing
app = QApplication(sys.argv)

def test_grid_functionality():
    """Test the grid functionality without GUI"""
    print("Testing BlockmakerGrid functionality...")
    
    # Create grid
    grid = BlockmakerGrid(grid_size=6)  # Smaller grid for testing
    
    # Test initial state
    assert len(grid.blocks) == 0, "Grid should start empty"
    assert len(grid.valid_positions) == 36, "All positions should be valid initially"
    
    # Test first block placement
    center = grid.grid_size // 2
    grid.add_block((center, center), 1)
    
    assert len(grid.blocks) == 1, "Should have one block"
    assert (center, center) in grid.blocks, "Block should be at center"
    assert grid.blocks[(center, center)] == 1, "Block should be numbered 1"
    
    # Test valid positions after first block
    assert len(grid.valid_positions) == 4, "Should have 4 adjacent positions"
    expected_positions = {
        (center-1, center), (center+1, center),
        (center, center-1), (center, center+1)
    }
    assert grid.valid_positions == expected_positions, "Valid positions should be adjacent"
    
    # Test second block placement
    grid.add_block((center+1, center), 2)
    assert len(grid.blocks) == 2, "Should have two blocks"
    assert grid.blocks[(center+1, center)] == 2, "Second block should be numbered 2"
    
    # Test valid positions after second block
    assert len(grid.valid_positions) == 6, "Should have 6 valid positions"
    
    # Test clear functionality
    grid.clear_grid()
    assert len(grid.blocks) == 0, "Grid should be empty after clear"
    assert len(grid.valid_positions) == 36, "All positions should be valid after clear"
    
    print("✓ All grid functionality tests passed!")

def test_position_calculation():
    """Test grid position calculation"""
    print("Testing position calculation...")
    
    grid = BlockmakerGrid(grid_size=4)
    
    # Test valid positions
    assert grid.get_grid_position(grid.mapFromGlobal(grid.mapToGlobal(grid.rect().center()))) is not None
    
    # Test invalid positions
    assert grid.get_grid_position(grid.mapFromGlobal(grid.mapToGlobal(grid.rect().topLeft() - grid.rect().topLeft()))) is None
    
    print("✓ Position calculation tests passed!")

if __name__ == "__main__":
    print("Blockmaker Module Test Suite")
    print("=" * 40)
    
    try:
        test_grid_functionality()
        test_position_calculation()
        print("\n🎉 All tests passed! Blockmaker module is working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1) 