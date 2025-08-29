/**
 * Grid-Piece Integration Bridge
 * Connects piece browser to grid system with proper placement and visual feedback
 */

class GridIntegration {
    constructor(mechaGrid) {
        this.mechaGrid = mechaGrid;
        this.placementMode = false;
        this.selectedPieceForPlacement = null;
        this.previewElement = null;
        this.currentHoverPosition = null;
        
        // Error and success feedback
        this.feedbackTimeout = null;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Listen for grid cell hover events
        document.addEventListener('mouseover', (e) => {
            if (e.target.classList.contains('grid-cell') && this.placementMode) {
                this.handleGridHover(e);
            }
        });
        
        // Listen for grid cell click events  
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('grid-cell') && this.placementMode) {
                this.handleGridClick(e);
            }
        });
        
        // Listen for escape key to cancel placement
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.placementMode) {
                this.cancelPlacement();
            }
        });
        
        // Listen for mouse leave to hide preview
        document.addEventListener('mouseleave', (e) => {
            if (e.target.closest('.mecha-grid-full') && this.placementMode) {
                this.hidePreview();
            }
        });
    }
    
    /**
     * Start piece placement mode
     * @param {Object} piece - Piece to place
     * @returns {boolean} - True if placement mode started successfully
     */
    startPiecePlacement(piece) {
        if (!piece || !this.mechaGrid) {
            this.showError('Cannot start placement: invalid piece or grid system');
            return false;
        }
        
        // Convert piece to grid-compatible format
        const gridPiece = this.convertPieceToGridFormat(piece);
        if (!gridPiece) {
            this.showError('Cannot place piece: invalid format');
            return false;
        }
        
        console.log('🎯 Starting piece placement for:', piece.name || piece.id);
        
        this.placementMode = true;
        this.selectedPieceForPlacement = gridPiece;
        
        // Set active piece in grid system
        this.mechaGrid.setActivePiece(gridPiece);
        
        // Add visual feedback to UI
        this.showPlacementInstructions();
        
        // Add placement mode class to grid
        const gridElement = document.getElementById('mechaGridFull');
        if (gridElement) {
            gridElement.classList.add('placement-mode');
        }
        
        return true;
    }
    
    /**
     * Convert piece from browser format to grid format
     * @param {Object} piece - Piece from browser
     * @returns {Object} - Grid-compatible piece
     */
    convertPieceToGridFormat(piece) {
        try {
            // Convert shape to grid coordinate format
            const gridShape = this.convertShapeToCoordinates(piece.shape);
            
            // Create grid piece object
            const gridPiece = {
                id: piece.id || `piece_${Date.now()}`,
                name: piece.name || 'Unknown Piece',
                shape: gridShape,
                hp: piece.stats?.hp || 0,
                attack: piece.stats?.attack || 0,
                defense: piece.stats?.defense || 0,
                speed: piece.stats?.speed || 0,
                blockCount: this.countBlocks(gridShape),
                placed: false,
                x: 0,
                y: 0,
                sourceType: piece.type || 'library' // Track source for analytics
            };
            
            return gridPiece;
        } catch (error) {
            console.error('Error converting piece to grid format:', error);
            return null;
        }
    }
    
    /**
     * Convert shape array to coordinate format expected by grid
     * @param {Array} shape - Shape in various formats
     * @returns {Array} - Array of [x, y] coordinates
     */
    convertShapeToCoordinates(shape) {
        if (!shape || !Array.isArray(shape)) {
            return [[0, 0]]; // Single block fallback
        }
        
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
        
        return coords.length > 0 ? coords : [[0, 0]];
    }
    
    /**
     * Count blocks in coordinate shape
     * @param {Array} shape - Array of [x, y] coordinates
     * @returns {number} - Block count
     */
    countBlocks(shape) {
        return Array.isArray(shape) ? shape.length : 1;
    }
    
    /**
     * Handle grid hover for placement preview
     * @param {Event} e - Mouse event
     */
    handleGridHover(e) {
        if (!this.placementMode || !this.selectedPieceForPlacement) return;
        
        const cell = e.target;
        const x = parseInt(cell.dataset.x);
        const y = parseInt(cell.dataset.y);
        
        if (this.currentHoverPosition?.x === x && this.currentHoverPosition?.y === y) {
            return; // Same position, no need to update
        }
        
        this.currentHoverPosition = { x, y };
        
        // Update preview
        this.showPlacementPreview(x, y);
    }
    
    /**
     * Show placement preview at coordinates
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate  
     */
    showPlacementPreview(x, y) {
        this.hidePreview(); // Clear any existing preview
        
        const canPlace = this.mechaGrid.canPlacePiece(this.selectedPieceForPlacement, x, y);
        
        // Highlight affected cells
        this.selectedPieceForPlacement.shape.forEach(([dx, dy]) => {
            const cellX = x + dx;
            const cellY = y + dy;
            const cell = document.querySelector(`[data-x="${cellX}"][data-y="${cellY}"]`);
            
            if (cell) {
                if (canPlace) {
                    cell.classList.add('placement-preview', 'valid');
                } else {
                    cell.classList.add('placement-preview', 'invalid');
                }
            }
        });
        
        // Update cursor
        const gridElement = document.getElementById('mechaGridFull');
        if (gridElement) {
            gridElement.style.cursor = canPlace ? 'pointer' : 'not-allowed';
        }
    }
    
    /**
     * Hide placement preview
     */
    hidePreview() {
        document.querySelectorAll('.placement-preview').forEach(cell => {
            cell.classList.remove('placement-preview', 'valid', 'invalid');
        });
        
        const gridElement = document.getElementById('mechaGridFull');
        if (gridElement) {
            gridElement.style.cursor = this.placementMode ? 'crosshair' : '';
        }
    }
    
    /**
     * Handle grid click for piece placement
     * @param {Event} e - Click event
     */
    handleGridClick(e) {
        if (!this.placementMode || !this.selectedPieceForPlacement) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        const cell = e.target;
        const x = parseInt(cell.dataset.x);
        const y = parseInt(cell.dataset.y);
        
        this.attemptPiecePlacement(x, y);
    }
    
    /**
     * Attempt to place piece at coordinates
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @returns {boolean} - True if placement successful
     */
    attemptPiecePlacement(x, y) {
        if (!this.mechaGrid.canPlacePiece(this.selectedPieceForPlacement, x, y)) {
            this.showError('Cannot place piece here - position is blocked or outside active area');
            return false;
        }
        
        try {
            // Attempt placement
            const success = this.mechaGrid.placePiece(this.selectedPieceForPlacement, x, y);
            
            if (success) {
                this.showSuccess(`${this.selectedPieceForPlacement.name} placed successfully!`);
                this.completePlacement();
                
                // Notify other systems
                this.notifyPlacementComplete(this.selectedPieceForPlacement);
                
                return true;
            } else {
                this.showError('Failed to place piece - placement system error');
                return false;
            }
        } catch (error) {
            console.error('Error placing piece:', error);
            this.showError(`Placement failed: ${error.message}`);
            return false;
        }
    }
    
    /**
     * Complete placement and clean up
     */
    completePlacement() {
        this.placementMode = false;
        this.selectedPieceForPlacement = null;
        this.currentHoverPosition = null;
        
        // Clean up UI
        this.hidePreview();
        this.hidePlacementInstructions();
        
        // Remove placement mode class
        const gridElement = document.getElementById('mechaGridFull');
        if (gridElement) {
            gridElement.classList.remove('placement-mode');
            gridElement.style.cursor = '';
        }
        
        // Clear active piece in grid system
        this.mechaGrid.clearActivePiece();
        
        console.log('🎯 Piece placement completed');
    }
    
    /**
     * Cancel piece placement
     */
    cancelPlacement() {
        this.showInfo('Piece placement cancelled');
        this.completePlacement();
    }
    
    /**
     * Show placement instructions to user
     */
    showPlacementInstructions() {
        const instructionElement = document.createElement('div');
        instructionElement.id = 'placement-instructions';
        instructionElement.className = 'placement-instructions';
        instructionElement.innerHTML = `
            <div class="instruction-content">
                <span class="instruction-text">Click on the grid to place "${this.selectedPieceForPlacement.name}"</span>
                <button class="instruction-cancel" onclick="gridIntegration.cancelPlacement()">Cancel</button>
            </div>
        `;
        
        // Remove any existing instructions
        this.hidePlacementInstructions();
        
        // Add to page
        document.body.appendChild(instructionElement);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            this.hidePlacementInstructions();
        }, 10000);
    }
    
    /**
     * Hide placement instructions
     */
    hidePlacementInstructions() {
        const existing = document.getElementById('placement-instructions');
        if (existing) {
            existing.remove();
        }
    }
    
    /**
     * Show success message
     * @param {string} message - Success message
     */
    showSuccess(message) {
        this.showFeedback(message, 'success');
    }
    
    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        this.showFeedback(message, 'error');
    }
    
    /**
     * Show info message
     * @param {string} message - Info message
     */
    showInfo(message) {
        this.showFeedback(message, 'info');
    }
    
    /**
     * Show feedback message to user
     * @param {string} message - Message to show
     * @param {string} type - Message type (success, error, info)
     */
    showFeedback(message, type = 'info') {
        // Clear any existing feedback
        this.clearFeedback();
        
        const feedbackElement = document.createElement('div');
        feedbackElement.id = 'grid-feedback';
        feedbackElement.className = `grid-feedback ${type}`;
        feedbackElement.textContent = message;
        
        // Add to page
        document.body.appendChild(feedbackElement);
        
        // Auto-hide after delay
        const delay = type === 'error' ? 5000 : 3000;
        this.feedbackTimeout = setTimeout(() => {
            this.clearFeedback();
        }, delay);
        
        console.log(`Grid Feedback [${type.toUpperCase()}]:`, message);
    }
    
    /**
     * Clear feedback message
     */
    clearFeedback() {
        if (this.feedbackTimeout) {
            clearTimeout(this.feedbackTimeout);
            this.feedbackTimeout = null;
        }
        
        const existing = document.getElementById('grid-feedback');
        if (existing) {
            existing.remove();
        }
    }
    
    /**
     * Notify other systems of placement completion
     * @param {Object} placedPiece - The piece that was placed
     */
    notifyPlacementComplete(placedPiece) {
        // Update stats display
        if (this.mechaGrid.updateStats) {
            this.mechaGrid.updateStats();
        }
        
        // Refresh piece browsers if available
        if (window.pieceBrowsers) {
            Object.values(window.pieceBrowsers).forEach(browser => {
                if (browser.refresh) {
                    browser.refresh();
                }
            });
        }
        
        // Dispatch custom event for other systems
        const event = new CustomEvent('pieceePlaced', {
            detail: {
                piece: placedPiece,
                timestamp: Date.now()
            }
        });
        document.dispatchEvent(event);
    }
    
    /**
     * Get current placement status
     * @returns {Object} - Status information
     */
    getStatus() {
        return {
            placementMode: this.placementMode,
            selectedPiece: this.selectedPieceForPlacement?.name || null,
            canPlace: this.selectedPieceForPlacement && this.currentHoverPosition ?
                this.mechaGrid.canPlacePiece(
                    this.selectedPieceForPlacement,
                    this.currentHoverPosition.x,
                    this.currentHoverPosition.y
                ) : null
        };
    }
}

