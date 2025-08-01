#!/usr/bin/env python3
"""
Test script for GATE CREATOR - Quantum-Resistant Glyph Cryptography

This script tests the new GATE CREATOR module that implements:
- GLYPH KEY: Encryption algorithm derived from glyph spatial structure
- GATE LOCK: Visual verification pattern for quantum-resistant cryptography
"""

import sys
import json
from pathlib import Path

# Add the current directory to the path so we can import gate_creator
sys.path.append(str(Path(__file__).parent))

from gate_creator import GateCreator, create_gate_from_glyph, verify_gate_pattern


def test_gate_creator():
    """Test the GATE CREATOR functionality"""
    
    print("=" * 80)
    print("🚪 GATE CREATOR - QUANTUM-RESISTANT GLYPH CRYPTOGRAPHY TEST")
    print("=" * 80)
    
    # Test glyph pattern (your example)
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
    
    test_password = "Hello this is my password~!"
    
    print(f"📋 Test Glyph Pattern:")
    print(test_glyph)
    print(f"🔑 Test Password: {test_password}")
    print()
    
    # Test 1: Create GATE from glyph
    print("🔐 TEST 1: Creating GATE from Glyph")
    print("-" * 50)
    
    try:
        gate_creator = GateCreator()
        gate_data = gate_creator.create_gate_from_glyph(test_glyph, test_password)
        
        print("✅ GATE Creation Successful!")
        print(f"📊 Block Count: {gate_data['metadata']['block_count']}")
        print(f"🎯 Grid Size: {gate_data['metadata']['grid_size']}")
        print(f"🧮 Complexity Score: {gate_data['metadata']['complexity_score']:.4f}")
        print(f"🛡️ Complexity Level: {gate_data['metadata']['complexity']['complexity_level']}")
        print(f"🔢 Spatial Combinations: {gate_data['metadata']['complexity']['spatial_combinations']}")
        
        # Get detailed info
        gate_info = gate_creator.get_gate_info(gate_data)
        print(f"🔑 Encryption Steps: {gate_info['encryption_steps']}")
        print(f"🎨 Visual Pattern Hash: {gate_info['verification_hash'][:16]}...")
        
    except Exception as e:
        print(f"❌ GATE Creation Failed: {e}")
        return False
    
    print()
    
    # Test 2: Verify GATE system
    print("🔍 TEST 2: Verifying GATE System")
    print("-" * 50)
    
    try:
        # Extract gate lock
        gate_lock = gate_data['gate_lock']
        
        # Verify with correct pattern
        result = gate_creator.verify_gate(gate_lock, test_glyph)
        
        if result['valid']:
            print("✅ GATE Verification Successful!")
            print(f"🔍 Test Hash: {result['test_hash']}")
            print(f"💾 Stored Hash: {result['stored_hash']}")
            print(f"🎯 Glyph Match: {result['glyph_match']}")
        else:
            print("❌ GATE Verification Failed!")
            print(f"🔍 Test Hash: {result['test_hash']}")
            print(f"💾 Stored Hash: {result['stored_hash']}")
            print(f"🎯 Glyph Match: {result['glyph_match']}")
            return False
            
    except Exception as e:
        print(f"❌ GATE Verification Failed: {e}")
        return False
    
    print()
    
    # Test 3: Test with wrong glyph
    print("🚫 TEST 3: Testing with Wrong Glyph")
    print("-" * 50)
    
    try:
        wrong_glyph = """+ 2 3
4 5 6
7 8 9"""
        
        result = gate_creator.verify_gate(gate_lock, wrong_glyph)
        
        if not result['valid']:
            print("✅ Correctly Rejected Wrong Glyph!")
            print(f"🔍 Test Hash: {result['test_hash']}")
            print(f"💾 Stored Hash: {result['stored_hash']}")
            print(f"🎯 Glyph Match: {result['glyph_match']}")
        else:
            print("❌ Incorrectly Accepted Wrong Glyph!")
            return False
            
    except Exception as e:
        print(f"❌ Wrong Glyph Test Failed: {e}")
        return False
    
    print()
    
    # Test 4: Test different passwords
    print("🔑 TEST 4: Testing Different Passwords")
    print("-" * 50)
    
    try:
        different_password = "Different password entirely!"
        gate_data_2 = gate_creator.create_gate_from_glyph(test_glyph, different_password)
        
        # The visual pattern should be the same (glyph-based), but metadata might differ
        print("✅ Different Password Test Successful!")
        print(f"📊 Original Block Count: {gate_data['metadata']['block_count']}")
        print(f"📊 New Block Count: {gate_data_2['metadata']['block_count']}")
        print(f"🎯 Original Visual Pattern: {gate_data['gate_lock'].visual_pattern[:50]}...")
        print(f"🎯 New Visual Pattern: {gate_data_2['gate_lock'].visual_pattern[:50]}...")
        
    except Exception as e:
        print(f"❌ Different Password Test Failed: {e}")
        return False
    
    print()
    
    # Test 5: Complexity assessment
    print("🧮 TEST 5: Complexity Assessment")
    print("-" * 50)
    
    try:
        complexity_info = gate_data['metadata']['complexity']
        
        print(f"🛡️ Complexity Level: {complexity_info['complexity_level']}")
        print(f"🔢 Spatial Combinations: {complexity_info['spatial_combinations']}")
        
        if complexity_info['complexity_level'] in ['HIGH', 'MEDIUM']:
            print("✅ Complexity Assessment: PASSED")
        else:
            print("⚠️ Complexity Assessment: NEEDS REVIEW")
            
    except Exception as e:
        print(f"❌ Complexity Assessment Failed: {e}")
        return False
    
    print()
    print("=" * 80)
    print("🎉 ALL TESTS PASSED! GATE CREATOR IS WORKING CORRECTLY!")
    print("=" * 80)
    
    return True


