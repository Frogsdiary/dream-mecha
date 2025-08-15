"""
Flask web application for Dream Mecha grid management
Provides drag-and-drop interface for managing mecha grids
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import json
import requests
from datetime import date, datetime
from pathlib import Path
from functools import wraps
import sys

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.managers.player_manager import PlayerManager
from core.managers.fortress_manager import FortressManager
from core.systems.grid_system import GridSystem
from core.systems.combat_system import CombatSystem
from core.systems.shop_system import ShopSystem

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')

# Development configuration
if os.getenv('FLASK_ENV') == 'development' or True:  # Force development mode
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Security configuration
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Rate limiting - DISABLED FOR DEVELOPMENT
# limiter = Limiter(
#     app=app,
#     key_func=get_remote_address,
#     default_limits=["200 per day", "50 per hour"]
# )

# CORS configuration
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, origins=allowed_origins, supports_credentials=True)

# Discord OAuth configuration
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')

# Flexible redirect URI - can be overridden with environment variable
default_redirect_uri = 'https://dream-mecha-production.up.railway.app/oauth/callback'
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', default_redirect_uri)

# Debug OAuth configuration
print(f"🔧 OAuth Configuration:")
print(f"   CLIENT_ID: {'SET' if DISCORD_CLIENT_ID else 'MISSING'}")
print(f"   CLIENT_SECRET: {'SET' if DISCORD_CLIENT_SECRET else 'MISSING'}")
print(f"   REDIRECT_URI: {DISCORD_REDIRECT_URI}")

# Initialize managers
player_manager = PlayerManager()
fortress_manager = FortressManager()
grid_system = GridSystem()
combat_system = CombatSystem()
shop_system = ShopSystem()

# Input validation schemas
GRID_MOVE_SCHEMA = {
    "type": "object",
    "properties": {
        "piece_id": {"type": "string", "minLength": 1},
        "from_position": {
            "type": "object",
            "properties": {
                "row": {"type": "integer", "minimum": 0, "maximum": 11},
                "col": {"type": "integer", "minimum": 0, "maximum": 11}
            },
            "required": ["row", "col"]
        },
        "to_position": {
            "type": "object", 
            "properties": {
                "row": {"type": "integer", "minimum": 0, "maximum": 11},
                "col": {"type": "integer", "minimum": 0, "maximum": 11}
            },
            "required": ["row", "col"]
        }
    },
    "required": ["piece_id", "from_position", "to_position"]
}

def require_auth(f):
    """Decorator to require Discord authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_json_schema(data, schema):
    """Validate JSON data against schema"""
    try:
        from jsonschema import validate
        validate(instance=data, schema=schema)
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False

@app.route('/')
def index():
    """Main grid interface"""
    print(f"🌐 Web UI: Root route accessed")
    return render_template('index_new.html')  # Use the refactored version

@app.route('/bypass')
def bypass_setup():
    """Bypass first-time setup for testing"""
    print(f"🌐 Web UI: Bypass route accessed")
    return render_template('index_new.html')

@app.route('/test')
def test():
    """Test route to verify Web UI is working"""
    return jsonify({'status': 'Web UI is working!', 'timestamp': datetime.now().isoformat()})

@app.route('/debug/oauth')
def debug_oauth():
    """Debug OAuth configuration"""
    return jsonify({
        'client_id_set': bool(DISCORD_CLIENT_ID),
        'client_secret_set': bool(DISCORD_CLIENT_SECRET),
        'redirect_uri': DISCORD_REDIRECT_URI,
        'session_data': {
            'discord_user_id': session.get('discord_user_id'),
            'discord_username': session.get('discord_username'),
            'session_keys': list(session.keys())
        }
    })

@app.route('/old')
def old_index():
    """Original index for comparison"""
    return render_template('index.html')

@app.route('/bypass')
def bypass():
    """Setup bypass page"""
    return render_template('bypass_setup.html')

@app.route('/login')
def login():
    """Discord OAuth login"""
    if 'discord_user_id' in session:
        return redirect(url_for('index'))
    
    # Check if OAuth is properly configured
    if not DISCORD_CLIENT_ID or not DISCORD_CLIENT_SECRET:
        return "Discord OAuth not configured. Please set DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET environment variables.", 500
    
    # URL-encode the redirect URI properly
    import urllib.parse
    encoded_redirect_uri = urllib.parse.quote(DISCORD_REDIRECT_URI, safe=':/?#[]@!$&\'()*+,;=')
    
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={encoded_redirect_uri}&response_type=code&scope=identify"
    print(f"🔗 OAuth URL: {auth_url}")
    return redirect(auth_url)