// CSS for integration components - inject into page
const integrationCSS = `
    .placement-mode {
        cursor: crosshair !important;
    }
    
    .placement-preview.valid {
        background-color: rgba(68, 255, 68, 0.4) !important;
        border: 2px solid #44ff44 !important;
    }
    
    .placement-preview.invalid {
        background-color: rgba(255, 68, 68, 0.4) !important;
        border: 2px solid #ff4444 !important;
    }
    
    .placement-instructions {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 12px 16px;
        border-radius: 4px;
        border: 1px solid #44ff44;
        font-family: monospace;
        animation: slideInRight 0.3s ease;
    }
    
    .instruction-content {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .instruction-cancel {
        background: #ff4444;
        color: white;
        border: none;
        padding: 4px 8px;
        border-radius: 2px;
        cursor: pointer;
        font-family: monospace;
        font-size: 12px;
    }
    
    .instruction-cancel:hover {
        background: #ff6666;
    }
    
    .grid-feedback {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        padding: 12px 16px;
        border-radius: 4px;
        font-family: monospace;
        font-weight: bold;
        animation: slideInUp 0.3s ease;
    }
    
    .grid-feedback.success {
        background: rgba(68, 255, 68, 0.9);
        color: black;
        border: 1px solid #44ff44;
    }
    
    .grid-feedback.error {
        background: rgba(255, 68, 68, 0.9);
        color: white;
        border: 1px solid #ff4444;
    }
    
    .grid-feedback.info {
        background: rgba(255, 255, 68, 0.9);
        color: black;
        border: 1px solid #ffff44;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideInUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
`;

// Inject CSS
const styleElement = document.createElement('style');
styleElement.textContent = integrationCSS;
document.head.appendChild(styleElement);

// Export for global use
window.GridIntegration = GridIntegration;