#!/usr/bin/env python3
"""
Test script to generate blocklock keys and GATE portals from glyph patterns
"""

import sys
import os

# Add the blockmaker directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blocklock import Blocklock, generate_random_symbol
from gate_portal import GatePortal, create_gate_portal, verify_gate_portal, get_integration_types


def test_glyph_key_generation():
    """Test both blocklock and GATE portal generation with complex glyphs"""
    
    print("=" * 60)
    print("🔐 BLOCKLOCK & GATE PORTAL GLYPH TEST")
    print("=" * 60)
    
    # Complex glyph pattern (like what blockmaker generates)
    test_glyph = """+ 2 3 4 5 6 7 8 9 10 11 12
13 14 15 16 17 18 19 20 21 22 23 24
25 26 27 28 29 30 31 32 33 34 35 36
37 38 39 40 41 42 43 44 45 46 47 48
49 50 51 52 53 54 55 56 57 58 59 60
61 62 63 64 65 66 67 68 69 70 71 72"""
    
    # Visual symbol
    test_symbol = ">"
    
    print(f"📋 Complex Glyph Pattern:")
    print(test_glyph)
    print(f"🎯 Visual Symbol: {test_symbol}")
    print()
    
    # Generate blocklock key
    print("🔑 GENERATING BLOCKLOCK KEY")
    print("-" * 30)
    
    blocklock = Blocklock()
    gate_pattern = blocklock.generate_key_from_sigil(test_glyph, test_symbol)
    key_info = blocklock.get_key_info(test_glyph, test_symbol)
    
    print(f"Gate Pattern: {gate_pattern}")
    print(f"Numbers Found: {len(key_info['numbers_found'])}")
    print(f"Total Elements: {key_info['total_elements']}")
    print(f"Entropy Bits: ~{key_info['entropy_bits']}")
    print()
    
    # Generate GATE portals for different integration types
    print("🚪 GENERATING GATE PORTALS")
    print("-" * 30)
    
    portal = GatePortal()
    integration_types = ['api', 'db', 'auth', 'crypto', 'admin', 'emergency']
    
    for integration_type in integration_types:
        result = portal.generate_gate_portal(test_glyph, test_symbol, integration_type)
        
        print(f"🔗 {integration_type.upper()} Portal:")
        print(f"   Code: {result['portal_code']}")
        print(f"   Integration: {result['metadata']['integration_name']}")
        print(f"   Blocks: {result['metadata']['sigil_complexity']['total_blocks']}")
        print(f"   Entropy: ~{result['metadata']['sigil_complexity']['entropy_estimate']} bits")
        print()
    
    # Test verification
    print("✅ VERIFICATION TESTS")
    print("-" * 30)
    
    # Test blocklock verification
    verify_result = blocklock.verify_gate_key(gate_pattern, test_symbol)
    print(f"Blocklock Verification: {'✅ SUCCESS' if verify_result['valid'] else '❌ FAILED'}")
    if verify_result['valid']:
        print(f"Reconstructed Glyph:\n{verify_result['reconstructed_glyph']}")
    print()
    
    # Test GATE portal verification
    api_result = portal.generate_gate_portal(test_glyph, test_symbol, 'api')
    verify_portal = portal.verify_gate_portal(
        api_result['portal_code'],
        api_result['verification_hash'],
        api_result['metadata']
    )
    print(f"GATE Portal Verification: {'✅ SUCCESS' if verify_portal['valid'] else '❌ FAILED'}")
    if verify_portal['valid']:
        print(f"Portal Type: {verify_portal['integration_name']}")
        print(f"Symbol: {verify_portal['symbol']}")
        print(f"Reconstructed Glyph:\n{verify_portal['reconstructed_glyph']}")
    print()
    
    # Show integration types
    print("📚 AVAILABLE INTEGRATION TYPES")
    print("-" * 30)
    for code, name in get_integration_types().items():
        print(f"  {code}: {name}")
    
    print()
    print("=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)


def test_visual_symbols():
    """Test different visual symbols"""
    
    print("\n" + "=" * 60)
    print("🎨 VISUAL SYMBOLS TEST")
    print("=" * 60)
    
    # Simple glyph for testing
    simple_glyph = """+ 2 3 4
5 6 7 .
8 9 . ."""
    
    # Test different visual symbols
    symbols = [">", "<", "=", "!", "@", "#", "$", "%", "^", "&", "*"]
    
    blocklock = Blocklock()
    portal = GatePortal()
    
    for symbol in symbols:
        print(f"🎯 Testing Symbol: {symbol}")
        
        # Generate blocklock key
        gate_pattern = blocklock.generate_key_from_sigil(simple_glyph, symbol)
        print(f"   Blocklock Pattern: {gate_pattern}")
        
        # Generate portal
        result = portal.generate_gate_portal(simple_glyph, symbol, 'api')
        print(f"   Portal Code: {result['portal_code']}")
        
        # Verify
        verify_result = blocklock.verify_gate_key(gate_pattern, symbol)
        print(f"   Verification: {'✅' if verify_result['valid'] else '❌'}")
        print()
    
    print("=" * 60)


def test_glyph_complexity():
    """Test with different glyph complexities"""
    
    print("\n" + "=" * 60)
    print("📊 GLYPH COMPLEXITY TEST")
    print("=" * 60)
    
    # Different complexity glyphs
    glyphs = {
        "Simple": """+ 2 3
4 5 .""",
        
        "Medium": """+ 2 3 4 5
6 7 8 9
10 11 12 13
14 15 16 17""",
        
        "Complex": """+ 2 3 4 5 6 7 8 9 10 11 12
13 14 15 16 17 18 19 20 21 22 23 24
25 26 27 28 29 30 31 32 33 34 35 36
37 38 39 40 41 42 43 44 45 46 47 48
49 50 51 52 53 54 55 56 57 58 59 60
61 62 63 64 65 66 67 68 69 70 71 72"""
    }
    
    symbol = ">"
    blocklock = Blocklock()
    
    for name, glyph in glyphs.items():
        print(f"📋 {name} Glyph:")
        print(glyph)
        print()
        
        # Generate key
        gate_pattern = blocklock.generate_key_from_sigil(glyph, symbol)
        key_info = blocklock.get_key_info(glyph, symbol)
        
        print(f"🔑 {name} Results:")
        print(f"   Pattern: {gate_pattern}")
        print(f"   Numbers: {len(key_info['numbers_found'])}")
        print(f"   Elements: {key_info['total_elements']}")
        print(f"   Entropy: ~{key_info['entropy_bits']} bits")
        print()
        
        # Verify
        verify_result = blocklock.verify_gate_key(gate_pattern, symbol)
        print(f"   Verification: {'✅ SUCCESS' if verify_result['valid'] else '❌ FAILED'}")
        if verify_result['valid']:
            print(f"   Reconstructed:\n{verify_result['reconstructed_glyph']}")
        print()
    
    print("=" * 60)


if __name__ == "__main__":
    test_glyph_key_generation()
    test_visual_symbols()
    test_glyph_complexity() 