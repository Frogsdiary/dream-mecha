#!/usr/bin/env python3
"""
Blocklock Module - Cryptographic key generation from blockmaker glyphs
Properly encodes and reconstructs exact glyph spatial structures
"""

import hashlib
import random
from typing import Dict, List, Optional, Tuple


class Blocklock:
    """Generate cryptographic keys from blockmaker glyph patterns with exact spatial reconstruction"""
    
    def __init__(self):
        # Visual symbols only - no letters or numbers
        self.symbols = [
            ">", "<", "=", "!", "@", "#", "$", "%", "^", "&", "*", 
            "(", ")", "-", "_", "+", "|", "\\", "/", "?", "~", "`",
            "°", "±", "§", "©", "®", "™", "¢", "£", "¥", "€", "¤",
            "¦", "¨", "¯", "´", "¸", "¹", "²", "³", "¼", "½", "¾",
            "×", "÷", "≠", "≈", "≤", "≥", "∞", "∑", "∏", "√", "∫",
            "∂", "∆", "∇", "∈", "∉", "∋", "∌", "∩", "∪", "⊂", "⊃",
            "⊆", "⊇", "⊕", "⊗", "⊥", "⊤", "∴", "∵", "∝", "∅", "∅",
            "⌈", "⌉", "⌊", "⌋", "〈", "〉", "⟨", "⟩", "⟪", "⟫", "⟦", "⟧"
        ]
    
    def generate_key_from_sigil(self, sigil_pattern: str, symbol: str) -> Dict:
        """
        Generate both a cryptographic key and spatial GATE pattern from a blockmaker glyph
        Returns: {'key': 'hash', 'lock': 'spatial_pattern'}
        """
        if symbol not in self.symbols:
            raise ValueError(f"Symbol '{symbol}' not in allowed visual symbols")
        
        # Parse the glyph into spatial structure
        glyph_data = self._parse_glyph_structure(sigil_pattern)
        
        # Generate the spatial GATE pattern (lock)
        gate_pattern = self._create_spatial_gate_pattern(glyph_data, symbol)
        
        # Generate the cryptographic key
        cryptographic_key = self._generate_cryptographic_key(glyph_data, symbol)
        
        return {
            'key': cryptographic_key,
            'lock': gate_pattern
        }
    
    def _parse_glyph_structure(self, sigil_pattern: str) -> Dict:
        """Parse glyph into spatial structure with exact positions"""
        lines = sigil_pattern.strip().split('\n')
        grid_size = len(lines)
        
        # Create spatial data structure
        spatial_data = {
            'grid_size': grid_size,
            'blocks': [],  # List of (row, col, number) tuples
            'anchor_pos': None,  # Position of the + anchor
            'max_number': 0
        }
        
        for row, line in enumerate(lines):
            parts = line.strip().split()
            for col, part in enumerate(parts):
                if part == '+':
                    spatial_data['anchor_pos'] = (row, col)
                elif part.isdigit():
                    number = int(part)
                    spatial_data['blocks'].append((row, col, number))
                    spatial_data['max_number'] = max(spatial_data['max_number'], number)
        
        return spatial_data
    
    def _create_spatial_gate_pattern(self, glyph_data: Dict, symbol: str) -> str:
        """Create GATE pattern that preserves exact spatial structure"""
        # Encode spatial information in a structured way
        anchor_row, anchor_col = glyph_data['anchor_pos']
        
        # Create spatial encoding: symbol + grid_size + anchor_pos + block_positions
        spatial_parts = [
            symbol,  # Visual symbol
            str(glyph_data['grid_size']),  # Grid size
            f"{anchor_row},{anchor_col}",  # Anchor position
        ]
        
        # Add all block positions in order
        for row, col, number in sorted(glyph_data['blocks'], key=lambda x: x[2]):
            spatial_parts.append(f"{row},{col},{number}")
        
        # Join with special separator to distinguish spatial data
        gate_pattern = "|".join(spatial_parts)
        return gate_pattern
    
    def _generate_cryptographic_key(self, glyph_data: Dict, symbol: str) -> str:
        """Generate a cryptographic key from glyph data"""
        # Create a deterministic string from the glyph data
        key_data = []
        key_data.append(symbol)
        key_data.append(str(glyph_data['grid_size']))
        key_data.append(f"{glyph_data['anchor_pos'][0]},{glyph_data['anchor_pos'][1]}")
        
        # Add all block positions in sorted order
        for row, col, number in sorted(glyph_data['blocks'], key=lambda x: x[2]):
            key_data.append(f"{row},{col},{number}")
        
        # Create the key string
        key_string = "|".join(key_data)
        
        # Generate cryptographic hash
        hash_obj = hashlib.sha256(key_string.encode())
        return hash_obj.hexdigest()[:32]  # 32 character key
    
    def verify_gate_key(self, gate_pattern: str, symbol: str) -> Dict:
        """
        Verify a GATE pattern and reconstruct the exact glyph for visual verification
        """
        try:
            # Parse the spatial GATE pattern
            spatial_data = self._parse_spatial_gate_pattern(gate_pattern, symbol)
            
            # Reconstruct the exact glyph
            reconstructed_glyph = self._reconstruct_exact_glyph(spatial_data, symbol)
            
            return {
                'valid': True,
                'reconstructed_glyph': reconstructed_glyph,
                'symbol': symbol,
                'pattern': gate_pattern,
                'spatial_data': spatial_data
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Verification failed: {str(e)}'
            }
    
    def _parse_spatial_gate_pattern(self, gate_pattern: str, symbol: str) -> Dict:
        """Parse spatial GATE pattern back into structured data"""
        parts = gate_pattern.split('|')
        
        if not parts or parts[0] != symbol:
            raise ValueError("Invalid GATE pattern format")
        
        # Extract spatial information
        grid_size = int(parts[1])
        anchor_pos = tuple(map(int, parts[2].split(',')))
        
        # Parse block positions
        blocks = []
        for part in parts[3:]:
            row, col, number = map(int, part.split(','))
            blocks.append((row, col, number))
        
        return {
            'grid_size': grid_size,
            'anchor_pos': anchor_pos,
            'blocks': blocks,
            'max_number': max([b[2] for b in blocks]) if blocks else 0
        }
    
    def _reconstruct_exact_glyph(self, spatial_data: Dict, symbol: str) -> str:
        """Reconstruct the exact glyph pattern from spatial data"""
        grid_size = spatial_data['grid_size']
        anchor_row, anchor_col = spatial_data['anchor_pos']
        blocks = spatial_data['blocks']
        
        # Create empty grid
        grid = [['.' for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Place the symbol at anchor position
        grid[anchor_row][anchor_col] = symbol
        
        # Place all blocks at their exact positions
        for row, col, number in blocks:
            grid[row][col] = str(number)
        
        # Convert to blockmaker ASCII format
        lines = []
        for row in range(grid_size):
            line_parts = []
            for col in range(grid_size):
                line_parts.append(grid[row][col])
            lines.append(' '.join(line_parts))
        
        return '\n'.join(lines)
    
    def get_key_info(self, sigil_pattern: str, symbol: str) -> Dict:
        """Get detailed information about the generated key"""
        glyph_data = self._parse_glyph_structure(sigil_pattern)
        gate_pattern = self.generate_key_from_sigil(sigil_pattern, symbol)
        
        # Calculate complexity metrics
        total_blocks = len(glyph_data['blocks']) + 1  # +1 for anchor
        entropy_bits = total_blocks * 8 + len(sigil_pattern) * 2
        
        return {
            'gate_pattern': gate_pattern,
            'symbol': symbol,
            'grid_size': glyph_data['grid_size'],
            'total_blocks': total_blocks,
            'max_number': glyph_data['max_number'],
            'anchor_pos': glyph_data['anchor_pos'],
            'entropy_bits': entropy_bits,
            'key_type': 'SPATIAL_GATE_PATTERN'
        }
    
    def generate_random_symbol(self) -> str:
        """Generate a random visual symbol"""
        return random.choice(self.symbols)


def generate_random_symbol() -> str:
    """Generate a random visual symbol for external use"""
    blocklock = Blocklock()
    return blocklock.generate_random_symbol()


def create_key_from_blockmaker_grid(grid_data: Dict, symbol: str) -> str:
    """Create a key from blockmaker grid data"""
    blocklock = Blocklock()
    
    # Convert grid data to sigil pattern
    sigil_pattern = _grid_to_sigil_pattern(grid_data)
    
    return blocklock.generate_key_from_sigil(sigil_pattern, symbol)


def _grid_to_sigil_pattern(grid_data: Dict) -> str:
    """Convert blockmaker grid data to sigil pattern"""
    # This would need to be implemented based on your grid data structure
    # For now, return a placeholder
    return "+ 2 3\n4 5 .\n6 . ."


if __name__ == "__main__":
    # Test with the exact glyph pattern you provided
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
    
    blocklock = Blocklock()
    symbol = ">"
    
    print("🔐 BLOCKLOCK SPATIAL GATE TEST")
    print("=" * 50)
    print(f"Original Glyph:\n{test_glyph}")
    print(f"Symbol: {symbol}")
    print()
    
    # Generate GATE pattern
    gate_pattern = blocklock.generate_key_from_sigil(test_glyph, symbol)
    key_info = blocklock.get_key_info(test_glyph, symbol)
    
    print(f"Generated GATE Pattern: {gate_pattern}")
    print(f"Grid Size: {key_info['grid_size']}x{key_info['grid_size']}")
    print(f"Total Blocks: {key_info['total_blocks']}")
    print(f"Max Number: {key_info['max_number']}")
    print(f"Anchor Position: {key_info['anchor_pos']}")
    print(f"Entropy Bits: ~{key_info['entropy_bits']}")
    print()
    
    # Test verification
    verify_result = blocklock.verify_gate_key(gate_pattern, symbol)
    print(f"Verification: {'✅ SUCCESS' if verify_result['valid'] else '❌ FAILED'}")
    if verify_result['valid']:
        print(f"Reconstructed Glyph:\n{verify_result['reconstructed_glyph']}")
    
    print()
    print("=" * 50) 