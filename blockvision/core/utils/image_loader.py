"""
Image Loader - BlockVision Core
Handles image loading, processing, and black & white conversion
"""

import os
from typing import Optional, Tuple, Dict, Any

# Check dependencies
try:
    import numpy as np
    from PIL import Image, ImageOps
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Image loader dependencies missing: {e}")
    print("Install with: pip install Pillow numpy")
    DEPENDENCIES_AVAILABLE = False

# Global image cache
_image_cache = {}


class ImageLoader:
    """Handles image loading and processing for flat objects"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tga']
        self.max_image_size = (1024, 1024)  # Maximum image dimensions
    
    def load_image(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load and process image file"""
        if not DEPENDENCIES_AVAILABLE:
            print("Image loader dependencies not available")
            return None
        
        if not os.path.exists(file_path):
            print(f"Image file not found: {file_path}")
            return None
        
        # Check cache first
        if file_path in _image_cache:
            return _image_cache[file_path]
        
        try:
            # Load image with PIL
            with Image.open(file_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large
                if img.size[0] > self.max_image_size[0] or img.size[1] > self.max_image_size[1]:
                    img.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                
                # Convert to black and white
                bw_img = self.convert_to_black_white(img)
                
                # Create image data
                image_data = {
                    'original_path': file_path,
                    'original_size': img.size,
                    'processed_size': bw_img.size,
                    'pixel_data': np.array(bw_img),
                    'width': bw_img.size[0],
                    'height': bw_img.size[1],
                    'format': 'bw',  # black and white
                    'original_color_data': np.array(img)  # Preserve original color data
                }
                
                # Cache the result
                _image_cache[file_path] = image_data
                
                print(f"Loaded image: {file_path} ({bw_img.size[0]}x{bw_img.size[1]})")
                return image_data
                
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            return None
    
    def convert_to_black_white(self, image: Image.Image) -> Image.Image:
        """Convert image to black and white"""
        # Convert to grayscale first
        gray_img = ImageOps.grayscale(image)
        
        # Apply threshold to create pure black and white
        # This creates a more GameBoy-like appearance
        threshold = 128
        def threshold_func(x):
            return 0 if x < threshold else 255
        bw_img = gray_img.point(threshold_func)
        
        return bw_img
    
    def resize_image(self, image_data: Dict[str, Any], new_size: Tuple[int, int]) -> Dict[str, Any]:
        """Resize image data"""
        if 'pixel_data' not in image_data:
            return image_data
        
        # Convert numpy array back to PIL image
        img = Image.fromarray(image_data['pixel_data'])
        
        # Resize
        resized_img = img.resize(new_size, Image.Resampling.NEAREST)
        
        # Update image data
        resized_data = image_data.copy()
        resized_data['pixel_data'] = np.array(resized_img)
        resized_data['processed_size'] = resized_img.size
        resized_data['width'] = resized_img.size[0]
        resized_data['height'] = resized_img.size[1]
        
        return resized_data
    
    def get_image_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get basic image information without loading"""
        if not os.path.exists(file_path):
            return None
        
        try:
            with Image.open(file_path) as img:
                return {
                    'path': file_path,
                    'size': img.size,
                    'mode': img.mode,
                    'format': img.format
                }
        except Exception as e:
            print(f"Error getting image info: {e}")
            return None
    
    def clear_cache(self):
        """Clear image cache"""
        global _image_cache
        _image_cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information"""
        return {
            'cached_images': len(_image_cache),
            'cache_size': sum(
                img_data['width'] * img_data['height'] 
                for img_data in _image_cache.values()
            )
        }


# Global image loader instance
_image_loader = None


def get_image_loader() -> ImageLoader:
    """Get the global image loader instance (singleton)"""
    global _image_loader
    if _image_loader is None:
        _image_loader = ImageLoader()
    return _image_loader 