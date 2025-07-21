"""
Test script for Solar Core System
Demonstrates energy distribution and shut-off mechanics
"""

import time
import threading
from core.managers.solar_core_manager import get_solar_core


def test_solar_core():
    """Test the solar core system"""
    print("🌞 Testing Solar Core System for Silver Void")
    print("=" * 50)
    
    # Get the solar core instance
    solar_core = get_solar_core()
    
    # Test 1: Basic functionality
    print("\n1. Testing basic energy generation...")
    time.sleep(2)
    status = solar_core.get_energy_status()
    print(f"   Core active: {status['is_active']}")
    print(f"   Energy generated: {status['total_generated']:.1f} units")
    print(f"   Current consumption: {status['current_consumption']:.1f} units/sec")
    
    # Test 2: Create energy nodes
    print("\n2. Creating energy nodes...")
    nodes = [
        ("Life Support", 10.0, "environment", (0.0, 0.0, 0.0), 1.0, 10.0),
        ("Navigation Systems", 5.0, "environment", (5.0, 0.0, 0.0), 1.5, 8.0),
        ("Environmental Controls", 3.0, "environment", (0.0, 5.0, 0.0), 2.0, 12.0),
        ("AI Processing", 8.0, "environment", (0.0, 0.0, 5.0), 3.0, 15.0)
    ]
    
    for name, rate, created_by, position, density, range_val in nodes:
        success = solar_core.create_node(name, rate, created_by, position, density, range_val)
        print(f"   Created {name}: {success}")
    
    # Test 3: Monitor energy consumption
    print("\n3. Monitoring energy consumption for 5 seconds...")
    start_time = time.time()
    while time.time() - start_time < 5:
        status = solar_core.get_energy_status()
        print(f"   Consumption: {status['current_consumption']:.1f} units/sec", end='\r')
        time.sleep(0.5)
    print()
    
    # Test 4: Test shut-off mechanism
    print("\n4. Testing shut-off mechanism...")
    print("   Attempting shut-off from different distances:")
    
    distances = [10.0, 3.0, 0.5]  # Far, close, very close
    for distance in distances:
        result = solar_core.attempt_shut_off(distance)
        print(f"   Distance {distance}: {result['message']}")
        if result['damage_taken'] > 0:
            print(f"     Damage taken: {result['damage_taken']}")
    
    # Test 5: Restart core
    print("\n5. Restarting solar core...")
    if solar_core.restart_core():
        print("   Core restarted successfully!")
    
    # Test 6: Real-time monitoring callback
    print("\n6. Testing real-time monitoring...")
    
    def monitoring_callback(status):
        print(f"   📊 Update: {status['current_consumption']:.1f} units/sec consumed")
    
    solar_core.add_monitoring_callback(monitoring_callback)
    time.sleep(3)
    solar_core.remove_monitoring_callback(monitoring_callback)
    
    # Test 7: Energy boost calculation
    print("\n7. Testing energy boost calculation...")
    test_positions = [
        ((0.0, 0.0, 0.0), "Center of Life Support"),
        ((5.0, 0.0, 0.0), "Navigation Systems"),
        ((0.0, 5.0, 0.0), "Environmental Controls"),
        ((0.0, 0.0, 5.0), "AI Processing"),
        ((2.5, 2.5, 2.5), "Between multiple nodes"),
        ((20.0, 20.0, 20.0), "Far from all nodes")
    ]
    
    for position, description in test_positions:
        boost = solar_core.calculate_energy_boost(position)
        print(f"   {description}: {boost:.2f}x energy boost")
    
    print("\n✅ Solar Core System test completed!")
    print("\nKey Features Demonstrated:")
    print("  • Infinite energy generation")
    print("  • Even energy distribution")
    print("  • Real-time consumption monitoring")
    print("  • Deadly shut-off mechanism")
    print("  • Node creation system")
    print("  • Energy boost based on node density")
    print("  • Thread-safe operation")


if __name__ == "__main__":
    test_solar_core() 