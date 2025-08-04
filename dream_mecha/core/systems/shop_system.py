"""
Shop System - Daily shop and piece trading

Handles AI-generated pieces, shop inventory, and player trading.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import random


@dataclass
class ShopPiece:
    """Piece available in the shop"""
    piece_id: str
    name: str
    shape: List[List[bool]]
    stats: Dict[str, int]
    price: int
    piece_type: str = 'stat'  # 'stat' or 'glyph'
    seller_id: Optional[str] = None  # None for AI-generated, player_id for trades


class ShopSystem:
    """Manages daily shop inventory and player trading"""
    
    def __init__(self):
        self.daily_inventory: List[ShopPiece] = []
        self.player_trades: List[ShopPiece] = []
        self.daily_purchases: Dict[str, int] = {}  # player_id -> purchase_count
        self.last_reset = datetime.now()
        self.base_prices = {
            'hp': 100,
            'attack': 150,
            'defense': 120,
            'speed': 80
        }
    
    def generate_daily_shop(self, voidstate: int, player_count: int) -> List[ShopPiece]:
        """Generate new daily shop inventory"""
        self.daily_inventory.clear()
        self.daily_purchases.clear()
        
        # Generate 6-8 pieces with guaranteed size distribution
        total_pieces = random.randint(6, 8)
        
        # Small pieces (1-2 blocks) for new players
        small_count = random.randint(2, 3)
        for _ in range(small_count):
            piece = self._generate_piece(1, 2, voidstate)
            self.daily_inventory.append(piece)
        
        # Medium pieces (3-5 blocks) for established players
        medium_count = random.randint(2, 3)
        for _ in range(medium_count):
            piece = self._generate_piece(3, 5, voidstate)
            self.daily_inventory.append(piece)
        
        # Large pieces (6+ blocks) for advanced players
        large_count = total_pieces - small_count - medium_count
        for _ in range(large_count):
            piece = self._generate_piece(6, 12, voidstate)
            self.daily_inventory.append(piece)
        
        self.last_reset = datetime.now()
        return self.daily_inventory
    
    def _generate_piece(self, min_blocks: int, max_blocks: int, voidstate: int) -> ShopPiece:
        """Generate a single piece with specified block range using headless blockmaker"""
        block_count = random.randint(min_blocks, max_blocks)
        
        try:
            # Use headless blockmaker for Railway-compatible generation
            from core.utils.headless_blockmaker import generate_single_piece
            
            piece_data = generate_single_piece(block_count, "random")
            
            # Extract headless blockmaker data
            shape = piece_data.get("shape", [[True]])
            stats = piece_data.get("stats", {})
            price = piece_data.get("price", 100)
            
            # Ensure stats format is correct
            formatted_stats = {
                'hp': stats.get('hp', 0),
                'attack': stats.get('attack', 0),
                'defense': stats.get('defense', 0),
                'speed': stats.get('speed', 0)
            }
            
            piece = ShopPiece(
                piece_id=piece_data.get("piece_id", f"piece_{random.randint(10000, 99999)}"),
                name=piece_data.get("name", f"Void Fragment {block_count}"),
                shape=shape,
                stats=formatted_stats,
                price=price,
                piece_type='stat'
            )
            
            return piece
            
        except Exception as e:
            print(f"Headless blockmaker generation failed: {e}")
            # Fallback to simple generation
            return self._generate_fallback_piece(min_blocks, max_blocks, voidstate)
    
    def _generate_fallback_piece(self, min_blocks: int, max_blocks: int, voidstate: int) -> ShopPiece:
        """Fallback piece generation if blockmaker fails"""
        block_count = random.randint(min_blocks, max_blocks)
        shape = self._generate_fallback_shape(block_count)
        stats = self._calculate_piece_stats(block_count, voidstate)
        price = self._calculate_piece_price(block_count, stats)
        
        piece = ShopPiece(
            piece_id=f"piece_{random.randint(10000, 99999)}",
            name=f"Void Fragment {block_count}",
            shape=shape,
            stats=stats,
            price=price,
            piece_type='stat'
        )
        
        return piece
    
    def _generate_shape(self, block_count: int) -> List[List[bool]]:
        """Generate a valid shape using blockmaker algorithm"""
        try:
            # Try to use blockmaker for proper generation
            from blockmaker.blockmaker_window import DailyShopWindow
            
            # Create a temporary instance for generation
            shop_generator = DailyShopWindow()
            piece_data = shop_generator.generate_single_piece_manual(block_count, "random")
            
            # Convert pattern to boolean grid
            pattern = piece_data.get("pattern", "")
            return self._pattern_to_bool_grid(pattern)
            
        except Exception as e:
            print(f"Blockmaker integration failed, using fallback: {e}")
            return self._generate_fallback_shape(block_count)
    
    def _pattern_to_bool_grid(self, pattern: str) -> List[List[bool]]:
        """Convert ASCII pattern to boolean grid"""
        lines = pattern.strip().split('\n')
        # Skip header lines that don't contain the pattern
        pattern_lines = [line for line in lines if '█' in line or '▓' in line or '░' in line]
        
        if not pattern_lines:
            return [[True]]  # Fallback for single block
        
        # Convert to boolean grid
        grid = []
        for line in pattern_lines:
            row = []
            for char in line:
                row.append(char in ['█', '▓'])  # Solid blocks are True
            grid.append(row)
        
        return grid if grid else [[True]]
    
    def _generate_fallback_shape(self, block_count: int) -> List[List[bool]]:
        """Fallback shape generation if blockmaker fails"""
        if block_count == 1:
            return [[True]]
        elif block_count == 2:
            return [[True, True]]
        elif block_count == 3:
            return [[True, True, True]]
        else:
            # Generate larger shapes (simplified)
            size = int(block_count ** 0.5) + 1
            shape = [[False for _ in range(size)] for _ in range(size)]
            
            # Fill blocks in a pattern
            blocks_placed = 0
            for y in range(size):
                for x in range(size):
                    if blocks_placed < block_count:
                        shape[y][x] = True
                        blocks_placed += 1
            
            return shape
    
    def _calculate_piece_stats(self, block_count: int, voidstate: int, stat_type: str = "random") -> Dict[str, int]:
        """Calculate stats for a piece based on block count"""
        # Exponential scaling as specified in rules
        base_multiplier = 100 * (block_count ** 2)
        voidstate_bonus = 1 + (voidstate * 0.1)
        
        # Calculate total power for this piece
        total_power = int(base_multiplier * voidstate_bonus)
        
        # Each piece gives ONLY ONE stat
        stat_types = ['hp', 'attack', 'defense', 'speed']
        
        # Use the specified stat_type, or random if "random"
        if stat_type == "random":
            chosen_stat = random.choice(stat_types)
        else:
            # Map stat_type to the correct stat name
            stat_mapping = {
                "hp": "hp",
                "attack": "attack", 
                "defense": "defense",
                "speed": "speed"
            }
            chosen_stat = stat_mapping.get(stat_type, "hp")  # Default to hp if invalid
        
        # All power goes to the chosen stat
        stats = {
            'hp': 0,
            'attack': 0,
            'defense': 0,
            'speed': 0
        }
        stats[chosen_stat] = total_power
        
        return stats
    
    def _calculate_piece_price(self, block_count: int, stats: Dict[str, int]) -> int:
        """Calculate price for a piece"""
        # Pricing formula: base_cost * (block_count ^ scaling_factor)
        base_cost = 100
        scaling_factor = 1.5
        
        price = int(base_cost * (block_count ** scaling_factor))
        
        # Adjust based on total stat power
        total_stats = sum(stats.values())
        stat_multiplier = 1 + (total_stats / 10000)
        
        return int(price * stat_multiplier)
    
    def purchase_piece(self, player_id: str, piece_id: str) -> Optional[ShopPiece]:
        """Purchase a piece from the shop"""
        # Check daily purchase limit
        if self.daily_purchases.get(player_id, 0) >= 1:
            return None
        
        # Find piece in inventory
        piece = None
        for p in self.daily_inventory:
            if p.piece_id == piece_id:
                piece = p
                break
        
        if not piece:
            return None
        
        # Update purchase count
        self.daily_purchases[player_id] = self.daily_purchases.get(player_id, 0) + 1
        
        # Remove from inventory
        self.daily_inventory.remove(piece)
        
        return piece
    
    def add_player_trade(self, player_id: str, piece: ShopPiece, asking_price: int) -> bool:
        """Add a piece to player trading section"""
        trade_piece = ShopPiece(
            piece_id=piece.piece_id,
            name=piece.name,
            shape=piece.shape,
            stats=piece.stats,
            price=asking_price,
            piece_type=piece.piece_type,
            seller_id=player_id
        )
        
        self.player_trades.append(trade_piece)
        return True
    
    def purchase_trade(self, buyer_id: str, piece_id: str) -> Optional[ShopPiece]:
        """Purchase a piece from player trading"""
        piece = None
        for p in self.player_trades:
            if p.piece_id == piece_id and p.seller_id != buyer_id:
                piece = p
                break
        
        if not piece:
            return None
        
        # Remove from trades
        self.player_trades.remove(piece)
        
        return piece
    
    def get_shop_inventory(self) -> List[ShopPiece]:
        """Get current shop inventory"""
        return self.daily_inventory.copy()
    
    def get_player_trades(self) -> List[ShopPiece]:
        """Get current player trades"""
        return self.player_trades.copy()
    
    def can_purchase_today(self, player_id: str) -> bool:
        """Check if player can purchase today"""
        return self.daily_purchases.get(player_id, 0) < 1
    
    def should_reset_daily(self) -> bool:
        """Check if daily shop should reset"""
        now = datetime.now()
        return (now - self.last_reset).days >= 1 