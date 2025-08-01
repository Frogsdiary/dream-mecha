"""
GATE CREATOR - Glyph-Based Cryptography

This module implements a cryptographic system where:
- GLYPH = Key Derivation Source (unique spatial entropy)
- GATE = Visual Pattern (verification and decryption)

The glyph's spatial structure provides entropy for key generation,
while established cryptography (AES) provides actual security.
"""

import hashlib
import random
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


@dataclass
class GlyphKey:
    """The encryption key derived from a glyph's spatial structure"""
    spatial_structure: Dict[str, Any]
    transformations: List[Dict[str, Any]]
    encryption_steps: int
    block_positions: List[Tuple[int, int, int]]  # (row, col, block_num)
    adjacency_matrix: Dict[Tuple[int, int], List[Tuple[int, int]]]


@dataclass
class GateLock:
    """The visual verification pattern (the GATE)"""
    visual_pattern: str
    verification_hash: str
    metadata: Dict[str, Any]
    glyph_complexity: Dict[str, Any]


class GateCreator:
    """
    Cryptography using glyphs for key derivation and AES for actual encryption.
    
    The glyph's spatial structure provides entropy for key generation,
    while established cryptography provides security.
    """
    
    def __init__(self):
        self.visual_symbols = [
            '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=', 
            '[', ']', '{', '}', '|', ';', ':', '"', ',', '.', '/', '<', '>', '?',
            '~', '`', '!', '\\', "'"
        ]
    
    def create_gate_from_glyph(self, glyph_pattern: str, password: str) -> Dict[str, Any]:
        """
        Create a GATE system from a glyph pattern and password.
        
        Args:
            glyph_pattern: The ASCII glyph pattern (e.g., "+ 2 3 4...")
            password: The password to use for additional entropy
            
        Returns:
            Dictionary containing both the GLYPH KEY and GATE LOCK
        """
        # Parse the glyph structure
        glyph_data = self._parse_glyph_structure(glyph_pattern)
        
        # Create the GLYPH KEY (key derivation source)
        glyph_key = self._create_glyph_key(glyph_data, password)
        
        # Create the GATE LOCK (visual verification)
        gate_lock = self._create_gate_lock(glyph_data, glyph_pattern)
        
        return {
            'glyph_key': glyph_key,
            'gate_lock': gate_lock,
            'metadata': {
                'block_count': glyph_data['block_count'],
                'grid_size': glyph_data['grid_size'],
                'complexity_score': self._calculate_complexity_score(glyph_data),
                'complexity': self._assess_quantum_resistance(glyph_data)
            }
        }
    
    def lock_data(self, data: bytes, glyph_pattern: str, password: str) -> bytes:
        """
        Encrypt data using glyph-derived key and AES-GCM.
        
        Args:
            data: The data to encrypt
            glyph_pattern: The glyph pattern to use for key derivation
            password: The password for additional entropy
            
        Returns:
            Encrypted data with authentication tag
        """
        # Generate cryptographic key from glyph + password
        key = self._derive_key_from_glyph(glyph_pattern, password)
        
        # Generate random IV for AES-GCM
        iv = os.urandom(12)  # 96 bits for GCM
        
        # Create AES-GCM cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Encrypt the data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Get authentication tag
        tag = encryptor.tag
        
        # Combine IV + tag + ciphertext
        return iv + tag + ciphertext
    
    def unlock_data(self, encrypted_data: bytes, glyph_pattern: str, password: str) -> bytes:
        """
        Decrypt data using glyph-derived key and AES-GCM.
        
        Args:
            encrypted_data: The data to decrypt (IV + tag + ciphertext)
            glyph_pattern: The glyph pattern used for key derivation
            password: The password for additional entropy
            
        Returns:
            Decrypted data
        """
        # Generate cryptographic key from glyph + password
        key = self._derive_key_from_glyph(glyph_pattern, password)
        
        # Extract IV, tag, and ciphertext
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]  # 16 bytes for GCM tag
        ciphertext = encrypted_data[28:]
        
        # Create AES-GCM cipher for decryption
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Decrypt the data
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext
    
    def _derive_key_from_glyph(self, glyph_pattern: str, password: str) -> bytes:
        """
        Derive a cryptographic key from glyph spatial properties + password.
        
        This is where the glyph's uniqueness provides entropy for key generation.
        """
        # Extract spatial entropy from glyph
        glyph_data = self._parse_glyph_structure(glyph_pattern)
        spatial_entropy = self._extract_spatial_entropy(glyph_data)
        
        # Combine glyph entropy with password
        combined_entropy = spatial_entropy + password.encode()
        
        # Use PBKDF2 for key derivation (256-bit key for AES-256)
        salt = b'gate_creator_salt'  # Fixed salt for deterministic key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # High iteration count for security
            backend=default_backend()
        )
        
        # Generate the master key
        key = kdf.derive(combined_entropy)
        
        return key
    
    def _extract_spatial_entropy(self, glyph_data: Dict[str, Any]) -> bytes:
        """
        Extract spatial entropy from glyph structure.
        
        This converts the glyph's unique spatial properties into entropy
        for key derivation.
        """
        # Create entropy from spatial properties
        entropy_parts = []
        
        # 1. Block positions as entropy
        for row, col, block_num in sorted(glyph_data['blocks'], key=lambda x: x[2]):
            entropy_parts.append(f"{row},{col},{block_num}".encode())
        
        # 2. Adjacency relationships as entropy
        for pos, adjacent in glyph_data['adjacency_map'].items():
            row, col = pos
            adj_str = f"{row},{col}:{len(adjacent)}"
            entropy_parts.append(adj_str.encode())
        
        # 3. Grid density patterns as entropy
        grid_size = glyph_data['grid_size']
        density_map = {}
        for row in range(grid_size):
            for col in range(grid_size):
                if (row, col) in glyph_data['blocks']:
                    # Count filled neighbors
                    filled_neighbors = 0
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if (row + dr, col + dc) in glyph_data['blocks']:
                            filled_neighbors += 1
                    density_map[(row, col)] = filled_neighbors
        
        # Add density entropy
        for pos, density in density_map.items():
            row, col = pos
            entropy_parts.append(f"density:{row},{col}:{density}".encode())
        
        # 4. Spatial distribution patterns
        positions = [(row, col) for row, col, _ in glyph_data['blocks']]
        row_distribution = len(set(row for row, _ in positions))
        col_distribution = len(set(col for _, col in positions))
        entropy_parts.append(f"dist:{row_distribution},{col_distribution}".encode())
        
        # Combine all entropy parts
        combined_entropy = b''.join(entropy_parts)
        
        # Hash to create consistent entropy
        return hashlib.sha256(combined_entropy).digest()
    
    def _parse_glyph_structure(self, glyph_pattern: str) -> Dict[str, Any]:
        """Parse glyph into spatial structure with exact positions"""
        lines = glyph_pattern.strip().split('\n')
        grid_size = len(lines)
        
        spatial_data = {
            'grid_size': grid_size,
            'block_count': 0,
            'blocks': [],  # List of (row, col, block_num) tuples
            'anchor_pos': None,  # Position of the + anchor
            'max_number': 0,
            'adjacency_map': {}  # Maps each block to its adjacent blocks
        }
        
        # Parse each line
        for row, line in enumerate(lines):
            parts = line.strip().split()
            for col, part in enumerate(parts):
                if part == '+':
                    spatial_data['anchor_pos'] = (row, col)
                    spatial_data['blocks'].append((row, col, 1))
                    spatial_data['block_count'] += 1
                    spatial_data['max_number'] = max(spatial_data['max_number'], 1)
                elif part.isdigit():
                    number = int(part)
                    spatial_data['blocks'].append((row, col, number))
                    spatial_data['block_count'] += 1
                    spatial_data['max_number'] = max(spatial_data['max_number'], number)
        
        # Build adjacency map
        spatial_data['adjacency_map'] = self._build_adjacency_map(spatial_data['blocks'])
        
        return spatial_data
    
    def _build_adjacency_map(self, blocks: List[Tuple[int, int, int]]) -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
        """Build adjacency map for all blocks"""
        adjacency_map = {}
        
        for row, col, number in blocks:
            adjacent = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row, new_col = row + dr, col + dc
                if any(b[0] == new_row and b[1] == new_col for b in blocks):
                    adjacent.append((new_row, new_col))
            adjacency_map[(row, col)] = adjacent
        
        return adjacency_map
    
    def _create_glyph_key(self, glyph_data: Dict[str, Any], password: str) -> GlyphKey:
        """Create the GLYPH KEY (key derivation source) from spatial data"""
        
        # Create transformations based on spatial structure
        transformations = []
        
        for row, col, block_num in sorted(glyph_data['blocks'], key=lambda x: x[2]):
            # Each block defines a transformation
            transformation = {
                'block_num': block_num,
                'position': (row, col),
                'adjacent_blocks': glyph_data['adjacency_map'].get((row, col), []),
                'spatial_weight': self._calculate_spatial_weight(row, col, glyph_data),
                'entropy_contribution': self._calculate_entropy_contribution(row, col, block_num, glyph_data)
            }
            transformations.append(transformation)
        
        # Create the glyph key
        glyph_key = GlyphKey(
            spatial_structure=glyph_data,
            transformations=transformations,
            encryption_steps=glyph_data['block_count'],
            block_positions=glyph_data['blocks'],
            adjacency_matrix=glyph_data['adjacency_map']
        )
        
        return glyph_key
    
    def _create_gate_lock(self, glyph_data: Dict[str, Any], glyph_pattern: str) -> GateLock:
        """Create the GATE LOCK (visual verification pattern)"""
        
        # Create verification hash from visual pattern
        verification_hash = hashlib.sha256(glyph_pattern.encode()).hexdigest()[:32]
        
        # Create metadata
        metadata = {
            'block_count': glyph_data['block_count'],
            'grid_size': glyph_data['grid_size'],
            'max_number': glyph_data['max_number'],
            'anchor_position': glyph_data['anchor_pos'],
            'complexity_metrics': self._calculate_complexity_metrics(glyph_data)
        }
        
        # Create the gate lock
        gate_lock = GateLock(
            visual_pattern=glyph_pattern,
            verification_hash=verification_hash,
            metadata=metadata,
            glyph_complexity=self._calculate_complexity_metrics(glyph_data)
        )
        
        return gate_lock
    
    def _calculate_spatial_weight(self, row: int, col: int, glyph_data: Dict[str, Any]) -> float:
        """Calculate spatial weight for a block position"""
        center_row = glyph_data['grid_size'] // 2
        center_col = glyph_data['grid_size'] // 2
        
        # Distance from center
        distance = abs(row - center_row) + abs(col - center_col)
        
        # Adjacency factor
        adjacent_count = len(glyph_data['adjacency_map'].get((row, col), []))
        
        # Complexity factor
        return (distance * 0.3) + (adjacent_count * 0.7)
    
    def _calculate_entropy_contribution(self, row: int, col: int, block_num: int, glyph_data: Dict[str, Any]) -> float:
        """Calculate how much entropy this block contributes to key derivation"""
        # Factors that contribute to entropy:
        # 1. Position uniqueness
        # 2. Adjacency complexity
        # 3. Block number significance
        # 4. Spatial distribution
        
        adjacency_count = len(glyph_data['adjacency_map'].get((row, col), []))
        position_factor = (row * 13 + col * 17) % 256
        block_factor = block_num / glyph_data['max_number']
        
        return (adjacency_count * 0.4) + (position_factor * 0.3) + (block_factor * 0.3)
    
    def _calculate_complexity_metrics(self, glyph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate complexity metrics for the glyph"""
        
        # Spatial complexity
        total_positions = glyph_data['grid_size'] ** 2
        density = glyph_data['block_count'] / total_positions
        
        # Adjacency complexity
        avg_adjacency = sum(len(adj) for adj in glyph_data['adjacency_map'].values()) / glyph_data['block_count']
        
        # Distribution complexity
        positions = [(row, col) for row, col, _ in glyph_data['blocks']]
        row_distribution = len(set(row for row, _ in positions)) / glyph_data['grid_size']
        col_distribution = len(set(col for _, col in positions)) / glyph_data['grid_size']
        
        return {
            'density': density,
            'avg_adjacency': avg_adjacency,
            'row_distribution': row_distribution,
            'col_distribution': col_distribution,
            'spatial_complexity': density * avg_adjacency * (row_distribution + col_distribution)
        }
    
    def _calculate_complexity_score(self, glyph_data: Dict[str, Any]) -> float:
        """Calculate overall complexity score"""
        metrics = self._calculate_complexity_metrics(glyph_data)
        return metrics['spatial_complexity']
    
    def _assess_quantum_resistance(self, glyph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess complexity of the glyph"""
        
        # Calculate theoretical combinations
        spatial_combinations = glyph_data['block_count'] ** glyph_data['block_count']
        
        # Simple complexity levels
        if spatial_combinations > 10**30:
            complexity_level = "HIGH"
        elif spatial_combinations > 10**15:
            complexity_level = "MEDIUM"
        else:
            complexity_level = "LOW"
        
        return {
            'spatial_combinations': spatial_combinations,
            'complexity_level': complexity_level
        }
    
    def verify_gate(self, gate_lock: GateLock, test_glyph: str) -> Dict[str, Any]:
        """
        Verify a GATE using a test glyph pattern.
        
        Args:
            gate_lock: The GATE LOCK to verify against
            test_glyph: The glyph pattern to test
            
        Returns:
            Verification result
        """
        # Calculate hash of test glyph
        test_hash = hashlib.sha256(test_glyph.encode()).hexdigest()[:32]
        
        # Compare with stored hash
        is_valid = test_hash == gate_lock.verification_hash
        
        return {
            'valid': is_valid,
            'test_hash': test_hash,
            'stored_hash': gate_lock.verification_hash,
            'glyph_match': test_glyph == gate_lock.visual_pattern
        }
    
    def get_gate_info(self, gate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a GATE system"""
        
        glyph_key = gate_data['glyph_key']
        gate_lock = gate_data['gate_lock']
        
        return {
            'block_count': glyph_key.encryption_steps,
            'grid_size': glyph_key.spatial_structure['grid_size'],
            'complexity_score': gate_data['metadata']['complexity_score'],
            'complexity': gate_data['metadata']['complexity'],
            'visual_pattern': gate_lock.visual_pattern,
            'verification_hash': gate_lock.verification_hash,
            'encryption_steps': glyph_key.encryption_steps,
            'spatial_combinations': gate_data['metadata']['complexity']['spatial_combinations']
        }


def create_gate_from_glyph(glyph_pattern: str, password: str) -> Dict[str, Any]:
    """Convenience function to create a GATE from a glyph"""
    creator = GateCreator()
    return creator.create_gate_from_glyph(glyph_pattern, password)


def verify_gate_pattern(gate_lock: GateLock, test_glyph: str) -> Dict[str, Any]:
    """Convenience function to verify a GATE"""
    creator = GateCreator()
    return creator.verify_gate(gate_lock, test_glyph) 