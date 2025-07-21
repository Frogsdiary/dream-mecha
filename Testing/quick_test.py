"""
Quick test to demonstrate Xaryxis Heart learning system
"""

import time
from core.managers.solar_core_manager import get_solar_core
from core.ai.xaryxis_heart import get_xaryxis_heart


def quick_demo():
    print("🧠 Xaryxis Heart - Learning System Demo")
    print("=" * 50)
    
    # Get systems
    solar_core = get_solar_core()
    xaryxis_heart = get_xaryxis_heart()
    
    # Show initial state
    print("\n📊 Initial State:")
    status = xaryxis_heart.get_system_status()
    print(f"   Learning Rate: {status['learning_rate']:.3f}")
    print(f"   Behavior Weights: {status['behavior_weights']}")
    
    # Create some energy nodes
    print("\n⚡ Creating energy nodes...")
    solar_core.create_node("Test Node 1", 5.0, "demo", (0, 0, 0), 1.0, 10.0)
    solar_core.create_node("Test Node 2", 3.0, "demo", (5, 0, 0), 1.5, 8.0)
    
    # Let it learn for 10 seconds
    print("\n🔄 Learning for 10 seconds...")
    print("   Time | Learning Rate | State | Energy | Decisions")
    print("   " + "-" * 50)
    
    start_time = time.time()
    while time.time() - start_time < 10:
        elapsed = time.time() - start_time
        status = xaryxis_heart.get_system_status()
        solar_status = solar_core.get_energy_status()
        
        print(f"   {elapsed:4.1f}s | {status['learning_rate']:11.3f} | {status['current_state']:6} | {solar_status['current_consumption']:6.1f} | {status['decisions_count']}")
        
        time.sleep(1)
    
    # Show final results
    print("\n📈 Learning Results:")
    final_status = xaryxis_heart.get_system_status()
    print(f"   Final Learning Rate: {final_status['learning_rate']:.3f}")
    print(f"   Total Decisions: {final_status['decisions_count']}")
    print(f"   Patterns Detected: {final_status['patterns']}")
    print(f"   Memories Stored: {final_status['memories_count']}")
    
    # Test decision making
    print("\n🎯 Testing Decision Making:")
    print("   Creating high energy situation...")
    solar_core.create_node("High Load", 20.0, "test", (0, 0, 0), 1.0, 5.0)
    
    time.sleep(3)
    
    # Show recent decisions
    recent_logs = xaryxis_heart.memory_logger.get_recent_logs(3)
    print("   Recent decisions:")
    for log in recent_logs:
        print(f"     {log['message']}")
    
    print("\n✅ Demo Complete!")
    print("\nKey Learning Behaviors Demonstrated:")
    print("  • Pattern recognition from energy data")
    print("  • Adaptive decision making")
    print("  • Memory-based learning")
    print("  • Behavioral weight adjustment")


if __name__ == "__main__":
    quick_demo() 