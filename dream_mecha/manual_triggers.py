#!/usr/bin/env python3
"""
Manual trigger script for testing void attacks and combat
"""

import sys
import os
from datetime import datetime

# Add the dream_mecha directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.managers.game_manager import GameManager
from core.managers.fortress_manager import FortressManager
from core.managers.voidstate_manager import VoidstateManager
from core.managers.player_manager import PlayerManager

def trigger_void_attack():
    """Manually trigger a void attack on the fortress"""
    print("🌌 Triggering Void Attack...")
    
    try:
        fortress_manager = FortressManager()
        
        # Get initial status
        initial_status = fortress_manager.get_fortress_status()
        print(f"🔴 Initial Fortress HP: {initial_status['current_hp']:,}")
        
        # Trigger attack
        enemy_power = 50000  # Test enemy power
        result = fortress_manager.fortress_under_attack(
            enemy_power=enemy_power,
            no_mechs_launched=True
        )
        
        # Get final status
        final_status = fortress_manager.get_fortress_status()
        
        print(f"⚔️ Enemy Power: {enemy_power:,}")
        print(f"💥 Fortress Damage: {result['fortress_damage']:,}")
        print(f"🟢 Final HP: {final_status['current_hp']:,}")
        print(f"📊 HP Percentage: {final_status['hp_percentage']:.1f}%")
        print(f"✅ Attack Occurred: {result['attack_occurred']}")
        print(f"📝 Message: {result['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Void attack failed: {e}")
        return False

def trigger_combat():
    """Manually trigger combat resolution"""
    print("⚔️ Triggering Combat...")
    
    try:
        game_manager = GameManager()
        voidstate_manager = VoidstateManager()
        
        # Generate enemies
        enemies = game_manager.combat_system.generate_enemies(
            voidstate=voidstate_manager.voidstate,
            player_power=10000
        )
        
        print(f"👹 Enemies Generated: {len(enemies)}")
        print(f"⚔️ Total Attack Power: {sum(e.attack for e in enemies):,}")
        print(f"🛡️ Total Defense: {sum(e.defense for e in enemies):,}")
        print(f"💀 Total HP: {sum(e.hp for e in enemies):,}")
        print(f"🌌 Voidstate: {voidstate_manager.voidstate}")
        
        # Resolve combat
        result = game_manager.resolve_combat()
        print(f"🎯 Combat Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Combat failed: {e}")
        return False

def reset_fortress():
    """Reset fortress to full HP"""
    print("🏰 Resetting Fortress...")
    
    try:
        fortress_manager = FortressManager()
        
        # Reset to full HP
        fortress_manager.fortress.current_hp = fortress_manager.fortress.max_hp
        fortress_manager.fortress.total_damage_taken = 0
        fortress_manager.fortress.days_under_attack = 0
        fortress_manager.fortress.last_attack_date = None
        
        # Save fortress
        fortress_manager.save_fortress()
        
        # Get status
        status = fortress_manager.get_fortress_status()
        print(f"✅ Fortress Reset Complete!")
        print(f"🟢 Current HP: {status['current_hp']:,}")
        print(f"📊 HP Percentage: {status['hp_percentage']:.1f}%")
        print(f"💥 Total Damage: {status['total_damage_taken']:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fortress reset failed: {e}")
        return False

def show_system_status():
    """Show current system status"""
    print("📊 System Status...")
    
    try:
        # Get all managers
        game_manager = GameManager()
        player_manager = PlayerManager()
        voidstate_manager = VoidstateManager()
        fortress_manager = FortressManager()
        
        # Get fortress status
        fortress_status = fortress_manager.get_fortress_status()
        
        print(f"🤖 Players: {len(player_manager.players)}")
        print(f"🏰 Fortress HP: {fortress_status['current_hp']:,}")
        print(f"🌌 Voidstate: {voidstate_manager.voidstate}")
        print(f"📊 HP Percentage: {fortress_status['hp_percentage']:.1f}%")
        print(f"💥 Total Damage: {fortress_status['total_damage_taken']:,}")
        print(f"📅 Days Under Attack: {fortress_status['days_under_attack']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

def main():
    """Main function"""
    print("🎮 Dream Mecha Manual Triggers")
    print("=" * 50)
    
    while True:
        print("\nAvailable Actions:")
        print("1. Trigger Void Attack")
        print("2. Trigger Combat")
        print("3. Reset Fortress")
        print("4. Show System Status")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            trigger_void_attack()
        elif choice == "2":
            trigger_combat()
        elif choice == "3":
            reset_fortress()
        elif choice == "4":
            show_system_status()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main() 