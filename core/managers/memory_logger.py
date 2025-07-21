"""
Memory Logger - Simple logging system for consciousness activities
"""

import time
from typing import Optional


class MemoryLogger:
    """Simple memory logging system"""
    
    def __init__(self):
        self.log_entries = []
        self.max_entries = 1000
    
    def log(self, message: str):
        """Log a message with timestamp"""
        entry = {
            'timestamp': time.time(),
            'message': message
        }
        self.log_entries.append(entry)
        
        # Keep only recent entries
        if len(self.log_entries) > self.max_entries:
            self.log_entries = self.log_entries[-self.max_entries:]
        
        # Also print to console for debugging
        print(f"[Memory] {message}")
    
    def get_recent_logs(self, count: int = 10) -> list:
        """Get recent log entries"""
        return self.log_entries[-count:]
    
    def clear_logs(self):
        """Clear all log entries"""
        self.log_entries.clear()


# Global instance
_memory_logger_instance: Optional[MemoryLogger] = None


def get_memory_logger() -> MemoryLogger:
    """Get the global memory logger instance"""
    global _memory_logger_instance
    if _memory_logger_instance is None:
        _memory_logger_instance = MemoryLogger()
    return _memory_logger_instance 