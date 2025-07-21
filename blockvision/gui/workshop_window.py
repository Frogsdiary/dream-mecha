"""
BlockVision Workshop Window
Main 3D workshop interface with debugger panel
"""

import sys
import os
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QGroupBox, QApplication,
                             QSplitter, QFileDialog, QMessageBox, QSlider,
                             QSpinBox, QDoubleSpinBox, QComboBox, QListWidget,
                             QListWidgetItem, QCheckBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPalette, QColor

from blockvision.core.managers.scene_manager import get_scene_manager
from blockvision.core.managers.camera_manager import get_camera_manager
from blockvision.core.managers.object_manager import get_object_manager
from blockvision.core.renderers.simple_renderer import SimpleRenderer
from blockvision.gui.debugger_panel import BlockVisionDebuggerPanel


class BlockVisionWorkshop(QMainWindow):
    """Main BlockVision workshop window with debugger panel"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.scene_manager = get_scene_manager()
        self.camera_manager = get_camera_manager()
        self.object_manager = get_object_manager()
        
        # Object selection state
        self.selected_object_id = None
        
        # Debugger panel state
        self.debugger_visible = True
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(100)  # 10 FPS updates
        
        # Add render callback
        self.scene_manager.add_render_callback(self.on_scene_update)
    
    def setup_ui(self):
        """Setup the main UI with Sharkman AI styling"""
        self.setWindowTitle("BlockVision Workshop v0.1.0 - Advanced 3D to Sprite Converter")
        self.setGeometry(100, 100, 1600, 900)  # Larger window for debugger
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create main splitter for resizable panels
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left panel - Controls
        self.controls_panel = self.create_controls_panel()
        main_splitter.addWidget(self.controls_panel)
        
        # Center panel - 3D View with renderer
        self.view_panel = self.create_view_panel()
        main_splitter.addWidget(self.view_panel)
        
        # Right panel - Debugger
        self.debugger_panel = self.create_debugger_panel()
        main_splitter.addWidget(self.debugger_panel)
        
        # Initialize renderer
        self.renderer = SimpleRenderer(self.view_panel)
        self.view_layout.addWidget(self.renderer)
        
        # Set splitter proportions (controls, view, debugger)
        main_splitter.setSizes([300, 900, 300])
    
    def create_controls_panel(self) -> QWidget:
        """Create the controls panel with Sharkman AI styling"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Apply Sharkman AI dark theme styling
        panel.setStyleSheet("""
            QWidget {
                background-color: #222b45;
                color: #eaeaea;
                font-family: 'Arial';
            }
            QGroupBox {
                border: 2px solid #394867;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: #f7c873;
                background-color: #263159;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #263159;
                border: 2px solid #394867;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                color: #eaeaea;
            }
            QPushButton:hover {
                background-color: #6e7ff3;
                border-color: #f7c873;
            }
            QPushButton:pressed {
                background-color: #1a2238;
            }
            QListWidget {
                background-color: #1a2238;
                border: 2px solid #394867;
                border-radius: 5px;
                color: #eaeaea;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #1a2238;
                border: 2px solid #394867;
                border-radius: 3px;
                padding: 5px;
                color: #eaeaea;
            }
            QLabel {
                color: #eaeaea;
            }
        """)
        
        # File operations
        file_group = QGroupBox("📁 File Operations")
        file_layout = QVBoxLayout(file_group)
        
        self.import_btn = QPushButton("📥 Import Object")
        self.import_btn.clicked.connect(self.import_object)
        file_layout.addWidget(self.import_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Scene")
        self.clear_btn.clicked.connect(self.clear_scene)
        file_layout.addWidget(self.clear_btn)
        
        layout.addWidget(file_group)
        
        # Object controls
        object_group = QGroupBox("🎯 Object Controls")
        object_layout = QVBoxLayout(object_group)
        
        # Template objects
        self.cube_btn = QPushButton("📦 Add Cube")
        self.cube_btn.clicked.connect(lambda: self.add_template_object('cube'))
        object_layout.addWidget(self.cube_btn)
        
        self.sphere_btn = QPushButton("🔵 Add Sphere")
        self.sphere_btn.clicked.connect(lambda: self.add_template_object('sphere'))
        object_layout.addWidget(self.sphere_btn)
        
        self.plane_btn = QPushButton("⬜ Add Plane")
        self.plane_btn.clicked.connect(lambda: self.add_template_object('plane'))
        object_layout.addWidget(self.plane_btn)
        
        # Object list
        self.object_list = QListWidget()
        self.object_list.itemClicked.connect(self.on_object_selected)
        object_layout.addWidget(QLabel("Objects:"))
        object_layout.addWidget(self.object_list)
        
        layout.addWidget(object_group)
        
        # Object transformation controls
        transform_group = QGroupBox("🎛️ Transform Controls")
        transform_layout = QVBoxLayout(transform_group)
        
        # Position controls
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Position:"))
        
        self.pos_x_spin = QDoubleSpinBox()
        self.pos_x_spin.setRange(-100, 100)
        self.pos_x_spin.setSuffix(" X")
        self.pos_x_spin.valueChanged.connect(self.on_position_changed)
        pos_layout.addWidget(self.pos_x_spin)
        
        self.pos_y_spin = QDoubleSpinBox()
        self.pos_y_spin.setRange(-100, 100)
        self.pos_y_spin.setSuffix(" Y")
        self.pos_y_spin.valueChanged.connect(self.on_position_changed)
        pos_layout.addWidget(self.pos_y_spin)
        
        self.pos_z_spin = QDoubleSpinBox()
        self.pos_z_spin.setRange(-100, 100)
        self.pos_z_spin.setSuffix(" Z")
        self.pos_z_spin.valueChanged.connect(self.on_position_changed)
        pos_layout.addWidget(self.pos_z_spin)
        
        transform_layout.addLayout(pos_layout)
        
        # Scale controls
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale:"))
        
        self.scale_x_spin = QDoubleSpinBox()
        self.scale_x_spin.setRange(0.1, 10.0)
        self.scale_x_spin.setValue(1.0)
        self.scale_x_spin.setSuffix(" X")
        self.scale_x_spin.valueChanged.connect(self.on_scale_changed)
        scale_layout.addWidget(self.scale_x_spin)
        
        self.scale_y_spin = QDoubleSpinBox()
        self.scale_y_spin.setRange(0.1, 10.0)
        self.scale_y_spin.setValue(1.0)
        self.scale_y_spin.setSuffix(" Y")
        self.scale_y_spin.valueChanged.connect(self.on_scale_changed)
        scale_layout.addWidget(self.scale_y_spin)
        
        self.scale_z_spin = QDoubleSpinBox()
        self.scale_z_spin.setRange(0.1, 10.0)
        self.scale_z_spin.setValue(1.0)
        self.scale_z_spin.setSuffix(" Z")
        self.scale_z_spin.valueChanged.connect(self.on_scale_changed)
        scale_layout.addWidget(self.scale_z_spin)
        
        transform_layout.addLayout(scale_layout)
        
        # Rotation controls
        rot_layout = QHBoxLayout()
        rot_layout.addWidget(QLabel("Rotation:"))
        
        self.rot_x_spin = QDoubleSpinBox()
        self.rot_x_spin.setRange(-180, 180)
        self.rot_x_spin.setSuffix("° X")
        self.rot_x_spin.valueChanged.connect(self.on_rotation_changed)
        rot_layout.addWidget(self.rot_x_spin)
        
        self.rot_y_spin = QDoubleSpinBox()
        self.rot_y_spin.setRange(-180, 180)
        self.rot_y_spin.setSuffix("° Y")
        self.rot_y_spin.valueChanged.connect(self.on_rotation_changed)
        rot_layout.addWidget(self.rot_y_spin)
        
        self.rot_z_spin = QDoubleSpinBox()
        self.rot_z_spin.setRange(-180, 180)
        self.rot_z_spin.setSuffix("° Z")
        self.rot_z_spin.valueChanged.connect(self.on_rotation_changed)
        rot_layout.addWidget(self.rot_z_spin)
        
        transform_layout.addLayout(rot_layout)
        
        layout.addWidget(transform_group)
        
        # Camera controls
        camera_group = QGroupBox("📷 Camera Controls")
        camera_layout = QVBoxLayout(camera_group)
        
        # Camera movement buttons
        camera_btn_layout = QHBoxLayout()
        
        self.zoom_in_btn = QPushButton("🔍 Zoom In")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        camera_btn_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("🔍 Zoom Out")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        camera_btn_layout.addWidget(self.zoom_out_btn)
        
        camera_layout.addLayout(camera_btn_layout)
        
        self.reset_camera_btn = QPushButton("🔄 Reset Camera")
        self.reset_camera_btn.clicked.connect(self.reset_camera)
        camera_layout.addWidget(self.reset_camera_btn)
        
        # Camera info
        self.camera_info_label = QLabel("Camera: Ready")
        self.camera_info_label.setStyleSheet("color: #7ed957; font-size: 10px;")
        camera_layout.addWidget(self.camera_info_label)
        
        layout.addWidget(camera_group)
        
        # Sprite controls
        sprite_group = QGroupBox("🎨 Sprite Controls")
        sprite_layout = QVBoxLayout(sprite_group)
        
        self.sprite_mode_btn = QPushButton("🎮 Sprite Mode: OFF")
        self.sprite_mode_btn.setCheckable(True)
        self.sprite_mode_btn.clicked.connect(self.toggle_sprite_mode)
        sprite_layout.addWidget(self.sprite_mode_btn)
        
        # Sprite mode specific controls
        self.pixel_grid_btn = QPushButton("🔲 Toggle Pixel Grid")
        self.pixel_grid_btn.clicked.connect(self.toggle_pixel_grid)
        sprite_layout.addWidget(self.pixel_grid_btn)
        
        self.palette_btn = QPushButton("🎨 Cycle Palette")
        self.palette_btn.clicked.connect(self.cycle_palette)
        sprite_layout.addWidget(self.palette_btn)
        
        self.capture_btn = QPushButton("📸 Capture Sprite")
        self.capture_btn.clicked.connect(self.capture_sprite)
        sprite_layout.addWidget(self.capture_btn)
        
        layout.addWidget(sprite_group)
        
        # Debug controls
        debug_group = QGroupBox("🔧 Debug Controls")
        debug_layout = QVBoxLayout(debug_group)
        
        self.debug_toggle_btn = QPushButton("👁️ Show Debugger")
        self.debug_toggle_btn.setCheckable(True)
        self.debug_toggle_btn.setChecked(True)
        self.debug_toggle_btn.clicked.connect(self.toggle_debugger)
        debug_layout.addWidget(self.debug_toggle_btn)
        
        layout.addWidget(debug_group)
        
        # Help section
        help_group = QGroupBox("❓ Controls Help")
        help_layout = QVBoxLayout(help_group)
        
        help_text = QLabel("""
🎮 Mouse Controls:
• Left Click + Drag: Pan camera
• Right Click + Drag: Zoom camera
• Mouse Wheel: Zoom in/out
• Left Click: Select object

🎨 Sprite Mode:
• Toggle sprite mode for pixel-perfect view
• Use pixel grid for precise editing
• Cycle GameBoy palettes
• Capture sprites to PNG files

⌨️ Keyboard Shortcuts:
• +/-: Zoom in/out
• 0: Reset camera
• Escape: Clear selection
        """)
        help_text.setStyleSheet("color: #eaeaea; font-size: 10px;")
        help_layout.addWidget(help_text)
        
        layout.addWidget(help_group)
        
        # Status display
        status_group = QGroupBox("📊 Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #7ed957; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(status_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return panel
    
    def create_view_panel(self) -> QWidget:
        """Create the 3D view panel with renderer"""
        panel = QWidget()
        self.view_layout = QVBoxLayout(panel)
        
        # Apply Sharkman AI dark theme styling
        panel.setStyleSheet("""
            QWidget {
                background-color: #1a2238;
                color: #eaeaea;
            }
        """)
        
        # Status label
        self.view_label = QLabel("🎮 3D View - BlockVision Renderer")
        self.view_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_label.setStyleSheet("""
            QLabel {
                background-color: #263159;
                color: #f7c873;
                border: 2px solid #394867;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.view_layout.addWidget(self.view_label)
        
        return panel
    
    def create_debugger_panel(self) -> QWidget:
        """Create the debugger panel"""
        self.debugger = BlockVisionDebuggerPanel(self)
        return self.debugger
    
    def setup_connections(self):
        """Setup signal connections"""
        # Scene manager callbacks
        self.scene_manager.add_render_callback(self.on_scene_update)
    
    def toggle_debugger(self):
        """Toggle debugger panel visibility"""
        self.debugger_visible = self.debug_toggle_btn.isChecked()
        
        if self.debugger_visible:
            self.debugger.show()
            self.debug_toggle_btn.setText("👁️ Hide Debugger")
        else:
            self.debugger.hide()
            self.debug_toggle_btn.setText("👁️ Show Debugger")
    
    def import_object(self):
        """Import object from file"""
        try:
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("All Files (*.obj *.fbx *.jpg *.png *.bmp)")
            file_dialog.setFileMode(QFileDialog.ExistingFile)
            
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                if not file_path:
                    return
                
                obj_id = self.object_manager.import_file(file_path)
                
                if obj_id:
                    # Add to scene with proper linking
                    obj_data = self.object_manager.get_object(obj_id)
                    if obj_data:
                        scene_obj_id = self.scene_manager.create_object_from_manager(
                            object_manager_id=obj_id,
                            name=obj_data.name,
                            obj_type=obj_data.type.value
                        )
                        self.status_label.setText(f"✅ Imported: {os.path.basename(file_path)}")
                        self.update_object_list()  # Refresh the list
                    else:
                        QMessageBox.warning(self, "Import Error", "Failed to get object data")
                else:
                    QMessageBox.warning(self, "Import Error", "Failed to import file")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Unexpected error: {str(e)}")
    
    def add_template_object(self, template_name: str):
        """Add template object to scene"""
        try:
            obj_id = self.object_manager.create_template_object(template_name)
            if obj_id:
                obj_data = self.object_manager.get_object(obj_id)
                if obj_data:
                    scene_obj_id = self.scene_manager.create_object_from_manager(
                        object_manager_id=obj_id,
                        name=obj_data.name,
                        obj_type=obj_data.type.value
                    )
                    self.status_label.setText(f"✅ Added: {template_name}")
                    self.update_object_list()  # Refresh the list
                else:
                    self.status_label.setText(f"❌ Failed to get object data for {template_name}")
            else:
                self.status_label.setText(f"❌ Failed to create {template_name}")
        except Exception as e:
            self.status_label.setText(f"❌ Error creating {template_name}: {str(e)}")
    
    def clear_scene(self):
        """Clear all objects from scene"""
        try:
            self.scene_manager.clear_scene()
            self.object_manager.clear_all_objects()
            self.selected_object_id = None  # Clear selection
            self.update_object_list()  # Refresh the list
            self.status_label.setText("🗑️ Scene cleared")
        except Exception as e:
            self.status_label.setText(f"❌ Error clearing scene: {str(e)}")
    
    def reset_camera(self):
        """Reset camera to default position"""
        try:
            self.camera_manager.reset_camera()
            if hasattr(self, 'renderer'):
                self.renderer.reset_camera()
            self.status_label.setText("🔄 Camera reset")
            self.update_camera_info()
        except Exception as e:
            self.status_label.setText(f"❌ Error resetting camera: {str(e)}")
    
    def zoom_in(self):
        """Zoom in camera"""
        try:
            if hasattr(self, 'renderer'):
                self.renderer.zoom_in()
            self.status_label.setText("🔍 Zoomed in")
            self.update_camera_info()
        except Exception as e:
            self.status_label.setText(f"❌ Error zooming in: {str(e)}")
    
    def zoom_out(self):
        """Zoom out camera"""
        try:
            if hasattr(self, 'renderer'):
                self.renderer.zoom_out()
            self.status_label.setText("🔍 Zoomed out")
            self.update_camera_info()
        except Exception as e:
            self.status_label.setText(f"❌ Error zooming out: {str(e)}")
    
    def update_camera_info(self):
        """Update camera information display"""
        try:
            if hasattr(self, 'renderer'):
                render_info = self.renderer.get_render_info()
                zoom = render_info.get('camera_zoom', 1.0)
                pan_x, pan_y = render_info.get('camera_pan', (0.0, 0.0))
                selected = render_info.get('selected_object', None)
                
                info_text = f"Zoom: {zoom:.2f}x | Pan: ({pan_x:.1f}, {pan_y:.1f})"
                if selected:
                    info_text += f" | Selected: {selected}"
                
                self.camera_info_label.setText(info_text)
        except Exception as e:
            self.camera_info_label.setText(f"Camera: Error - {str(e)}")
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        try:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                # Plus key or equals key for zoom in
                self.zoom_in()
            elif event.key() == Qt.Key.Key_Minus:
                # Minus key for zoom out
                self.zoom_out()
            elif event.key() == Qt.Key.Key_0:
                # Zero key for reset camera
                self.reset_camera()
            elif event.key() == Qt.Key.Key_Escape:
                # Escape key to clear selection
                if hasattr(self, 'renderer'):
                    self.renderer.selected_object_id = None
                    self.renderer.update()
                self.status_label.setText("🎯 Selection cleared")
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"Error in keyPressEvent: {e}")
    
    def toggle_sprite_mode(self):
        """Toggle sprite conversion mode"""
        try:
            is_on = self.sprite_mode_btn.isChecked()
            self.sprite_mode_btn.setText(f"🎮 Sprite Mode: {'ON' if is_on else 'OFF'}")
            
            # Update renderer
            if hasattr(self, 'renderer'):
                self.renderer.set_sprite_mode(is_on)
            
            if is_on:
                self.status_label.setText("🎮 Sprite mode enabled")
            else:
                self.status_label.setText("🎮 Sprite mode disabled")
        except Exception as e:
            self.status_label.setText(f"❌ Error toggling sprite mode: {str(e)}")
    
    def on_object_selected(self, item):
        """Handle object selection"""
        try:
            if not item:
                return
                
            obj_id = item.data(Qt.ItemDataRole.UserRole)
            if obj_id:
                self.selected_object_id = obj_id
                self.update_transform_controls(obj_id)
                self.status_label.setText(f"🎯 Selected: {item.text()}")
        except Exception as e:
            self.status_label.setText(f"❌ Error selecting object: {str(e)}")
    
    def update_transform_controls(self, obj_id: str):
        """Update transform controls for selected object"""
        try:
            # Try to get scene object first
            scene_obj = self.scene_manager.get_object(obj_id)
            if not scene_obj:
                # If not found in scene, try to find by object manager ID
                scene_obj = self.scene_manager.get_object_by_manager_id(obj_id)
            
            if not scene_obj:
                print(f"Object not found: {obj_id}")
                return
            
            # Update position controls
            self.pos_x_spin.setValue(scene_obj.position[0])
            self.pos_y_spin.setValue(scene_obj.position[1])
            self.pos_z_spin.setValue(scene_obj.position[2])
            
            # Update scale controls
            self.scale_x_spin.setValue(scene_obj.scale[0])
            self.scale_y_spin.setValue(scene_obj.scale[1])
            self.scale_z_spin.setValue(scene_obj.scale[2])
            
            # Update rotation controls
            self.rot_x_spin.setValue(scene_obj.rotation[0])
            self.rot_y_spin.setValue(scene_obj.rotation[1])
            self.rot_z_spin.setValue(scene_obj.rotation[2])
        except Exception as e:
            print(f"Error updating transform controls: {e}")
    
    def on_position_changed(self):
        """Handle position control changes"""
        try:
            if self.selected_object_id:
                new_position = (
                    self.pos_x_spin.value(),
                    self.pos_y_spin.value(),
                    self.pos_z_spin.value()
                )
                # Try scene object first, then by manager ID
                if not self.scene_manager.update_object_position(self.selected_object_id, new_position):
                    scene_obj = self.scene_manager.get_object_by_manager_id(self.selected_object_id)
                    if scene_obj:
                        self.scene_manager.update_object_position(scene_obj.id, new_position)
        except Exception as e:
            print(f"Error updating position: {e}")
    
    def on_scale_changed(self):
        """Handle scale control changes"""
        try:
            if self.selected_object_id:
                new_scale = (
                    self.scale_x_spin.value(),
                    self.scale_y_spin.value(),
                    self.scale_z_spin.value()
                )
                # Try scene object first, then by manager ID
                if not self.scene_manager.update_object_scale(self.selected_object_id, new_scale):
                    scene_obj = self.scene_manager.get_object_by_manager_id(self.selected_object_id)
                    if scene_obj:
                        self.scene_manager.update_object_scale(scene_obj.id, new_scale)
        except Exception as e:
            print(f"Error updating scale: {e}")
    
    def on_rotation_changed(self):
        """Handle rotation control changes"""
        try:
            if self.selected_object_id:
                new_rotation = (
                    self.rot_x_spin.value(),
                    self.rot_y_spin.value(),
                    self.rot_z_spin.value()
                )
                # Try scene object first, then by manager ID
                if not self.scene_manager.update_object_rotation(self.selected_object_id, new_rotation):
                    scene_obj = self.scene_manager.get_object_by_manager_id(self.selected_object_id)
                    if scene_obj:
                        self.scene_manager.update_object_rotation(scene_obj.id, new_rotation)
        except Exception as e:
            print(f"Error updating rotation: {e}")
    
    def update_object_list(self):
        """Update the object list display"""
        try:
            self.object_list.clear()
            scene_data = self.scene_manager.get_scene_data()
            
            for obj_id, obj_data in scene_data['objects'].items():
                item = QListWidgetItem()
                item.setText(obj_data['name'])
                # Store the scene object ID for selection
                item.setData(Qt.ItemDataRole.UserRole, obj_id)
                self.object_list.addItem(item)
        except Exception as e:
            print(f"Error updating object list: {e}")
    
    def capture_sprite(self):
        """Capture current view as sprite"""
        try:
            if not hasattr(self, 'renderer') or not self.renderer.sprite_mode:
                self.status_label.setText("📸 Enable sprite mode first")
                return
            
            # Get selected object
            if not self.selected_object_id:
                self.status_label.setText("📸 Select an object to capture")
                return
            
            # Get object data
            scene_data = self.scene_manager.get_scene_data()
            obj_data = scene_data.get('objects', {}).get(self.selected_object_id)
            if not obj_data:
                self.status_label.setText("📸 Object not found")
                return
            
            # Get object from object manager
            object_manager_id = obj_data.get('object_manager_id', self.selected_object_id)
            object_data = self.object_manager.get_object(object_manager_id)
            
            if not object_data or not hasattr(object_data, 'texture_data'):
                self.status_label.setText("📸 No texture data available")
                return
            
            texture_data = object_data.texture_data
            if not texture_data or 'pixel_data' not in texture_data:
                self.status_label.setText("📸 No pixel data available")
                return
            
            # Save sprite to file
            from PyQt5.QtWidgets import QFileDialog
            from PIL import Image
            import numpy as np
            
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("PNG Files (*.png)")
            file_dialog.setDefaultSuffix("png")
            
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                
                # Convert to PIL image and save
                pixel_data = texture_data['pixel_data']
                img = Image.fromarray(pixel_data)
                img.save(file_path)
                
                self.status_label.setText(f"📸 Sprite saved to {file_path}")
            else:
                self.status_label.setText("📸 Sprite capture cancelled")
                
        except Exception as e:
            self.status_label.setText(f"❌ Error capturing sprite: {str(e)}")
    
    def toggle_pixel_grid(self):
        """Toggle pixel grid overlay"""
        try:
            if hasattr(self, 'renderer'):
                self.renderer.toggle_pixel_grid()
                self.status_label.setText("🔲 Pixel grid toggled")
        except Exception as e:
            self.status_label.setText(f"❌ Error toggling pixel grid: {str(e)}")
    
    def cycle_palette(self):
        """Cycle through GameBoy palettes"""
        try:
            if hasattr(self, 'renderer'):
                self.renderer.cycle_palette()
                self.status_label.setText("🎨 Palette cycled")
        except Exception as e:
            self.status_label.setText(f"❌ Error cycling palette: {str(e)}")
    
    def on_scene_update(self, scene_data: Dict[str, Any]):
        """Handle scene updates from render loop"""
        try:
            # Update status with scene info
            object_count = scene_data.get('object_count', 0)
            state = scene_data.get('state', 'unknown')
            self.status_label.setText(f"📊 Scene: {state}, Objects: {object_count}")
            
            # Update debugger with renderer info
            if hasattr(self, 'renderer'):
                render_info = self.renderer.get_render_info()
                self.debugger.set_renderer_info(render_info)
        except Exception as e:
            print(f"Error in scene update: {e}")
    
    def update_display(self):
        """Update display (called by timer)"""
        try:
            # Update camera status
            camera_status = self.camera_manager.get_camera_status()
            scene_status = self.scene_manager.get_scene_status()
            
            # Update view label with status info
            status_text = f"📷 Camera: {camera_status['mode']}\n"
            status_text += f"📏 Distance: {camera_status['distance']:.1f}\n"
            status_text += f"🎯 Objects: {scene_status['object_count']}"
            
            self.view_label.setText(f"🎮 3D View\n{status_text}")
            
            # Update camera info
            self.update_camera_info()
            
            # Update object list
            self.update_object_list()
        except Exception as e:
            print(f"Error updating display: {e}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Stop rendering loop
            self.scene_manager._stop_rendering = True
            event.accept()
        except Exception as e:
            print(f"Error closing window: {e}")
            event.accept()


def main():
    """Main function to run the workshop"""
    app = QApplication(sys.argv)
    
    # Set Sharkman AI dark theme
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(26, 34, 56))  # #1a2238
    palette.setColor(QPalette.WindowText, QColor(234, 234, 234))  # #eaeaea
    palette.setColor(QPalette.Base, QColor(26, 34, 56))  # #1a2238
    palette.setColor(QPalette.AlternateBase, QColor(34, 43, 69))  # #222b45
    palette.setColor(QPalette.ToolTipBase, QColor(38, 49, 89))  # #263159
    palette.setColor(QPalette.ToolTipText, QColor(234, 234, 234))  # #eaeaea
    palette.setColor(QPalette.Text, QColor(234, 234, 234))  # #eaeaea
    palette.setColor(QPalette.Button, QColor(38, 49, 89))  # #263159
    palette.setColor(QPalette.ButtonText, QColor(234, 234, 234))  # #eaeaea
    palette.setColor(QPalette.BrightText, QColor(255, 111, 97))  # #ff6f61
    palette.setColor(QPalette.Link, QColor(110, 127, 243))  # #6e7ff3
    palette.setColor(QPalette.Highlight, QColor(110, 127, 243))  # #6e7ff3
    palette.setColor(QPalette.HighlightedText, QColor(234, 234, 234))  # #eaeaea
    app.setPalette(palette)
    
    # Create and show workshop window
    workshop = BlockVisionWorkshop()
    workshop.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 