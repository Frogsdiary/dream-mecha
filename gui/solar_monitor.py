"""
Solar Core Monitor - Real-time energy monitoring interface
Shows energy distribution and consumption in the Silver Void
"""

import sys
import os
import time
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTableWidget, 
                             QTableWidgetItem, QGroupBox, QApplication)
from PyQt5.QtCore import QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor

from core.managers.solar_core_manager import get_solar_core


class SolarMonitorWidget(QWidget):
    """Real-time solar core monitoring widget"""
    
    def __init__(self):
        super().__init__()
        self.solar_core = get_solar_core()
        self.setup_ui()
        self.setup_monitoring()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(100)  # 10 FPS updates
    
    def setup_ui(self):
        """Setup the monitoring interface"""
        self.setWindowTitle("Silver Void - Solar Core Monitor")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        # Status section
        status_group = QGroupBox("Solar Core Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("🟢 ACTIVE")
        self.status_label.setFont(QFont("Arial", 16, QFont.Bold))
        status_layout.addWidget(self.status_label)
        
        self.energy_generated_label = QLabel("Total Energy Generated: ∞")
        self.energy_generated_label.setFont(QFont("Arial", 12))
        status_layout.addWidget(self.energy_generated_label)
        
        self.consumption_label = QLabel("Current Consumption: 0.0 units/sec")
        self.consumption_label.setFont(QFont("Arial", 12))
        status_layout.addWidget(self.consumption_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Control section
        control_group = QGroupBox("Core Controls")
        control_layout = QHBoxLayout()
        
        self.shut_off_btn = QPushButton("🛑 Emergency Shut-Off")
        self.shut_off_btn.setStyleSheet("background-color: #ff4444; color: white; font-weight: bold;")
        self.shut_off_btn.clicked.connect(self.simulate_shut_off)
        control_layout.addWidget(self.shut_off_btn)
        
        self.restart_btn = QPushButton("🔄 Restart Core")
        self.restart_btn.setStyleSheet("background-color: #44ff44; color: white; font-weight: bold;")
        self.restart_btn.clicked.connect(self.restart_core)
        control_layout.addWidget(self.restart_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Nodes table
        nodes_group = QGroupBox("Energy Nodes")
        nodes_layout = QVBoxLayout()
        
        self.nodes_table = QTableWidget()
        self.nodes_table.setColumnCount(8)
        self.nodes_table.setHorizontalHeaderLabels([
            "Node", "Consumption Rate", "Status", "Total Consumed", "Created By", "Position", "Density", "Range"
        ])
        nodes_layout.addWidget(self.nodes_table)
        
        # Add some test nodes
        test_btn = QPushButton("Add Test Nodes")
        test_btn.clicked.connect(self.add_test_nodes)
        nodes_layout.addWidget(test_btn)
        
        nodes_group.setLayout(nodes_layout)
        layout.addWidget(nodes_group)
        
        self.setLayout(layout)
    
    def setup_monitoring(self):
        """Setup real-time monitoring callbacks"""
        self.solar_core.add_monitoring_callback(self.on_energy_update)
    
    def on_energy_update(self, status: Dict[str, Any]):
        """Callback for energy status updates"""
        # Update status display
        if status['is_active']:
            self.status_label.setText("🟢 ACTIVE")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("🔴 SHUT DOWN")
            self.status_label.setStyleSheet("color: red;")
        
        self.energy_generated_label.setText(f"Total Energy Generated: {status['total_generated']:.1f} units")
        self.consumption_label.setText(f"Current Consumption: {status['current_consumption']:.1f} units/sec")
        
        # Update nodes table
        self.update_nodes_table(status['nodes'])
    
    def update_nodes_table(self, nodes: Dict[str, Any]):
        """Update the nodes table with current data"""
        self.nodes_table.setRowCount(len(nodes))
        
        for row, (name, data) in enumerate(nodes.items()):
            self.nodes_table.setItem(row, 0, QTableWidgetItem(name))
            self.nodes_table.setItem(row, 1, QTableWidgetItem(f"{data['consumption_rate']:.1f}"))
            
            status = "🟢 Active" if data['is_active'] else "🔴 Inactive"
            self.nodes_table.setItem(row, 2, QTableWidgetItem(status))
            
            self.nodes_table.setItem(row, 3, QTableWidgetItem(f"{data['total_consumed']:.1f}"))
            self.nodes_table.setItem(row, 4, QTableWidgetItem(data['created_by']))
            self.nodes_table.setItem(row, 5, QTableWidgetItem(f"{data['position']}"))
            self.nodes_table.setItem(row, 6, QTableWidgetItem(f"{data['density']:.2f}"))
            self.nodes_table.setItem(row, 7, QTableWidgetItem(f"{data['range']:.1f}"))
    
    def update_display(self):
        """Update display (called by timer)"""
        # This is handled by the monitoring callback
        pass
    
    def simulate_shut_off(self):
        """Simulate a player attempting to shut off the core"""
        result = self.solar_core.attempt_shut_off(player_distance=0.5)  # Close enough to succeed
        
        if result['success']:
            self.shut_off_btn.setEnabled(False)
            self.restart_btn.setEnabled(True)
        
        print(f"Shut-off attempt: {result['message']}")
        if result['damage_taken'] > 0:
            print(f"Player took {result['damage_taken']} radiant damage!")
    
    def restart_core(self):
        """Restart the solar core"""
        if self.solar_core.restart_core():
            self.shut_off_btn.setEnabled(True)
            self.restart_btn.setEnabled(False)
            print("Solar core restarted successfully!")
    
    def add_test_nodes(self):
        """Add some test energy nodes"""
        test_nodes = [
            ("Life Support", 10.0, "environment", (0.0, 0.0, 0.0), 1.0, 10.0),
            ("Navigation Systems", 5.0, "environment", (5.0, 0.0, 0.0), 1.5, 8.0),
            ("Environmental Controls", 3.0, "environment", (0.0, 5.0, 0.0), 2.0, 12.0),
            ("Decorative Lighting", 1.0, "environment", (-5.0, 0.0, 0.0), 0.8, 6.0),
            ("AI Processing", 8.0, "environment", (0.0, 0.0, 5.0), 3.0, 15.0),
            ("Communication Array", 4.0, "environment", (3.0, 3.0, 0.0), 1.2, 9.0)
        ]
        
        for name, rate, created_by, position, density, range_val in test_nodes:
            self.solar_core.create_node(name, rate, created_by, position, density, range_val)
        
        print("Added test energy nodes!")


def main():
    """Run the solar monitor as a standalone application"""
    app = QApplication(sys.argv)
    
    # Set dark theme
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    monitor = SolarMonitorWidget()
    monitor.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 