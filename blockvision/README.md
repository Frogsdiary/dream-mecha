# BlockVision: 3D-to-Sprite Workshop

## Version Info
- **Version**: v0.1.0
- **Status**: Initial Implementation
- **Last Updated**: 2025-01-08
- **Target**: Simple 3D workshop for GameBoy-style sprite generation

## Project Overview

BlockVision is a 3D workshop environment that converts 3D models and images into GameBoy-style sprites. Users can import objects, position them in 3D space, and toggle real-time sprite conversion to see instant GameBoy-style previews.

## Core Features

### Phase 1: Basic Workshop (v0.1.0)
- [x] 3D scene management
- [x] Object import (3D models + images)
- [x] Basic move/scale/rotate controls
- [x] Camera controls (orbit, zoom, reset)
- [x] Simple GUI interface
- [x] Image loading and black & white conversion
- [x] Basic OpenGL rendering
- [x] Detailed transform controls

### Phase 2: Sprite Conversion (v0.2.0)
- [ ] GameBoy color palette (4 colors)
- [ ] Real-time conversion pipeline
- [ ] Live preview system
- [ ] Toggle functionality (3D ↔ Sprite)

### Phase 3: Export & Polish (v0.3.0)
- [ ] Sprite capture functionality
- [ ] Multi-angle sprite sheets
- [ ] Animation frame generation
- [ ] Export to game formats

## Architecture

```
blockvision/
├── core/
│   ├── managers/
│   │   ├── scene_manager.py          # 3D scene management
│   │   ├── camera_manager.py         # Camera positioning
│   │   └── object_manager.py         # Object manipulation
│   ├── renderers/
│   │   ├── opengl_renderer.py        # OpenGL 3D rendering
│   │   └── sprite_converter.py       # GameBoy conversion
│   └── utils/
│       ├── model_loader.py           # 3D model import
│       └── color_palettes.py         # GameBoy colors
├── gui/
│   ├── workshop_window.py            # Main workshop interface
│   ├── scene_viewer.py               # 3D scene viewer
│   └── controls_panel.py             # Object/camera controls
└── tests/
    ├── test_scene_manager.py         # Scene management tests
    └── test_sprite_converter.py      # Conversion tests
```

## Technical Implementation

### Dependencies
- **OpenGL**: 3D rendering
- **PyOpenGL**: Python OpenGL bindings
- **NumPy**: 3D math operations
- **Pillow**: Image processing
- **PyQt5**: GUI framework (existing)

### Performance Targets
- Real-time rendering: 30 FPS
- Sprite conversion: < 100ms
- Object manipulation: Smooth response
- Memory usage: < 500MB

### File Formats
- **Input**: OBJ, FBX, JPG, PNG, BMP
- **Output**: PNG sprite sheets, individual sprites

## Usage Workflow

1. **Import Object**: Load 3D model or image
2. **Position**: Use move/scale/rotate controls
3. **Adjust Camera**: Orbit/zoom to desired angle
4. **Toggle Sprite Mode**: See GameBoy preview
5. **Capture**: Save sprite when satisfied

## Integration with Xaryxis

BlockVision integrates with the existing Xaryxis project:
- Uses established manager patterns
- Follows modular architecture
- Compatible with existing GUI framework
- Thread-safe operation

## Development Status

### Completed (v0.1.0)
- [x] Module structure setup
- [x] Basic documentation
- [x] Scene manager foundation
- [x] Object manager system
- [x] Image loader with black & white conversion
- [x] Basic OpenGL renderer
- [x] GUI with detailed transform controls
- [x] Object list and selection system

### In Progress
- [ ] Sprite conversion pipeline
- [ ] Real-time GameBoy preview
- [ ] 3D model loading implementation

### Next Steps
- [ ] Sprite conversion pipeline
- [ ] Real-time preview system
- [ ] Export functionality
- [ ] Integration testing 