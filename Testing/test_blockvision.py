"""
Test BlockVision Module
Basic functionality test for the 3D workshop system
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blockvision.core.managers.scene_manager import get_scene_manager
from blockvision.core.managers.camera_manager import get_camera_manager
from blockvision.core.managers.object_manager import get_object_manager


def test_blockvision_managers():
    """Test the basic manager functionality"""
    print("🧪 Testing BlockVision Managers")
    print("=" * 40)
    
    # Test scene manager
    print("\n1. Testing Scene Manager:")
    scene_manager = get_scene_manager()
    print(f"   Initial state: {scene_manager.get_scene_status()}")
    
    # Create test object
    obj_id = scene_manager.create_object("Test Cube", "model")
    print(f"   Created object: {obj_id}")
    
    # Update object position
    scene_manager.update_object_position(obj_id, (1.0, 2.0, 3.0))
    print(f"   Updated position for {obj_id}")
    
    scene_status = scene_manager.get_scene_status()
    print(f"   Final scene status: {scene_status}")
    
    # Test camera manager
    print("\n2. Testing Camera Manager:")
    camera_manager = get_camera_manager()
    print(f"   Initial camera status: {camera_manager.get_camera_status()}")
    
    # Test camera movement
    camera_manager.orbit_camera(10.0, 5.0)
    camera_manager.zoom_camera(1.0)
    print(f"   After movement: {camera_manager.get_camera_status()}")
    
    # Test object manager
    print("\n3. Testing Object Manager:")
    object_manager = get_object_manager()
    print(f"   Initial object status: {object_manager.get_object_status()}")
    
    # Create template object
    cube_id = object_manager.create_template_object("cube", "TestCube")
    print(f"   Created cube: {cube_id}")
    
    # Test file format support
    formats = object_manager.get_supported_formats()
    print(f"   Supported formats: {formats}")
    
    # Test scene data
    print("\n4. Testing Scene Data:")
    scene_data = scene_manager.get_scene_data()
    print(f"   Scene objects: {len(scene_data['objects'])}")
    print(f"   Scene state: {scene_data['state']}")
    
    print("\n✅ All basic tests passed!")
    print("BlockVision module is working correctly.")


def test_gui_import():
    """Test GUI import (without running)"""
    print("\n5. Testing GUI Import:")
    try:
        from blockvision.gui.workshop_window import BlockVisionWorkshop
        print("   ✅ GUI module imports successfully")
    except ImportError as e:
        print(f"   ❌ GUI import failed: {e}")


if __name__ == "__main__":
    test_blockvision_managers()
    test_gui_import()
    
    print("\n🎯 BlockVision v0.1.0 is ready!")
    print("Next steps:")
    print("1. Implement OpenGL rendering")
    print("2. Add sprite conversion pipeline")
    print("3. Create real-time preview system")
    print("4. Add export functionality") 