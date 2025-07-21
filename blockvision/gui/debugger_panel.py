"""
BlockVision Debugger Panel
Real-time monitoring and debugging interface for BlockVision
"""

import sys
import os
import time
from typing import Dict, Any, List

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTableWidget, 
                             QTableWidgetItem, QGroupBox, QTextEdit,
                             QSplitter, QTabWidget, QCheckBox)
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

from blockvision.core.managers.scene_manager import get_scene_manager
from blockvision.core.managers.camera_manager import get_camera_manager
from blockvision.core.managers.object_manager import get_object_manager
from blockvision.core.renderers.simple_renderer import SimpleRenderer


class BlockVisionDebuggerPanel(QWidget):
    """Real-time BlockVision debugging and monitoring panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize managers
        self.scene_manager = get_scene_manager()
        self.camera_manager = get_camera_manager()
        self.object_manager = get_object_manager()
        
        # Debug state
        self.debug_log = []
        self.max_log_entries = 100
        
        # Setup UI
        self.setup_ui()
        self.setup_monitoring()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(500)  # 2 FPS updates
    
    def setup_ui(self):
        """Setup the debugging interface"""
        layout = QVBoxLayout()
        
        # Apply Sharkman AI styling
        self.setStyleSheet("""
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
            QTableWidget {
                background-color: #1a2238;
                border: 2px solid #394867;
                border-radius: 5px;
                color: #eaeaea;
                gridline-color: #394867;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #6e7ff3;
                color: #eaeaea;
            }
            QHeaderView::section {
                background-color: #263159;
                color: #f7c873;
                border: 1px solid #394867;
                padding: 5px;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #1a2238;
                border: 2px solid #394867;
                border-radius: 5px;
                color: #eaeaea;
                padding: 5px;
            }
            QLabel {
                color: #eaeaea;
            }
            QTabWidget::pane {
                border: 2px solid #394867;
                background-color: #222b45;
            }
            QTabBar::tab {
                background-color: #263159;
                color: #eaeaea;
                border: 2px solid #394867;
                border-bottom: none;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #6e7ff3;
                color: #eaeaea;
            }
            QTabBar::tab:hover {
                background-color: #f7c873;
                color: #1a2238;
            }
        """)
        
        # Header
        header_label = QLabel("🔍 BlockVision Debugger")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #f7c873; margin: 5px;")
        layout.addWidget(header_label)
        
        # Create tab widget for different debug views
        self.tab_widget = QTabWidget()
        
        # Tab 1: System Status
        self.setup_system_status_tab()
        
        # Tab 2: Scene Debug
        self.setup_scene_debug_tab()
        
        # Tab 3: Object Debug
        self.setup_object_debug_tab()
        
        # Tab 4: Render Debug
        self.setup_render_debug_tab()
        
        # Tab 5: Debug Log
        self.setup_debug_log_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Control section
        control_group = QGroupBox("Debug Controls")
        control_layout = QHBoxLayout()
        
        self.clear_log_btn = QPushButton("🗑️ Clear Log")
        self.clear_log_btn.clicked.connect(self.clear_debug_log)
        control_layout.addWidget(self.clear_log_btn)
        
        self.export_log_btn = QPushButton("📊 Export Log")
        self.export_log_btn.clicked.connect(self.export_debug_log)
        control_layout.addWidget(self.export_log_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_debug_info)
        control_layout.addWidget(self.refresh_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        self.setLayout(layout)
    
    def setup_system_status_tab(self):
        """Setup the system status tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # System status section
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout()
        
        self.system_status_label = QLabel("🟢 ACTIVE")
        self.system_status_label.setFont(QFont("Arial", 12, QFont.Bold))
        status_layout.addWidget(self.system_status_label)
        
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.fps_label)
        
        self.memory_label = QLabel("Memory Usage: 0 MB")
        self.memory_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.memory_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Performance section
        perf_group = QGroupBox("Performance Metrics")
        perf_layout = QVBoxLayout()
        
        self.render_time_label = QLabel("Render Time: 0ms")
        perf_layout.addWidget(self.render_time_label)
        
        self.update_time_label = QLabel("Update Time: 0ms")
        perf_layout.addWidget(self.update_time_label)
        
        self.object_count_label = QLabel("Objects: 0")
        perf_layout.addWidget(self.object_count_label)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        # Error section
        error_group = QGroupBox("Error Log")
        error_layout = QVBoxLayout()
        
        self.error_text = QTextEdit()
        self.error_text.setMaximumHeight(100)
        self.error_text.setReadOnly(True)
        error_layout.addWidget(self.error_text)
        
        error_group.setLayout(error_layout)
        layout.addWidget(error_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "System Status")
    
    def setup_scene_debug_tab(self):
        """Setup the scene debugging tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Scene info section
        scene_group = QGroupBox("Scene Information")
        scene_layout = QVBoxLayout()
        
        self.scene_state_label = QLabel("State: Unknown")
        scene_layout.addWidget(self.scene_state_label)
        
        self.scene_objects_label = QLabel("Objects: 0")
        scene_layout.addWidget(self.scene_objects_label)
        
        self.scene_callback_label = QLabel("Callbacks: 0")
        scene_layout.addWidget(self.scene_callback_label)
        
        scene_group.setLayout(scene_layout)
        layout.addWidget(scene_group)
        
        # Scene objects table
        objects_group = QGroupBox("Scene Objects")
        objects_layout = QVBoxLayout()
        
        self.scene_objects_table = QTableWidget()
        self.scene_objects_table.setColumnCount(6)
        self.scene_objects_table.setHorizontalHeaderLabels([
            "ID", "Name", "Type", "Position", "Scale", "Rotation"
        ])
        objects_layout.addWidget(self.scene_objects_table)
        
        objects_group.setLayout(objects_layout)
        layout.addWidget(objects_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Scene Debug")
    
    def setup_object_debug_tab(self):
        """Setup the object debugging tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Object manager info
        obj_group = QGroupBox("Object Manager")
        obj_layout = QVBoxLayout()
        
        self.obj_count_label = QLabel("Total Objects: 0")
        obj_layout.addWidget(self.obj_count_label)
        
        self.obj_models_label = QLabel("Models: 0")
        obj_layout.addWidget(self.obj_models_label)
        
        self.obj_images_label = QLabel("Images: 0")
        obj_layout.addWidget(self.obj_images_label)
        
        obj_group.setLayout(obj_layout)
        layout.addWidget(obj_group)
        
        # Object details table
        details_group = QGroupBox("Object Details")
        details_layout = QVBoxLayout()
        
        self.object_details_table = QTableWidget()
        self.object_details_table.setColumnCount(5)
        self.object_details_table.setHorizontalHeaderLabels([
            "ID", "Name", "Type", "File Path", "Created"
        ])
        details_layout.addWidget(self.object_details_table)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Object Debug")
    
    def setup_render_debug_tab(self):
        """Setup the render debugging tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Renderer info
        render_group = QGroupBox("Renderer Information")
        render_layout = QVBoxLayout()
        
        self.render_mode_label = QLabel("Mode: Simple")
        render_layout.addWidget(self.render_mode_label)
        
        self.sprite_mode_label = QLabel("Sprite Mode: OFF")
        render_layout.addWidget(self.sprite_mode_label)
        
        self.viewport_label = QLabel("Viewport: 0x0")
        render_layout.addWidget(self.viewport_label)
        
        self.rendered_objects_label = QLabel("Rendered Objects: 0")
        render_layout.addWidget(self.rendered_objects_label)
        
        render_group.setLayout(render_layout)
        layout.addWidget(render_group)
        
        # Camera info
        camera_group = QGroupBox("Camera Information")
        camera_layout = QVBoxLayout()
        
        self.camera_mode_label = QLabel("Mode: Orbit")
        camera_layout.addWidget(self.camera_mode_label)
        
        self.camera_pos_label = QLabel("Position: (0, 0, 0)")
        camera_layout.addWidget(self.camera_pos_label)
        
        self.camera_distance_label = QLabel("Distance: 0.0")
        camera_layout.addWidget(self.camera_distance_label)
        
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Render Debug")
    
    def setup_debug_log_tab(self):
        """Setup the debug log tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Debug log
        log_group = QGroupBox("Debug Log")
        log_layout = QVBoxLayout()
        
        self.debug_text = QTextEdit()
        self.debug_text.setReadOnly(True)
        log_layout.addWidget(self.debug_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Debug Log")
    
    def setup_monitoring(self):
        """Setup monitoring callbacks"""
        # Add scene manager callback
        self.scene_manager.add_render_callback(self.on_scene_update)
    
    def on_scene_update(self, scene_data: Dict[str, Any]):
        """Callback for scene updates"""
        self.add_debug_log("Scene update", f"Objects: {scene_data.get('object_count', 0)}")
    
    def add_debug_log(self, category: str, message: str):
        """Add entry to debug log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {category}: {message}"
        
        self.debug_log.append(log_entry)
        
        # Keep log size manageable
        if len(self.debug_log) > self.max_log_entries:
            self.debug_log.pop(0)
    
    def update_system_status(self):
        """Update system status display"""
        try:
            # Get scene status
            scene_status = self.scene_manager.get_scene_status()
            camera_status = self.camera_manager.get_camera_status()
            object_status = self.object_manager.get_object_status()
            
            # Update status labels
            if scene_status['rendering_active']:
                self.system_status_label.setText("🟢 ACTIVE")
                self.system_status_label.setStyleSheet("color: green;")
            else:
                self.system_status_label.setText("🔴 INACTIVE")
                self.system_status_label.setStyleSheet("color: red;")
            
            self.object_count_label.setText(f"Objects: {scene_status['object_count']}")
            
            # Update performance metrics
            self.fps_label.setText(f"FPS: ~30")
            self.memory_label.setText("Memory Usage: ~5 MB")
            
        except Exception as e:
            self.add_debug_log("ERROR", f"System status update failed: {e}")
    
    def update_scene_debug(self):
        """Update scene debugging information"""
        try:
            scene_data = self.scene_manager.get_scene_data()
            scene_status = self.scene_manager.get_scene_status()
            
            # Update scene info
            self.scene_state_label.setText(f"State: {scene_data['state']}")
            self.scene_objects_label.setText(f"Objects: {scene_status['object_count']}")
            self.scene_callback_label.setText(f"Callbacks: {scene_status['callback_count']}")
            
            # Update objects table
            objects = scene_data.get('objects', {})
            self.scene_objects_table.setRowCount(len(objects))
            
            for row, (obj_id, obj_data) in enumerate(objects.items()):
                self.scene_objects_table.setItem(row, 0, QTableWidgetItem(obj_id))
                self.scene_objects_table.setItem(row, 1, QTableWidgetItem(obj_data['name']))
                self.scene_objects_table.setItem(row, 2, QTableWidgetItem(obj_data['type']))
                self.scene_objects_table.setItem(row, 3, QTableWidgetItem(str(obj_data['position'])))
                self.scene_objects_table.setItem(row, 4, QTableWidgetItem(str(obj_data['scale'])))
                self.scene_objects_table.setItem(row, 5, QTableWidgetItem(str(obj_data['rotation'])))
                
        except Exception as e:
            self.add_debug_log("ERROR", f"Scene debug update failed: {e}")
    
    def update_object_debug(self):
        """Update object debugging information"""
        try:
            object_status = self.object_manager.get_object_status()
            all_objects = self.object_manager.get_all_objects()
            
            # Update object info
            self.obj_count_label.setText(f"Total Objects: {object_status['total_objects']}")
            self.obj_models_label.setText(f"Models: {object_status['models']}")
            self.obj_images_label.setText(f"Images: {object_status['images']}")
            
            # Update object details table
            self.object_details_table.setRowCount(len(all_objects))
            
            for row, obj in enumerate(all_objects):
                self.object_details_table.setItem(row, 0, QTableWidgetItem(obj.id))
                self.object_details_table.setItem(row, 1, QTableWidgetItem(obj.name))
                self.object_details_table.setItem(row, 2, QTableWidgetItem(obj.type.value))
                self.object_details_table.setItem(row, 3, QTableWidgetItem(obj.file_path or "N/A"))
                self.object_details_table.setItem(row, 4, QTableWidgetItem(
                    time.strftime("%H:%M:%S", time.localtime(obj.created_at)) if obj.created_at else "N/A"
                ))
                
        except Exception as e:
            self.add_debug_log("ERROR", f"Object debug update failed: {e}")
    
    def update_render_debug(self):
        """Update render debugging information"""
        try:
            camera_status = self.camera_manager.get_camera_status()
            
            # Update renderer info
            self.render_mode_label.setText("Mode: Simple")
            self.sprite_mode_label.setText("Sprite Mode: OFF")  # Will be updated by renderer
            self.viewport_label.setText("Viewport: 800x600")  # Default size
            self.rendered_objects_label.setText("Rendered Objects: 0")  # Will be updated by renderer
            
            # Update camera info
            self.camera_mode_label.setText(f"Mode: {camera_status['mode']}")
            self.camera_pos_label.setText(f"Position: {camera_status['position']}")
            self.camera_distance_label.setText(f"Distance: {camera_status['distance']:.1f}")
            
        except Exception as e:
            self.add_debug_log("ERROR", f"Render debug update failed: {e}")
    
    def update_debug_log(self):
        """Update debug log display"""
        try:
            # Update debug text
            log_text = "\n".join(self.debug_log)
            self.debug_text.setPlainText(log_text)
            
            # Auto-scroll to bottom
            scrollbar = self.debug_text.verticalScrollBar()
            if scrollbar:
                scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            print(f"Debug log update failed: {e}")
    
    def update_display(self):
        """Update all debug displays"""
        self.update_system_status()
        self.update_scene_debug()
        self.update_object_debug()
        self.update_render_debug()
        self.update_debug_log()
    
    def clear_debug_log(self):
        """Clear the debug log"""
        self.debug_log.clear()
        self.debug_text.clear()
        self.add_debug_log("SYSTEM", "Debug log cleared")
    
    def export_debug_log(self):
        """Export debug log to file"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("Text Files (*.txt)")
            file_dialog.setDefaultSuffix("txt")
            
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                with open(file_path, 'w') as f:
                    f.write("BlockVision Debug Log\n")
                    f.write("=" * 50 + "\n\n")
                    f.write("\n".join(self.debug_log))
                
                self.add_debug_log("SYSTEM", f"Debug log exported to {file_path}")
        except Exception as e:
            self.add_debug_log("ERROR", f"Export failed: {e}")
    
    def refresh_debug_info(self):
        """Refresh all debug information"""
        self.add_debug_log("SYSTEM", "Debug information refreshed")
        self.update_display()
    
    def set_renderer_info(self, renderer_info: Dict[str, Any]):
        """Update renderer information from main window"""
        try:
            self.sprite_mode_label.setText(f"Sprite Mode: {'ON' if renderer_info.get('sprite_mode', False) else 'OFF'}")
            self.rendered_objects_label.setText(f"Rendered Objects: {renderer_info.get('rendered_objects', 0)}")
            self.viewport_label.setText(f"Viewport: {renderer_info.get('viewport_size', (0, 0))}")
        except Exception as e:
            self.add_debug_log("ERROR", f"Renderer info update failed: {e}")


def main():
    """Run the debugger panel as a standalone application"""
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Set Sharkman AI dark theme
    app.setStyle("Fusion")
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
    
    debugger = BlockVisionDebuggerPanel()
    debugger.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 