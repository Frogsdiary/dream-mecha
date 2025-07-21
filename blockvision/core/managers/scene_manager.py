"""
Scene Manager - BlockVision Core
Manages 3D scene, objects, and rendering pipeline
"""

import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Global scene manager instance
_scene_manager = None


class SceneState(Enum):
    EMPTY = "empty"
    LOADING = "loading"
    READY = "ready"
    RENDERING = "rendering"


@dataclass
class SceneObject:
    """Represents an object in the 3D scene"""
    id: str
    name: str
    type: str  # 'model', 'image', 'flat'
    position: tuple  # (x, y, z)
    scale: tuple  # (x, y, z)
    rotation: tuple  # (x, y, z) in degrees
    visible: bool = True
    object_manager_id: Optional[str] = None  # Link to object manager
    created_at: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class SceneManager:
    """
    Manages 3D scene, objects, and rendering pipeline
    Follows singleton pattern like solar_core_manager
    """
    
    def __init__(self):
        self.state = SceneState.EMPTY
        self.objects: Dict[str, SceneObject] = {}
        self.object_counter = 0
        
        # Scene properties
        self.background_color = (0.2, 0.2, 0.2)  # Dark gray
        self.lighting_enabled = True
        
        # Threading for rendering
        self._render_thread = None
        self._stop_rendering = False
        self._render_callbacks: List[Any] = []
        
        # Start rendering loop
        self._start_rendering()
    
    def _start_rendering(self):
        """Start the rendering loop thread"""
        self._render_thread = threading.Thread(target=self._render_loop, daemon=True)
        self._render_thread.start()
    
    def _render_loop(self):
        """Main rendering loop"""
        while not self._stop_rendering:
            if self.state == SceneState.READY:
                self._render_frame()
            time.sleep(0.033)  # ~30 FPS
    
    def _render_frame(self):
        """Render a single frame"""
        # Notify callbacks of frame update
        for callback in self._render_callbacks:
            try:
                callback(self.get_scene_data())
            except Exception as e:
                print(f"Render callback error: {e}")
    
    def add_render_callback(self, callback: Any):
        """Add callback for render updates"""
        self._render_callbacks.append(callback)
    
    def create_object(self, name: str, obj_type: str, object_manager_id: Optional[str] = None, **kwargs) -> str:
        """Create a new object in the scene"""
        self.object_counter += 1
        obj_id = f"scene_obj_{self.object_counter}"
        
        # Default object properties
        position = kwargs.get('position', (0.0, 0.0, 0.0))
        scale = kwargs.get('scale', (1.0, 1.0, 1.0))
        rotation = kwargs.get('rotation', (0.0, 0.0, 0.0))
        
        obj = SceneObject(
            id=obj_id,
            name=name,
            type=obj_type,
            position=position,
            scale=scale,
            rotation=rotation,
            object_manager_id=object_manager_id
        )
        
        self.objects[obj_id] = obj
        self.state = SceneState.READY
        
        return obj_id
    
    def create_object_from_manager(self, object_manager_id: str, name: str, obj_type: str, **kwargs) -> str:
        """Create scene object linked to object manager object"""
        return self.create_object(name, obj_type, object_manager_id, **kwargs)
    
    def remove_object(self, obj_id: str) -> bool:
        """Remove an object from the scene"""
        if obj_id in self.objects:
            del self.objects[obj_id]
            if not self.objects:
                self.state = SceneState.EMPTY
            return True
        return False
    
    def get_object(self, obj_id: str) -> Optional[SceneObject]:
        """Get object by ID"""
        return self.objects.get(obj_id)
    
    def get_object_by_manager_id(self, object_manager_id: str) -> Optional[SceneObject]:
        """Get scene object by object manager ID"""
        for obj in self.objects.values():
            if obj.object_manager_id == object_manager_id:
                return obj
        return None
    
    def update_object_position(self, obj_id: str, position: tuple) -> bool:
        """Update object position"""
        obj = self.get_object(obj_id)
        if obj:
            obj.position = position
            return True
        return False
    
    def update_object_scale(self, obj_id: str, scale: tuple) -> bool:
        """Update object scale"""
        obj = self.get_object(obj_id)
        if obj:
            obj.scale = scale
            return True
        return False
    
    def update_object_rotation(self, obj_id: str, rotation: tuple) -> bool:
        """Update object rotation"""
        obj = self.get_object(obj_id)
        if obj:
            obj.rotation = rotation
            return True
        return False
    
    def get_scene_data(self) -> Dict[str, Any]:
        """Get current scene data for rendering"""
        return {
            'state': self.state.value,
            'objects': {obj_id: {
                'name': obj.name,
                'type': obj.type,
                'position': obj.position,
                'scale': obj.scale,
                'rotation': obj.rotation,
                'visible': obj.visible,
                'object_manager_id': obj.object_manager_id
            } for obj_id, obj in self.objects.items()},
            'background_color': self.background_color,
            'lighting_enabled': self.lighting_enabled,
            'object_count': len(self.objects)
        }
    
    def clear_scene(self):
        """Clear all objects from scene"""
        self.objects.clear()
        self.object_counter = 0
        self.state = SceneState.EMPTY
    
    def get_scene_status(self) -> Dict[str, Any]:
        """Get scene status for monitoring"""
        return {
            'state': self.state.value,
            'object_count': len(self.objects),
            'rendering_active': not self._stop_rendering,
            'callback_count': len(self._render_callbacks)
        }


def get_scene_manager() -> SceneManager:
    """Get the global scene manager instance (singleton)"""
    global _scene_manager
    if _scene_manager is None:
        _scene_manager = SceneManager()
    return _scene_manager 