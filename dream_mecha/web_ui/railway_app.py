"""
Railway deployment entry point for Dream Mecha Web UI
Handles production environment configuration
"""

import os
from flask import Flask
from app import app

if __name__ == "__main__":
    # Get port from Railway environment
    port = int(os.environ.get("PORT", 3000))
    
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Run the app
    app.run(
        host='0.0.0.0',  # Allow external connections
        port=port,
        debug=False  # Disable debug mode in production
    ) 