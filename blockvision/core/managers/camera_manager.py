"""
Camera Manager - BlockVision Core
Handles camera positioning, movement, and view controls
"""

import math
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Global camera manager instance
_camera_manager = None


class CameraMode(Enum):
    ORBIT = "orbit"
    FREE = "free"
    FIXED = "fixed"


@dataclass
class CameraPosition:
    """Camera position and orientation"""
    x: float = 0.0
    y: float = 0.0
    z: float = 5.0  # Default distance from origin
    rotation_x: float = 0.0  # Pitch (degrees)
    rotation_y: float = 0.0  # Yaw (degrees)
    rotation_z: float = 0.0  # Roll (degrees)


class CameraManager:
    """
    Manages camera positioning, movement, and view controls
    Follows singleton pattern like scene_manager
    """
    
    def __init__(self):
        self.position = CameraPosition()
        self.mode = CameraMode.ORBIT
        self.target = (0.0, 0.0, 0.0)  # Look-at target
        self.fov = 45.0  # Field of view (degrees)
        self.near_plane = 0.1
        self.far_plane = 1000.0
        
        # Movement settings
        self.orbit_speed = 1.0
        self.zoom_speed = 1.0
        self.pan_speed = 1.0
    
    def set_position(self, x: float, y: float, z: float):
        """Set camera position"""
        self.position.x = x
        self.position.y = y
        self.position.z = z
    
    def set_rotation(self, rx: float, ry: float, rz: float):
        """Set camera rotation in degrees"""
        self.position.rotation_x = rx
        self.position.rotation_y = ry
        self.position.rotation_z = rz
    
    def orbit_camera(self, delta_x: float, delta_y: float):
        """Orbit camera around target"""
        if self.mode != CameraMode.ORBIT:
            return
        
        # Convert to radians
        rx = math.radians(self.position.rotation_x)
        ry = math.radians(self.position.rotation_y)
        
        # Update rotation based on mouse movement
        ry -= delta_x * self.orbit_speed
        rx -= delta_y * self.orbit_speed
        
        # Clamp pitch to prevent gimbal lock
        rx = max(-89.0, min(89.0, math.degrees(rx)))
        
        self.position.rotation_x = rx
        self.position.rotation_y = ry
    
    def zoom_camera(self, delta: float):
        """Zoom camera in/out"""
        # Adjust distance from target
        distance = math.sqrt(
            self.position.x**2 + 
            self.position.y**2 + 
            self.position.z**2
        )
        
        new_distance = distance + delta * self.zoom_speed
        new_distance = max(0.1, new_distance)  # Don't get too close
        
        # Scale position to maintain direction
        scale = new_distance / distance
        self.position.x *= scale
        self.position.y *= scale
        self.position.z *= scale
    
    def pan_camera(self, delta_x: float, delta_y: float):
        """Pan camera horizontally/vertically"""
        # Calculate right and up vectors
        rx = math.radians(self.position.rotation_x)
        ry = math.radians(self.position.rotation_y)
        
        # Right vector
        right_x = math.cos(ry + math.pi/2)
        right_y = 0
        right_z = math.sin(ry + math.pi/2)
        
        # Up vector
        up_x = math.sin(rx) * math.sin(ry)
        up_y = math.cos(rx)
        up_z = math.sin(rx) * math.cos(ry)
        
        # Apply pan movement
        pan_speed = self.pan_speed * 0.01
        self.position.x += (right_x * delta_x + up_x * delta_y) * pan_speed
        self.position.y += (right_y * delta_x + up_y * delta_y) * pan_speed
        self.position.z += (right_z * delta_x + up_z * delta_y) * pan_speed
    
    def reset_camera(self):
        """Reset camera to default position"""
        self.position = CameraPosition()
        self.target = (0.0, 0.0, 0.0)
    
    def set_target(self, x: float, y: float, z: float):
        """Set camera look-at target"""
        self.target = (x, y, z)
    
    def get_camera_data(self) -> Dict[str, Any]:
        """Get camera data for rendering"""
        return {
            'position': (self.position.x, self.position.y, self.position.z),
            'rotation': (self.position.rotation_x, self.position.rotation_y, self.position.rotation_z),
            'target': self.target,
            'mode': self.mode.value,
            'fov': self.fov,
            'near_plane': self.near_plane,
            'far_plane': self.far_plane
        }
    
    def get_camera_status(self) -> Dict[str, Any]:
        """Get camera status for monitoring"""
        distance = math.sqrt(
            self.position.x**2 + 
            self.position.y**2 + 
            self.position.z**2
        )
        
        return {
            'mode': self.mode.value,
            'distance': distance,
            'position': (self.position.x, self.position.y, self.position.z),
            'rotation': (self.position.rotation_x, self.position.rotation_y, self.position.rotation_z),
            'target': self.target
        }
    
    def set_mode(self, mode: CameraMode):
        """Set camera mode"""
        self.mode = mode
    
    def set_fov(self, fov: float):
        """Set field of view"""
        self.fov = max(1.0, min(179.0, fov))
    
    def set_movement_speeds(self, orbit: Optional[float] = None, zoom: Optional[float] = None, pan: Optional[float] = None):
        """Set movement speeds"""
        if orbit is not None:
            self.orbit_speed = orbit
        if zoom is not None:
            self.zoom_speed = zoom
        if pan is not None:
            self.pan_speed = pan


def get_camera_manager() -> CameraManager:
    """Get the global camera manager instance (singleton)"""
    global _camera_manager
    if _camera_manager is None:
        _camera_manager = CameraManager()
    return _camera_manager 