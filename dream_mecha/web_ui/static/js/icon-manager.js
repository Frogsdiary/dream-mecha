/**
 * Centralized Icon Management System
 * Handles icon paths, generation, and fallbacks across the entire application
 */

class IconManager {
    constructor() {
        this.iconCache = new Map();
        this.fallbackIcons = new Map();
        this.loadingIcons = new Set();
        
        // Base paths for different icon types
        this.basePaths = {
            daily: '/static/daily',
            player: '/static/player_pieces', 
            guest: '/static/guest_pieces',
            starter: '/static/starter_pieces'
        };
        
        // Icon generation settings
        this.iconSize = 64;
        this.fallbackColors = {
            hp: '#44ff44',
            attack: '#ff4444', 
            defense: '#ff8800',
            speed: '#ffff44'
        };
    }
    
    /**
     * Get icon URL for a piece with proper fallback handling
     * @param {Object} piece - Piece object with metadata
     * @returns {string} - Icon URL
     */
    getIconUrl(piece) {
        // Try to get from piece data first
        if (piece.icon_path) {
            return this.normalizeIconPath(piece.icon_path);
        }
        
        // Generate based on piece type and date
        const today = new Date().toISOString().split('T')[0];
        const pieceId = this.sanitizePieceId(piece.piece_id || piece.name || 'unknown');
        
        // Determine icon type and path
        let iconPath;
        if (piece.type === 'shop' || piece.seller_id === null) {
            // Daily shop piece
            iconPath = `${this.basePaths.daily}/${today}/icons/${pieceId}.webp`;
        } else if (piece.type === 'player' || piece.type === 'library') {
            // Player piece
            iconPath = `${this.basePaths.player}/${pieceId}.webp`;
        } else {
            // Guest or unknown piece
            iconPath = `${this.basePaths.guest}/${pieceId}.webp`;
        }
        
        return iconPath;
    }
    
    /**
     * Normalize icon path to web-compatible format
     * @param {string} iconPath - Raw icon path
     * @returns {string} - Normalized web path
     */
    normalizeIconPath(iconPath) {
        // If already a web path, return as-is
        if (iconPath.startsWith('/static/') || iconPath.startsWith('http')) {
            return iconPath;
        }
        
        // Convert file system path to web path
        const dailyIndex = iconPath.indexOf('daily');
        if (dailyIndex !== -1) {
            return '/static/' + iconPath.substring(dailyIndex).replace(/\\/g, '/');
        }
        
        // Fallback: assume it's relative to static
        return '/static/' + iconPath.replace(/\\/g, '/');
    }
    
    /**
     * Sanitize piece ID for use in file names
     * @param {string} pieceId - Raw piece ID
     * @returns {string} - Sanitized ID
     */
    sanitizePieceId(pieceId) {
        return pieceId.replace(/[^a-zA-Z0-9_-]/g, '_');
    }
    
    /**
     * Generate fallback icon as data URL for pieces without icons
     * @param {Object} piece - Piece object
     * @returns {string} - Data URL for generated icon
     */
    generateFallbackIcon(piece) {
        const cacheKey = this.getFallbackCacheKey(piece);
        
        // Check cache first
        if (this.fallbackIcons.has(cacheKey)) {
            return this.fallbackIcons.get(cacheKey);
        }
        
        // Create canvas for icon generation
        const canvas = document.createElement('canvas');
        canvas.width = this.iconSize;
        canvas.height = this.iconSize;
        const ctx = canvas.getContext('2d');
        
        // Clear canvas
        ctx.clearRect(0, 0, this.iconSize, this.iconSize);
        
        // Get primary stat and color
        const primaryStat = this.getPrimaryStat(piece.stats || {});
        const color = this.fallbackColors[primaryStat] || this.fallbackColors.hp;
        
        // Draw piece shape
        this.drawPieceShape(ctx, piece.shape, color);
        
        // Convert to data URL
        const dataUrl = canvas.toDataURL('image/png');
        
        // Cache result
        this.fallbackIcons.set(cacheKey, dataUrl);
        
        return dataUrl;
    }
    
