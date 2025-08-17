/**
 * Unified Piece Browser Component
 * Handles both piece library (player pieces) and shop (daily pieces) with pagination and filtering
 */

class PieceBrowser {
    constructor(containerId, mode = 'library') {
        this.containerId = containerId;
        this.mode = mode; // 'library' or 'shop'
        this.currentPage = 1;
        this.piecesPerPage = 20;
        this.allPieces = [];
        this.filteredPieces = [];
        this.sortAscending = false; // Default to descending (high to low)
        
        // Filter state
        this.filters = {
            blockCount: { min: 1, max: 120 },
            sortBy: 'blocks' // 'hp', 'attack', 'defense', 'speed', 'zoltan', 'blocks'
        };
        
        this.init();
    }
    
    init() {
        this.createUI();
        this.bindEvents();
        this.loadPieces();
    }
    
    createUI() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }
        
        container.innerHTML = `
            <div class="piece-browser">
                <!-- Header with filters -->
                <div class="piece-browser-header">
                    <h3>${this.mode === 'library' ? 'Piece Library' : 'RBHI Shop'}</h3>
                    
                    <div class="browser-filters">
                        <!-- Block count slider -->
                        <div class="filter-group">
                            <label>Block Count: <span id="blockCountDisplay_${this.containerId}">1 - 120</span></label>
                            <div class="range-slider-container">
                                <input type="range" id="blockCountMin_${this.containerId}" min="1" max="120" value="1" class="range-slider">
                                <input type="range" id="blockCountMax_${this.containerId}" min="1" max="120" value="120" class="range-slider">
                            </div>
                        </div>
                        
                        <!-- Sort dropdown with toggle -->
                        <div class="filter-group">
                            <label>Sort by:</label>
                            <div class="sort-controls">
                                <select id="sortBy_${this.containerId}" class="filter-select">
                                    <option value="blocks">Block Count</option>
                                    <option value="hp">HP</option>
                                    <option value="attack">Attack</option>
                                    <option value="defense">Defense</option>
                                    <option value="speed">Speed</option>
                                    <option value="zoltan">Zoltan Price</option>
                                </select>
                                <button id="sortToggle_${this.containerId}" class="sort-toggle" title="Toggle sort direction">
                                    ↓
                                </button>
                            </div>
                        </div>
                        
                        <!-- Reset filters -->
                        <button id="resetFilters_${this.containerId}" class="filter-reset-btn">Reset</button>
                    </div>
                </div>
                
                <!-- Pieces grid -->
                <div class="pieces-grid" id="piecesGrid_${this.containerId}">
                    <!-- Pieces will be rendered here -->
                </div>
                
                <!-- Pagination -->
                <div class="pagination" id="pagination_${this.containerId}">
                    <!-- Pagination controls will be rendered here -->
                </div>
                
                <!-- Loading state -->
                <div class="loading-state" id="loadingState_${this.containerId}" style="display: none;">
                    <div class="loading-spinner"></div>
                    <p>Loading pieces...</p>
                </div>
                
                <!-- Empty state -->
                <div class="empty-state" id="emptyState_${this.containerId}" style="display: none;">
                    <p>No pieces found matching your criteria.</p>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        // Block count range sliders
        const minSlider = document.getElementById(`blockCountMin_${this.containerId}`);
        const maxSlider = document.getElementById(`blockCountMax_${this.containerId}`);
        const display = document.getElementById(`blockCountDisplay_${this.containerId}`);
        
        const updateBlockCountFilter = () => {
            const min = parseInt(minSlider.value);
            const max = parseInt(maxSlider.value);
            
            // Ensure min <= max
            if (min > max) {
                if (minSlider === document.activeElement) {
                    maxSlider.value = min;
                } else {
                    minSlider.value = max;
                }
            }
            
            this.filters.blockCount.min = parseInt(minSlider.value);
            this.filters.blockCount.max = parseInt(maxSlider.value);
            display.textContent = `${this.filters.blockCount.min} - ${this.filters.blockCount.max}`;
            
            this.applyFilters();
        };
        
        minSlider.addEventListener('input', updateBlockCountFilter);
        maxSlider.addEventListener('input', updateBlockCountFilter);
        
        // Sort controls
        document.getElementById(`sortBy_${this.containerId}`).addEventListener('change', (e) => {
            this.filters.sortBy = e.target.value;
            this.applyFilters();
        });
        
        document.getElementById(`sortToggle_${this.containerId}`).addEventListener('click', () => {
            this.sortAscending = !this.sortAscending;
            const toggle = document.getElementById(`sortToggle_${this.containerId}`);
            toggle.textContent = this.sortAscending ? '↑' : '↓';
            toggle.title = this.sortAscending ? 'High to Low' : 'Low to High';
            this.applyFilters();
        });
        
        // Reset filters
        document.getElementById(`resetFilters_${this.containerId}`).addEventListener('click', () => {
            this.resetFilters();
        });
    }
    
    resetFilters() {
        // Reset filter state
        this.filters.blockCount.min = 1;
        this.filters.blockCount.max = 120;
        this.filters.sortBy = 'blocks';
        this.sortAscending = false;
        this.currentPage = 1;
        
        // Reset UI
        document.getElementById(`blockCountMin_${this.containerId}`).value = 1;
        document.getElementById(`blockCountMax_${this.containerId}`).value = 120;
        document.getElementById(`blockCountDisplay_${this.containerId}`).textContent = '1 - 120';
        document.getElementById(`sortBy_${this.containerId}`).value = 'blocks';
        document.getElementById(`sortToggle_${this.containerId}`).textContent = '↓';
        
        this.applyFilters();
    }
    
    async loadPieces() {
        this.showLoading(true);
        
        try {
            let url, processFunction;
            
            if (this.mode === 'library') {
                url = '/api/player/pieces';
                processFunction = this.processLibraryPieces.bind(this);
            } else {
                url = '/api/player/shop';
                processFunction = this.processShopPieces.bind(this);
            }
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.allPieces = processFunction(data);
            this.applyFilters();
            
        } catch (error) {
            console.error('Failed to load pieces:', error);
            this.showError(`Failed to load ${this.mode}: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }
    
    processLibraryPieces(data) {
        // Process player pieces from library API
        return data.map(piece => ({
            id: piece.name || 'Unknown',
            name: piece.name || 'Unknown Piece',
            blockCount: this.countBlocks(piece.shape),
            stats: {
                hp: piece.hp || 0,
                attack: piece.attack || 0,
                defense: piece.defense || 0,
                speed: piece.speed || 0
            },
            zoltan: piece.price || 0,
            shape: piece.shape,
            iconUrl: this.getIconUrl(piece),
            type: 'player'
        }));
    }
    
    processShopPieces(data) {
        // Process shop pieces from shop API
        const items = data.items || [];
        return items.map(item => ({
            id: item.piece_id || 'Unknown',
            name: item.name || 'Unknown Piece',
            blockCount: this.countBlocks(item.shape),
            stats: {
                hp: item.stats?.hp || 0,
                attack: item.stats?.attack || 0,
                defense: item.stats?.defense || 0,
                speed: item.stats?.speed || 0
            },
            zoltan: item.price || 0,
            shape: item.shape,
            iconUrl: this.getIconUrl(item),
            type: 'shop',
            sellerId: item.seller_id
        }));
    }
    
    countBlocks(shape) {
        if (!shape || !Array.isArray(shape)) return 0;
        
        // Check if it's coordinate array format [[x,y], [x,y], ...]
        if (shape.length > 0 && Array.isArray(shape[0]) && typeof shape[0][0] === 'number') {
            return shape.length; // Each coordinate is one block
        }
        
        // Check if it's 2D boolean array format
        return shape.reduce((total, row) => {
            if (!Array.isArray(row)) return total;
            return total + row.filter(cell => cell === true).length;
        }, 0);
    }
    
    getIconUrl(piece) {
        // Try to get icon URL from piece data
        if (piece.icon_path) {
            // If it's already a web path, use as-is
            if (piece.icon_path.startsWith('/static/') || piece.icon_path.startsWith('http')) {
                return piece.icon_path;
            }
            // Convert file path to web path - look for 'daily' in the path
            const dailyIndex = piece.icon_path.indexOf('daily');
            if (dailyIndex !== -1) {
                return '/static/' + piece.icon_path.substring(dailyIndex);
            }
        }
        
        // Fallback to generated icon path based on piece ID and date
        const today = new Date().toISOString().split('T')[0];
        const iconName = (piece.piece_id || piece.name || 'unknown').replace(/[^a-zA-Z0-9_-]/g, '_');
        return `/static/daily/${today}/icons/${iconName}.webp`;
    }
    
    applyFilters() {
        // Filter by block count
        this.filteredPieces = this.allPieces.filter(piece => {
            return piece.blockCount >= this.filters.blockCount.min && 
                   piece.blockCount <= this.filters.blockCount.max;
        });
        
        // Sort pieces
        this.sortPieces();
        
        // Reset to first page
        this.currentPage = 1;
        
        // Render
        this.renderPieces();
        this.renderPagination();
    }
    
    sortPieces() {
        const sortBy = this.filters.sortBy;
        
        this.filteredPieces.sort((a, b) => {
            let valueA, valueB;
            
            switch (sortBy) {
                case 'blocks':
                    valueA = a.blockCount;
                    valueB = b.blockCount;
                    break;
                case 'zoltan':
                    valueA = a.zoltan;
                    valueB = b.zoltan;
                    break;
                case 'hp':
                case 'attack':
                case 'defense':
                case 'speed':
                    valueA = a.stats[sortBy];
                    valueB = b.stats[sortBy];
                    break;
                default:
                    valueA = a.blockCount;
                    valueB = b.blockCount;
            }
            
            const comparison = valueA - valueB;
            return this.sortAscending ? comparison : -comparison;
        });
    }
    
    renderPieces() {
        const grid = document.getElementById(`piecesGrid_${this.containerId}`);
        const emptyState = document.getElementById(`emptyState_${this.containerId}`);
        
        if (this.filteredPieces.length === 0) {
            grid.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }
        
        grid.style.display = 'grid';
        emptyState.style.display = 'none';
        
        // Calculate pagination
        const startIndex = (this.currentPage - 1) * this.piecesPerPage;
        const endIndex = startIndex + this.piecesPerPage;
        const pagePieces = this.filteredPieces.slice(startIndex, endIndex);
        
        // Render pieces
        grid.innerHTML = pagePieces.map(piece => this.renderPieceCard(piece)).join('');
        
        // Add click handlers
        this.bindPieceEvents();
    }
    
    renderPieceCard(piece) {
        const primaryStat = this.getPrimaryStat(piece.stats);
        const statClass = primaryStat ? `stat-${primaryStat}` : '';
        
        return `
            <div class="piece-card ${statClass}" data-piece-id="${piece.id}">
                <div class="piece-icon">
                    <img src="${piece.iconUrl}" alt="${piece.name}" 
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div class="piece-icon-fallback" style="display: none;">
                        <span class="block-count">${piece.blockCount}</span>
                    </div>
                </div>
                
                <div class="piece-info">
                    <h4 class="piece-name">${piece.name}</h4>
                    <div class="piece-stats">
                        ${piece.stats.hp > 0 ? `<span class="stat-hp">HP: ${piece.stats.hp.toLocaleString()}</span>` : ''}
                        ${piece.stats.attack > 0 ? `<span class="stat-attack">ATK: ${piece.stats.attack.toLocaleString()}</span>` : ''}
                        ${piece.stats.defense > 0 ? `<span class="stat-defense">DEF: ${piece.stats.defense.toLocaleString()}</span>` : ''}
                        ${piece.stats.speed > 0 ? `<span class="stat-speed">SPD: ${piece.stats.speed.toLocaleString()}</span>` : ''}
                    </div>
                    <div class="piece-meta">
                        <span class="block-count">${piece.blockCount} blocks</span>
                        ${piece.zoltan > 0 ? `<span class="piece-price">${piece.zoltan.toLocaleString()} Z</span>` : ''}
                    </div>
                </div>
                
                <div class="piece-actions">
                    ${this.renderPieceActions(piece)}
                </div>
            </div>
        `;
    }
    
    renderPieceActions(piece) {
        if (this.mode === 'library') {
            return `
                <button class="action-btn place-btn" data-action="place" data-piece-id="${piece.id}">
                    Place
                </button>
                <button class="action-btn sell-btn" data-action="sell" data-piece-id="${piece.id}">
                    Sell
                </button>
            `;
        } else {
            return `
                <button class="action-btn buy-btn" data-action="buy" data-piece-id="${piece.id}">
                    Buy
                </button>
            `;
        }
    }
    
    getPrimaryStat(stats) {
        const statValues = {
            hp: stats.hp || 0,
            attack: stats.attack || 0,
            defense: stats.defense || 0,
            speed: stats.speed || 0
        };
        
        let maxStat = 'hp';
        let maxValue = 0;
        
        for (const [stat, value] of Object.entries(statValues)) {
            if (value > maxValue) {
                maxValue = value;
                maxStat = stat;
            }
        }
        
        return maxValue > 0 ? maxStat : null;
    }
    
    renderPagination() {
        const pagination = document.getElementById(`pagination_${this.containerId}`);
        const totalPages = Math.ceil(this.filteredPieces.length / this.piecesPerPage);
        
        if (totalPages <= 1) {
            pagination.style.display = 'none';
            return;
        }
        
        pagination.style.display = 'flex';
        
        let paginationHTML = '';
        
        // Previous button
        if (this.currentPage > 1) {
            paginationHTML += `<button class="page-btn" data-page="${this.currentPage - 1}">‹ Previous</button>`;
        }
        
        // Page numbers
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);
        
        if (startPage > 1) {
            paginationHTML += `<button class="page-btn" data-page="1">1</button>`;
            if (startPage > 2) {
                paginationHTML += `<span class="page-ellipsis">...</span>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === this.currentPage ? 'active' : '';
            paginationHTML += `<button class="page-btn ${activeClass}" data-page="${i}">${i}</button>`;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `<span class="page-ellipsis">...</span>`;
            }
            paginationHTML += `<button class="page-btn" data-page="${totalPages}">${totalPages}</button>`;
        }
        
        // Next button
        if (this.currentPage < totalPages) {
            paginationHTML += `<button class="page-btn" data-page="${this.currentPage + 1}">Next ›</button>`;
        }
        
        // Results info
        const startResult = (this.currentPage - 1) * this.piecesPerPage + 1;
        const endResult = Math.min(this.currentPage * this.piecesPerPage, this.filteredPieces.length);
        paginationHTML += `<div class="pagination-info">Showing ${startResult}-${endResult} of ${this.filteredPieces.length} pieces</div>`;
        
        pagination.innerHTML = paginationHTML;
        
        // Bind pagination events
        pagination.querySelectorAll('.page-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = parseInt(e.target.dataset.page);
                if (page && page !== this.currentPage) {
                    this.currentPage = page;
                    this.renderPieces();
                    this.renderPagination();
                }
            });
        });
    }
    
    bindPieceEvents() {
        // Handle piece actions
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                const pieceId = e.target.dataset.pieceId;
                this.handlePieceAction(action, pieceId);
            });
        });
    }
    
    handlePieceAction(action, pieceId) {
        const piece = this.filteredPieces.find(p => p.id === pieceId);
        if (!piece) return;
        
        switch (action) {
            case 'place':
                this.placePiece(piece);
                break;
            case 'sell':
                this.sellPiece(piece);
                break;
            case 'buy':
                this.buyPiece(piece);
                break;
        }
    }
    
    placePiece(piece) {
        // Integration with existing placement system
        if (window.mechaGrid) {
            window.mechaGrid.placePieceFromLibrary(piece);
        }
    }
    
    async sellPiece(piece) {
        // TODO: Implement sell functionality
        const confirmed = confirm(`Sell ${piece.name} for ${Math.floor(piece.zoltan * 0.5)} Zoltans?`);
        if (confirmed) {
            try {
                const response = await fetch('/api/player/sell-piece', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ piece_id: piece.id })
                });
                
                if (response.ok) {
                    await this.loadPieces(); // Refresh
                    // Update zoltans display if available
                    if (window.mechaGrid) {
                        window.mechaGrid.updateStats();
                    }
                } else {
                    throw new Error('Sell failed');
                }
            } catch (error) {
                alert(`Failed to sell piece: ${error.message}`);
            }
        }
    }
    
    async buyPiece(piece) {
        // Integration with existing purchase system
        const confirmed = confirm(`Buy ${piece.name} for ${piece.zoltan} Zoltans?`);
        if (confirmed) {
            try {
                const response = await fetch('/api/player/shop/buy', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ piece_id: piece.id })
                });
                
                const result = await response.json();
                if (response.ok) {
                    await this.loadPieces(); // Refresh
                    // Update library and stats if available
                    if (window.mechaGrid) {
                        window.mechaGrid.loadSamplePieces();
                        window.mechaGrid.updateStats();
                    }
                } else {
                    throw new Error(result.error || 'Purchase failed');
                }
            } catch (error) {
                alert(`Purchase failed: ${error.message}`);
            }
        }
    }
    
    showLoading(show) {
        const loading = document.getElementById(`loadingState_${this.containerId}`);
        const grid = document.getElementById(`piecesGrid_${this.containerId}`);
        const pagination = document.getElementById(`pagination_${this.containerId}`);
        
        if (show) {
            loading.style.display = 'block';
            grid.style.display = 'none';
            pagination.style.display = 'none';
        } else {
            loading.style.display = 'none';
        }
    }
    
    showError(message) {
        const grid = document.getElementById(`piecesGrid_${this.containerId}`);
        grid.innerHTML = `
            <div class="error-state">
                <p>Error: ${message}</p>
                <button onclick="location.reload()">Retry</button>
            </div>
        `;
    }
    
    // Public API
    refresh() {
        this.loadPieces();
    }
    
    setMode(mode) {
        this.mode = mode;
        this.resetFilters();
        this.loadPieces();
    }
}

// Export for use
window.PieceBrowser = PieceBrowser;