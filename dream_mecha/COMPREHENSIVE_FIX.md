# COMPREHENSIVE FIX PLAN

## Issues Identified:

### 1. SHOP AUTH PROBLEM
- The `/api/player/shop` endpoint is redirecting to OAuth
- This happens because there's likely a missing import or the Flask app is using a cached route
- **Fix:** Restart the Flask server or check for global middleware

### 2. PIECE COLORS ISSUE  
- Starter pieces have correct stats (HP: 337, others: 0)
- The `getStatType` function should return 'hp' for HP pieces
- All pieces showing red means the function is defaulting to 'attack'
- **Fix:** Debug the getStatType function output

### 3. LIBRARY LAYOUT
- 2-column grid conflicts with existing piece-item styling
- **Fix:** Adjust piece-item CSS to work with grid

### 4. GRID CONTROLS
- **Status:** FIXED - now left-aligned row

## Comprehensive Solution:

1. Fix shop endpoint by ensuring no auth decorators
2. Fix piece colors by checking CSS selectors
3. Fix library layout by adjusting piece sizing
4. Add proper mobile responsive design