#!/usr/bin/env python3
"""
Test glyph reconstruction from GATE patterns
"""

import sys
import os

# Add the blockmaker directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blocklock import Blocklock
from gate_portal import GatePortal


def test_glyph_reconstruction():
    """Test exact glyph reconstruction from GATE patterns"""
    
    print("=" * 60)
    print("🔐 GLYPH RECONSTRUCTION TEST")
    print("=" * 60)
    
    # Example glyph pattern (like your example)
    test_glyph = """+ 2 3 4 5 6 7 8 9 10 11 12
44 45 . . . . . . . . 46 13
43 . . . . 66 65 . . . . 14
42 . . . . . . . . . . 15
41 . . . 67 50 49 68 . . . 16
40 . . 69 59 51 52 60 70 . . 17
39 . 71 61 53 . . 54 62 72 . 18
38 . . 73 . 55 56 . . . . 19
37 . . . . 58 57 . . . . 20
36 . . . . 64 63 . . . . 21
35 47 . . . . . . . . 48 22
34 33 32 31 30 29 28 27 26 25 24 23"""
    
    symbol = ">"
    
    print(f"📋 Original Glyph Pattern:")
    print(test_glyph)
    print(f"🎯 Visual Symbol: {symbol}")
    print()
    
    # Test blocklock reconstruction
    print("🔑 BLOCKLOCK RECONSTRUCTION")
    print("-" * 30)
    
    blocklock = Blocklock()
    gate_pattern = blocklock.generate_key_from_sigil(test_glyph, symbol)
    print(f"Generated GATE Pattern: {gate_pattern}")
    print()
    
    # Verify and reconstruct
    verify_result = blocklock.verify_gate_key(gate_pattern, symbol)
    print(f"Verification: {'✅ SUCCESS' if verify_result['valid'] else '❌ FAILED'}")
    if verify_result['valid']:
        print(f"Reconstructed Glyph:\n{verify_result['reconstructed_glyph']}")
    print()
    
    # Test GATE portal reconstruction
    print("🚪 GATE PORTAL RECONSTRUCTION")
    print("-" * 30)
    
    portal = GatePortal()
    result = portal.generate_gate_portal(test_glyph, symbol, 'api')
    print(f"Portal Code: {result['portal_code']}")
    print()
    
    # Verify portal
    verify_portal = portal.verify_gate_portal(
        result['portal_code'],
        result['verification_hash'],
        result['metadata']
    )
    print(f"Portal Verification: {'✅ SUCCESS' if verify_portal['valid'] else '❌ FAILED'}")
    if verify_portal['valid']:
        print(f"Reconstructed Glyph:\n{verify_portal['reconstructed_glyph']}")
    
    print()
    print("=" * 60)
    print("✅ RECONSTRUCTION TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_glyph_reconstruction() 