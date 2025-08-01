"""
Dream Mecha Debugger Module

Comprehensive logging and validation system for Dream Mecha game.
Handles piece generation validation, player data backup, and error tracking.
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from pathlib import Path


class DreamMechaDebugger:
    """Debugger for Dream Mecha game system"""
    
    def __init__(self, log_file: str = "dream_mecha_debug.log"):
        self.log_file = log_file
        self.error_count = 0
        self.warning_count = 0
        self.generation_count = 0
        
        # Setup logging
        self.setup_logging()
        
        # Create debug directory
        self.debug_dir = Path("dream_mecha/debug")
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_generation(self, piece_data: Dict[str, Any], success: bool):
        """Log piece generation attempts"""
        timestamp = datetime.now().isoformat()
        
        if success:
            self.generation_count += 1
            self.logger.info(f"Piece generation successful: {piece_data.get('id', 'unknown')}")
        else:
            self.error_count += 1
            self.logger.error(f"Piece generation failed: {piece_data.get('id', 'unknown')}")
            
        # Save generation data to debug file
        debug_data = {
            "timestamp": timestamp,
            "success": success,
            "piece_data": piece_data,
            "generation_count": self.generation_count,
            "error_count": self.error_count
        }
        
        debug_file = self.debug_dir / f"generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(debug_file, 'w') as f:
            json.dump(debug_data, f, indent=2)
            
    def validate_daily_content(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate daily JSON before export"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Check required fields
        required_fields = ["date", "voidstate", "shop_pieces", "enemies"]
        for field in required_fields:
            if field not in json_data:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
                
        # Validate date format
        if "date" in json_data:
            try:
                date.fromisoformat(json_data["date"])
            except ValueError:
                validation_result["valid"] = False
                validation_result["errors"].append("Invalid date format")
                
        # Validate voidstate
        if "voidstate" in json_data:
            voidstate = json_data["voidstate"]
            if not isinstance(voidstate, int) or voidstate < 1:
                validation_result["valid"] = False
                validation_result["errors"].append("Invalid voidstate value")
                
        # Validate shop pieces
        if "shop_pieces" in json_data:
            pieces = json_data["shop_pieces"]
            if not isinstance(pieces, list):
                validation_result["valid"] = False
                validation_result["errors"].append("Shop pieces must be a list")
            else:
                for i, piece in enumerate(pieces):
                    piece_validation = self.validate_piece(piece)
                    if not piece_validation["valid"]:
                        validation_result["valid"] = False
                        validation_result["errors"].extend([
                            f"Piece {i}: {error}" for error in piece_validation["errors"]
                        ])
                        
        # Validate enemies
        if "enemies" in json_data:
            enemies = json_data["enemies"]
            if not isinstance(enemies, list):
                validation_result["valid"] = False
                validation_result["errors"].append("Enemies must be a list")
            else:
                for i, enemy in enumerate(enemies):
                    enemy_validation = self.validate_enemy(enemy)
                    if not enemy_validation["valid"]:
                        validation_result["valid"] = False
                        validation_result["errors"].extend([
                            f"Enemy {i}: {error}" for error in enemy_validation["errors"]
                        ])
                        
        # Log validation result
        if validation_result["valid"]:
            self.logger.info("Daily content validation successful")
        else:
            self.error_count += 1
            self.logger.error(f"Daily content validation failed: {validation_result['errors']}")
            
        return validation_result
        
    def validate_piece(self, piece: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual piece data"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required piece fields
        required_fields = ["id", "pattern", "blocks", "stats", "stat_type", "price"]
        for field in required_fields:
            if field not in piece:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
                
        # Validate blocks count
        if "blocks" in piece:
            blocks = piece["blocks"]
            if not isinstance(blocks, int) or blocks < 1 or blocks > 144:
                validation_result["valid"] = False
                validation_result["errors"].append("Invalid block count (must be 1-144)")
                
        # Validate stats
        if "stats" in piece:
            stats = piece["stats"]
            if not isinstance(stats, dict):
                validation_result["valid"] = False
                validation_result["errors"].append("Stats must be a dictionary")
            else:
                required_stats = ["hp", "att", "def", "spd"]
                for stat in required_stats:
                    if stat not in stats:
                        validation_result["valid"] = False
                        validation_result["errors"].append(f"Missing stat: {stat}")
                    elif not isinstance(stats[stat], int) or stats[stat] < 0:
                        validation_result["valid"] = False
                        validation_result["errors"].append(f"Invalid {stat} value")
                        
        # Validate price
        if "price" in piece:
            price = piece["price"]
            if not isinstance(price, int) or price < 0:
                validation_result["valid"] = False
                validation_result["errors"].append("Invalid price value")
                
        return validation_result
        
    def validate_enemy(self, enemy: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual enemy data"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required enemy fields
        required_fields = ["id", "hp", "att", "def", "spd", "description"]
        for field in required_fields:
            if field not in enemy:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
                
        # Validate stats
        for stat in ["hp", "att", "def", "spd"]:
            if stat in enemy:
                value = enemy[stat]
                if not isinstance(value, int) or value < 0:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Invalid {stat} value")
                    
        # Validate description
        if "description" in enemy:
            desc = enemy["description"]
            if not isinstance(desc, str) or len(desc.strip()) == 0:
                validation_result["valid"] = False
                validation_result["errors"].append("Invalid description")
                
        return validation_result
        
    def backup_player_data(self, player_id: str, player_data: Dict[str, Any]):
        """Create backup before any player data modification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.debug_dir / f"player_backup_{player_id}_{timestamp}.json"
        
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "player_id": player_id,
            "player_data": player_data,
            "backup_type": "pre_modification"
        }
        
        try:
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            self.logger.info(f"Player data backup created: {backup_file}")
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to create player backup: {e}")
            
    def validate_stat_calculation(self, block_count: int, calculated_stats: Dict[str, int]) -> bool:
        """Validate stat calculations against system limits"""
        # Check for overflow
        max_stat_value = 100_000_000_000  # 100 billion limit
        
        for stat_name, stat_value in calculated_stats.items():
            if stat_value > max_stat_value:
                self.logger.error(f"Stat overflow detected: {stat_name} = {stat_value}")
                return False
                
        # Check for reasonable scaling
        expected_min = int(block_count ** 2.5 * 100 * 0.7)  # 30% variance minimum
        expected_max = int(block_count ** 2.5 * 100 * 1.3)  # 30% variance maximum
        
        total_stats = sum(calculated_stats.values())
        if total_stats < expected_min or total_stats > expected_max:
            self.warning_count += 1
            self.logger.warning(f"Stat scaling may be unusual: {total_stats} for {block_count} blocks")
            
        return True
        
    def log_combat_resolution(self, combat_data: Dict[str, Any]):
        """Log combat resolution for debugging"""
        timestamp = datetime.now().isoformat()
        
        combat_log = {
            "timestamp": timestamp,
            "combat_data": combat_data,
            "debug_info": {
                "error_count": self.error_count,
                "warning_count": self.warning_count
            }
        }
        
        combat_file = self.debug_dir / f"combat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(combat_file, 'w') as f:
                json.dump(combat_log, f, indent=2)
            self.logger.info(f"Combat resolution logged: {combat_file}")
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to log combat resolution: {e}")
            
    def get_debug_summary(self) -> Dict[str, Any]:
        """Get summary of debug information"""
        return {
            "timestamp": datetime.now().isoformat(),
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "generation_count": self.generation_count,
            "log_file": self.log_file,
            "debug_directory": str(self.debug_dir)
        }
        
    def cleanup_old_logs(self, days_to_keep: int = 7):
        """Clean up old debug files"""
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        for file_path in self.debug_dir.glob("*.json"):
            if file_path.stat().st_mtime < cutoff_date:
                try:
                    file_path.unlink()
                    self.logger.info(f"Cleaned up old debug file: {file_path}")
                except Exception as e:
                    self.logger.error(f"Failed to clean up {file_path}: {e}")


# Global debugger instance
debugger = DreamMechaDebugger()


def get_debugger() -> DreamMechaDebugger:
    """Get the global debugger instance"""
    return debugger 