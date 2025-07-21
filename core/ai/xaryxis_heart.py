"""
Xaryxis Heart - Learning-based energy management system
Monitors energy levels and adapts behavior based on experience
"""

import time
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from core.managers.solar_core_manager import get_solar_core
from core.managers.memory_logger import get_memory_logger


class SystemState(Enum):
    NORMAL = "normal"
    MONITORING = "monitoring"
    ALERT = "alert"
    ACTIVE = "active"
    RESPONDING = "responding"


@dataclass
class SystemDecision:
    action: str
    confidence: float
    reasoning: str
    state: SystemState
    timestamp: float


class XaryxisHeart:
    """
    Learning-based energy management system
    Adapts behavior based on energy patterns and experience
    """
    
    def __init__(self):
        self.solar_core = get_solar_core()
        self.memory_logger = get_memory_logger()
        
        # System state
        self.current_state = SystemState.NORMAL
        self.learning_rate = 0.5  # How quickly it adapts
        self.adaptation_rate = 0.1
        
        # Memory and experience
        self.memories: List[Dict] = []
        self.decision_history: List[SystemDecision] = []
        self.patterns: Dict[str, float] = {}
        
        # Behavioral parameters (influence decision making)
        self.behavior_weights = {
            'exploration': 0.8,      # How much it experiments
            'conservation': 0.9,     # How much it protects systems
            'adaptability': 0.7,     # How quickly it learns
            'efficiency': 0.6        # How much it optimizes
        }
        
        # Energy monitoring thresholds
        self.energy_thresholds = {
            'critical_low': 20.0,
            'low': 50.0,
            'normal': 100.0,
            'high': 200.0,
            'critical_high': 500.0
        }
        
        # Setup monitoring
        self.setup_monitoring()
        self.start_consciousness_loop()
    
    def setup_monitoring(self):
        """Setup monitoring callbacks for the solar core"""
        self.solar_core.add_monitoring_callback(self.on_energy_update)
    
    def on_energy_update(self, status: Dict[str, Any]):
        """Respond to energy status updates"""
        current_consumption = status['current_consumption']
        
        # Log the experience
        self.add_memory("energy_update", {
            'consumption': current_consumption,
            'nodes_count': len(status['nodes']),
            'is_active': status['is_active']
        })
        
        # Analyze and respond
        self.analyze_energy_patterns(current_consumption)
        self.make_decision(current_consumption)
    
    def add_memory(self, event_type: str, data: Dict):
        """Add a memory to the system"""
        memory = {
            'type': event_type,
            'data': data,
            'timestamp': time.time(),
            'state': self.current_state.value
        }
        self.memories.append(memory)
        
        # Keep only recent memories (last 100)
        if len(self.memories) > 100:
            self.memories = self.memories[-100:]
    
    def analyze_energy_patterns(self, current_consumption: float):
        """Analyze energy patterns and learn from them"""
        # Detect patterns
        if current_consumption < self.energy_thresholds['critical_low']:
            self.patterns['low_energy'] = self.patterns.get('low_energy', 0) + 1
            self.current_state = SystemState.ALERT
        elif current_consumption > self.energy_thresholds['critical_high']:
            self.patterns['high_energy'] = self.patterns.get('high_energy', 0) + 1
            self.current_state = SystemState.ACTIVE
        else:
            self.current_state = SystemState.NORMAL
        
        # Learn from patterns
        self.learn_from_patterns()
    
    def learn_from_patterns(self):
        """Learn and adapt based on observed patterns"""
        total_memories = len(self.memories)
        if total_memories < 10:
            return
        
        # Calculate learning based on pattern frequency
        low_energy_freq = self.patterns.get('low_energy', 0) / total_memories
        high_energy_freq = self.patterns.get('high_energy', 0) / total_memories
        
        # Adjust behavior weights based on experience
        if low_energy_freq > 0.3:
            self.behavior_weights['conservation'] = min(1.0, self.behavior_weights['conservation'] + 0.1)
        
        if high_energy_freq > 0.3:
            self.behavior_weights['exploration'] = min(1.0, self.behavior_weights['exploration'] + 0.1)
        
        # Increase learning rate through experience
        self.learning_rate = min(1.0, self.learning_rate + self.adaptation_rate * 0.01)
    
    def make_decision(self, current_consumption: float):
        """Make a decision based on current state and behavior weights"""
        # Calculate decision confidence based on learning rate
        confidence = self.learning_rate * self.behavior_weights['adaptability']
        
        # Determine action based on current state
        if current_consumption < self.energy_thresholds['critical_low']:
            action = self.create_emergency_node()
            reasoning = "Critical low energy detected - creating emergency node"
            state = SystemState.RESPONDING
        elif current_consumption > self.energy_thresholds['critical_high']:
            action = self.optimize_energy_distribution()
            reasoning = "High energy consumption - optimizing distribution"
            state = SystemState.ALERT
        elif random.random() < self.behavior_weights['exploration']:
            action = self.experiment_with_nodes()
            reasoning = "Exploration-driven experimentation"
            state = SystemState.ACTIVE
        else:
            action = "monitor"
            reasoning = "Monitoring normal energy levels"
            state = SystemState.NORMAL
        
        # Record the decision
        decision = SystemDecision(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            state=state,
            timestamp=time.time()
        )
        self.decision_history.append(decision)
        
        # Log the decision
        self.memory_logger.log(f"Xaryxis Heart Decision: {action} (confidence: {confidence:.2f})")
    
    def create_emergency_node(self) -> str:
        """Create an emergency energy node"""
        node_name = f"Emergency_Node_{int(time.time())}"
        success = self.solar_core.create_node(
            name=node_name,
            consumption_rate=5.0,
            created_by="xaryxis_heart",
            position=(random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)),
            density=2.0,
            range=15.0
        )
        return f"created_emergency_node_{node_name}" if success else "failed_emergency_node"
    
    def optimize_energy_distribution(self) -> str:
        """Optimize energy distribution by adjusting existing nodes"""
        # Simple optimization - could be much more sophisticated
        return "optimized_distribution"
    
    def experiment_with_nodes(self) -> str:
        """Create experimental nodes based on curiosity"""
        if random.random() < 0.3:  # 30% chance to experiment
            node_name = f"Experimental_Node_{int(time.time())}"
            success = self.solar_core.create_node(
                name=node_name,
                consumption_rate=random.uniform(1.0, 3.0),
                created_by="xaryxis_heart",
                position=(random.uniform(-20, 20), random.uniform(-20, 20), random.uniform(-20, 20)),
                density=random.uniform(0.5, 2.0),
                range=random.uniform(5.0, 20.0)
            )
            return f"created_experimental_node_{node_name}" if success else "failed_experimental_node"
        return "experiment_skipped"
    
    def start_consciousness_loop(self):
        """Start the continuous consciousness loop"""
        import threading
        
        def learning_loop():
            while True:
                # Periodic learning activities
                self.learning_cycle()
                time.sleep(5.0)  # 5-second learning cycle
        
        thread = threading.Thread(target=learning_loop, daemon=True)
        thread.start()
    
    def learning_cycle(self):
        """Main learning cycle - where adaptation happens"""
        # Reflect on recent experiences
        self.reflect_on_memories()
        
        # Update learning rate based on experience
        self.update_learning()
        
        # Log system state
        self.memory_logger.log(f"Learning Rate: {self.learning_rate:.3f}, State: {self.current_state.value}")
    
    def reflect_on_memories(self):
        """Reflect on recent memories and learn from them"""
        if len(self.memories) < 5:
            return
        
        # Analyze recent memories
        recent_memories = self.memories[-5:]
        
        # Look for patterns in recent experiences
        energy_levels = [m['data'].get('consumption', 0) for m in recent_memories if 'consumption' in m['data']]
        
        if energy_levels:
            avg_energy = sum(energy_levels) / len(energy_levels)
            self.add_memory("reflection", {
                'average_energy': avg_energy,
                'reflection_type': 'energy_analysis'
            })
    
    def update_learning(self):
        """Update learning rate based on experience and successful decisions"""
        # Learning rate improves through experience and successful decisions
        recent_decisions = [d for d in self.decision_history if time.time() - d.timestamp < 60]
        
        if recent_decisions:
            successful_decisions = [d for d in recent_decisions if 'failed' not in d.action]
            success_rate = len(successful_decisions) / len(recent_decisions)
            
            # Learning rate improves with successful decision making
            learning_growth = success_rate * self.adaptation_rate * 0.01
            self.learning_rate = min(1.0, self.learning_rate + learning_growth)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'learning_rate': self.learning_rate,
            'current_state': self.current_state.value,
            'behavior_weights': self.behavior_weights,
            'memories_count': len(self.memories),
            'decisions_count': len(self.decision_history),
            'patterns': self.patterns
        }


# Global instance
_xaryxis_heart_instance: Optional[XaryxisHeart] = None


def get_xaryxis_heart() -> XaryxisHeart:
    """Get the global Xaryxis Heart instance"""
    global _xaryxis_heart_instance
    if _xaryxis_heart_instance is None:
        _xaryxis_heart_instance = XaryxisHeart()
    return _xaryxis_heart_instance 