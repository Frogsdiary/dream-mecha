#!/usr/bin/env python3
"""
Main entry point for Dream Mecha Discord Bot
Railway will use this as the start command
"""

import sys
import os
import threading
from flask import Flask, jsonify

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create minimal Flask app for health checks
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'discord-bot'})

def run_health_server():
    """Run minimal health check server"""
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 3000)))

# Import and run the bot
from bot.main import main

if __name__ == "__main__":
    # Start health server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Run the Discord bot
    main() 