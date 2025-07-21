"""
Flask web application for Dream Mecha grid management
Provides drag-and-drop interface for managing mecha grids
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json

# Import game systems
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.managers.player_manager import PlayerManager
from core.managers.game_manager import GameManager
from core.managers.voidstate_manager import VoidstateManager

app = Flask(__name__)
CORS(app)

# Initialize game managers
player_manager = PlayerManager()
game_manager = GameManager()
voidstate_manager = VoidstateManager()

@app.route('/')
def index():
    """Main grid management page"""
    return render_template('index.html')

@app.route('/api/player/<player_id>/grid', methods=['GET'])
def get_player_grid(player_id):
    """Get player's current grid state"""
    player = player_manager.get_player(player_id)
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    return jsonify({
        'grid': player.grid_system.to_json(),
        'mecha': player.mecha.to_dict() if player.mecha else None,
        'zoltans': player.total_zoltans_earned
    })

@app.route('/api/player/<player_id>/grid', methods=['POST'])
def update_player_grid(player_id):
    """Update player's grid state"""
    player = player_manager.get_player(player_id)
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    data = request.json
    grid_data = data.get('grid')
    
    if grid_data:
        player.grid_system.from_json(grid_data)
        player_manager.save_player_data()
        
        # Recalculate mecha stats
        if player.mecha:
            stats = player.grid_system.calculate_stats()
            player.mecha.stats.hp = stats['hp']
            player.mecha.stats.attack = stats['attack']
            player.mecha.stats.defense = stats['defense']
            player.mecha.stats.speed = stats['speed']
    
    return jsonify({'success': True})

@app.route('/api/shop', methods=['GET'])
def get_shop():
    """Get current shop inventory"""
    shop_items = game_manager.shop_system.get_shop_inventory()
    return jsonify({'items': shop_items})

@app.route('/api/shop/purchase', methods=['POST'])
def purchase_item():
    """Purchase item from shop"""
    data = request.json
    player_id = data.get('player_id')
    item_id = data.get('item_id')
    
    player = player_manager.get_player(player_id)
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    result = game_manager.shop_system.purchase_piece(player_id, item_id)
    if result['success']:
        player_manager.save_player_data()
    
    return jsonify(result)

@app.route('/api/game/status', methods=['GET'])
def get_game_status():
    """Get overall game status"""
    return jsonify({
        'voidstate': voidstate_manager.voidstate,
        'active_players': len(player_manager.get_active_players()),
        'total_players': len(player_manager.players)
    })

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({'status': 'healthy', 'service': 'dream-mecha-web'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False) 