"""
Test script for Xaryxis Reasoning Engine
Demonstrates environmental reasoning and energy management
"""

import time
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.managers.solar_core_manager import get_solar_core
from core.ai.xaryxis_heart import get_xaryxis_heart
from core.reasoning.observer import EnvironmentalObserver
from core.reasoning.analyzer import EnergyContextAnalyzer
from core.reasoning.strategies import EnergyStrategySelector


def test_reasoning_engine():
    """Test the reasoning engine with various energy scenarios"""
    print("🧠 Testing Xaryxis Reasoning Engine")
    print("=" * 50)
    
    # Initialize components
    solar_core = get_solar_core()
    xaryxis_heart = get_xaryxis_heart()
    observer = EnvironmentalObserver(solar_core, xaryxis_heart)
    analyzer = EnergyContextAnalyzer()
    strategy_selector = EnergyStrategySelector()
    
    print("✅ Components initialized")
    
    # Test 1: Normal operation
    print("\n📊 Test 1: Normal Energy Operation")
    print("-" * 30)
    
    # Create some normal nodes
    solar_core.create_node("Life Support", 5.0, "test", (0, 0, 0), 1.0, 10.0)
    solar_core.create_node("Navigation", 3.0, "test", (5, 0, 0), 1.0, 8.0)
    
    status = solar_core.get_energy_status()
    observer.observe_energy_analysis(status, status['nodes'])
    
    system_state = xaryxis_heart.get_system_status()
    context = analyzer.analyze(status, {}, system_state)
    strategy = strategy_selector.select_strategy(context, system_state)
    
    print(f"Consumption: {status['current_consumption']:.1f}")
    print(f"Context Analysis: {context['risk_level']} risk, {context['environmental_stability']['level']} stability")
    print(f"Selected Strategy: {strategy['strategy']['name']}")
    print(f"Confidence: {strategy['confidence']:.1%}")
    print(f"Reasoning: {strategy['reasoning']}")
    
    # Test 2: High consumption scenario
    print("\n📊 Test 2: High Energy Consumption")
    print("-" * 30)
    
    # Create high-consumption nodes
    solar_core.create_node("Heavy Processing", 50.0, "test", (0, 5, 0), 2.0, 15.0)
    solar_core.create_node("Industrial Systems", 30.0, "test", (-5, 0, 0), 1.5, 12.0)
    
    status = solar_core.get_energy_status()
    observer.observe_energy_analysis(status, status['nodes'])
    
    context = analyzer.analyze(status, {}, system_state)
    strategy = strategy_selector.select_strategy(context, system_state)
    
    print(f"Consumption: {status['current_consumption']:.1f}")
    print(f"Context Analysis: {context['risk_level']} risk, {context['environmental_stability']['level']} stability")
    print(f"Selected Strategy: {strategy['strategy']['name']}")
    print(f"Confidence: {strategy['confidence']:.1%}")
    print(f"Reasoning: {strategy['reasoning']}")
    
    # Test 3: Crisis scenario
    print("\n📊 Test 3: Crisis Scenario")
    print("-" * 30)
    
    # Create crisis-level consumption
    solar_core.create_node("Emergency Systems", 100.0, "test", (0, 0, 5), 3.0, 20.0)
    solar_core.create_node("Defense Grid", 80.0, "test", (10, 0, 0), 2.5, 18.0)
    
    status = solar_core.get_energy_status()
    observer.observe_energy_analysis(status, status['nodes'])
    
    context = analyzer.analyze(status, {}, system_state)
    strategy = strategy_selector.select_strategy(context, system_state)
    
    print(f"Consumption: {status['current_consumption']:.1f}")
    print(f"Context Analysis: {context['risk_level']} risk, {context['environmental_stability']['level']} stability")
    print(f"Selected Strategy: {strategy['strategy']['name']}")
    print(f"Confidence: {strategy['confidence']:.1%}")
    print(f"Reasoning: {strategy['reasoning']}")
    
    # Test 4: Node clustering scenario
    print("\n📊 Test 4: Node Clustering Analysis")
    print("-" * 30)
    
    # Create clustered nodes
    solar_core.create_node("Cluster Node 1", 5.0, "test", (1, 1, 1), 1.0, 5.0)
    solar_core.create_node("Cluster Node 2", 5.0, "test", (1.5, 1.5, 1.5), 1.0, 5.0)
    solar_core.create_node("Cluster Node 3", 5.0, "test", (0.5, 0.5, 0.5), 1.0, 5.0)
    
    status = solar_core.get_energy_status()
    observer.observe_energy_analysis(status, status['nodes'])
    
    context = analyzer.analyze(status, {}, system_state)
    strategy = strategy_selector.select_strategy(context, system_state)
    
    print(f"Consumption: {status['current_consumption']:.1f}")
    print(f"Node Clustering: {context['node_clustering']['clustered']}")
    print(f"Distribution Score: {context['node_clustering']['distribution_score']:.2f}")
    print(f"Selected Strategy: {strategy['strategy']['name']}")
    print(f"Confidence: {strategy['confidence']:.1%}")
    
    # Show reasoning traces
    print("\n📊 Reasoning Trace Summary")
    print("-" * 30)
    
    summary = observer.get_trace_summary()
    print(f"Total Traces: {summary['total_traces']}")
    print(f"Average Consumption: {summary['average_consumption']:.1f}")
    print(f"Boost Zones Identified: {summary['boost_zones_identified']}")
    
    print("\nMost Common Reasoning Notes:")
    for note, count in summary['most_common_notes']:
        print(f"  {note}: {count} times")
    
    # Show recent traces
    print("\n📊 Recent Reasoning Traces")
    print("-" * 30)
    
    recent_traces = observer.get_recent_traces(3)
    for i, trace in enumerate(recent_traces, 1):
        print(f"Trace {i}:")
        print(f"  Timestamp: {trace.get('timestamp', '')}")
        print(f"  Consumption: {trace.get('consumption', 0):.1f}")
        print(f"  Active Nodes: {trace.get('nodes_active', 0)}")
        print(f"  Reasoning: {trace.get('reasoning_notes', '')}")
        print()
    
    print("✅ Reasoning engine test completed!")
    print("\n💡 Key Features Demonstrated:")
    print("  • Real-time energy monitoring and analysis")
    print("  • Context-aware strategy selection")
    print("  • Pattern recognition and learning")
    print("  • Crisis detection and response")
    print("  • Node distribution analysis")
    print("  • Reasoning trace logging and analysis")


if __name__ == "__main__":
    test_reasoning_engine() 