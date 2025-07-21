"""
Energy Context Analyzer - Phase 2 of Xaryxis Reasoning Engine
Understands energy situations and provides context for decision making
"""

from typing import Dict, Any, List


class EnergyContextAnalyzer:
    """Understands what type of energy situation we're dealing with"""
    
    def __init__(self):
        self.crisis_threshold = 200  # Energy consumption threshold for crisis
        self.inefficiency_threshold = 0.7  # Efficiency threshold for optimization
        
    def analyze(self, energy_status: Dict[str, Any], node_patterns: Dict[str, Any], system_state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the current energy context"""
        return {
            'is_crisis': self._detect_crisis(energy_status),
            'is_inefficient': self._detect_inefficiency(energy_status),
            'node_clustering': self._analyze_node_distribution(energy_status.get('nodes', {})),
            'energy_flow_patterns': self._detect_flow_issues(energy_status),
            'environmental_stability': self._assess_stability(energy_status),
            'optimization_opportunities': self._find_optimization_opportunities(energy_status),
            'risk_level': self._assess_risk_level(energy_status, system_state)
        }
    
    def _detect_crisis(self, energy_status: Dict[str, Any]) -> bool:
        """Detect if current situation is a crisis"""
        consumption = energy_status.get('current_consumption', 0)
        return consumption > self.crisis_threshold
    
    def _detect_inefficiency(self, energy_status: Dict[str, Any]) -> bool:
        """Detect if current energy usage is inefficient"""
        nodes = energy_status.get('nodes', {})
        if not nodes:
            return False
        
        # Calculate efficiency based on node utilization
        active_nodes = [n for n in nodes.values() if n.get('is_active', False)]
        total_consumption = energy_status.get('current_consumption', 0)
        
        if not active_nodes:
            return True
        
        # Calculate average consumption per active node
        avg_consumption_per_node = total_consumption / len(active_nodes)
        
        # Check if some nodes are consuming much more than others
        consumption_values = [n.get('consumption_rate', 0) for n in active_nodes]
        if consumption_values:
            max_consumption = max(consumption_values)
            min_consumption = min(consumption_values)
            
            # If there's a huge disparity, it's inefficient
            if max_consumption > 0 and min_consumption > 0:
                efficiency_ratio = min_consumption / max_consumption
                return efficiency_ratio < self.inefficiency_threshold
        
        return False
    
    def _analyze_node_distribution(self, nodes: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how energy nodes are distributed"""
        if not nodes:
            return {'clustered': False, 'distribution_score': 0.0, 'gaps': []}
        
        positions = []
        for node_data in nodes.values():
            if node_data.get('is_active', False):
                pos = node_data.get('position', (0, 0, 0))
                positions.append(pos)
        
        if len(positions) < 2:
            return {'clustered': False, 'distribution_score': 1.0, 'gaps': []}
        
        # Calculate average distance between nodes
        total_distance = 0
        distance_count = 0
        
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dist = self._calculate_distance(positions[i], positions[j])
                total_distance += dist
                distance_count += 1
        
        avg_distance = total_distance / distance_count if distance_count > 0 else 0
        
        # Determine if nodes are clustered (close together) or well-distributed
        clustered = avg_distance < 5.0  # Threshold for clustering
        
        # Calculate distribution score (higher = better distributed)
        distribution_score = min(1.0, avg_distance / 10.0)
        
        # Find gaps in coverage
        gaps = self._find_coverage_gaps(positions)
        
        return {
            'clustered': clustered,
            'distribution_score': distribution_score,
            'average_distance': avg_distance,
            'gaps': gaps
        }
    
    def _detect_flow_issues(self, energy_status: Dict[str, Any]) -> List[str]:
        """Detect issues with energy flow patterns"""
        issues = []
        nodes = energy_status.get('nodes', {})
        
        if not nodes:
            return ["No energy nodes active"]
        
        # Check for energy bottlenecks
        high_consumption_nodes = []
        for name, node_data in nodes.items():
            if node_data.get('is_active', False):
                consumption = node_data.get('consumption_rate', 0)
                if consumption > 15:  # High consumption threshold
                    high_consumption_nodes.append(name)
        
        if len(high_consumption_nodes) > 3:
            issues.append(f"Multiple high-consumption nodes: {', '.join(high_consumption_nodes)}")
        
        # Check for energy waste
        low_efficiency_nodes = []
        for name, node_data in nodes.items():
            if node_data.get('is_active', False):
                density = node_data.get('density', 1.0)
                range_val = node_data.get('range', 10.0)
                efficiency = density * range_val / node_data.get('consumption_rate', 1.0)
                
                if efficiency < 0.5:  # Low efficiency threshold
                    low_efficiency_nodes.append(name)
        
        if low_efficiency_nodes:
            issues.append(f"Inefficient nodes detected: {', '.join(low_efficiency_nodes)}")
        
        return issues
    
    def _assess_stability(self, energy_status: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the stability of the current energy system"""
        consumption = energy_status.get('current_consumption', 0)
        nodes = energy_status.get('nodes', {})
        active_nodes = len([n for n in nodes.values() if n.get('is_active', False)])
        
        # Calculate stability score
        stability_score = 1.0
        
        # Reduce stability for high consumption
        if consumption > 100:
            stability_score -= 0.3
        elif consumption > 50:
            stability_score -= 0.1
        
        # Reduce stability for too few or too many nodes
        if active_nodes < 2:
            stability_score -= 0.4
        elif active_nodes > 15:
            stability_score -= 0.2
        
        stability_score = max(0.0, stability_score)
        
        # Determine stability level
        if stability_score > 0.8:
            level = "stable"
        elif stability_score > 0.5:
            level = "moderate"
        else:
            level = "unstable"
        
        return {
            'score': stability_score,
            'level': level,
            'factors': self._get_stability_factors(energy_status)
        }
    
    def _find_optimization_opportunities(self, energy_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find opportunities to optimize energy usage"""
        opportunities = []
        nodes = energy_status.get('nodes', {})
        
        # Look for underutilized nodes
        for name, node_data in nodes.items():
            if node_data.get('is_active', False):
                consumption = node_data.get('consumption_rate', 0)
                density = node_data.get('density', 1.0)
                range_val = node_data.get('range', 10.0)
                
                # Check if node could be optimized
                potential_boost = density * range_val
                utilization_ratio = consumption / potential_boost if potential_boost > 0 else 0
                
                if utilization_ratio < 0.3:  # Underutilized
                    opportunities.append({
                        'type': 'underutilized_node',
                        'node_name': name,
                        'current_utilization': utilization_ratio,
                        'potential_improvement': 1.0 - utilization_ratio
                    })
        
        # Look for clustering opportunities
        node_distribution = self._analyze_node_distribution(nodes)
        if node_distribution['clustered']:
            opportunities.append({
                'type': 'node_clustering',
                'description': 'Nodes are clustered together - could benefit from redistribution',
                'potential_improvement': 0.2
            })
        
        return opportunities
    
    def _assess_risk_level(self, energy_status: Dict[str, Any], system_state: Dict[str, Any]) -> str:
        """Assess the current risk level"""
        risk_factors = 0
        
        # High consumption risk
        if energy_status.get('current_consumption', 0) > 150:
            risk_factors += 2
        elif energy_status.get('current_consumption', 0) > 100:
            risk_factors += 1
        
        # System state risk
        if system_state.get('current_state') == 'alert':
            risk_factors += 2
        elif system_state.get('learning_rate', 0.5) < 0.3:
            risk_factors += 1
        
        # Node distribution risk
        nodes = energy_status.get('nodes', {})
        active_nodes = len([n for n in nodes.values() if n.get('is_active', False)])
        if active_nodes < 3:
            risk_factors += 1
        
        if risk_factors >= 4:
            return "high"
        elif risk_factors >= 2:
            return "medium"
        else:
            return "low"
    
    def _calculate_distance(self, pos1: tuple, pos2: tuple) -> float:
        """Calculate Euclidean distance between two positions"""
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)**0.5
    
    def _find_coverage_gaps(self, positions: List[tuple]) -> List[tuple]:
        """Find areas with poor energy coverage"""
        # Simple gap detection - areas far from any node
        gaps = []
        
        # Check a grid of points for coverage
        for x in range(-10, 11, 2):
            for y in range(-10, 11, 2):
                for z in range(-10, 11, 2):
                    point = (x, y, z)
                    
                    # Find distance to nearest node
                    min_distance = float('inf')
                    for pos in positions:
                        dist = self._calculate_distance(point, pos)
                        min_distance = min(min_distance, dist)
                    
                    # If too far from any node, it's a gap
                    if min_distance > 8.0:
                        gaps.append(point)
        
        return gaps[:10]  # Limit to 10 gaps
    
    def _get_stability_factors(self, energy_status: Dict[str, Any]) -> List[str]:
        """Get factors affecting stability"""
        factors = []
        consumption = energy_status.get('current_consumption', 0)
        nodes = energy_status.get('nodes', {})
        active_nodes = len([n for n in nodes.values() if n.get('is_active', False)])
        
        if consumption > 100:
            factors.append("High energy consumption")
        if active_nodes < 3:
            factors.append("Insufficient active nodes")
        if active_nodes > 15:
            factors.append("Too many active nodes")
        
        if not factors:
            factors.append("Balanced energy distribution")
        
        return factors 