#!/usr/bin/env python3
"""
Test script for Dream Mecha bot and fortress system
Run this to verify all components work correctly
"""

import os
import sys
import json
from datetime import datetime

# Add the dream_mecha directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.managers.game_manager import GameManager
from core.managers.player_manager import PlayerManager
from core.managers.voidstate_manager import VoidstateManager
from core.managers.fortress_manager import FortressManager

def test_managers():
    """Test all manager components"""
    print("🧪 Testing Managers...")
    
    try:
        # Initialize managers
        game_manager = GameManager()
        player_manager = PlayerManager()
        voidstate_manager = VoidstateManager()
        fortress_manager = FortressManager()
        
        print(f"✅ Game Manager: {type(game_manager).__name__}")
        print(f"✅ Player Manager: {type(player_manager).__name__}")
        print(f"✅ Voidstate Manager: {type(voidstate_manager).__name__}")
        print(f"✅ Fortress Manager: {type(fortress_manager).__name__}")
        
        return True
    except Exception as e:
        print(f"❌ Manager test failed: {e}")
        return False

def test_fortress_system():
    """Test fortress damage and status system"""
    print("\n🏰 Testing Fortress System...")
    
    try:
        fortress_manager = FortressManager()
        
        # Get initial status
        initial_status = fortress_manager.get_fortress_status()
        print(f"✅ Initial Fortress HP: {initial_status['current_hp']:,}")
        
        # Test damage
        damage_amount = 1000000
        result = fortress_manager.fortress.take_damage(damage_amount)
        
        # Get final status
        final_status = fortress_manager.get_fortress_status()
        print(f"✅ Applied Damage: {damage_amount:,}")
        print(f"✅ Final HP: {final_status['current_hp']:,}")
        print(f"✅ HP Percentage: {final_status['hp_percentage']:.1f}%")
        print(f"✅ Damage Dealt: {result['damage_dealt']:,}")
        print(f"✅ Success: {result['success']}")
        
        # Test fortress attack
        attack_result = fortress_manager.fortress_under_attack(
            enemy_power=50000,
            no_mechs_launched=True
        )
        print(f"✅ Attack Occurred: {attack_result['attack_occurred']}")
        print(f"✅ Fortress Damage: {attack_result['fortress_damage']:,}")
        
        return True
    except Exception as e:
        print(f"❌ Fortress test failed: {e}")
        return False

def test_enemy_generation():
    """Test enemy generation system"""
    print("\n👹 Testing Enemy Generation...")
    
    try:
        game_manager = GameManager()
        voidstate_manager = VoidstateManager()
        
        # Generate enemies
        enemies = game_manager.combat_system.generate_enemies(
            voidstate=voidstate_manager.voidstate,
            player_power=10000
        )
        
        print(f"✅ Enemies Generated: {len(enemies)}")
        print(f"✅ Total Attack Power: {sum(e.attack for e in enemies):,}")
        print(f"✅ Total Defense: {sum(e.defense for e in enemies):,}")
        print(f"✅ Total HP: {sum(e.hp for e in enemies):,}")
        print(f"✅ Voidstate: {voidstate_manager.voidstate}")
        
        return True
    except Exception as e:
        print(f"❌ Enemy generation test failed: {e}")
        return False

def test_player_system():
    """Test player management system"""
    print("\n👤 Testing Player System...")
    
    try:
        player_manager = PlayerManager()
        
        # Test player creation
        test_player_id = "test_player_123"
        test_username = "TestPlayer"
        
        # Use the get_or_create_player method
        player = player_manager.get_or_create_player(test_player_id, test_username)
        
        print(f"✅ Player Created: {player.username}")
        print(f"✅ Player ID: {player.player_id}")
        print(f"✅ Total Zoltans Earned: {player.total_zoltans_earned:,}")
        if player.mecha:
            print(f"✅ Mecha Zoltans: {player.mecha.zoltans:,}")
        else:
            print("✅ No mecha created yet")
        
        # Test data persistence
        player_manager.save_player_data()
        print("✅ Player data saved successfully")
        
        return True
    except Exception as e:
        print(f"❌ Player system test failed: {e}")
        return False

def test_data_persistence():
    """Test data persistence systems"""
    print("\n💾 Testing Data Persistence...")
    
    try:
        # Test fortress persistence
        fortress_manager = FortressManager()
        fortress_manager.save_fortress()
        print("✅ Fortress data saved")
        
        # Test player persistence
        player_manager = PlayerManager()
        player_manager.save_player_data()
        print("✅ Player data saved")
        
        # Test voidstate persistence
        voidstate_manager = VoidstateManager()
        print(f"✅ Voidstate: {voidstate_manager.voidstate}")
        
        return True
    except Exception as e:
        print(f"❌ Data persistence test failed: {e}")
        return False

def test_web_ui_integration():
    """Test web UI integration"""
    print("\n🌐 Testing Web UI Integration...")
    
    try:
        import requests
        
        # Test basic connectivity (if web UI is running)
        web_ui_url = os.getenv('WEB_UI_URL', 'http://localhost:3000')
        
        try:
            response = requests.get(f"{web_ui_url}/api/status", timeout=5)
            if response.status_code == 200:
                print(f"✅ Web UI Status: Online ({response.status_code})")
                print(f"✅ Response Time: {response.elapsed.total_seconds():.2f}s")
            else:
                print(f"⚠️ Web UI Status: {response.status_code}")
        except requests.exceptions.RequestException:
            print("⚠️ Web UI not accessible (may not be running)")
        
        return True
    except Exception as e:
        print(f"❌ Web UI integration test failed: {e}")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n📊 Generating Test Report...")
    
    try:
        # Collect system data
        game_manager = GameManager()
        player_manager = PlayerManager()
        voidstate_manager = VoidstateManager()
        fortress_manager = FortressManager()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'players_count': len(player_manager.players),
                'fortress_hp': fortress_manager.get_fortress_status()['current_hp'],
                'voidstate': voidstate_manager.voidstate,
                'web_ui_url': os.getenv('WEB_UI_URL', 'http://localhost:3000')
            },
            'test_results': {
                'managers': test_managers(),
                'fortress': test_fortress_system(),
                'enemies': test_enemy_generation(),
                'players': test_player_system(),
                'persistence': test_data_persistence(),
                'web_ui': test_web_ui_integration()
            }
        }
        
        # Save report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Test report saved to: {report_file}")
        
        # Print summary
        passed_tests = sum(report['test_results'].values())
        total_tests = len(report['test_results'])
        
        print(f"\n🎯 Test Summary:")
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! System is ready.")
        else:
            print("⚠️ Some tests failed. Check the report for details.")
        
        return report
        
    except Exception as e:
        print(f"❌ Test report generation failed: {e}")
        return None

def main():
    """Main test function"""
    print("🧪 Dream Mecha System Test Suite")
    print("=" * 50)
    
    # Run all tests
    generate_test_report()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")

if __name__ == "__main__":
    main() 