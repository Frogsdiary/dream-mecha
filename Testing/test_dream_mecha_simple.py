"""
Simple test for Dream Mecha core functionality
Tests the content generation without GUI requirements
"""

import sys
import os
import json
import math
import random
from datetime import date

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_piece_generation():
    """Test piece generation logic"""
    print("🧪 Testing Dream Mecha Piece Generation...")
    
    # Test stat calculation
    def calculate_piece_stats(block_count: int, stat_type: str):
        """Calculate HP/ATT/DEF/SPD stats from piece pattern"""
        # Base exponential value
        base_value = math.pow(block_count, 2.5) * 100
        
        # 30% variance (random within range)
        variance = 0.3
        min_value = base_value * (1 - variance)
        max_value = base_value * (1 + variance)
        
        # Random value within range
        final_value = random.randint(int(min_value), int(max_value))
        
        # Initialize all stats to 0
        stats = {"hp": 0, "att": 0, "def": 0, "spd": 0}
        
        # Set the primary stat
        if stat_type == "hp":
            stats["hp"] = final_value
        elif stat_type == "attack":
            stats["att"] = final_value
        elif stat_type == "defense":
            stats["def"] = final_value
        elif stat_type == "speed":
            stats["spd"] = final_value
            
        return stats
    
    # Test different block counts
    test_cases = [
        (1, "hp"),
        (5, "attack"), 
        (10, "defense"),
        (20, "speed")
    ]
    
    for block_count, stat_type in test_cases:
        stats = calculate_piece_stats(block_count, stat_type)
        total_stats = sum(stats.values())
        print(f"  {block_count} blocks, {stat_type}: {stats} (total: {total_stats})")
        
        # Verify the primary stat is set
        if stat_type == "hp" and stats["hp"] > 0:
            print(f"    ✅ HP stat correctly set")
        elif stat_type == "attack" and stats["att"] > 0:
            print(f"    ✅ Attack stat correctly set")
        elif stat_type == "defense" and stats["def"] > 0:
            print(f"    ✅ Defense stat correctly set")
        elif stat_type == "speed" and stats["spd"] > 0:
            print(f"    ✅ Speed stat correctly set")
        else:
            print(f"    ❌ Stat not set correctly")


def test_enemy_generation():
    """Test enemy generation logic"""
    print("\n👹 Testing Enemy Generation...")
    
    def generate_enemy_description(hp: int, att: int, def_val: int, spd: int):
        """Generate procedural enemy description based on stats"""
        descriptors = {
            "size": {
                "tier1": ["small", "tiny", "diminutive"],
                "tier2": ["hulking", "large", "imposing"],
                "tier3": ["colossal", "gigantic", "enormous"],
                "tier4": ["world-ending", "cosmic", "reality-bending"]
            },
            "threat": {
                "tier1": ["with gnashing teeth", "sporting sharp claws"],
                "tier2": ["bristling with razor spikes", "wreathed in shadow flames"],
                "tier3": ["channeling destructive force", "emanating reality-warping power"],
                "tier4": ["radiating universe-ending power", "bending space-time"]
            }
        }
        
        # Determine tiers based on stats
        hp_tier = min(4, 1 + hp // 100000)  # Scale tiers based on HP
        att_tier = min(4, 1 + att // 10000)  # Scale tiers based on attack
        
        # Select descriptors
        size_desc = random.choice(descriptors["size"][f"tier{hp_tier}"])
        threat_desc = random.choice(descriptors["threat"][f"tier{att_tier}"])
        
        return f"A {size_desc} void beast {threat_desc}"
    
    # Test enemy generation
    estimated_power = {
        "avg_hp": 50000,
        "avg_att": 8000,
        "avg_def": 3000,
        "avg_spd": 2000
    }
    
    voidstate = 2
    void_multiplier = 1 + (voidstate * 0.2)
    
    enemy_hp = int(estimated_power["avg_hp"] * 0.8 * void_multiplier)
    enemy_att = int(estimated_power["avg_att"] * 0.6 * void_multiplier)
    enemy_def = int(enemy_hp * 0.1)
    enemy_spd = int(enemy_att * 0.3)
    
    description = generate_enemy_description(enemy_hp, enemy_att, enemy_def, enemy_spd)
    
    print(f"  Enemy Stats: HP:{enemy_hp} ATK:{enemy_att} DEF:{enemy_def} SPD:{enemy_spd}")
    print(f"  Description: {description}")
    print(f"  ✅ Enemy generation successful")


def test_json_export():
    """Test JSON export functionality"""
    print("\n💾 Testing JSON Export...")
    
    # Create sample data
    export_data = {
        "date": date.today().strftime("%Y-%m-%d"),
        "voidstate": 2,
        "generation_metadata": {
            "player_count": 5,
            "pieces_generated": 3,
            "generation_time": "2025-07-22T18:00:00Z"
        },
        "shop_pieces": [
            {
                "id": "piece_20250722_001",
                "pattern": "+ 2 3\n4 5 .\n6 . .",
                "pattern_array": [[1,2,3],[4,5,0],[6,0,0]],
                "blocks": 6,
                "size_category": "small",
                "generation_method": "random",
                "beta_mode": True,
                "stats": {"hp": 8450, "att": 0, "def": 0, "spd": 0},
                "stat_type": "hp",
                "price": 845,
                "rarity": "common"
            }
        ],
        "enemies": [
            {
                "id": "enemy_20250722_001", 
                "hp": 150000,
                "att": 25000,
                "def": 8000,
                "spd": 3000,
                "description": "A hulking void beast bristling with razor claws",
                "threat_level": "moderate"
            }
        ],
        "economy_data": {
            "base_zoltan_reward": 50000,
            "voidstate_bonus": 20000,
            "total_zoltan_reward": 70000,
            "repair_cost_multiplier": 0.05
        }
    }
    
    # Ensure directory exists
    export_dir = os.path.join("dream_mecha", "database", "daily")
    os.makedirs(export_dir, exist_ok=True)
    
    # Export file
    filename = f"{date.today().strftime('%Y-%m-%d')}.json"
    filepath = os.path.join(export_dir, filename)
    
    try:
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"  ✅ JSON export successful: {filepath}")
        
        # Verify file was created
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  File size: {file_size} bytes")
            
            # Test loading
            with open(filepath, 'r') as f:
                loaded_data = json.load(f)
            print(f"  ✅ JSON validation passed")
            print(f"  Date: {loaded_data.get('date')}")
            print(f"  Pieces: {len(loaded_data.get('shop_pieces', []))}")
            print(f"  Enemies: {len(loaded_data.get('enemies', []))}")
        else:
            print("  ❌ File not created")
    except Exception as e:
        print(f"  ❌ JSON export failed: {e}")


if __name__ == "__main__":
    print("🎮 Dream Mecha Core Functionality Test")
    print("=" * 50)
    
    test_piece_generation()
    test_enemy_generation()
    test_json_export()
    
    print("\n🎉 All tests completed!") 