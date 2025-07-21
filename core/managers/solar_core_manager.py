"""
Solar Core Manager - Infinite Energy Source for Silver Void
Controls energy distribution and provides shut-off mechanism
"""

import time
import threading
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class EnergyNode:
    name: str
    consumption_rate: float  # Energy units per second
    is_active: bool = True
    last_consumption: float = 0.0
    total_consumed: float = 0.0
    created_by: str = "environment"  # "environment" or entity name
    position: tuple = (0.0, 0.0, 0.0)  # x, y, z coordinates
    density: float = 1.0  # Node density (1.0 = normal, higher = more dense)
    range: float = 10.0  # Range of energy boost effect


class SolarCoreManager:
    """
    Infinite energy source and distribution system for Silver Void
    Provides shut-off mechanism accessible to players (but deadly)
    """
    
    def __init__(self):
        self._energy_generation_rate = float('inf')  # Infinite energy
        self._is_active = True
        self._nodes: Dict[str, EnergyNode] = {}
        self._shut_off_accessible = True  # Can be reached by players
        self._radiant_damage_threshold = 100000000000.0  # Damage per second near core
        
        # Monitoring
        self._total_energy_generated = 0.0
        self._current_consumption = 0.0
        self._start_time = time.time()
        
        # Threading for real-time updates
        self._monitoring_thread = None
        self._stop_monitoring = False
        
        # Callbacks for real-time monitoring
        self._monitoring_callbacks: List[Callable] = []
        
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start real-time energy monitoring thread"""
        self._monitoring_thread = threading.Thread(target=self._monitor_energy, daemon=True)
        self._monitoring_thread.start()
    
    def _monitor_energy(self):
        """Real-time energy monitoring loop"""
        while not self._stop_monitoring:
            if self._is_active:
                # Update energy generation
                current_time = time.time()
                elapsed = current_time - self._start_time
                self._total_energy_generated = elapsed * self._energy_generation_rate
                
                # Update consumption
                self._current_consumption = sum(
                    node.consumption_rate 
                    for node in self._nodes.values() 
                    if node.is_active
                )
                
                # Notify monitoring callbacks
                self._notify_monitoring_callbacks()
            
            time.sleep(0.1)  # 10 FPS monitoring
    
    def _notify_monitoring_callbacks(self):
        """Notify all registered monitoring callbacks"""
        for callback in self._monitoring_callbacks:
            try:
                callback(self.get_energy_status())
            except Exception as e:
                print(f"Error in monitoring callback: {e}")
    
    def create_node(self, name: str, consumption_rate: float, created_by: str = "environment", 
                   position: tuple = (0.0, 0.0, 0.0), density: float = 1.0, range: float = 10.0) -> bool:
        """Create a new energy node"""
        if name in self._nodes:
            return False
        
        node = EnergyNode(
            name=name,
            consumption_rate=consumption_rate,
            created_by=created_by,
            position=position,
            density=density,
            range=range
        )
        self._nodes[name] = node
        return True
    
    def remove_node(self, name: str) -> bool:
        """Remove an energy node"""
        if name in self._nodes:
            del self._nodes[name]
            return True
        return False
    
    def set_node_active(self, name: str, active: bool) -> bool:
        """Activate or deactivate an energy node"""
        if name in self._nodes:
            self._nodes[name].is_active = active
            return True
        return False
    
    def calculate_energy_boost(self, position: tuple) -> float:
        """
        Calculate energy boost at a given position based on nearby nodes
        Returns multiplier (1.0 = normal, 2.0 = 2x energy)
        """
        total_boost = 0.0
        
        for node in self._nodes.values():
            if not node.is_active:
                continue
            
            # Calculate distance to node
            distance = ((position[0] - node.position[0])**2 + 
                       (position[1] - node.position[1])**2 + 
                       (position[2] - node.position[2])**2)**0.5
            
            # If within range, calculate boost
            if distance <= node.range:
                # High exponential curve: density^3 for strong effect
                # Normalize to 0-1 range within node range
                distance_factor = 1.0 - (distance / node.range)
                node_boost = (node.density ** 3) * distance_factor
                total_boost += node_boost
        
        # Cap at 2x energy boost maximum
        final_multiplier = 1.0 + min(total_boost, 1.0)
        return final_multiplier
    
    def get_energy_status(self) -> Dict:
        """Get current energy status for monitoring"""
        return {
            'is_active': self._is_active,
            'total_generated': self._total_energy_generated,
            'current_consumption': self._current_consumption,
            'nodes': {
                name: {
                    'consumption_rate': node.consumption_rate,
                    'is_active': node.is_active,
                    'total_consumed': node.total_consumed,
                    'created_by': node.created_by,
                    'position': node.position,
                    'density': node.density,
                    'range': node.range
                }
                for name, node in self._nodes.items()
            },
            'shut_off_accessible': self._shut_off_accessible,
            'radiant_damage_threshold': self._radiant_damage_threshold
        }
    
    def attempt_shut_off(self, player_distance: float) -> Dict:
        """
        Attempt to shut off the solar core
        Returns damage taken and success status
        """
        if not self._shut_off_accessible:
            return {
                'success': False,
                'damage_taken': 0,
                'message': 'Shut-off mechanism is not accessible'
            }
        
        # Calculate radiant damage based on distance
        if player_distance <= 1.0:  # Very close to core
            damage = self._radiant_damage_threshold
            self._is_active = False
            return {
                'success': True,
                'damage_taken': damage,
                'message': 'Solar core shut off successfully - but you took massive radiant damage!'
            }
        elif player_distance <= 5.0:  # Close to core
            damage = self._radiant_damage_threshold * 0.5
            return {
                'success': False,
                'damage_taken': damage,
                'message': 'Too far from core to shut off - took significant radiant damage'
            }
        else:  # Too far
            return {
                'success': False,
                'damage_taken': 0,
                'message': 'Too far from solar core to access shut-off mechanism'
            }
    
    def restart_core(self) -> bool:
        """Restart the solar core after shut-off"""
        if not self._is_active:
            self._is_active = True
            return True
        return False
    
    def add_monitoring_callback(self, callback: Callable):
        """Add a callback for real-time energy monitoring"""
        self._monitoring_callbacks.append(callback)
    
    def remove_monitoring_callback(self, callback: Callable):
        """Remove a monitoring callback"""
        if callback in self._monitoring_callbacks:
            self._monitoring_callbacks.remove(callback)
    
    def shutdown(self):
        """Clean shutdown of the solar core manager"""
        self._stop_monitoring = True
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=1.0)


# Global instance for easy access
_solar_core_instance: Optional[SolarCoreManager] = None


def get_solar_core() -> SolarCoreManager:
    """Get the global solar core instance"""
    global _solar_core_instance
    if _solar_core_instance is None:
        _solar_core_instance = SolarCoreManager()
    return _solar_core_instance


def shutdown_solar_core():
    """Shutdown the global solar core instance"""
    global _solar_core_instance
    if _solar_core_instance:
        _solar_core_instance.shutdown()
        _solar_core_instance = None 