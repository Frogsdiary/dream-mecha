"""
Test script for Dream Mecha integration
Tests the content generation and JSON export functionality
"""

import sys
import os
import json
from datetime import date

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockmaker.blockmaker_window import DreamMechaIntegration


def test_dream_mecha_integration():
    """Test the Dream Mecha integration functionality"""
    print("🧪 Testing Dream Mecha Integration...")
    
    # Test daily content generation
    print("\n📦 Testing daily content generation...")
    
    # Create integration instance
    integration = DreamMechaIntegration()
    
    # Set test parameters
    integration.player_count_spinbox.setValue(5)
    integration.voidstate_spinbox.setValue(2)
    integration.date_edit.setDate(date.today())
    
    # Generate content
    integration.generate_daily_content()
    
    if integration.generated_pieces:
        print(f"✅ Generated {len(integration.generated_pieces)} pieces")
        
        # Show first piece details
        first_piece = integration.generated_pieces[0]
        print(f"  First piece: {first_piece['id']}")
        print(f"  Blocks: {first_piece['blocks']}")
        print(f"  Stats: {first_piece['stats']}")
        print(f"  Price: {first_piece['price']} Zoltans")
    else:
        print("❌ No pieces generated")
        
    if integration.generated_enemies:
        print(f"✅ Generated {len(integration.generated_enemies)} enemies")
        
        # Show first enemy details
        first_enemy = integration.generated_enemies[0]
        print(f"  First enemy: {first_enemy['id']}")
        print(f"  Stats: HP:{first_enemy['hp']} ATK:{first_enemy['att']} DEF:{first_enemy['def']} SPD:{first_enemy['spd']}")
        print(f"  Description: {first_enemy['description']}")
    else:
        print("❌ No enemies generated")
        
    # Test manual piece generation
    print("\n🔧 Testing manual piece generation...")
    integration.manual_block_count.setValue(8)
    integration.manual_stat_type.setCurrentText("hp")
    integration.generate_manual_piece()
    
    if len(integration.generated_pieces) > 0:
        print("✅ Manual piece generation successful")
        manual_piece = integration.generated_pieces[-1]  # Get the last piece (manual one)
        print(f"  Manual piece: {manual_piece['id']}")
        print(f"  Blocks: {manual_piece['blocks']}")
        print(f"  Stats: {manual_piece['stats']}")
    else:
        print("❌ Manual piece generation failed")
        
    # Test JSON export
    print("\n💾 Testing JSON export...")
    integration.export_to_json()
    
    # Check if file was created
    export_file = f"dream_mecha/database/daily/{date.today().strftime('%Y-%m-%d')}.json"
    if os.path.exists(export_file):
        print(f"✅ JSON export successful: {export_file}")
        
        # Show file size
        file_size = os.path.getsize(export_file)
        print(f"  File size: {file_size} bytes")
        
        # Test JSON loading
        try:
            with open(export_file, 'r') as f:
                json_data = json.load(f)
            print("✅ JSON file is valid")
            print(f"  Date: {json_data.get('date')}")
            print(f"  Voidstate: {json_data.get('voidstate')}")
            print(f"  Pieces: {len(json_data.get('shop_pieces', []))}")
            print(f"  Enemies: {len(json_data.get('enemies', []))}")
        except Exception as e:
            print(f"❌ JSON validation failed: {e}")
    else:
        print("❌ JSON export failed")
        
    print("\n🎉 Dream Mecha integration test completed!")


if __name__ == "__main__":
    test_dream_mecha_integration() 