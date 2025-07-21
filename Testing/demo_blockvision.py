"""
BlockVision Demo
Test image loading and rendering functionality
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blockvision.core.managers.scene_manager import get_scene_manager
from blockvision.core.managers.object_manager import get_object_manager
from blockvision.core.utils.image_loader import get_image_loader


def demo_image_loading():
    """Demo image loading functionality"""
    print("🎨 BlockVision Image Loading Demo")
    print("=" * 40)
    
    # Initialize components
    scene_manager = get_scene_manager()
    object_manager = get_object_manager()
    image_loader = get_image_loader()
    
    print("\n1. Testing Image Loader:")
    print(f"   Supported formats: {image_loader.supported_formats}")
    
    # Test with a sample image path (you can replace this)
    test_image_path = "C:/Users/Jason/Desktop/recent drawings/asdf.jpg"
    
    if os.path.exists(test_image_path):
        print(f"\n2. Loading test image: {test_image_path}")
        
        # Load image
        image_data = image_loader.load_image(test_image_path)
        if image_data:
            print(f"   ✅ Image loaded successfully!")
            print(f"   Original size: {image_data['original_size']}")
            print(f"   Processed size: {image_data['processed_size']}")
            print(f"   Format: {image_data['format']}")
            
            # Import as object
            obj_id = object_manager.import_file(test_image_path)
            if obj_id:
                print(f"   ✅ Object created: {obj_id}")
                
                # Add to scene
                scene_obj_id = scene_manager.create_object(
                    name=f"Image_{obj_id}",
                    obj_type="image"
                )
                print(f"   ✅ Added to scene: {scene_obj_id}")
                
                # Get scene status
                scene_status = scene_manager.get_scene_status()
                print(f"   Scene objects: {scene_status['object_count']}")
                
            else:
                print("   ❌ Failed to create object")
        else:
            print("   ❌ Failed to load image")
    else:
        print(f"\n2. Test image not found: {test_image_path}")
        print("   Please provide a valid image path to test")
    
    print("\n3. Cache Information:")
    cache_info = image_loader.get_cache_info()
    print(f"   Cached images: {cache_info['cached_images']}")
    print(f"   Cache size: {cache_info['cache_size']} pixels")
    
    print("\n✅ Image loading demo complete!")
    print("\nNext steps:")
    print("1. Run the GUI to see the rendered image")
    print("2. Test with different image formats")
    print("3. Try the transform controls")


if __name__ == "__main__":
    demo_image_loading() 