    /**
     * Draw piece shape on canvas
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {Array} shape - Piece shape array
     * @param {string} color - Fill color
     */
    drawPieceShape(ctx, shape, color) {
        if (!shape || !Array.isArray(shape)) {
            // Draw single block fallback
            ctx.fillStyle = color;
            ctx.fillRect(this.iconSize/4, this.iconSize/4, this.iconSize/2, this.iconSize/2);
            return;
        }
        
        // Convert shape to coordinates
        const coords = this.shapeToCoordinates(shape);
        
        if (coords.length === 0) {
            // Draw single block fallback
            ctx.fillStyle = color;
            ctx.fillRect(this.iconSize/4, this.iconSize/4, this.iconSize/2, this.iconSize/2);
            return;
        }
        
        // Calculate bounds and scaling
        const bounds = this.calculateShapeBounds(coords);
        const padding = this.iconSize / 8;
        const availableSize = this.iconSize - (2 * padding);
        const scaleX = availableSize / Math.max(1, bounds.width);
        const scaleY = availableSize / Math.max(1, bounds.height);
        const scale = Math.min(scaleX, scaleY);
        const cellSize = Math.max(2, Math.floor(scale));
        
        // Calculate offset to center the shape
        const shapeWidth = bounds.width * cellSize;
        const shapeHeight = bounds.height * cellSize;
        const offsetX = (this.iconSize - shapeWidth) / 2;
        const offsetY = (this.iconSize - shapeHeight) / 2;
        
        // Draw each block
        ctx.fillStyle = color;
        coords.forEach(([x, y]) => {
            const drawX = offsetX + (x - bounds.minX) * cellSize;
            const drawY = offsetY + (y - bounds.minY) * cellSize;
            ctx.fillRect(drawX, drawY, cellSize - 1, cellSize - 1);
        });
        
        // Add border for definition
        if (cellSize > 3) {
            ctx.strokeStyle = this.darkenColor(color, 0.3);
            ctx.lineWidth = 1;
            coords.forEach(([x, y]) => {
                const drawX = offsetX + (x - bounds.minX) * cellSize;
                const drawY = offsetY + (y - bounds.minY) * cellSize;
                ctx.strokeRect(drawX, drawY, cellSize - 1, cellSize - 1);
            });
        }
    }
    
    /**
     * Convert shape array to coordinates
     * @param {Array} shape - Shape in various formats
     * @returns {Array} - Array of [x, y] coordinates
     */
    shapeToCoordinates(shape) {
        if (!shape || !Array.isArray(shape)) return [];
        
        // Check if it's already coordinate format [[x,y], [x,y], ...]
        if (shape.length > 0 && Array.isArray(shape[0]) && typeof shape[0][0] === 'number') {
            return shape;
        }
        
        // Convert 2D boolean array to coordinates
        const coords = [];
        for (let y = 0; y < shape.length; y++) {
            if (!Array.isArray(shape[y])) continue;
            for (let x = 0; x < shape[y].length; x++) {
                if (shape[y][x] === true) {
                    coords.push([x, y]);
                }
            }
        }
        
        return coords;
    }
    
    /**
     * Calculate bounds of shape coordinates
     * @param {Array} coords - Array of [x, y] coordinates  
     * @returns {Object} - Bounds object with minX, maxX, minY, maxY, width, height
     */
    calculateShapeBounds(coords) {
        if (coords.length === 0) {
            return { minX: 0, maxX: 0, minY: 0, maxY: 0, width: 1, height: 1 };
        }
        
        const xs = coords.map(([x, y]) => x);
        const ys = coords.map(([x, y]) => y);
        
        const minX = Math.min(...xs);
        const maxX = Math.max(...xs);
        const minY = Math.min(...ys);
        const maxY = Math.max(...ys);
        
        return {
            minX,
            maxX, 
            minY,
            maxY,
            width: maxX - minX + 1,
            height: maxY - minY + 1
        };
    }
    
