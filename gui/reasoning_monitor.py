"""
Reasoning Monitor - Real-time environmental reasoning interface
Shows Xaryxis's reasoning process and energy management decisions
"""

import sys
import os
import time
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTableWidget, 
                             QTableWidgetItem, QGroupBox, QApplication,
                             QTextEdit, QSplitter, QTabWidget)
from PyQt5.QtCore import QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor

from core.managers.solar_core_manager import get_solar_core
from core.ai.xaryxis_heart import XaryxisHeart
from core.reasoning.observer import EnvironmentalObserver
from core.reasoning.analyzer import EnergyContextAnalyzer
from core.reasoning.strategies import EnergyStrategySelector


class ReasoningMonitorWidget(QWidget):
    """Real-time reasoning monitoring widget"""
    
    def __init__(self):
        super().__init__()
        self.solar_core = get_solar_core()
        self.xaryxis_heart = XaryxisHeart()
        
        # Initialize reasoning components
        self.environmental_observer = EnvironmentalObserver(self.solar_core, self.xaryxis_heart)
        self.context_analyzer = EnergyContextAnalyzer()
        self.strategy_selector = EnergyStrategySelector()
        
        # Initialize pending update
        self._pending_update = None
        
        self.setup_ui()
        self.setup_monitoring()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(500)  # 2 FPS updates for reasoning
    
    def setup_ui(self):
        """Setup the reasoning monitoring interface"""
        self.setWindowTitle("Silver Void - Environmental Reasoning Monitor")
        self.setGeometry(100, 100, 1200, 800)
        
        layout = QVBoxLayout()
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Tab 1: Current Reasoning
        self.setup_current_reasoning_tab()
        
        # Tab 2: Strategy Analysis
        self.setup_strategy_analysis_tab()
        
        # Tab 3: Trace History
        self.setup_trace_history_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Control section
        control_group = QGroupBox("Reasoning Controls")
        control_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh Analysis")
        self.refresh_btn.clicked.connect(self.refresh_analysis)
        control_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("📊 Export Traces")
        self.export_btn.clicked.connect(self.export_traces)
        control_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Traces")
        self.clear_btn.clicked.connect(self.clear_traces)
        control_layout.addWidget(self.clear_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        self.setLayout(layout)
    
    def setup_current_reasoning_tab(self):
        """Setup the current reasoning analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Current context section
        context_group = QGroupBox("Current Environmental Context")
        context_layout = QVBoxLayout()
        
        self.context_label = QLabel("Analyzing environment...")
        self.context_label.setFont(QFont("Arial", 12))
        context_layout.addWidget(self.context_label)
        
        # Context details
        self.context_details = QTextEdit()
        self.context_details.setMaximumHeight(150)
        self.context_details.setReadOnly(True)
        context_layout.addWidget(self.context_details)
        
        context_group.setLayout(context_layout)
        layout.addWidget(context_group)
        
        # Selected strategy section
        strategy_group = QGroupBox("Selected Energy Strategy")
        strategy_layout = QVBoxLayout()
        
        self.strategy_label = QLabel("No strategy selected")
        self.strategy_label.setFont(QFont("Arial", 14, QFont.Bold))
        strategy_layout.addWidget(self.strategy_label)
        
        self.strategy_description = QLabel("")
        self.strategy_description.setFont(QFont("Arial", 11))
        strategy_layout.addWidget(self.strategy_description)
        
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setMaximum(100)
        strategy_layout.addWidget(self.confidence_bar)
        
        self.reasoning_text = QTextEdit()
        self.reasoning_text.setMaximumHeight(100)
        self.reasoning_text.setReadOnly(True)
        strategy_layout.addWidget(self.reasoning_text)
        
        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group)
        
        # Recent traces section
        traces_group = QGroupBox("Recent Reasoning Traces")
        traces_layout = QVBoxLayout()
        
        self.traces_table = QTableWidget()
        self.traces_table.setColumnCount(5)
        self.traces_table.setHorizontalHeaderLabels([
            "Timestamp", "Consumption", "Active Nodes", "Boost Zones", "Reasoning Notes"
        ])
        traces_layout.addWidget(self.traces_table)
        
        traces_group.setLayout(traces_layout)
        layout.addWidget(traces_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Current Reasoning")
    
    def setup_strategy_analysis_tab(self):
        """Setup the strategy analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Available strategies section
        strategies_group = QGroupBox("Available Energy Strategies")
        strategies_layout = QVBoxLayout()
        
        self.strategies_table = QTableWidget()
        self.strategies_table.setColumnCount(4)
        self.strategies_table.setHorizontalHeaderLabels([
            "Strategy", "Priority", "Conditions", "Actions"
        ])
        strategies_layout.addWidget(self.strategies_table)
        
        strategies_group.setLayout(strategies_layout)
        layout.addWidget(strategies_group)
        
        # Strategy effectiveness section
        effectiveness_group = QGroupBox("Strategy Effectiveness Estimates")
        effectiveness_layout = QVBoxLayout()
        
        self.effectiveness_text = QTextEdit()
        self.effectiveness_text.setReadOnly(True)
        effectiveness_layout.addWidget(self.effectiveness_text)
        
        effectiveness_group.setLayout(effectiveness_layout)
        layout.addWidget(effectiveness_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Strategy Analysis")
    
    def setup_trace_history_tab(self):
        """Setup the trace history tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Trace summary section
        summary_group = QGroupBox("Reasoning Trace Summary")
        summary_layout = QVBoxLayout()
        
        self.summary_label = QLabel("Loading summary...")
        self.summary_label.setFont(QFont("Arial", 12))
        summary_layout.addWidget(self.summary_label)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Detailed trace view
        trace_group = QGroupBox("Detailed Trace View")
        trace_layout = QVBoxLayout()
        
        self.trace_text = QTextEdit()
        self.trace_text.setReadOnly(True)
        trace_layout.addWidget(self.trace_text)
        
        trace_group.setLayout(trace_layout)
        layout.addWidget(trace_group)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Trace History")
    
    def setup_monitoring(self):
        """Setup real-time monitoring callbacks"""
        self.solar_core.add_monitoring_callback(self.on_energy_update)
    
    def on_energy_update(self, status: Dict[str, Any]):
        """Callback for energy status updates"""
        # Observe energy analysis
        self.environmental_observer.observe_energy_analysis(status, status.get('nodes', {}))
        
        # Analyze context
        system_state = self.xaryxis_heart.get_system_status() if hasattr(self.xaryxis_heart, 'get_system_status') else {
            'learning_rate': 0.5,
            'current_state': 'normal',
            'confidence': 0.5
        }
        
        context_analysis = self.context_analyzer.analyze(status, {}, system_state)
        
        # Select strategy
        strategy_result = self.strategy_selector.select_strategy(context_analysis, system_state)
        
        # Store the data for the main thread to update
        self._pending_update = {
            'context': context_analysis,
            'strategy': strategy_result,
            'status': status
        }
    
    def update_current_reasoning_display(self, context: Dict[str, Any], strategy: Dict[str, Any], status: Dict[str, Any]):
        """Update the current reasoning display"""
        # Update context
        context_text = f"Consumption: {status.get('current_consumption', 0):.1f} | "
        context_text += f"Active Nodes: {len([n for n in status.get('nodes', {}).values() if n.get('is_active', False)])} | "
        context_text += f"Risk Level: {context.get('risk_level', 'unknown')}"
        
        self.context_label.setText(context_text)
        
        # Update context details
        details = []
        if context.get('is_crisis', False):
            details.append("🚨 CRISIS DETECTED")
        if context.get('is_inefficient', False):
            details.append("⚠️ Inefficient energy usage")
        if context.get('node_clustering', {}).get('clustered', False):
            details.append("📍 Nodes are clustered")
        
        stability = context.get('environmental_stability', {})
        details.append(f"Stability: {stability.get('level', 'unknown')} ({stability.get('score', 0):.2f})")
        
        self.context_details.setText("\n".join(details))
        
        # Update strategy
        strategy_info = strategy.get('strategy', {})
        self.strategy_label.setText(strategy_info.get('name', 'Unknown Strategy'))
        self.strategy_description.setText(strategy_info.get('description', ''))
        
        confidence = strategy.get('confidence', 0) * 100
        self.confidence_bar.setValue(int(confidence))
        self.confidence_bar.setFormat(f"Confidence: {confidence:.1f}%")
        
        self.reasoning_text.setText(strategy.get('reasoning', 'No reasoning available'))
        
        # Update recent traces
        self.update_traces_table()
    
    def update_traces_table(self):
        """Update the recent traces table"""
        recent_traces = self.environmental_observer.get_recent_traces(10)
        
        self.traces_table.setRowCount(len(recent_traces))
        
        for row, trace in enumerate(recent_traces):
            # Timestamp
            timestamp = trace.get('timestamp', '')
            if timestamp:
                timestamp = timestamp.split('T')[1][:8]  # Just time part
            self.traces_table.setItem(row, 0, QTableWidgetItem(timestamp))
            
            # Consumption
            consumption = trace.get('consumption', 0)
            self.traces_table.setItem(row, 1, QTableWidgetItem(f"{consumption:.1f}"))
            
            # Active nodes
            active_nodes = trace.get('nodes_active', 0)
            self.traces_table.setItem(row, 2, QTableWidgetItem(str(active_nodes)))
            
            # Boost zones
            boost_zones = len(trace.get('energy_boost_areas', []))
            self.traces_table.setItem(row, 3, QTableWidgetItem(str(boost_zones)))
            
            # Reasoning notes
            notes = trace.get('reasoning_notes', '')
            self.traces_table.setItem(row, 4, QTableWidgetItem(notes))
    
    def update_strategy_analysis_display(self):
        """Update the strategy analysis display"""
        strategies = self.strategy_selector.get_all_strategies()
        
        self.strategies_table.setRowCount(len(strategies))
        
        for row, (strategy_id, strategy) in enumerate(strategies.items()):
            self.strategies_table.setItem(row, 0, QTableWidgetItem(strategy['name']))
            self.strategies_table.setItem(row, 1, QTableWidgetItem(str(strategy['priority'])))
            self.strategies_table.setItem(row, 2, QTableWidgetItem(", ".join(strategy['conditions'])))
            self.strategies_table.setItem(row, 3, QTableWidgetItem(", ".join(strategy['actions'])))
        
        # Update effectiveness text
        effectiveness_text = "Strategy Effectiveness Estimates:\n\n"
        for strategy_id, strategy in strategies.items():
            details = self.strategy_selector.get_strategy_details(strategy_id)
            effectiveness = details.get('estimated_effectiveness', {})
            effectiveness_text += f"{strategy['name']}:\n"
            effectiveness_text += f"  Immediate: {effectiveness.get('immediate', 0):.1%}\n"
            effectiveness_text += f"  Long-term: {effectiveness.get('long_term', 0):.1%}\n\n"
        
        self.effectiveness_text.setText(effectiveness_text)
    
    def update_trace_history_display(self):
        """Update the trace history display"""
        summary = self.environmental_observer.get_trace_summary()
        
        summary_text = f"Total Traces: {summary['total_traces']}\n"
        summary_text += f"Average Consumption: {summary['average_consumption']:.1f}\n"
        summary_text += f"Boost Zones Identified: {summary['boost_zones_identified']}\n\n"
        
        summary_text += "Most Common Reasoning Notes:\n"
        for note, count in summary['most_common_notes']:
            summary_text += f"  {note}: {count} times\n"
        
        self.summary_label.setText(summary_text)
        
        # Show detailed trace
        recent_traces = self.environmental_observer.get_recent_traces(5)
        trace_text = "Recent Detailed Traces:\n\n"
        
        for trace in recent_traces:
            trace_text += f"Timestamp: {trace.get('timestamp', '')}\n"
            trace_text += f"Consumption: {trace.get('consumption', 0):.1f}\n"
            trace_text += f"Active Nodes: {trace.get('nodes_active', 0)}\n"
            trace_text += f"Reasoning: {trace.get('reasoning_notes', '')}\n"
            trace_text += "-" * 50 + "\n"
        
        self.trace_text.setText(trace_text)
    
    def update_display(self):
        """Update display (called by timer)"""
        # Check for pending updates from energy monitoring
        if self._pending_update:
            self.update_current_reasoning_display(
                self._pending_update['context'],
                self._pending_update['strategy'],
                self._pending_update['status']
            )
            self._pending_update = None
        
        # Update strategy analysis
        self.update_strategy_analysis_display()
        
        # Update trace history
        self.update_trace_history_display()
    
    def refresh_analysis(self):
        """Refresh the current analysis"""
        current_status = self.solar_core.get_energy_status()
        self.on_energy_update(current_status)
    
    def export_traces(self):
        """Export reasoning traces to file"""
        try:
            import json
            from datetime import datetime
            
            filename = f"reasoning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w') as f:
                json.dump(self.environmental_observer.reasoning_log, f, indent=2)
            
            print(f"Reasoning traces exported to {filename}")
        except Exception as e:
            print(f"Failed to export traces: {e}")
    
    def clear_traces(self):
        """Clear all reasoning traces"""
        self.environmental_observer.reasoning_log = []
        self.environmental_observer.save_trace()
        print("Reasoning traces cleared")


def main():
    """Run the reasoning monitor as a standalone application"""
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
    
    monitor = ReasoningMonitorWidget()
    monitor.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 