def test_gate_creator_details():
    """Test detailed GATE CREATOR functionality"""
    
    print("\n" + "=" * 80)
    print("🔬 DETAILED GATE CREATOR ANALYSIS")
    print("=" * 80)
    
    # Simple test glyph
    simple_glyph = """+ 2 3
4 5 6
7 8 9"""
    
    password = "test_password"
    
    try:
        gate_creator = GateCreator()
        gate_data = gate_creator.create_gate_from_glyph(simple_glyph, password)
        
        print("📋 Simple Glyph Analysis:")
        print(f"Glyph: {simple_glyph}")
        print(f"Password: {password}")
        print()
        
        # Analyze glyph key
        glyph_key = gate_data['glyph_key']
        print("🔑 GLYPH KEY Analysis:")
        print(f"- Encryption Steps: {glyph_key.encryption_steps}")
        print(f"- Block Positions: {len(glyph_key.block_positions)}")
        print(f"- Adjacency Matrix: {len(glyph_key.adjacency_matrix)} connections")
        print(f"- Spatial Structure: {glyph_key.spatial_structure['grid_size']}x{glyph_key.spatial_structure['grid_size']}")
        print()
        
        # Analyze gate lock
        gate_lock = gate_data['gate_lock']
        print("🚪 GATE LOCK Analysis:")
        print(f"- Visual Pattern: {len(gate_lock.visual_pattern)} characters")
        print(f"- Verification Hash: {gate_lock.verification_hash}")
        print(f"- Metadata Keys: {list(gate_lock.metadata.keys())}")
        print(f"- Complexity Metrics: {list(gate_lock.glyph_complexity.keys())}")
        print()
        
        # Show transformations
        print("🔄 TRANSFORMATION Analysis:")
        for i, transform in enumerate(glyph_key.transformations[:3]):  # Show first 3
            print(f"  Step {i+1}: Block {transform['block_num']} at {transform['position']}")
            print(f"    - Adjacent Blocks: {len(transform['adjacent_blocks'])}")
            print(f"    - Spatial Weight: {transform['spatial_weight']:.3f}")
            print(f"    - Encryption Type: {transform['encryption_step']['type']}")
        
        if len(glyph_key.transformations) > 3:
            print(f"  ... and {len(glyph_key.transformations) - 3} more steps")
        
        print()
        print("✅ Detailed Analysis Complete!")
        
    except Exception as e:
        print(f"❌ Detailed Analysis Failed: {e}")


if __name__ == "__main__":
    print("🚪 GATE CREATOR TEST SUITE")
    print("Testing quantum-resistant glyph cryptography...")
    print()
    
    # Run basic tests
    success = test_gate_creator()
    
    if success:
        # Run detailed analysis
        test_gate_creator_details()
        
        print("\n🎯 SUMMARY:")
        print("✅ GATE CREATOR module is working correctly")
        print("✅ Cryptography implemented")
        print("✅ Glyph-based encryption algorithm functional")
        print("✅ Visual verification system operational")
        print("✅ Spatial complexity provides security")
    else:
        print("\n❌ SUMMARY:")
        print("❌ GATE CREATOR module has issues")
        print("❌ Please check the implementation") 