    /**
     * Get primary stat from stats object
     * @param {Object} stats - Stats object
     * @returns {string} - Primary stat name
     */
    getPrimaryStat(stats) {
        const statTypes = ['hp', 'attack', 'defense', 'speed'];
        let maxStat = 'hp';
        let maxValue = 0;
        
        for (const stat of statTypes) {
            const value = stats[stat] || 0;
            if (value > maxValue) {
                maxValue = value;
                maxStat = stat;
            }
        }
        
        return maxStat;
    }
    
    /**
     * Darken a hex color by a percentage
     * @param {string} color - Hex color (e.g., "#ff4444")
     * @param {number} percent - Percentage to darken (0-1)
     * @returns {string} - Darkened hex color
     */
    darkenColor(color, percent) {
        // Remove # if present
        const hex = color.replace('#', '');
        
        // Parse RGB
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        
        // Darken
        const newR = Math.floor(r * (1 - percent));
        const newG = Math.floor(g * (1 - percent));
        const newB = Math.floor(b * (1 - percent));
        
        // Convert back to hex
        return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
    }
    
    /**
     * Get cache key for fallback icon
     * @param {Object} piece - Piece object
     * @returns {string} - Cache key
     */
    getFallbackCacheKey(piece) {
        const shape = JSON.stringify(piece.shape || []);
        const stats = JSON.stringify(piece.stats || {});
        return `${shape}_${stats}`;
    }
    
    /**
     * Create image element with proper error handling and fallback
     * @param {Object} piece - Piece object
     * @param {Object} options - Options (className, alt, etc.)
     * @returns {HTMLImageElement} - Configured image element
     */
    createPieceImage(piece, options = {}) {
        const img = document.createElement('img');
        const iconUrl = this.getIconUrl(piece);
        
        // Set basic attributes
        img.src = iconUrl;
        img.alt = options.alt || piece.name || 'Piece';
        img.className = options.className || 'piece-icon';
        
        // Add error handling with fallback
        img.onerror = () => {
            if (!img.dataset.fallbackAttempted) {
                img.dataset.fallbackAttempted = 'true';
                img.src = this.generateFallbackIcon(piece);
            }
        };
        
        return img;
    }
    
    /**
     * Preload icon and return promise
     * @param {string} url - Icon URL
     * @returns {Promise} - Resolves when loaded or fails
     */
    preloadIcon(url) {
        if (this.iconCache.has(url)) {
            return Promise.resolve(url);
        }
        
        if (this.loadingIcons.has(url)) {
            // Return existing promise for this URL
            return new Promise((resolve, reject) => {
                const checkLoading = () => {
                    if (this.iconCache.has(url)) {
                        resolve(url);
                    } else if (!this.loadingIcons.has(url)) {
                        reject(new Error('Icon loading failed'));
                    } else {
                        setTimeout(checkLoading, 50);
                    }
                };
                checkLoading();
            });
        }
        
        this.loadingIcons.add(url);
        
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                this.iconCache.set(url, true);
                this.loadingIcons.delete(url);
                resolve(url);
            };
            img.onerror = () => {
                this.loadingIcons.delete(url);
                reject(new Error(`Failed to load icon: ${url}`));
            };
            img.src = url;
        });
    }
    
    /**
     * Clear cache (useful for testing or memory management)
     */
    clearCache() {
        this.iconCache.clear();
        this.fallbackIcons.clear();
        this.loadingIcons.clear();
    }
    
    /**
     * Get cache statistics
     * @returns {Object} - Cache stats
     */
    getCacheStats() {
        return {
            iconsCached: this.iconCache.size,
            fallbacksCached: this.fallbackIcons.size,
            currentlyLoading: this.loadingIcons.size
        };
    }
}

// Global instance
window.iconManager = new IconManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IconManager;
}