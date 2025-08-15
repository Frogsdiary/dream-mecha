# Icon Generation Module for Dream Mecha

This module generates small WebP icons for Dream Mecha game pieces with transparent backgrounds and stat-based colors.

## Features

- **Transparent Backgrounds**: Icons have transparent backgrounds showing only the piece shape
- **Stat-Based Colors**: Colors match Dream Mecha's stat system (HP=Green, Attack=Red, Defense=Orange, Speed=Yellow)
- **WebP Format**: Optimized for smallest file size with good quality
- **Scalable**: Configurable icon sizes (default 64px)
- **Integration**: Seamlessly integrates with both Daily Content and Unique Pieces workflows

## Color Scheme

| Stat | Color | Hex Code | Visual |
|------|-------|----------|--------|
| HP | Green | #44ff44 | ![HP Color](https://via.placeholder.com/20x20/44ff44/44ff44) |
| Attack | Red | #ff4444 | ![Attack Color](https://via.placeholder.com/20x20/ff4444/ff4444) |
| Defense | Orange | #ff8800 | ![Defense Color](https://via.placeholder.com/20x20/ff8800/ff8800) |
| Speed | Yellow | #ffff44 | ![Speed Color](https://via.placeholder.com/20x20/ffff44/ffff44) |

## Installation

1. Install required dependencies:
   ```bash
   pip install -r icon_requirements.txt
   ```

2. The module is automatically imported in blockmaker_window.py

## Usage

### Daily Content Export
1. Open Blockmaker → Dream Mecha tab
2. Set generation parameters 
3. Click "Generate Daily Content"
4. Click "Export to JSON"
5. Icons are automatically generated and saved to `dream_mecha/database/daily/YYYY-MM-DD/icons/`

### Unique Pieces Export  
1. Open Blockmaker → Unique Pieces tab
2. Draw your piece on the grid
3. Select stat type
4. Click "Generate Unique Piece" to preview
5. Click "Export Piece with Icon" to save both JSON and icon
6. Files saved to `dream_mecha/database/unique_pieces/`

### Programmatic Usage

```python
from icon_generator import PieceIconGenerator

# Create generator
generator = PieceIconGenerator(icon_size=64)

# Sample piece data
piece_data = {
    'pattern_array': [
        [1, 0, 2],
        [3, 4, 0]
    ],
    'stat_type': 'hp',
    'id': 'my_piece_001'
}

# Generate icon
icon = generator.generate_icon(piece_data, 'output_path.webp')
```

## File Structure

After export, files are organized as:

```
dream_mecha/
├── database/
│   ├── daily/
│   │   ├── 2025-01-15/
│   │   │   ├── 2025-01-15.json
│   │   │   └── icons/
│   │   │       ├── piece_20250115_001.webp
│   │   │       ├── piece_20250115_002.webp
│   │   │       └── ...
│   │   └── ...
│   └── unique_pieces/
│       ├── unique_piece_20250115_143052.json
│       ├── unique_piece_20250115_143052.webp
│       └── ...
```

## Web Integration

Icons can be served by the web UI using the URL format:
- Daily pieces: `/static/daily/YYYY-MM-DD/icons/piece_id.webp`
- Unique pieces: `/static/unique_pieces/piece_id.webp`

The `get_icon_url()` method provides proper URL generation.

## Technical Details

- **Icon Size**: Default 64x64px (configurable)
- **Format**: WebP with 85% quality, method 6 for optimal compression
- **Scaling**: Auto-scales piece patterns to fit within icon bounds with padding
- **Border**: Subtle darker border on cells for definition (when cell size allows)
- **Transparency**: Full alpha channel support

## Testing

Run the test suite to verify functionality:

```bash
python test_icon_generation.py
```

This will:
- Test icon generation for all stat types and sizes
- Verify daily content integration
- Test URL generation
- Create sample icons in test directories

## Troubleshooting

### Common Issues

1. **PIL/Pillow Import Error**
   ```bash
   pip install Pillow
   ```

2. **Empty Pattern Array**
   - Ensure the piece has a valid pattern_array field
   - Check that grid contains blocks before export

3. **Icon Not Generated**
   - Check file permissions in output directory
   - Verify stat_type is valid ('hp', 'attack', 'defense', 'speed')

4. **File Size Too Large**
   - Icons are optimized WebP format, typically 1-3KB
   - Check if transparency is preserved

## Future Enhancements

- Multiple icon sizes for different UI contexts
- Custom color schemes for special piece types  
- SVG format support for infinite scalability
- Batch processing utilities
- Integration with web UI pagination system