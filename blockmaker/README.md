# Blockmaker

Blockmaker is a grid-based block creation tool for generating patterns ("sigils") for use in Sharkman AI and related projects.

## Features
- **12x12 grid** with 24x24 pixel blocks (matching upgrade grid size)
- **Click or drag to place blocks** sequentially with unique numbering
- **First block is always '+'** (block 1), regardless of spinbox value
- **Adjacency rules**: Each block must be placed adjacent to existing blocks
- **Random pattern generation** (respects block count and grid limits)
- **Visual feedback**: Valid placement highlights, block flashes, hover effects
- **Debug log** with real-time placement tracking
- **ASCII export** of current pattern (copy to clipboard)
- **QSplitter layout** for better UI organization
- **Consistent styling** with main application (imports from `core/style.py`)

## Usage
- **Run from the project root** for style imports to work:
  ```
  python blockmaker/blockmaker_window.py
  ```
- **Keyboard shortcuts**:
  - Enter: Create block
  - Ctrl+R: Random generate

## Block Rules
1. **First block** is numbered with "+" (block 1)
2. **Second block** is numbered "2"
3. **Each additional block** must be placed adjacent to a prior numbered block
4. **Each block includes** all numbers lower than itself
5. **Blocks can be placed** in any adjacent direction (up, down, left, right)

## Recent Fixes (v0.3.2)
- ✅ **Fixed duplicate block numbers** during drag placement
- ✅ **Drag placement** now increments block numbers correctly for each block placed
- ✅ **ASCII export** never shows -999 (flash value)
- ✅ **First block** is always '+' (1) on a fresh grid, regardless of spinbox value
- ✅ **Visual feedback** with proper flash effects that don't corrupt block numbers
- ✅ **QSplitter layout** for better UI organization

## Technical Details
- **Grid size**: 12x12 (144 maximum blocks)
- **Block size**: 24x24 pixels (matches upgrade grid)
- **Drag detection**: Prevents duplicate signals with visited/processing position tracking
- **Flash effect**: 200ms duration, restores original block number (not current count)
- **Style integration**: Uses `core/style.py` for consistent theming

## Bug Fix History
- **Duplicate numbers**: Fixed flash_block function overwriting block numbers with current count instead of restoring original
- **Drag placement**: Added proper duplicate prevention with `_drag_visited` and `_processing_positions` sets
- **First block numbering**: Ensured first block is always "+" regardless of spinbox value

## Troubleshooting
- **Style errors**: Make sure you're running from project root so `core/style.py` can be imported
- **Linter warnings**: Qt constant warnings are false positives (PyQt5 import issues)
- **UI stretching**: Update to latest version for QSplitter layout improvements

## AI Integration
The tool is designed for AI automation:
- **Python API**: Core logic can be imported and used programmatically
- **Pattern export**: ASCII format suitable for AI processing
- **Rule enforcement**: Built-in adjacency and numbering validation

## License
MIT 