#!/usr/bin/env python3
"""
Main entry point for Dream Mecha Discord Bot
Railway will use this as the start command
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the bot
from bot.main import main

if __name__ == "__main__":
    main() 