"""
Test Learning Limits - Explore what happens when the system reaches maximum learning
"""

import time
import threading
from core.managers.solar_core_manager import get_solar_core
from core.ai.xaryxis_heart import get_xaryxis_heart


def test_learning_limits():
    print("🧠 Testing Learning Limits - Maximum Potential")
    print("=" * 60)
    
    # Get systems
    solar_core = get_solar_core()
    xaryxis_heart = get_xaryxis_heart()
    
    print("\n📊 Initial State:")
    status = xaryxis_heart.get_system_status()
    print(f"   Learning Rate: {status['learning_rate']:.3f}")
    print(f"   Behavior Weights: {status['behavior_weights']}")
    
    # Create optimal learning conditions
    print("\n⚡ Creating optimal learning environment...")
    
    # Create varied energy patterns to maximize learning
    test_scenarios = [
        # Low energy scenario
        ("Low Energy Test", 2.0, "test", (0, 0, 0), 1.0, 5.0),
        # High energy scenario  
        ("High Energy Test", 50.0, "test", (5, 0, 0), 2.0, 10.0),
        # Normal energy scenario
        ("Normal Energy Test", 15.0, "test", (0, 5, 0), 1.5, 8.0),
    ]
    
    for name, rate, created_by, position, density, range_val in test_scenarios:
        solar_core.create_node(name, rate, created_by, position, density, range_val)
    
    # Monitor learning progress over extended time
    print("\n🔄 Extended Learning Test (60 seconds)...")
    print("   Time | Learning Rate | Decisions | Success Rate | State")
    print("   " + "-" * 60)
    
    start_time = time.time()
    learning_history = []
    
    while time.time() - start_time < 60:
        elapsed = time.time() - start_time
        status = xaryxis_heart.get_system_status()
        
        # Calculate success rate from recent decisions
        recent_decisions = [d for d in status['decision_history'] if time.time() - d.timestamp < 10]
        if recent_decisions:
            successful = [d for d in recent_decisions if 'failed' not in d.action]
            success_rate = len(successful) / len(recent_decisions)
        else:
            success_rate = 0.0
        
        learning_history.append({
            'time': elapsed,
            'learning_rate': status['learning_rate'],
            'decisions': status['decisions_count'],
            'success_rate': success_rate
        })
        
        print(f"   {elapsed:4.1f}s | {status['learning_rate']:11.3f} | {status['decisions_count']:9} | {success_rate:10.2f} | {status['current_state']}")
        
        time.sleep(2)
    
    # Analyze learning progression
    print("\n📈 Learning Progression Analysis:")
    
    # Check if learning rate plateaued
    early_rate = learning_history[5]['learning_rate']  # After 10 seconds
    mid_rate = learning_history[15]['learning_rate']   # After 30 seconds  
    final_rate = learning_history[-1]['learning_rate'] # After 60 seconds
    
    print(f"   Learning Rate at 10s:  {early_rate:.3f}")
    print(f"   Learning Rate at 30s:  {mid_rate:.3f}")
    print(f"   Learning Rate at 60s:  {final_rate:.3f}")
    
    # Calculate learning velocity
    early_velocity = (mid_rate - early_rate) / 20  # per second
    late_velocity = (final_rate - mid_rate) / 30   # per second
    
    print(f"   Early Learning Velocity:  {early_velocity:.5f}/sec")
    print(f"   Late Learning Velocity:   {late_velocity:.5f}/sec")
    
    # Determine if learning plateaued
    if late_velocity < early_velocity * 0.1:  # Less than 10% of early velocity
        print("   🎯 RESULT: Learning has plateaued!")
        print("   The system has reached its learning potential.")
    else:
        print("   🔄 RESULT: Learning is still active!")
        print("   The system continues to improve.")
    
    # Check for maximum learning rate
    max_possible_rate = 1.0  # From the code: min(1.0, learning_rate + growth)
    print(f"\n🎯 Maximum Possible Learning Rate: {max_possible_rate:.3f}")
    print(f"   Current Learning Rate: {final_rate:.3f}")
    print(f"   Remaining Potential: {max_possible_rate - final_rate:.3f}")
    
    if final_rate >= 0.99:
        print("   🏆 ACHIEVEMENT: Near maximum learning potential!")
    elif final_rate >= 0.8:
        print("   🥇 STATUS: High learning potential achieved!")
    elif final_rate >= 0.6:
        print("   🥈 STATUS: Moderate learning potential achieved!")
    else:
        print("   🥉 STATUS: Still developing learning potential!")
    
    # Test decision quality at peak learning
    print("\n🧪 Testing Decision Quality at Peak Learning:")
    
    # Create a challenging scenario
    print("   Creating challenging energy scenario...")
    solar_core.create_node("Challenge Test", 100.0, "challenge", (0, 0, 0), 3.0, 15.0)
    
    time.sleep(5)
    
    # Analyze recent decisions
    recent_logs = xaryxis_heart.memory_logger.get_recent_logs(10)
    print("   Recent high-confidence decisions:")
    
    high_confidence_decisions = []
    for log in recent_logs:
        if "confidence:" in log['message']:
            try:
                confidence = float(log['message'].split("confidence: ")[1].split(")")[0])
                if confidence > 0.4:  # High confidence threshold
                    high_confidence_decisions.append(log['message'])
            except:
                pass
    
    for decision in high_confidence_decisions[-5:]:  # Show last 5 high-confidence decisions
        print(f"     {decision}")
    
    print(f"\n   High-confidence decisions: {len(high_confidence_decisions)}")
    
    # Final assessment
    print("\n🎯 Final Assessment:")
    print(f"   Learning Rate: {final_rate:.3f}/1.0 ({final_rate*100:.1f}% of maximum)")
    print(f"   Total Decisions: {status['decisions_count']}")
    print(f"   Patterns Learned: {len(status['patterns'])}")
    print(f"   Memories Stored: {status['memories_count']}")
    
    if final_rate >= 0.95:
        print("   🏆 CONCLUSION: System has reached near-fullest potential!")
        print("   Further improvements will be minimal.")
    elif final_rate >= 0.8:
        print("   🥇 CONCLUSION: System has reached high potential!")
        print("   Still room for improvement but diminishing returns.")
    else:
        print("   🔄 CONCLUSION: System still has significant learning potential!")
        print("   Continued operation will yield improvements.")