@app.route('/oauth/callback')
def oauth_callback():
    """Handle Discord OAuth callback"""
    # Check for error parameters first
    error = request.args.get('error')
    if error:
        error_description = request.args.get('error_description', 'No description provided')
        print(f"❌ OAuth Error: {error} - {error_description}")
        return f"Discord OAuth Error: {error} - {error_description}", 400
    
    code = request.args.get('code')
    if not code:
        print("❌ No authorization code received")
        return "Authorization failed - no code received", 400
    
    print(f"✅ Received auth code: {code[:10]}...")
    
    # Exchange code for token
    token_data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    
    print(f"🔄 Requesting token from Discord...")
    try:
        response = requests.post('https://discord.com/api/oauth2/token', 
                               data=token_data,
                               headers={'Content-Type': 'application/x-www-form-urlencoded'},
                               timeout=10)
        
        print(f"📡 Token response status: {response.status_code}")
        
        if response.status_code != 200:
            error_detail = response.text
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"❌ Response: {error_detail}")
            return f"Token exchange failed (Status {response.status_code}): {error_detail}", 400
        
        token_info = response.json()
        access_token = token_info.get('access_token')
        
        if not access_token:
            print(f"❌ No access token in response: {token_info}")
            return "Failed to get access token from Discord", 400
            
        print(f"✅ Access token received")
        
        # Get user info
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get('https://discord.com/api/users/@me', 
                                   headers=headers, 
                                   timeout=10)
        
        if user_response.status_code != 200:
            print(f"❌ User info request failed: {user_response.status_code} - {user_response.text}")
            return f"Failed to get user info: {user_response.text}", 400
        
        user_info = user_response.json()
        print(f"✅ User info received for: {user_info.get('username', 'Unknown')}")
        
        session['discord_user_id'] = user_info['id']
        session['discord_username'] = user_info['username']
        
        # Ensure player exists
        player_manager.get_or_create_player(user_info['id'], user_info['username'])
        print(f"✅ Player created/updated for {user_info['username']}")
        
        return redirect(url_for('index'))
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error during OAuth: {e}")
        return f"Network error during authentication: {e}", 500
    except Exception as e:
        print(f"❌ Unexpected error during OAuth: {e}")
        return f"Unexpected error during authentication: {e}", 500

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/player/grid', methods=['GET'])
@require_auth
# @limiter.limit("100 per hour")  # DISABLED FOR DEVELOPMENT
def get_player_grid():
    """Get player's current grid state"""
    try:
        player_id = session['discord_user_id']
        player = player_manager.get_player(player_id)
        
        if not player:
            return jsonify({'error': 'Player not found'}), 404
        
        grid_data = grid_system.get_player_grid(player_id)
        return jsonify({
            'grid': grid_data,
            'player': {
                'id': player.player_id,
                'username': player.username,
                'zoltan': player.zoltan,
                'last_active': player.last_active.isoformat() if player.last_active else None
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/grid/move', methods=['POST'])
@require_auth
# @limiter.limit("200 per hour")  # DISABLED FOR DEVELOPMENT
def move_grid_piece():
    """Move a piece on the grid"""
    try:
        # Validate input
        data = request.get_json()
        if not validate_json_schema(data, GRID_MOVE_SCHEMA):
            return jsonify({'error': 'Invalid input format'}), 400
        
        player_id = session['discord_user_id']
        piece_id = data['piece_id']
        from_pos = data['from_position']
        to_pos = data['to_position']
        
        # Validate move
        if not grid_system.is_valid_move(player_id, piece_id, from_pos, to_pos):
            return jsonify({'error': 'Invalid move'}), 400
        
        # Execute move
        success = grid_system.move_piece(player_id, piece_id, from_pos, to_pos)
        if not success:
            return jsonify({'error': 'Move failed'}), 400
        
        # Return updated grid
        updated_grid = grid_system.get_player_grid(player_id)
        return jsonify({
            'success': True,
            'grid': updated_grid
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/shop', methods=['GET'])
# @limiter.limit("50 per hour")  # DISABLED FOR DEVELOPMENT
def get_shop_items():
    """Get available shop items"""
    try:
        player_id = session.get('discord_user_id')
        
        # Generate shop if empty (for testing/first run)
        if not shop_system.daily_inventory:
            player_count = len(player_manager.players) if player_manager.players else 1
            voidstate = 0  # Default voidstate
            shop_system.generate_daily_shop(voidstate, player_count)
        
        # Get both daily items and player trades
        daily_items = shop_system.get_shop_inventory()
        player_trades = shop_system.player_trades
        
        # Combine both types of items
        all_items = daily_items + player_trades
        
        # Convert to frontend-expected format
        formatted_items = []
        for item in all_items:
            # Convert List[List[bool]] to coordinate array format
            shape_coords = []
            for y, row in enumerate(item.shape):
                for x, cell in enumerate(row):
                    if cell:  # If cell is True/occupied
                        shape_coords.append([x, y])
            
            formatted_items.append({
                'piece_id': item.piece_id,
                'name': item.name,
                'pattern': shape_coords,  # Frontend expects coordinate array
                'shape': shape_coords,
                'stats': item.stats,
                'price': item.price,
                'piece_type': item.piece_type,
                'seller_id': getattr(item, 'seller_id', None),
                'icon_path': getattr(item, 'icon_path', None)
            })
        
        return jsonify({'items': formatted_items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/shop/buy', methods=['POST'])
@require_auth
# @limiter.limit("20 per hour")  # DISABLED FOR DEVELOPMENT
def buy_shop_item():
    """Purchase an item from the shop"""
    try:
        data = request.get_json()
        if not data or 'piece_id' not in data:
            return jsonify({'error': 'Missing piece_id'}), 400
        
        player_id = session['discord_user_id']
        piece_id = data['piece_id']
        
        # Get or create player
        player = player_manager.get_player(player_id)
        if not player:
            # Create new player if doesn't exist
            player = player_manager.create_player(player_id, session.get('discord_username', 'Unknown'))
        
        # Attempt to purchase piece
        purchased_piece = shop_system.purchase_piece(player_id, piece_id)
        if not purchased_piece:
            return jsonify({'error': 'Purchase failed - item not available or insufficient funds'}), 400
        
        # Add piece to player's library
        player.add_piece_to_library({
            'piece_id': purchased_piece.piece_id,
            'name': purchased_piece.name,
            'shape': purchased_piece.shape,
            'stats': purchased_piece.stats,
            'piece_type': purchased_piece.piece_type
        })
        
        # Save player data
        player_manager.save_player_data()
        
        return jsonify({
            'success': True,
            'piece_name': purchased_piece.name,
            'player_zoltans': player.zoltans
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/sell-piece', methods=['POST'])
@require_auth
def sell_piece_to_shop():
    """Sell a piece back to the shop for zoltans (piece gets deleted)"""
    try:
        data = request.get_json()
        if not data or 'piece_id' not in data:
            return jsonify({'error': 'Missing piece_id'}), 400
            
        player_id = session['discord_user_id']
        piece_name = data['piece_id']  # piece_id is actually piece name in our system
        
        # Get player
        player = player_manager.get_player(player_id)
        if not player:
            return jsonify({'error': 'Player not found'}), 404
            
        # Find the piece in player's inventory
        piece_to_sell = None
        for piece in player.pieces:
            if piece.name == piece_name:
                piece_to_sell = piece
                break
        
        if not piece_to_sell:
            return jsonify({'error': 'Piece not found in inventory'}), 404
            
        # Calculate sell price (50% of market value, minimum 10 zoltans)
        sell_price = max(10, (piece_to_sell.price or 100) // 2)
        
        # Remove piece from player inventory
        player.pieces.remove(piece_to_sell)
        
        # Add zoltans to player
        player.zoltans += sell_price
        
        # Save player data
        player_manager.save_player_data()
        
        return jsonify({
            'success': True,
            'message': f'Sold {piece_to_sell.name} for {sell_price} zoltans',
            'zoltans_gained': sell_price,
            'player_zoltans': player.zoltans
        })
        
    except Exception as e:
        return jsonify({'error': f'Sell failed: {str(e)}'}), 500

@app.route('/api/player/list-piece', methods=['POST'])
@require_auth
def list_piece_for_sale():
    """List a piece for sale to other players"""
    try:
        data = request.get_json()
        if not data or 'piece_id' not in data:
            return jsonify({'error': 'Missing piece_id'}), 400
            
        player_id = session['discord_user_id']
        piece_name = data['piece_id']
        asking_price = data.get('price', 0)
        
        if asking_price < 0:
            return jsonify({'error': 'Price must be non-negative'}), 400
            
        # Get player
        player = player_manager.get_player(player_id)
        if not player:
            return jsonify({'error': 'Player not found'}), 404
            
        # Find the piece in player's inventory
        piece_to_sell = None
        for piece in player.pieces:
            if piece.name == piece_name:
                piece_to_sell = piece
                break
        
        if not piece_to_sell:
            return jsonify({'error': 'Piece not found in inventory'}), 404
            
        # Create shop piece for player trading
        from core.systems.shop_system import ShopPiece
        trade_piece = ShopPiece(
            piece_id=f"player_trade_{player_id}_{piece_name}",
            name=piece_to_sell.name,
            shape=piece_to_sell.shape,
            stats={
                'hp': piece_to_sell.hp,
                'attack': piece_to_sell.attack, 
                'defense': piece_to_sell.defense,
                'speed': piece_to_sell.speed
            },
            price=asking_price,
            piece_type='stat',
            seller_id=player_id
        )
        
        # Add to shop trading system
        shop_system.player_trades.append(trade_piece)
        
        # Remove from player inventory (it's now in the shop)
        player.pieces.remove(piece_to_sell)
        
        # Save data
        player_manager.save_player_data()
        
        return jsonify({
            'success': True,
            'message': f'Listed {piece_to_sell.name} for {asking_price} zoltans',
            'piece_id': trade_piece.piece_id
        })
        
    except Exception as e:
        return jsonify({'error': f'List failed: {str(e)}'}), 500

@app.route('/api/player/combat', methods=['POST'])
@require_auth
# @limiter.limit("30 per hour")  # DISABLED FOR DEVELOPMENT
def initiate_combat():
    """Initiate combat with an enemy"""
    try:
        player_id = session['discord_user_id']
        
        # Get or create player
        player = player_manager.get_player(player_id)
        if not player:
            return jsonify({'error': 'Player not found'}), 404
        
        # Check if player has a mecha
        if not player.mecha:
            return jsonify({'error': 'No mecha available'}), 400
        
        # Launch mecha for combat
        if player.mecha.state.value != 'launched':
            player.mecha.state.value = 'launched'
            combat_system.add_mecha(player.mecha)
        
        # Initiate combat
        result = combat_system.initiate_combat(player_id)
        
        if not result.get('success', False):
            return jsonify({'error': result.get('error', 'Combat failed')}), 400
        
        # Update player rewards
        if 'player_reward' in result:
            player.earn_zoltans(result['player_reward'])
            player.increment_combat_participation()
            player_manager.save_player_data()
        
        return jsonify({
            'success': True,
            'result': result,
            'player_zoltans': player.zoltans
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/combat/status', methods=['GET'])
@require_auth
# @limiter.limit("100 per hour")  # DISABLED FOR DEVELOPMENT
def get_combat_status():
    """Get current combat status"""
    try:
        status = combat_system.get_combat_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/combat/log', methods=['GET'])
@require_auth
# @limiter.limit("100 per hour")  # DISABLED FOR DEVELOPMENT
def get_combat_log():
    """Get recent combat log entries"""
    try:
        user_id = session['discord_user_id']
        
        # Get combat status with detailed log
        status = combat_system.get_combat_status()
        
        # Add additional combat information
        log_data = {
            'combat_log': status.get('combat_log', []),
            'enemies_remaining': status.get('enemies_remaining', 0),
            'mechas_launched': status.get('mechas_launched', 0),
            'voidstate': status.get('voidstate', 0),
            'state': status.get('state', 'preparing'),
            'last_combat_result': getattr(combat_system, 'last_combat_result', None)
        }
        
        return jsonify(log_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get pilot leaderboard rankings with optional player filter"""
    try:
        from core.managers.leaderboard_manager import leaderboard_manager
        from core.managers.combat_history_manager import combat_history_manager
        
        # Get parameters
        limit = request.args.get('limit', 10, type=int)
        player_id = request.args.get('player_id')
        
        if player_id:
            # Get specific player data
            ranking = leaderboard_manager.get_player_ranking(player_id)
            combat_stats = combat_history_manager.get_player_combat_stats(player_id)
            
            if ranking:
                return jsonify({
                    'player_ranking': ranking,
                    'combat_stats': combat_stats
                })
            else:
                return jsonify({'error': 'Player not found'}), 404
        else:
            # Get all rankings
            rankings = leaderboard_manager.get_leaderboard_rankings(limit=limit)
            summary = leaderboard_manager.get_leaderboard_summary()
            
            return jsonify({
                'rankings': rankings,
                'summary': summary
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/status')
# @limiter.limit("100 per hour")  # DISABLED FOR DEVELOPMENT
def auth_status():
    """Get authentication status"""
    try:
        if 'discord_user_id' in session:
            player_id = session['discord_user_id']
            player = player_manager.get_player(player_id)
            setup_completed = player.setup_completed if player else False
            
            return jsonify({
                'authenticated': True,
                'user_id': player_id,
                'username': session.get('discord_username', 'Unknown'),
                'setup_completed': setup_completed
            })
        else:
            return jsonify({
                'authenticated': False,
                'user_id': None,
                'username': None,
                'setup_completed': False
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/data', methods=['GET'])
@require_auth
# @limiter.limit("100 per hour")  # DISABLED FOR DEVELOPMENT
def get_player_data():
    """Get player data and stats"""
    try:
        player_id = session['discord_user_id']
        player = player_manager.get_player(player_id)
        
        if not player:
            return jsonify({'error': 'Player not found'}), 404
        
        return jsonify({
            'player_id': player.player_id,
            'username': player.username,
            'zoltans': player.zoltans,
            'piece_library': player.piece_library,
            'mecha_stats': player.mecha.stats.__dict__ if player.mecha else None,
            'days_played': player.days_played,
            'total_zoltans_earned': player.total_zoltans_earned,
            'combat_participation': player.combat_participation
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/setup/complete', methods=['POST'])
def complete_setup():
    """Mark player's first-time setup as complete"""
    try:
        if 'discord_user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
            
        player_id = session['discord_user_id']
        player = player_manager.get_player(player_id)
        
        if not player:
            return jsonify({'error': 'Player not found'}), 404
            
        # Update setup status
        player.setup_completed = True
        player_manager.save_player_data()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/pieces', methods=['GET'])
def get_player_pieces():
    """Get player's piece library - works without auth for demo"""
    try:
        # Try to get authenticated player first
        if 'discord_user_id' in session:
            player_id = session['discord_user_id']
            player = player_manager.get_player(player_id)
            if player and player.piece_library:
                return jsonify(player.piece_library)
        
        # Fallback: return starter pieces for demo
        from create_starter_pieces import generate_starter_pieces
        starter_pieces = generate_starter_pieces()
        return jsonify(starter_pieces)
        
    except Exception as e:
        print(f"⚠️ Error loading pieces: {e}")
        # Final fallback: return empty array
        return jsonify([])

@app.route('/api/player/layout', methods=['GET'])
@require_auth
def get_player_layout():
    """Get player's UI layout settings"""
    try:
        player_id = session['discord_user_id']
        player = player_manager.get_player(player_id)
        
        if not player:
            return jsonify({'error': 'Player not found'}), 404
        
        return jsonify({
            'layout': player.ui_layout
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/layout', methods=['POST'])
@require_auth
def save_player_layout():
    """Save player's UI layout settings"""
    try:
        player_id = session['discord_user_id']
        player = player_manager.get_player(player_id)
        
        if not player:
            return jsonify({'error': 'Player not found'}), 404
        
        data = request.get_json()
        if not data or 'layout' not in data:
            return jsonify({'error': 'Layout data required'}), 400
        
        # Validate layout data structure
        layout_data = data['layout']
        if not isinstance(layout_data, dict):
            return jsonify({'error': 'Invalid layout data format'}), 400
        
        # Save layout data
        player.ui_layout = layout_data
        player_manager.save_player_data()
        
        return jsonify({
            'success': True,
            'message': 'Layout saved successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fortress/status', methods=['GET'])
# @limiter.limit("100 per hour")  # DISABLED FOR DEVELOPMENT
def get_fortress_status():
    """Get fortress status"""
    try:
        fortress_status = fortress_manager.get_fortress_status()
        return jsonify({
            'success': True,
            'fortress': fortress_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
# @limiter.limit("100 per hour")  # DISABLED FOR DEVELOPMENT
def status():
    """System status endpoint"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '0.4.0'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('FLASK_ENV') == 'development' or True  # Force debug mode for development
    app.run(host='0.0.0.0', port=port, debug=debug) 