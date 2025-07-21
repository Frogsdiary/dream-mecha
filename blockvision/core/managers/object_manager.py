"""
Object Manager - BlockVision Core
Handles object creation, manipulation, and file imports
"""

import os
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from ..utils.image_loader import get_image_loader

# Global object manager instance
_object_manager = None


class ObjectType(Enum):
    MODEL = "model"
    IMAGE = "image"
    FLAT = "flat"


@dataclass
class ObjectData:
    """Object data and properties"""
    id: str
    name: str
    type: ObjectType
    file_path: Optional[str] = None
    mesh_data: Optional[Dict] = None
    texture_data: Optional[Dict] = None
    created_at: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class ObjectManager:
    """
    Manages object creation, manipulation, and file imports
    Follows singleton pattern like scene_manager
    """
    
    def __init__(self):
        self.objects: Dict[str, ObjectData] = {}
        self.object_counter = 0
        
        # Initialize image loader
        self.image_loader = get_image_loader()
        
        # Supported file formats
        self.supported_models = ['.obj', '.fbx', '.gltf', '.glb']
        self.supported_images = ['.jpg', '.jpeg', '.png', '.bmp', '.tga']
        
        # Object templates
        self.templates = {
            'cube': self._create_cube_template,
            'sphere': self._create_sphere_template,
            'plane': self._create_plane_template
        }
    
    def import_file(self, file_path: str) -> Optional[str]:
        """Import object from file"""
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in self.supported_models:
            return self._import_model(file_path)
        elif file_ext in self.supported_images:
            return self._import_image(file_path)
        else:
            print(f"Unsupported file format: {file_ext}")
            return None
    
    def _import_model(self, file_path: str) -> Optional[str]:
        """Import 3D model file"""
        try:
            # For now, create a placeholder object
            # TODO: Implement actual model loading
            obj_id = self._create_object_from_file(file_path, ObjectType.MODEL)
            print(f"Imported model: {file_path}")
            return obj_id
        except Exception as e:
            print(f"Error importing model: {e}")
            return None
    
    def _import_image(self, file_path: str) -> Optional[str]:
        """Import image file as flat object"""
        try:
            # Load and process image
            image_data = self.image_loader.load_image(file_path)
            if not image_data:
                print(f"Failed to load image: {file_path}")
                return None
            
            # Create object with image data
            obj_id = self._create_object_from_file(file_path, ObjectType.IMAGE)
            obj_data = self.get_object(obj_id)
            if obj_data:
                obj_data.texture_data = image_data
            
            print(f"Imported image: {file_path} ({image_data['width']}x{image_data['height']})")
            return obj_id
        except Exception as e:
            print(f"Error importing image: {e}")
            return None
    
    def _create_object_from_file(self, file_path: str, obj_type: ObjectType) -> str:
        """Create object from file"""
        self.object_counter += 1
        obj_id = f"obj_{self.object_counter}"
        
        name = os.path.splitext(os.path.basename(file_path))[0]
        
        obj_data = ObjectData(
            id=obj_id,
            name=name,
            type=obj_type,
            file_path=file_path
        )
        
        self.objects[obj_id] = obj_data
        return obj_id
    
    def create_template_object(self, template_name: str, name: Optional[str] = None) -> Optional[str]:
        """Create object from template"""
        if template_name not in self.templates:
            print(f"Unknown template: {template_name}")
            return None
        
        if name is None:
            name = f"{template_name}_{self.object_counter + 1}"
        
        self.object_counter += 1
        obj_id = f"obj_{self.object_counter}"
        
        obj_data = ObjectData(
            id=obj_id,
            name=name,
            type=ObjectType.MODEL
        )
        
        # Apply template data
        template_func = self.templates[template_name]
        template_data = template_func()
        obj_data.mesh_data = template_data
        
        self.objects[obj_id] = obj_data
        return obj_id
    
    def _create_cube_template(self) -> Dict:
        """Create cube mesh template"""
        return {
            'type': 'cube',
            'vertices': [
                # Front face
                (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
                # Back face
                (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1)
            ],
            'faces': [
                [0, 1, 2, 3],  # Front
                [5, 4, 7, 6],  # Back
                [4, 0, 3, 7],  # Left
                [1, 5, 6, 2],  # Right
                [3, 2, 6, 7],  # Top
                [4, 5, 1, 0]   # Bottom
            ]
        }
    
    def _create_sphere_template(self) -> Dict:
        """Create sphere mesh template"""
        return {
            'type': 'sphere',
            'radius': 1.0,
            'segments': 16,
            'rings': 8
        }
    
    def _create_plane_template(self) -> Dict:
        """Create plane mesh template"""
        return {
            'type': 'plane',
            'width': 2.0,
            'height': 2.0,
            'segments_x': 1,
            'segments_y': 1
        }
    
    def get_object(self, obj_id: str) -> Optional[ObjectData]:
        """Get object by ID"""
        return self.objects.get(obj_id)
    
    def remove_object(self, obj_id: str) -> bool:
        """Remove object"""
        if obj_id in self.objects:
            del self.objects[obj_id]
            return True
        return False
    
    def get_all_objects(self) -> List[ObjectData]:
        """Get all objects"""
        return list(self.objects.values())
    
    def get_objects_by_type(self, obj_type: ObjectType) -> List[ObjectData]:
        """Get objects by type"""
        return [obj for obj in self.objects.values() if obj.type == obj_type]
    
    def get_object_status(self) -> Dict[str, Any]:
        """Get object manager status"""
        return {
            'total_objects': len(self.objects),
            'models': len(self.get_objects_by_type(ObjectType.MODEL)),
            'images': len(self.get_objects_by_type(ObjectType.IMAGE)),
            'supported_formats': {
                'models': self.supported_models,
                'images': self.supported_images
            }
        }
    
    def clear_all_objects(self):
        """Clear all objects"""
        self.objects.clear()
        self.object_counter = 0
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported file formats"""
        return {
            'models': self.supported_models,
            'images': self.supported_images
        }


def get_object_manager() -> ObjectManager:
    """Get the global object manager instance (singleton)"""
    global _object_manager
    if _object_manager is None:
        _object_manager = ObjectManager()
    return _object_manager 