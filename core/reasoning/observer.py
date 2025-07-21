"""
Environmental Observer - Phase 1 of Xaryxis Reasoning Engine
Watches energy processes and logs reasoning without disrupting functionality
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


class EnvironmentalObserver:
    """Watches Xaryxis's energy processes and logs reasoning"""
    
    def __init__(self, solar_core, xaryxis_heart):
        self.solar_core = solar_core
        self.xaryxis_heart = xaryxis_heart
        self.reasoning_log = []
        self.trace_folder = Path("reasoning_traces")
        self.trace_folder.mkdir(exist_ok=True)
        
        # Create today's trace file
        today = datetime.now().strftime("%Y-%m-%d")
        self.current_trace_file = self.trace_folder / f"environmental_trace_{today}.json"
        
        # Load existing traces if file exists
        if self.current_trace_file.exists():
            try:
                with open(self.current_trace_file, 'r') as f:
                    self.reasoning_log = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.reasoning_log = []
    
    def observe_energy_analysis(self, energy_status: Dict[str, Any], node_activity: Dict[str, Any]):
        """Log why certain energy decisions were made"""
        trace_entry = {
            'stage': 'energy_analysis',
            'timestamp': datetime.now().isoformat(),
            'consumption': energy_status.get('current_consumption', 0),
            'nodes_active': len([n for n in energy_status.get('nodes', {}).values() if n.get('is_active', False)]),
            'total_nodes': len(energy_status.get('nodes', {})),
            'energy_boost_areas': self._identify_boost_zones(energy_status),
            'system_state': self._get_system_state(),
            'reasoning_notes': self._generate_reasoning_notes(energy_status)
        }
        
        self.reasoning_log.append(trace_entry)
        
        # Save to file every 10 entries to avoid data loss
        if len(self.reasoning_log) % 10 == 0:
            self.save_trace()
    
    def _identify_boost_zones(self, energy_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify areas with high energy boost potential"""
        boost_zones = []
        nodes = energy_status.get('nodes', {})
        
        for name, node_data in nodes.items():
            if node_data.get('is_active', False):
                # Calculate boost potential based on density and range
                density = node_data.get('density', 1.0)
                range_val = node_data.get('range', 10.0)
                boost_potential = density * range_val
                
                if boost_potential > 10:  # High boost potential
                    boost_zones.append({
                        'node_name': name,
                        'position': node_data.get('position', (0, 0, 0)),
                        'boost_potential': boost_potential,
                        'density': density,
                        'range': range_val
                    })
        
        return boost_zones
    
    def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state from Xaryxis Heart"""
        try:
            if hasattr(self.xaryxis_heart, 'get_system_state'):
                return self.xaryxis_heart.get_system_state()
            else:
                return {
                    'learning_rate': 0.5,
                    'current_state': 'normal',
                    'confidence': 0.5
                }
        except Exception:
            return {
                'learning_rate': 0.5,
                'current_state': 'normal', 
                'confidence': 0.5
            }
    
    def _generate_reasoning_notes(self, energy_status: Dict[str, Any]) -> str:
        """Generate simple reasoning notes about the current energy state"""
        consumption = energy_status.get('current_consumption', 0)
        nodes = energy_status.get('nodes', {})
        active_nodes = len([n for n in nodes.values() if n.get('is_active', False)])
        
        notes = []
        
        if consumption > 100:
            notes.append("High energy consumption detected")
        elif consumption < 10:
            notes.append("Low energy consumption - potential optimization opportunity")
        
        if active_nodes > 10:
            notes.append("Many active nodes - monitoring for efficiency")
        elif active_nodes < 3:
            notes.append("Few active nodes - system may be underutilized")
        
        if not notes:
            notes.append("Normal energy state - no immediate action required")
        
        return "; ".join(notes)
    
    def save_trace(self):
        """Save current reasoning log to file"""
        try:
            with open(self.current_trace_file, 'w') as f:
                json.dump(self.reasoning_log, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save reasoning trace: {e}")
    
    def get_recent_traces(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent reasoning traces for analysis"""
        return self.reasoning_log[-count:] if self.reasoning_log else []
    
    def get_trace_summary(self) -> Dict[str, Any]:
        """Get summary statistics of current reasoning traces"""
        if not self.reasoning_log:
            return {
                'total_traces': 0,
                'average_consumption': 0,
                'most_common_notes': [],
                'boost_zones_identified': 0
            }
        
        total_traces = len(self.reasoning_log)
        avg_consumption = sum(t.get('consumption', 0) for t in self.reasoning_log) / total_traces
        
        # Count reasoning notes
        all_notes = []
        for trace in self.reasoning_log:
            notes = trace.get('reasoning_notes', '')
            all_notes.extend(notes.split('; '))
        
        note_counts = {}
        for note in all_notes:
            note_counts[note] = note_counts.get(note, 0) + 1
        
        most_common = sorted(note_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        total_boost_zones = sum(len(t.get('energy_boost_areas', [])) for t in self.reasoning_log)
        
        return {
            'total_traces': total_traces,
            'average_consumption': avg_consumption,
            'most_common_notes': most_common,
            'boost_zones_identified': total_boost_zones
        } 