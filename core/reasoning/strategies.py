"""
Energy Strategy Selector - Phase 2 of Xaryxis Reasoning Engine
Chooses how Xaryxis should manage energy based on context
"""

from typing import Dict, Any, List


class EnergyStrategySelector:
    """Chooses HOW Xaryxis should manage energy based on context"""
    
    def __init__(self):
        self.strategies = {
            'conservation': {
                'name': "Energy Conservation",
                'description': "Reduce energy consumption, optimize existing nodes",
                'priority': 1,
                'conditions': ['high_consumption', 'inefficient_usage'],
                'actions': ['optimize_nodes', 'reduce_consumption', 'monitor_efficiency']
            },
            'expansion': {
                'name': "Strategic Expansion", 
                'description': "Create new energy nodes in strategic locations",
                'priority': 2,
                'conditions': ['low_coverage', 'stable_consumption', 'available_resources'],
                'actions': ['create_nodes', 'strategic_placement', 'monitor_effectiveness']
            },
            'redistribution': {
                'name': "Energy Redistribution",
                'description': "Move energy from low-priority to high-priority areas",
                'priority': 3,
                'conditions': ['node_clustering', 'coverage_gaps', 'efficiency_issues'],
                'actions': ['reposition_nodes', 'balance_distribution', 'optimize_flow']
            },
            'crisis_response': {
                'name': "Crisis Response",
                'description': "Emergency node creation and system shutdown",
                'priority': 0,  # Highest priority
                'conditions': ['crisis_detected', 'high_risk', 'system_instability'],
                'actions': ['emergency_nodes', 'system_shutdown', 'stabilize_environment']
            },
            'maintenance': {
                'name': "System Maintenance",
                'description': "Monitor and maintain current energy distribution",
                'priority': 4,  # Lowest priority
                'conditions': ['stable_system', 'normal_operation', 'no_issues'],
                'actions': ['monitor_status', 'routine_checks', 'maintain_balance']
            }
        }
    
    def select_strategy(self, context_analysis: Dict[str, Any], system_state: Dict[str, Any]) -> Dict[str, Any]:
        """Select the best energy management strategy based on context"""
        applicable_strategies = []
        
        # Check each strategy against current conditions
        for strategy_id, strategy in self.strategies.items():
            if self._is_strategy_applicable(strategy, context_analysis, system_state):
                applicable_strategies.append((strategy_id, strategy))
        
        if not applicable_strategies:
            # Default to maintenance if no strategies are applicable
            return {
                'strategy_id': 'maintenance',
                'strategy': self.strategies['maintenance'],
                'confidence': 0.5,
                'reasoning': "No specific conditions detected, defaulting to maintenance mode"
            }
        
        # Sort by priority (lower number = higher priority)
        applicable_strategies.sort(key=lambda x: x[1]['priority'])
        
        # Select the highest priority strategy
        selected_id, selected_strategy = applicable_strategies[0]
        
        # Calculate confidence based on how well conditions match
        confidence = self._calculate_confidence(selected_strategy, context_analysis, system_state)
        
        # Generate reasoning for the selection
        reasoning = self._generate_reasoning(selected_strategy, context_analysis, system_state)
        
        return {
            'strategy_id': selected_id,
            'strategy': selected_strategy,
            'confidence': confidence,
            'reasoning': reasoning,
            'alternative_strategies': [s[0] for s in applicable_strategies[1:3]]  # Top 3 alternatives
        }
    
    def _is_strategy_applicable(self, strategy: Dict[str, Any], context: Dict[str, Any], system_state: Dict[str, Any]) -> bool:
        """Check if a strategy is applicable given the current context"""
        conditions = strategy.get('conditions', [])
        
        for condition in conditions:
            if not self._check_condition(condition, context, system_state):
                return False
        
        return True
    
    def _check_condition(self, condition: str, context: Dict[str, Any], system_state: Dict[str, Any]) -> bool:
        """Check if a specific condition is met"""
        if condition == 'high_consumption':
            return context.get('is_crisis', False) or context.get('environmental_stability', {}).get('score', 1.0) < 0.7
        
        elif condition == 'inefficient_usage':
            return context.get('is_inefficient', False)
        
        elif condition == 'low_coverage':
            node_dist = context.get('node_clustering', {})
            return node_dist.get('distribution_score', 1.0) < 0.5 or len(node_dist.get('gaps', [])) > 5
        
        elif condition == 'stable_consumption':
            return not context.get('is_crisis', False) and context.get('environmental_stability', {}).get('level') == 'stable'
        
        elif condition == 'available_resources':
            # Assume resources are available if system is not in crisis
            return not context.get('is_crisis', False)
        
        elif condition == 'node_clustering':
            return context.get('node_clustering', {}).get('clustered', False)
        
        elif condition == 'coverage_gaps':
            return len(context.get('node_clustering', {}).get('gaps', [])) > 0
        
        elif condition == 'efficiency_issues':
            return len(context.get('energy_flow_patterns', [])) > 0
        
        elif condition == 'crisis_detected':
            return context.get('is_crisis', False) or context.get('risk_level') == 'high'
        
        elif condition == 'high_risk':
            return context.get('risk_level') in ['high', 'medium']
        
        elif condition == 'system_instability':
            return context.get('environmental_stability', {}).get('level') == 'unstable'
        
        elif condition == 'stable_system':
            return context.get('environmental_stability', {}).get('level') == 'stable'
        
        elif condition == 'normal_operation':
            return not context.get('is_crisis', False) and context.get('risk_level') == 'low'
        
        elif condition == 'no_issues':
            return len(context.get('energy_flow_patterns', [])) == 0 and not context.get('is_inefficient', False)
        
        return False
    
    def _calculate_confidence(self, strategy: Dict[str, Any], context: Dict[str, Any], system_state: Dict[str, Any]) -> float:
        """Calculate confidence level for a strategy based on how well conditions match"""
        conditions = strategy.get('conditions', [])
        matched_conditions = 0
        
        for condition in conditions:
            if self._check_condition(condition, context, system_state):
                matched_conditions += 1
        
        # Base confidence on percentage of conditions met
        base_confidence = matched_conditions / len(conditions) if conditions else 0.5
        
        # Adjust based on system state
        learning_rate = system_state.get('learning_rate', 0.5)
        confidence = base_confidence * (0.5 + learning_rate * 0.5)
        
        return min(1.0, max(0.0, confidence))
    
    def _generate_reasoning(self, strategy: Dict[str, Any], context: Dict[str, Any], system_state: Dict[str, Any]) -> str:
        """Generate reasoning explanation for strategy selection"""
        reasoning_parts = []
        
        # Add primary reasoning based on strategy type
        if strategy['name'] == "Crisis Response":
            if context.get('is_crisis', False):
                reasoning_parts.append("Crisis detected - immediate response required")
            if context.get('risk_level') == 'high':
                reasoning_parts.append("High risk level requires emergency measures")
        
        elif strategy['name'] == "Energy Conservation":
            if context.get('is_inefficient', False):
                reasoning_parts.append("Inefficient energy usage detected")
            if context.get('environmental_stability', {}).get('score', 1.0) < 0.7:
                reasoning_parts.append("System stability below optimal levels")
        
        elif strategy['name'] == "Strategic Expansion":
            node_dist = context.get('node_clustering', {})
            if node_dist.get('distribution_score', 1.0) < 0.5:
                reasoning_parts.append("Poor node distribution detected")
            if len(node_dist.get('gaps', [])) > 5:
                reasoning_parts.append("Multiple coverage gaps identified")
        
        elif strategy['name'] == "Energy Redistribution":
            if context.get('node_clustering', {}).get('clustered', False):
                reasoning_parts.append("Nodes are clustered - redistribution needed")
            if len(context.get('energy_flow_patterns', [])) > 0:
                reasoning_parts.append("Energy flow issues detected")
        
        elif strategy['name'] == "System Maintenance":
            reasoning_parts.append("System operating normally - maintenance mode")
        
        # Add system state context
        learning_rate = system_state.get('learning_rate', 0.5)
        if learning_rate > 0.7:
            reasoning_parts.append("High learning rate enables advanced strategies")
        elif learning_rate < 0.3:
            reasoning_parts.append("Low learning rate - using conservative approach")
        
        return "; ".join(reasoning_parts) if reasoning_parts else "Strategy selected based on current conditions"
    
    def get_strategy_details(self, strategy_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific strategy"""
        if strategy_id not in self.strategies:
            return {}
        
        strategy = self.strategies[strategy_id]
        return {
            'id': strategy_id,
            'name': strategy['name'],
            'description': strategy['description'],
            'priority': strategy['priority'],
            'conditions': strategy['conditions'],
            'actions': strategy['actions'],
            'estimated_effectiveness': self._estimate_effectiveness(strategy_id)
        }
    
    def _estimate_effectiveness(self, strategy_id: str) -> Dict[str, float]:
        """Estimate the effectiveness of a strategy"""
        effectiveness_map = {
            'crisis_response': {'immediate': 0.9, 'long_term': 0.7},
            'conservation': {'immediate': 0.6, 'long_term': 0.8},
            'expansion': {'immediate': 0.4, 'long_term': 0.9},
            'redistribution': {'immediate': 0.7, 'long_term': 0.8},
            'maintenance': {'immediate': 0.8, 'long_term': 0.9}
        }
        
        return effectiveness_map.get(strategy_id, {'immediate': 0.5, 'long_term': 0.5})
    
    def get_all_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Get all available strategies"""
        return self.strategies.copy() 