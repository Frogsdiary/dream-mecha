#!/usr/bin/env python3
"""
Main entry point for Dream Mecha Discord Bot + Web UI
Railway will use this as the start command
"""

import sys
import os
import threading
from flask import Flask, jsonify

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Web UI Flask app
from web_ui.app import app as web_app

# Add health endpoint to Web UI app
@web_app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'discord-bot'})

def run_web_ui():
    """Run Web UI Flask app with health endpoint"""
    port = int(os.getenv('PORT', 3000))
    print(f"🌐 Starting Web UI on port {port}")
    web_app.run(host='0.0.0.0', port=port)

# Import and run the bot
from bot.main import main

if __name__ == "__main__":
    print("🚀 Starting Dream Mecha Bot + Web UI...")
    
    # Start Web UI in background thread
    web_thread = threading.Thread(target=run_web_ui, daemon=True)
    web_thread.start()
    print("✅ Web UI thread started")
    
    # Run the Discord bot
    print("🤖 Starting Discord bot...")
    main() 