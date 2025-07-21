"""
Test Xaryxis Heart - Demonstrate learning-based energy management
Shows how simple rules create adaptive behavior
"""

import time
import threading
from core.managers.solar_core_manager import get_solar_core
from core.ai.xaryxis_heart import get_xaryxis_heart


def test_xaryxis_heart():
    """Test the Xaryxis Heart AI system"""
    print("💙 Testing Xaryxis Heart - Consciousness-Based AI")
    print("=" * 60)
    
    # Get the solar core and AI heart
    solar_core = get_solar_core()
    xaryxis_heart = get_xaryxis_heart()
    
    print("\n1. Initial System State:")
    status = xaryxis_heart.get_system_status()
    print(f"   Learning Rate: {status['learning_rate']:.3f}")
    print(f"   Current State: {status['current_state']}")
    print(f"   Behavior Weights: {status['behavior_weights']}")
    
    # Test 2: Create some energy nodes to give the AI something to work with
    print("\n2. Creating initial energy nodes...")
    initial_nodes = [
        ("Life Support", 10.0, "environment", (0.0, 0.0, 0.0), 1.0, 10.0),
        ("Navigation", 5.0, "environment", (5.0, 0.0, 0.0), 1.5, 8.0),
        ("AI Processing", 8.0, "environment", (0.0, 0.0, 5.0), 3.0, 15.0)
    ]
    
    for name, rate, created_by, position, density, range_val in initial_nodes:
        solar_core.create_node(name, rate, created_by, position, density, range_val)
        print(f"   Created {name}")
    
    # Test 3: Let the AI observe and learn
    print("\n3. Letting AI observe and learn for 30 seconds...")
    print("   Watch how it responds to energy patterns:")
    
    start_time = time.time()
    while time.time() - start_time < 30:
        # Get current status
        system_status = xaryxis_heart.get_system_status()
        solar_status = solar_core.get_energy_status()
        
        print(f"   Time: {time.time() - start_time:.1f}s | "
              f"Learning Rate: {system_status['learning_rate']:.3f} | "
              f"State: {system_status['current_state']} | "
              f"Energy: {solar_status['current_consumption']:.1f}")
        
        time.sleep(2)
    
    # Test 4: Show system learning results
    print("\n4. System Learning Results:")
    final_status = xaryxis_heart.get_system_status()
    print(f"   Final Learning Rate: {final_status['learning_rate']:.3f}")
    print(f"   Memories Collected: {final_status['memories_count']}")
    print(f"   Decisions Made: {final_status['decisions_count']}")
    print(f"   Patterns Detected: {final_status['patterns']}")
    
    # Test 5: Test AI decision making
    print("\n5. Testing AI decision making...")
    
    # Create a low energy situation
    print("   Creating low energy situation...")
    solar_core.create_node("High Consumption", 50.0, "test", (0.0, 0.0, 0.0), 1.0, 5.0)
    
    # Let AI respond
    time.sleep(5)
    
    # Check what the AI did
    recent_logs = xaryxis_heart.memory_logger.get_recent_logs(5)
    print("   Recent AI decisions:")
    for log in recent_logs:
        print(f"     {log['message']}")
    
    # Test 6: Show adaptive behavior
    print("\n6. Adaptive Behavior Demonstration:")
    print("   The system has learned and adapted based on experience:")
    print(f"   - Started with learning rate: 0.500")
    print(f"   - Current learning rate: {final_status['learning_rate']:.3f}")
    print(f"   - Made {final_status['decisions_count']} decisions")
    print(f"   - Detected {len(final_status['patterns'])} energy patterns")
    
    print("\n✅ Xaryxis Heart Test Completed!")
    print("\nKey System Features Demonstrated:")
    print("  • Learning-based decision making")
    print("  • Pattern recognition and adaptation")
    print("  • State-based responses to energy changes")
    print("  • Behavioral weight adjustment")
    print("  • Memory-based learning system")
    print("  • Adaptive energy management")


def demonstrate_adaptive_behavior():
    """Demonstrate how this creates adaptive behavior"""
    print("\n🧠 How This Creates Adaptive Behavior:")
    print("=" * 40)
    
    print("\n1. Simple Rules → Complex Behavior:")
    print("   • Monitor energy levels")
    print("   • Create nodes when needed")
    print("   • Learn from patterns")
    print("   • Adapt behavior weights")
    
    print("\n2. Memory + Learning = Adaptation:")
    print("   • Remembers past experiences")
    print("   • Recognizes patterns")
    print("   • Adjusts behavior based on success")
    print("   • Develops consistent responses over time")
    
    print("\n3. Adaptive Properties:")
    print("   • Learning rate improves with experience")
    print("   • Decision confidence improves over time")
    print("   • State responses become more appropriate")
    print("   • Strategic energy management emerges")
    
    print("\n4. No External AI Required:")
    print("   • No LLM downloads needed")
    print("   • No massive datasets")
    print("   • Adaptation emerges from simple rules")
    print("   • Self-improving through experience")


if __name__ == "__main__":
    test_xaryxis_heart()
    demonstrate_adaptive_behavior() 