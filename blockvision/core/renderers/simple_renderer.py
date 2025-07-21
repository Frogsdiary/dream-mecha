"""
Simple Renderer - BlockVision Core
Basic OpenGL rendering for flat image objects with mouse controls
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import QPainter, QPixmap, QImage, QMouseEvent, QWheelEvent, QPen, QBrush, QColor

from ..managers.scene_manager import get_scene_manager
from ..managers.camera_manager import get_camera_manager
from ..managers.object_manager import get_object_manager


class SimpleRenderer(QWidget):
    """Simple renderer for flat image objects with mouse controls"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize managers
        self.scene_manager = get_scene_manager()
        self.camera_manager = get_camera_manager()
        self.object_manager = get_object_manager()
        
        # Rendering state
        self.sprite_mode = False
        self.rendered_objects = []
        
        # Mouse control state
        self.last_mouse_pos = QPoint()
        self.mouse_pressed = False
        self.pan_mode = False
        self.zoom_mode = False
        self.selected_object_id = None
        
        # Camera and view state
        self.camera_zoom = 1.0
        self.camera_pan_x = 0.0
        self.camera_pan_y = 0.0
        self.min_zoom = 0.1
        self.max_zoom = 50.0  # Increased for pixel-perfect zoom
        
        # Sprite mode specific settings
        self.pixel_grid_enabled = True
        self.gameboy_palette = [
            QColor(15, 56, 15),    # Dark green
            QColor(48, 98, 48),    # Medium green  
            QColor(139, 172, 15),  # Light green
            QColor(155, 188, 15)   # Very light green
        ]
        self.current_palette_index = 0
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_scene)
        self.update_timer.start(33)  # ~30 FPS
        
        # Set background color
        self.setStyleSheet("background-color: #1a2238;")
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events"""
        self.last_mouse_pos = event.pos()
        self.mouse_pressed = True
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Left click: Select object or pan camera
            self.pan_mode = True
            self.zoom_mode = False
        elif event.button() == Qt.MouseButton.RightButton:
            # Right click: Zoom mode
            self.zoom_mode = True
            self.pan_mode = False
        
        # Check for object selection
        if event.button() == Qt.MouseButton.LeftButton:
            self.check_object_selection(event.pos())
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events"""
        self.mouse_pressed = False
        self.pan_mode = False
        self.zoom_mode = False
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events"""
        if not self.mouse_pressed:
            return
        
        delta_x = event.x() - self.last_mouse_pos.x()
        delta_y = event.y() - self.last_mouse_pos.y()
        
        if self.pan_mode:
            # Pan camera
            pan_speed = 0.01 if not self.sprite_mode else 0.005
            self.camera_pan_x += delta_x * pan_speed
            self.camera_pan_y -= delta_y * pan_speed  # Invert Y for natural feel
        
        elif self.zoom_mode:
            # Zoom camera
            zoom_speed = 0.01 if not self.sprite_mode else 0.005
            zoom_delta = delta_y * zoom_speed
            self.camera_zoom = max(self.min_zoom, min(self.max_zoom, self.camera_zoom - zoom_delta))
        
        self.last_mouse_pos = event.pos()
        self.update()
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming"""
        zoom_delta = event.angleDelta().y() * 0.001
        if self.sprite_mode:
            # More precise zoom in sprite mode
            zoom_delta *= 0.5
        self.camera_zoom = max(self.min_zoom, min(self.max_zoom, self.camera_zoom + zoom_delta))
        self.update()
    
    def check_object_selection(self, mouse_pos: QPoint):
        """Check if mouse click selects an object"""
        # Get scene data
        scene_data = self.scene_manager.get_scene_data()
        objects = scene_data.get('objects', {})
        
        # Convert mouse position to world coordinates
        world_x = (mouse_pos.x() - self.width() / 2 - self.camera_pan_x * 100) / (self.camera_zoom * 100)
        world_y = (mouse_pos.y() - self.height() / 2 + self.camera_pan_y * 100) / (self.camera_zoom * 100)
        
        # Check each object for selection
        for obj_id, obj_data in objects.items():
            obj_x, obj_y, obj_z = obj_data.get('position', (0, 0, 0))
            scale_x, scale_y, scale_z = obj_data.get('scale', (1, 1, 1))
            
            # Get actual object dimensions from object manager
            object_manager_id = obj_data.get('object_manager_id', obj_id)
            object_data = self.object_manager.get_object(object_manager_id)
            
            if object_data and hasattr(object_data, 'texture_data'):
                texture_data = object_data.texture_data
                if texture_data and 'pixel_data' in texture_data:
                    # Use actual image dimensions
                    pixel_data = texture_data['pixel_data']
                    if pixel_data is not None:
                        height, width = pixel_data.shape
                        obj_width = width * scale_x
                        obj_height = height * scale_y
                    else:
                        obj_width = 50 * scale_x
                        obj_height = 50 * scale_y
                else:
                    obj_width = 50 * scale_x
                    obj_height = 50 * scale_y
            else:
                obj_width = 50 * scale_x
                obj_height = 50 * scale_y
            
            if (abs(world_x - obj_x) < obj_width / 2 and 
                abs(world_y - obj_y) < obj_height / 2):
                self.selected_object_id = obj_id
                print(f"Selected object: {obj_data.get('name', 'Unknown')}")
                return
        
        # No object selected
        self.selected_object_id = None
    
    def paintEvent(self, event):
        """Main rendering function"""
        # Get scene data
        scene_data = self.scene_manager.get_scene_data()
        camera_data = self.camera_manager.get_camera_data()
        
        # Render objects
        self.render_objects(scene_data, camera_data)
        
        # Render selection indicator
        if self.selected_object_id:
            self.render_selection_indicator()
        
        # Render sprite mode overlay
        if self.sprite_mode:
            self.render_sprite_overlay()
    
    def render_objects(self, scene_data: Dict[str, Any], camera_data: Dict[str, Any]):
        """Render all objects in scene"""
        objects = scene_data.get('objects', {})
        
        for obj_id, obj_data in objects.items():
            if not obj_data.get('visible', True):
                continue
            
            # Get object from object manager using the linked ID
            object_manager_id = obj_data.get('object_manager_id')
            if not object_manager_id:
                # Fallback to scene object ID if no manager link
                object_manager_id = obj_id
            
            object_data = self.object_manager.get_object(object_manager_id)
            if not object_data:
                # If not found in object manager, render as placeholder
                self.render_placeholder(obj_data.get('position', (0, 0, 0)), 
                                     obj_data.get('scale', (1, 1, 1)), obj_id)
                continue
            
            # Render based on object type
            if object_data.type.value == 'image':
                self.render_image_object(obj_data, object_data, camera_data, obj_id)
            else:
                self.render_model_object(obj_data, object_data, camera_data, obj_id)
    
    def render_image_object(self, scene_obj: Dict[str, Any], object_data: Any, camera_data: Dict[str, Any], obj_id: str):
        """Render flat image object"""
        if not hasattr(object_data, 'texture_data') or not object_data.texture_data:
            # Render placeholder if no texture data
            self.render_placeholder(scene_obj.get('position', (0, 0, 0)), 
                                 scene_obj.get('scale', (1, 1, 1)), obj_id)
            return
        
        texture_data = object_data.texture_data
        pixel_data = texture_data.get('pixel_data')
        
        if pixel_data is None:
            # Render placeholder if no pixel data
            self.render_placeholder(scene_obj.get('position', (0, 0, 0)), 
                                 scene_obj.get('scale', (1, 1, 1)), obj_id)
            return
        
        # Get object position and scale
        position = scene_obj.get('position', (0, 0, 0))
        scale = scene_obj.get('scale', (1, 1, 1))
        
        if self.sprite_mode:
            # Render in sprite mode with pixel-perfect rendering
            self.render_sprite_image(pixel_data, position, scale, obj_id)
        else:
            # Render in normal mode
            self.render_normal_image(pixel_data, position, scale, obj_id)
    
    def render_sprite_image(self, pixel_data: np.ndarray, position: tuple, scale: tuple, obj_id: str):
        """Render image in sprite mode with pixel-perfect control"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)  # Pixel-perfect
        
        x, y, z = position
        scale_x, scale_y, scale_z = scale
        
        # Apply camera transformations
        screen_x = int(self.width() / 2 + (x + self.camera_pan_x) * 100 * self.camera_zoom)
        screen_y = int(self.height() / 2 - (y + self.camera_pan_y) * 100 * self.camera_zoom)
        
        # Get image dimensions
        height, width = pixel_data.shape
        
        # Calculate scaled dimensions
        scaled_width = int(width * scale_x * self.camera_zoom)
        scaled_height = int(height * scale_y * self.camera_zoom)
        
        # Draw each pixel individually for pixel-perfect rendering
        pixel_size = max(1, int(self.camera_zoom))
        
        for py in range(height):
            for px in range(width):
                # Get pixel value (0-255)
                pixel_value = pixel_data[py, px]
                
                # Convert to GameBoy palette
                if pixel_value < 64:
                    color = self.gameboy_palette[0]  # Dark green
                elif pixel_value < 128:
                    color = self.gameboy_palette[1]  # Medium green
                elif pixel_value < 192:
                    color = self.gameboy_palette[2]  # Light green
                else:
                    color = self.gameboy_palette[3]  # Very light green
                
                # Calculate screen position
                pixel_screen_x = screen_x - scaled_width // 2 + px * pixel_size
                pixel_screen_y = screen_y - scaled_height // 2 + py * pixel_size
                
                # Draw pixel
                painter.setBrush(color)
                painter.drawRect(
                    pixel_screen_x, pixel_screen_y, pixel_size, pixel_size
                )
        
        painter.end()
    
    def render_normal_image(self, pixel_data: np.ndarray, position: tuple, scale: tuple, obj_id: str):
        """Render image in normal mode"""
        # Convert numpy array to QImage
        height, width = pixel_data.shape
        qimage = QImage(pixel_data.tobytes(), width, height, width, QImage.Format_Grayscale8)
        
        # Convert to QPixmap for rendering
        pixmap = QPixmap.fromImage(qimage)
        
        # Use QPainter for 2D rendering
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate position and size
        x, y, z = position
        scale_x, scale_y, scale_z = scale
        
        # Apply camera transformations
        screen_x = int(self.width() / 2 + (x + self.camera_pan_x) * 100 * self.camera_zoom)
        screen_y = int(self.height() / 2 - (y + self.camera_pan_y) * 100 * self.camera_zoom)
        
        # Scale the pixmap
        scaled_pixmap = pixmap.scaled(
            int(pixmap.width() * scale_x * self.camera_zoom),
            int(pixmap.height() * scale_y * self.camera_zoom),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Draw the image
        painter.drawPixmap(
            screen_x - scaled_pixmap.width() // 2,
            screen_y - scaled_pixmap.height() // 2,
            scaled_pixmap
        )
        
        painter.end()
    
    def render_model_object(self, scene_obj: Dict[str, Any], object_data: Any, camera_data: Dict[str, Any], obj_id: str):
        """Render 3D model object (placeholder)"""
        # TODO: Implement 3D model rendering
        position = scene_obj.get('position', (0, 0, 0))
        scale = scene_obj.get('scale', (1, 1, 1))
        
        # For now, just render a placeholder
        self.render_placeholder(position, scale, obj_id)
    
    def render_placeholder(self, position: tuple, scale: tuple, obj_id: str):
        """Render placeholder for 3D objects"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        x, y, z = position
        scale_x, scale_y, scale_z = scale
        
        # Apply camera transformations
        screen_x = int(self.width() / 2 + (x + self.camera_pan_x) * 100 * self.camera_zoom)
        screen_y = int(self.height() / 2 - (y + self.camera_pan_y) * 100 * self.camera_zoom)
        
        # Draw a simple rectangle as placeholder
        size = int(50 * scale_x * self.camera_zoom)
        
        # Set color based on selection
        if obj_id == self.selected_object_id:
            painter.setPen(Qt.GlobalColor.yellow)
            painter.setBrush(Qt.GlobalColor.yellow)
        else:
            painter.setPen(Qt.GlobalColor.gray)
            painter.setBrush(Qt.GlobalColor.gray)
        
        painter.drawRect(
            screen_x - size // 2, screen_y - size // 2, size, size
        )
        
        painter.end()
    
    def render_selection_indicator(self):
        """Render selection indicator for selected object"""
        if not self.selected_object_id:
            return
        
        # Get selected object data
        scene_data = self.scene_manager.get_scene_data()
        obj_data = scene_data.get('objects', {}).get(self.selected_object_id)
        if not obj_data:
            return
        
        position = obj_data.get('position', (0, 0, 0))
        scale = obj_data.get('scale', (1, 1, 1))
        
        # Get actual object dimensions
        object_manager_id = obj_data.get('object_manager_id', self.selected_object_id)
        object_data = self.object_manager.get_object(object_manager_id)
        
        if object_data and hasattr(object_data, 'texture_data'):
            texture_data = object_data.texture_data
            if texture_data and 'pixel_data' in texture_data:
                pixel_data = texture_data['pixel_data']
                if pixel_data is not None:
                    height, width = pixel_data.shape
                    obj_width = width * scale[0] * self.camera_zoom
                    obj_height = height * scale[1] * self.camera_zoom
                else:
                    obj_width = 60 * scale[0] * self.camera_zoom
                    obj_height = 60 * scale[1] * self.camera_zoom
            else:
                obj_width = 60 * scale[0] * self.camera_zoom
                obj_height = 60 * scale[1] * self.camera_zoom
        else:
            obj_width = 60 * scale[0] * self.camera_zoom
            obj_height = 60 * scale[1] * self.camera_zoom
        
        # Apply camera transformations
        screen_x = int(self.width() / 2 + (position[0] + self.camera_pan_x) * 100 * self.camera_zoom)
        screen_y = int(self.height() / 2 - (position[1] + self.camera_pan_y) * 100 * self.camera_zoom)
        
        # Draw selection border
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawRect(
            screen_x - obj_width // 2,
            screen_y - obj_height // 2,
            obj_width, obj_height
        )
        
        painter.end()
    
    def render_sprite_overlay(self):
        """Render sprite mode overlay (pixel grid, palette info)"""
        if not self.sprite_mode:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        
        # Draw pixel grid if zoomed in enough
        if self.camera_zoom >= 2.0:
            self.draw_pixel_grid(painter)
        
        # Draw palette info
        self.draw_palette_info(painter)
        
        painter.end()
    
    def draw_pixel_grid(self, painter: QPainter):
        """Draw pixel grid overlay"""
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
        
        # Get selected object for grid reference
        if not self.selected_object_id:
            return
        
        scene_data = self.scene_manager.get_scene_data()
        obj_data = scene_data.get('objects', {}).get(self.selected_object_id)
        if not obj_data:
            return
        
        object_manager_id = obj_data.get('object_manager_id', self.selected_object_id)
        object_data = self.object_manager.get_object(object_manager_id)
        
        if not object_data or not hasattr(object_data, 'texture_data'):
            return
        
        texture_data = object_data.texture_data
        if not texture_data or 'pixel_data' not in texture_data:
            return
        
        pixel_data = texture_data['pixel_data']
        if pixel_data is None:
            return
        
        height, width = pixel_data.shape
        position = obj_data.get('position', (0, 0, 0))
        scale = obj_data.get('scale', (1, 1, 1))
        
        # Calculate screen position
        screen_x = int(self.width() / 2 + (position[0] + self.camera_pan_x) * 100 * self.camera_zoom)
        screen_y = int(self.height() / 2 - (position[1] + self.camera_pan_y) * 100 * self.camera_zoom)
        
        scaled_width = int(width * scale[0] * self.camera_zoom)
        scaled_height = int(height * scale[1] * self.camera_zoom)
        
        pixel_size = max(1, int(self.camera_zoom))
        
        # Draw vertical lines
        for x in range(width + 1):
            line_x = screen_x - scaled_width // 2 + x * pixel_size
            painter.drawLine(line_x, screen_y - scaled_height // 2, 
                           line_x, screen_y + scaled_height // 2)
        
        # Draw horizontal lines
        for y in range(height + 1):
            line_y = screen_y - scaled_height // 2 + y * pixel_size
            painter.drawLine(screen_x - scaled_width // 2, line_y,
                           screen_x + scaled_width // 2, line_y)
    
    def draw_palette_info(self, painter: QPainter):
        """Draw palette information"""
        # Draw palette swatches in top-right corner
        palette_x = self.width() - 120
        palette_y = 10
        swatch_size = 20
        
        for i, color in enumerate(self.gameboy_palette):
            x = palette_x + (i * (swatch_size + 5))
            painter.fillRect(x, palette_y, swatch_size, swatch_size, color)
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            painter.drawRect(x, palette_y, swatch_size, swatch_size)
    
    def update_scene(self):
        """Update scene (called by timer)"""
        self.update()
    
    def set_sprite_mode(self, enabled: bool):
        """Toggle sprite mode with proper functionality"""
        self.sprite_mode = enabled
        
        if enabled:
            # Adjust zoom limits for sprite mode
            self.min_zoom = 0.5
            self.max_zoom = 50.0
            # Reset camera for better sprite view
            if self.camera_zoom < 2.0:
                self.camera_zoom = 2.0
        else:
            # Reset zoom limits for normal mode
            self.min_zoom = 0.1
            self.max_zoom = 10.0
            # Reset camera for normal view
            if self.camera_zoom > 5.0:
                self.camera_zoom = 1.0
        
        self.update()
    
    def get_render_info(self) -> Dict[str, Any]:
        """Get renderer information"""
        return {
            'sprite_mode': self.sprite_mode,
            'viewport_size': (self.width(), self.height()),
            'rendered_objects': len(self.rendered_objects),
            'camera_zoom': self.camera_zoom,
            'camera_pan': (self.camera_pan_x, self.camera_pan_y),
            'selected_object': self.selected_object_id,
            'pixel_grid_enabled': self.pixel_grid_enabled,
            'current_palette': self.current_palette_index
        }
    
    def reset_camera(self):
        """Reset camera to default position"""
        self.camera_zoom = 1.0 if not self.sprite_mode else 2.0
        self.camera_pan_x = 0.0
        self.camera_pan_y = 0.0
        self.selected_object_id = None
        self.update()
    
    def zoom_in(self):
        """Zoom in"""
        self.camera_zoom = min(self.max_zoom, self.camera_zoom * 1.2)
        self.update()
    
    def zoom_out(self):
        """Zoom out"""
        self.camera_zoom = max(self.min_zoom, self.camera_zoom / 1.2)
        self.update()
    
    def toggle_pixel_grid(self):
        """Toggle pixel grid overlay"""
        self.pixel_grid_enabled = not self.pixel_grid_enabled
        self.update()
    
    def cycle_palette(self):
        """Cycle through different GameBoy palettes"""
        # TODO: Implement different palette sets
        self.current_palette_index = (self.current_palette_index + 1) % 4
        self.update() 