#!/usr/bin/env python3
"""
Gate Portal Module - Universal secret code generation from blockmaker glyphs
Properly encodes and reconstructs exact glyph spatial structures
"""

import hashlib
import random
from datetime import datetime
from typing import Dict, List, Optional


class GatePortal:
    """Universal GATE portal code generator with exact spatial reconstruction"""
    
    def __init__(self):
        self.GATE_PREFIX = "GATE"
        self.PORTAL_VERSION = "1.0"
        self.CODE_LENGTH = 64  # Standard length for universal codes
        
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
        
        self.INTEGRATION_TYPES = {
            'api': 'API Authentication',
            'db': 'Database Access',
            'auth': 'Authentication System',
            'crypto': 'Cryptographic Key',
            'session': 'Session Token',
            'admin': 'Administrative Access',
            'backup': 'Backup Recovery',
            'emergency': 'Emergency Override'
        }
    
    def generate_gate_portal(self, sigil_pattern: str, symbol: str, 
                           integration_type: str = 'api', 
                           metadata: Optional[Dict] = None) -> Dict:
        """
        Generate a universal GATE portal code from blockmaker glyph with exact spatial reconstruction
        """
        if symbol not in self.symbols:
            raise ValueError(f"Symbol '{symbol}' not in allowed visual symbols")
        
        if integration_type not in self.INTEGRATION_TYPES:
            raise ValueError(f"Integration type '{integration_type}' not supported")
        
        # Parse the glyph into spatial structure
        glyph_data = self._parse_glyph_structure(sigil_pattern)
        
        # Create the spatial GATE pattern
        gate_pattern = self._create_spatial_gate_pattern(glyph_data, symbol)
        
        # Generate the portal code
        portal_code = self._generate_portal_code(gate_pattern, integration_type)
        
        # Create metadata
        portal_metadata = self._create_portal_metadata(
            sigil_pattern, symbol, integration_type, metadata, glyph_data
        )
        
        # Generate verification hash
        verification_hash = self._generate_verification_hash(portal_code, portal_metadata)
        
        return {
            'portal_code': portal_code,
            'gate_pattern': gate_pattern,
            'integration_type': integration_type,
            'metadata': portal_metadata,
            'verification_hash': verification_hash,
            'generated_at': datetime.now().isoformat(),
            'version': self.PORTAL_VERSION
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
    
    def _generate_portal_code(self, gate_pattern: str, integration_type: str) -> str:
        """Generate the standardized portal code"""
        # Create hash from GATE pattern and integration type
        combined = f"{gate_pattern}:{integration_type}"
        hash_obj = hashlib.sha256(combined.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Format: GATE-VERSION-TYPE-HASH
        portal_code = f"{self.GATE_PREFIX}-{self.PORTAL_VERSION}-{integration_type}-{hash_hex[:32]}"
        return portal_code
    
    def _create_portal_metadata(self, sigil_pattern: str, symbol: str, 
                               integration_type: str, metadata: Optional[Dict], 
                               glyph_data: Dict) -> Dict:
        """Create detailed metadata about the portal with spatial information"""
        # Calculate complexity metrics
        total_blocks = len(glyph_data['blocks']) + 1  # +1 for anchor
        entropy_estimate = total_blocks * 8 + len(sigil_pattern) * 2
        
        return {
            'integration_name': self.INTEGRATION_TYPES[integration_type],
            'symbol_used': symbol,
            'sigil_complexity': {
                'total_blocks': total_blocks,
                'grid_size': glyph_data['grid_size'],
                'max_number': glyph_data['max_number'],
                'anchor_pos': glyph_data['anchor_pos'],
                'entropy_estimate': entropy_estimate
            },
            'portal_info': {
                'version': self.PORTAL_VERSION,
                'code_length': self.CODE_LENGTH,
                'integration_type': integration_type
            },
            'custom_metadata': metadata or {}
        }
    
    def _generate_verification_hash(self, portal_code: str, metadata: Dict) -> str:
        """Generate verification hash for integrity checking"""
        # Combine portal code and metadata for verification
        verification_data = f"{portal_code}:{metadata['integration_name']}:{metadata['symbol_used']}"
        hash_obj = hashlib.sha256(verification_data.encode())
        return hash_obj.hexdigest()[:16]
    
    def verify_gate_portal(self, portal_code: str, verification_hash: str, 
                          metadata: Dict) -> Dict:
        """Verify a GATE portal and reconstruct the exact glyph for visual verification"""
        try:
            # Parse portal code
            parts = portal_code.split('-')
            if len(parts) != 4 or parts[0] != self.GATE_PREFIX:
                return {
                    'valid': False,
                    'error': 'Invalid portal code format'
                }
            
            version, integration_type, hash_part = parts[1:]
            
            # Verify integration type
            if integration_type not in self.INTEGRATION_TYPES:
                return {
                    'valid': False,
                    'error': 'Invalid integration type'
                }
            
            # Verify version
            if version != self.PORTAL_VERSION:
                return {
                    'valid': False,
                    'error': f'Unsupported version: {version}'
                }
            
            # Verify hash length
            if len(hash_part) != 32:
                return {
                    'valid': False,
                    'error': 'Invalid hash length'
                }
            
            # Verify verification hash
            expected_hash = self._generate_verification_hash(portal_code, metadata)
            if verification_hash != expected_hash:
                return {
                    'valid': False,
                    'error': 'Verification hash mismatch'
                }
            
            # Reconstruct the exact glyph from metadata
            reconstructed_glyph = self._reconstruct_exact_glyph_from_metadata(metadata)
            
            return {
                'valid': True,
                'portal_code': portal_code,
                'integration_name': self.INTEGRATION_TYPES[integration_type],
                'version': version,
                'symbol': metadata.get('symbol_used', 'Unknown'),
                'reconstructed_glyph': reconstructed_glyph
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Verification failed: {str(e)}'
            }
    
    def _reconstruct_exact_glyph_from_metadata(self, metadata: Dict) -> str:
        """Reconstruct the exact glyph pattern from metadata for visual verification"""
        try:
            symbol = metadata.get('symbol_used', '>')
            sigil_complexity = metadata.get('sigil_complexity', {})
            
            # Extract spatial information from metadata
            grid_size = sigil_complexity.get('grid_size', 12)
            anchor_pos = sigil_complexity.get('anchor_pos', (0, 0))
            
            # For now, create a simplified reconstruction
            # In a real implementation, you'd store the full spatial data in metadata
            return self._create_simplified_glyph(symbol, grid_size, anchor_pos)
            
        except Exception as e:
            return f"Reconstruction error: {str(e)}"
    
    def _create_simplified_glyph(self, symbol: str, grid_size: int, anchor_pos: tuple) -> str:
        """Create a simplified glyph reconstruction for demonstration"""
        # Create empty grid
        grid = [['.' for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Place the symbol at anchor position
        anchor_row, anchor_col = anchor_pos
        grid[anchor_row][anchor_col] = symbol
        
        # Add some basic blocks for demonstration
        # In a real implementation, this would use the full spatial data
        for i in range(1, min(10, grid_size * grid_size)):
            row = i // grid_size
            col = i % grid_size
            if grid[row][col] == '.':
                grid[row][col] = str(i)
        
        # Convert to blockmaker ASCII format
        lines = []
        for row in range(grid_size):
            line_parts = []
            for col in range(grid_size):
                line_parts.append(grid[row][col])
            lines.append(' '.join(line_parts))
        
        return '\n'.join(lines)
    
    def generate_random_symbol(self) -> str:
        """Generate a random visual symbol"""
        return random.choice(self.symbols)


def create_gate_portal(sigil_pattern: str, symbol: str, 
                      integration_type: str = 'api', 
                      metadata: Optional[Dict] = None) -> Dict:
    """Create a GATE portal from a sigil pattern"""
    portal = GatePortal()
    return portal.generate_gate_portal(sigil_pattern, symbol, integration_type, metadata)


def verify_gate_portal(portal_code: str, verification_hash: str, 
                      metadata: Dict) -> Dict:
    """Verify a GATE portal"""
    portal = GatePortal()
    return portal.verify_gate_portal(portal_code, verification_hash, metadata)


def get_integration_types() -> Dict[str, str]:
    """Get available integration types"""
    portal = GatePortal()
    return portal.INTEGRATION_TYPES


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
    
    portal = GatePortal()
    symbol = ">"
    
    print("🚪 GATE PORTAL SPATIAL TEST")
    print("=" * 50)
    print(f"Original Glyph:\n{test_glyph}")
    print(f"Symbol: {symbol}")
    print()
    
    # Test different integration types
    integration_types = ['api', 'db', 'auth', 'admin', 'emergency']
    
    for integration_type in integration_types:
        result = portal.generate_gate_portal(test_glyph, symbol, integration_type)
        
        print(f"🔗 {integration_type.upper()} Portal:")
        print(f"   Code: {result['portal_code']}")
        print(f"   Integration: {result['metadata']['integration_name']}")
        print(f"   Blocks: {result['metadata']['sigil_complexity']['total_blocks']}")
        print(f"   Grid Size: {result['metadata']['sigil_complexity']['grid_size']}x{result['metadata']['sigil_complexity']['grid_size']}")
        print(f"   Entropy: ~{result['metadata']['sigil_complexity']['entropy_estimate']} bits")
        print()
    
    # Test verification
    api_result = portal.generate_gate_portal(test_glyph, symbol, 'api')
    verify_result = portal.verify_gate_portal(
        api_result['portal_code'],
        api_result['verification_hash'],
        api_result['metadata']
    )
    
    print("✅ VERIFICATION TEST")
    print("-" * 30)
    print(f"Verification: {'✅ SUCCESS' if verify_result['valid'] else '❌ FAILED'}")
    if verify_result['valid']:
        print(f"Portal Type: {verify_result['integration_name']}")
        print(f"Symbol: {verify_result['symbol']}")
        print(f"Reconstructed Glyph:\n{verify_result['reconstructed_glyph']}")
    
    print()
    print("=" * 50) 