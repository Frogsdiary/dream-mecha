#!/usr/bin/env python3
"""
Create starter pieces for new players
Generates 4 pieces (HP, ATT, DEF, SPD) with varying stats
"""

import sys
import os
from datetime import datetime
import random

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.utils.headless_blockmaker import HeadlessBlockmaker

def generate_starter_pieces():
    """Generate 4 starter pieces for new players"""
    
    # Initialize headless blockmaker
    blockmaker = HeadlessBlockmaker()
    
    # Define starter piece configurations - ALL with 2 blocks
    starter_configs = [
        {"name": "Starter HP Core", "stat_type": "hp", "blocks": 2, "description": "Basic health module"},
        {"name": "Starter Attack Core", "stat_type": "attack", "blocks": 2, "description": "Basic attack module"},
        {"name": "Starter Defense Core", "stat_type": "defense", "blocks": 2, "description": "Basic defense module"},
        {"name": "Starter Speed Core", "stat_type": "speed", "blocks": 2, "description": "Basic speed module"}
    ]
    
    starter_pieces = []
    
    for config in starter_configs:
        # Generate piece using headless blockmaker
        piece = blockmaker.generate_single_piece(
            block_count=config['blocks'],
            stat_type=config['stat_type']
        )
        
        # Add starter piece metadata
        piece['id'] = f"starter_{config['stat_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        piece['name'] = config['name']
        piece['description'] = config['description']
        piece['rarity'] = 'starter'
        piece['generation_method'] = 'starter_pieces'
        
        starter_pieces.append(piece)
    
    return starter_pieces

def create_starter_pieces():
    """Create 4 starter pieces for new players"""
    
    print("🎮 Creating Dream Mecha Starter Pieces...")
    print("=" * 50)
    
    # Generate starter pieces
    starter_pieces = generate_starter_pieces()
    
    for piece in starter_pieces:
        print(f"\n🔧 Generated {piece['name']}...")
        
        # Display piece info
        print(f"  📊 Blocks: {piece.get('block_count', 'N/A')}")
        
        # Determine stat type from stats
        stat_type = 'UNKNOWN'
        for stat_name, stat_value in piece['stats'].items():
            if stat_value > 0:
                stat_type = stat_name.upper()
                break
        print(f"  ⚡ Type: {stat_type}")
        
        # Show active stat
        active_stat = None
        for stat_name, stat_value in piece['stats'].items():
            if stat_value > 0:
                active_stat = (stat_name.upper(), stat_value)
                break
        
        if active_stat:
            print(f"  💪 Stats: {active_stat[0]}: {active_stat[1]}")
        else:
            print(f"  ❌ ERROR: No active stat!")
            
        print(f"  💰 Price: {piece['price']} Zoltans")
        if 'shape' in piece:
            print(f"  🎨 Shape: {piece['shape']}")
        else:
            print(f"  🎨 Shape: (generated)")
    
    # Save to JSON file
    output_file = "starter_pieces.json"
    import json
    
    with open(output_file, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'version': '0.3.5',
            'description': 'Dream Mecha starter pieces for new players',
            'pieces': starter_pieces
        }, f, indent=2)
    
    print(f"\n✅ Generated {len(starter_pieces)} starter pieces!")
    print(f"📁 Saved to: {output_file}")
    
    # Display summary
    print(f"\n📋 Starter Pieces Summary:")
    print("-" * 30)
    for piece in starter_pieces:
        # Determine stat type from stats
        stat_name = 'UNKNOWN'
        stat_value = 0
        for stat_key, stat_val in piece['stats'].items():
            if stat_val > 0:
                stat_name = stat_key.upper()
                stat_value = stat_val
                break
        print(f"  {piece['name']}: {stat_name} {stat_value} ({piece.get('block_count', 'N/A')} blocks)")
    
    return starter_pieces

if __name__ == "__main__":
    create_starter_pieces() 