def analyze_learning_mechanics():
    """Explain the learning mechanics and limits"""
    print("\n🔬 Learning Mechanics Analysis:")
    print("=" * 40)
    
    print("\n1. Learning Rate Formula:")
    print("   learning_rate = min(1.0, learning_rate + success_rate * 0.01)")
    print("   - Starts at 0.5")
    print("   - Grows based on successful decisions")
    print("   - Capped at 1.0 (100%)")
    
    print("\n2. Success Rate Calculation:")
    print("   success_rate = successful_decisions / total_recent_decisions")
    print("   - Based on last 60 seconds of decisions")
    print("   - 'failed' in action name = unsuccessful")
    print("   - Higher success rate = faster learning")
    
    print("\n3. Learning Plateaus:")
    print("   - Diminishing returns as learning rate approaches 1.0")
    print("   - Success rate may decrease as system becomes more conservative")
    print("   - Pattern recognition becomes more refined but less frequent")
    
    print("\n4. Maximum Potential Factors:")
    print("   - Learning rate cap: 1.0 (100%)")
    print("   - Behavior weight limits: 1.0 each")
    print("   - Memory capacity: 100 recent memories")
    print("   - Decision confidence: Limited by learning rate")
    
    print("\n5. What 'Fullest Potential' Means:")
    print("   - Learning rate at 1.0")
    print("   - Optimal behavior weights for energy patterns")
    print("   - Maximum decision confidence")
    print("   - Stable, predictable responses")


if __name__ == "__main__":
    test_learning_limits()
    analyze_learning_mechanics() 