"""
BlockVision: 3D-to-Sprite Workshop
Simple 3D environment for GameBoy-style sprite generation
"""

__version__ = "0.1.0"
__author__ = "Xaryxis Project"
__description__ = "3D workshop for GameBoy-style sprite generation"

# Core managers
from .core.managers.scene_manager import get_scene_manager
from .core.managers.camera_manager import get_camera_manager
from .core.managers.object_manager import get_object_manager

# GUI components
from .gui.workshop_window import BlockVisionWorkshop

__all__ = [
    'get_scene_manager',
    'get_camera_manager', 
    'get_object_manager',
    'BlockVisionWorkshop'
] 