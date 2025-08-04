// ===== CLEAN DREAM MECHA GRID SYSTEM =====

// Parse blockmaker ASCII patterns into coordinate arrays
function parsePattern(pattern) {
    const lines = pattern.trim().split('\n');
    const coords = [];
    let anchorX = 0, anchorY = 0;
    
    // Find anchor point (+)
    lines.forEach((line, y) => {
        const cells = line.trim().split(/\s+/);
        cells.forEach((cell, x) => {
            if (cell === '+') {
                anchorX = x;
                anchorY = y;
            }
        });
    });
    
    // Get all filled cells relative to anchor
    lines.forEach((line, y) => {
        const cells = line.trim().split(/\s+/);
        cells.forEach((cell, x) => {
            if (cell && cell !== '.' && cell !== '0') {
                const relX = x - anchorX;
                const relY = y - anchorY;
                coords.push([relX, relY]);
            }
        });
    });
    
    return coords.length > 0 ? coords : [[0, 0]];
}

// Main grid system class
class MechaGrid {
    constructor() {
        // Grid system - individual cell tracking  
        this.maxGridSize = 18; // Game rules maximum
        this.baseActiveWidth = 8;   // Starting active area width
        this.baseActiveHeight = 8;  // Starting active area height
        this.activeStartX = 0;  // Active area starts at top-left
        this.activeStartY = 0;
        
        // Track individually expanded cells
        this.expandedCells = new Set(); // Set of "x,y" strings for expanded cells
        
        // Full grid is always 18x18, but only active area is usable
        this.fullGrid = Array(this.maxGridSize).fill().map(() => Array(this.maxGridSize).fill(null));
        
        this.pieces = {};
        this.selectedPiece = null;
        this.activePiece = null;
        this.floatingLibraryActive = false;
        this.upgradeMode = false; // New: upgrade mode for grid expansion
        this.pendingTuneUp = null; // Tune-up confirmation state
        
        // Player identity with fallback
        this.operatorName = localStorage.getItem('operatorName') || null;
        this.mechaName = localStorage.getItem('mechaName') || null;
        
        // Check if first-time setup is needed
        this.isFirstTime = !localStorage.getItem('setup_completed');
        
        // Player stats
        this.maxHp = 0;
        this.currentHp = 0;
        this.zoltans = 10000; // Starting currency
        this.upgradePoints = 20; // Starting with 20 for testing grid expansion
        this.hpCostMultiplier = 0.1; // 0.1 Z per HP point (placeholder)
        
        // Library filters
        this.filters = {
            statType: 'all',
            maxHp: 500,
            maxBlockCount: 10
        };
        
        // Authentication
        this.authenticated = false;
        this.currentUserId = null;
        this.currentUsername = null;
        
        this.init();
    }
    
    init() {
        // Check if first-time setup is needed
        if (this.isFirstTime) {
            this.startFirstTimeSetup();
        } else {
        // Set default names if not already set
        if (!this.operatorName) {
            this.operatorName = 'Operator';
            localStorage.setItem('operatorName', this.operatorName);
        }
        if (!this.mechaName) {
            this.mechaName = 'Dream Mecha';
            localStorage.setItem('mechaName', this.mechaName);
        }
        
        this.initializeMainUI();
        }
    }

    initializeMainUI() {
        // Check if required elements exist before proceeding
        const gridElement = document.getElementById('mechaGridFull');
        if (!gridElement) {
            console.warn('Grid element not found, delaying initialization...');
            // Prevent infinite retry loops
            if (!this._initRetryCount) this._initRetryCount = 0;
            this._initRetryCount++;
            
            if (this._initRetryCount > 50) { // Max 5 seconds
                console.error('Failed to initialize UI after 50 retries');
                return;
            }
            
            setTimeout(() => this.initializeMainUI(), 100);
            return;
        }
        
        this.setupAuthentication();
        this.createFullGrid();
        this.createHpBar();
        this.loadSamplePieces();
        this.loadShopItems(); 
        this.setupControls();
        this.setupFloatingLibrary();
        this.setupTuneUp();
        this.setupFilters();
        this.setupNameEditing();
        this.setupCombatLog();
        this.loadFortressStatus();
        this.updateStats();
        this.updateGridStatistics();
        this.updateHeaderNames();
    }
    
    createFullGrid() {
        const gridElement = document.getElementById('mechaGridFull');
        gridElement.innerHTML = '';
        
        // Calculate the bounding box of all active cells (base + expanded)
        let minX = this.activeStartX;
        let maxX = this.activeStartX + this.baseActiveWidth - 1;
        let minY = this.activeStartY;
        let maxY = this.activeStartY + this.baseActiveHeight - 1;
        
        // Include expanded cells in bounding box
        for (const cellKey of this.expandedCells) {
            const [x, y] = cellKey.split(',').map(Number);
            minX = Math.min(minX, x);
            maxX = Math.max(maxX, x);
            minY = Math.min(minY, y);
            maxY = Math.max(maxY, y);
        }
        
        // If in upgrade mode, extend to show expansion options
        if (this.upgradeMode) {
            minX = Math.max(0, minX - 1);
            maxX = Math.min(this.maxGridSize - 1, maxX + 1);
            minY = Math.max(0, minY - 1);
            maxY = Math.min(this.maxGridSize - 1, maxY + 1);
        }
        
        const gridWidth = maxX - minX + 1;
        const gridHeight = maxY - minY + 1;
        
        // Set CSS grid template to match display area
        gridElement.style.gridTemplateColumns = `repeat(${gridWidth}, var(--grid-cell))`;
        gridElement.style.gridTemplateRows = `repeat(${gridHeight}, var(--grid-cell))`;
        
        // Create cells for the display area
        for (let y = minY; y <= maxY; y++) {
            for (let x = minX; x <= maxX; x++) {
                const cell = document.createElement('div');
                cell.dataset.x = x;
                cell.dataset.y = y;
                
                if (this.isCellActive(x, y)) {
                    cell.className = 'grid-cell active';
                    cell.addEventListener('click', () => this.onCellClick(x, y));
                } else if (this.upgradeMode && this.isCellExpandable(x, y)) {
                    cell.className = 'grid-cell expansion';
                    cell.addEventListener('click', () => this.expandSingleCell(x, y));
                } else {
                    cell.className = 'grid-cell inactive';
                }
                
                gridElement.appendChild(cell);
            }
        }
    }

    isCellActive(x, y) {
        // Check base active area
        const inBaseArea = x >= this.activeStartX && 
                          x < this.activeStartX + this.baseActiveWidth &&
                          y >= this.activeStartY && 
                          y < this.activeStartY + this.baseActiveHeight;
        
        // Check expanded cells
        const isExpanded = this.expandedCells.has(`${x},${y}`);
        
        return inBaseArea || isExpanded;
    }

    isCellExpandable(x, y) {
        // Don't expand if already active or out of bounds
        if (this.isCellActive(x, y) || x < 0 || x >= this.maxGridSize || y < 0 || y >= this.maxGridSize) {
            return false;
        }
        
        // Check if adjacent to any active cell (base area or expanded)
        const directions = [[-1,0], [1,0], [0,-1], [0,1], [-1,-1], [-1,1], [1,-1], [1,1]];
        
        for (const [dx, dy] of directions) {
            const adjX = x + dx;
            const adjY = y + dy;
            
            if (this.isCellActive(adjX, adjY)) {
                return true;
            }
        }
        
        return false;
    }
    
    onCellClick(x, y) {
        // Only allow interactions in active area
        if (!this.isCellActive(x, y)) {
            return;
        }
        
        if (this.activePiece) {
            // Placing piece from library
            this.placePiece(this.activePiece, x, y);
        } else if (this.selectedPiece && !this.fullGrid[y][x]) {
            // Moving selected piece to empty cell
            this.movePieceToPosition(this.selectedPiece, x, y);
        } else if (this.fullGrid[y][x]) {
            // Selecting piece on grid
            this.selectPiece(x, y);
        } else {
            // Clicking empty space - clear selection
            this.clearSelection();
        }
    }
    
    placePiece(piece, x, y) {
        if (this.canPlacePiece(piece, x, y)) {
            // Remove from current position if already placed
            if (piece.placed) {
                this.removePiece(piece.id);
            }
            
            // Place piece
            piece.shape.forEach(([dx, dy]) => {
                const nx = x + dx;
                const ny = y + dy;
                if (this.isCellActive(nx, ny)) {
                    this.fullGrid[ny][nx] = {
                        pieceId: piece.id,
                        isAnchor: dx === 0 && dy === 0
                    };
                }
            });
            
            piece.x = x;
            piece.y = y;
            piece.placed = true;
            
            this.clearActivePiece();
            this.updateDisplay();
            this.updateStats();
        }
    }
    
    canPlacePiece(piece, x, y) {
        for (const [dx, dy] of piece.shape) {
            const nx = x + dx;
            const ny = y + dy;
            if (!this.isCellActive(nx, ny)) return false;
            
            const cellOccupant = this.fullGrid[ny][nx];
            // Allow placement if cell is empty OR occupied by the same piece (for moving)
            if (cellOccupant && cellOccupant.pieceId !== piece.id) {
                return false;
            }
        }
        return true;
    }
    
    removePiece(pieceId) {
        for (let y = 0; y < this.maxGridSize; y++) {
            for (let x = 0; x < this.maxGridSize; x++) {
                if (this.fullGrid[y][x] && this.fullGrid[y][x].pieceId === pieceId) {
                    this.fullGrid[y][x] = null;
                }
            }
        }
        this.pieces[pieceId].placed = false;
    }
    
    movePieceToPosition(pieceId, newX, newY) {
        const piece = this.pieces[pieceId];
        if (!piece || !piece.placed) return;
        
        // Check if we can place at new position
        if (this.canPlacePiece(piece, newX, newY)) {
            // Remove from current position
            this.removePiece(pieceId);
            
            // Place at new position
            piece.shape.forEach(([dx, dy]) => {
                const nx = newX + dx;
                const ny = newY + dy;
                if (this.isCellActive(nx, ny)) {
                    this.fullGrid[ny][nx] = {
                        pieceId: pieceId,
                        isAnchor: dx === 0 && dy === 0
                    };
                }
            });
            
            piece.x = newX;
            piece.y = newY;
            piece.placed = true;
            
            this.clearSelection();
            this.updateDisplay();
            this.updateStats();
        }
    }
    
    selectPiece(x, y) {
        const cell = this.fullGrid[y][x];
        if (cell) {
            this.selectedPiece = cell.pieceId;
            this.clearActivePiece(); // Clear library selection
            this.showDropZones(); // Show where piece can move
            this.updateDisplay();
        }
    }
    
    clearSelection() {
        this.selectedPiece = null;
        this.hideDropZones();
        this.updateDisplay();
    }
    
    setActivePiece(piece) {
        this.activePiece = piece;
        this.clearSelection();
        this.updatePieceLibrary();
        this.showDropZones();
    }
    
    clearActivePiece() {
        this.activePiece = null;
        this.updatePieceLibrary();
        this.hideDropZones();
    }
    
    showDropZones() {
        if (!this.activePiece && !this.selectedPiece) return;
        
        const pieceToPlace = this.activePiece || this.pieces[this.selectedPiece];
        
        document.querySelectorAll('.grid-cell.active').forEach(cell => {
            const x = parseInt(cell.dataset.x);
            const y = parseInt(cell.dataset.y);
            
            // Only show valid drop zones, not invalid ones
            if (this.canPlacePiece(pieceToPlace, x, y)) {
                cell.classList.add('drop-zone');
            }
        });
    }
    
    hideDropZones() {
        document.querySelectorAll('.grid-cell').forEach(cell => {
            cell.classList.remove('drop-zone', 'invalid');
        });
    }
    
    rotatePiece(pieceId) {
        const piece = this.pieces[pieceId];
        if (!piece) return;
        
        // Rotate shape 90 degrees clockwise
        piece.shape = piece.shape.map(([x, y]) => [-y, x]);
        
        // If placed, try smart rotation
        if (piece.placed) {
            const validPosition = this.findValidRotationPosition(piece, piece.x, piece.y);
            
            if (validPosition) {
                this.removePiece(pieceId);
                this.placePiece(piece, validPosition.x, validPosition.y);
            } else {
                // Only revert if absolutely no valid position found
                piece.shape = piece.shape.map(([x, y]) => [y, -x]);
                console.log(`Cannot rotate ${piece.name} - no valid position found`);
            }
        }
        
        this.updateDisplay();
    }

    findValidRotationPosition(piece, originalX, originalY) {
        // Try current position first
        if (this.canPlacePiece(piece, originalX, originalY)) {
            return { x: originalX, y: originalY };
        }
        
        // Try nearby positions in expanding rings (radius 1, then 2)
        for (let radius = 1; radius <= 2; radius++) {
            for (let dx = -radius; dx <= radius; dx++) {
                for (let dy = -radius; dy <= radius; dy++) {
                    // Skip positions not on the current ring
                    if (Math.abs(dx) !== radius && Math.abs(dy) !== radius) continue;
                    
                    const testX = originalX + dx;
                    const testY = originalY + dy;
                    
                    // Stay within active grid bounds
                    if (!this.isCellActive(testX, testY)) continue;
                    
                    if (this.canPlacePiece(piece, testX, testY)) {
                        console.log(`Smart rotation: moved ${piece.name} from (${originalX},${originalY}) to (${testX},${testY})`);
                        return { x: testX, y: testY };
                    }
                }
            }
        }
        
        return null; // No valid position found
    }

    createHpBar() {
        const hpBar = document.getElementById('hpBar');
        if (!hpBar) return;
        
        hpBar.innerHTML = '';
        
        // Create 20 cells for HP bar (representing percentage)
        for (let i = 0; i < 20; i++) {
            const cell = document.createElement('div');
            cell.className = 'hp-cell';
            cell.dataset.index = i;
            hpBar.appendChild(cell);
        }
    }

    updateHpBar() {
        // Temporarily disabled to prevent JavaScript errors
        return;
    }

    setupTuneUp() {
        const tuneUpFullBtn = document.getElementById('tuneUpFullBtn');
        const tuneUpCustomBtn = document.getElementById('tuneUpCustomBtn');
        const customInputGroup = document.getElementById('customInputGroup');
        const confirmationSection = document.getElementById('confirmationSection');
        const confirmBtn = document.getElementById('confirmBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        const upgradeGridBtn = document.getElementById('upgradeGridBtn');
        
        if (!tuneUpFullBtn || !tuneUpCustomBtn) return;
        
        // FULL tune up button
        tuneUpFullBtn.addEventListener('click', () => {
            if (this.currentHp >= this.maxHp) {
                alert('Your mecha is already at full health!');
                return;
            }
            
            const hpNeeded = this.maxHp - this.currentHp;
            const fullCost = Math.ceil(hpNeeded * this.hpCostMultiplier);
            
            if (this.zoltans < fullCost) {
                alert(`Not enough Zoltans! You have ${this.zoltans}Z but need ${fullCost}Z for full heal.`);
                return;
            }
            
            this.showConfirmation('FULL', hpNeeded, fullCost);
        });
        
        // Custom tune up button
        tuneUpCustomBtn.addEventListener('click', () => {
            if (this.currentHp >= this.maxHp) {
                alert('Your mecha is already at full health!');
                return;
            }
            
            if (customInputGroup) {
                customInputGroup.style.display = 'block';
                setTimeout(() => {
                    const tuneUpAmount = document.getElementById('tuneUpAmount');
                    if (tuneUpAmount) {
                        tuneUpAmount.focus();
                        
                        // Add enter key listener for custom amount
                        tuneUpAmount.addEventListener('keypress', (e) => {
                            if (e.key === 'Enter') {
                                this.processCustomTuneUp();
                            }
                        });
                    }
                }, 100);
            }
        });
        
        // Confirmation buttons
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                if (this.pendingTuneUp) {
                    this.executeTuneUp(this.pendingTuneUp);
                }
            });
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.hideConfirmation();
            });
        }
        
        // Upgrade grid button
        if (upgradeGridBtn) {
            upgradeGridBtn.addEventListener('click', () => {
                this.toggleUpgradeMode();
            });
        }
    }

    processCustomTuneUp() {
        const tuneUpAmount = document.getElementById('tuneUpAmount');
        const healAmount = parseInt(tuneUpAmount.value) || 0;
        
        if (healAmount <= 0) {
            alert('Please enter a valid amount of Zoltans to spend on healing.');
            return;
        }
        
        if (this.zoltans < healAmount) {
            alert(`Not enough Zoltans! You have ${this.zoltans}Z but need ${healAmount}Z.`);
            return;
        }
        
        const hpCanRestore = Math.floor(healAmount / this.hpCostMultiplier);
        const hpNeeded = this.maxHp - this.currentHp;
        const hpToRestore = Math.min(hpCanRestore, hpNeeded);
        const actualCost = Math.ceil(hpToRestore * this.hpCostMultiplier);
        
        this.showConfirmation('CUSTOM', hpToRestore, actualCost);
        tuneUpAmount.value = '';
    }

    showConfirmation(type, hpToRestore, cost) {
        const confirmationText = document.getElementById('confirmationText');
        const confirmationSection = document.getElementById('confirmationSection');
        const customInputGroup = document.getElementById('customInputGroup');
        
        if (confirmationText) {
            confirmationText.textContent = `${type} HEAL: Restore ${hpToRestore} HP for ${cost}Z?`;
        }
        
        this.pendingTuneUp = { type, hpToRestore, cost };
        
        if (customInputGroup) customInputGroup.style.display = 'none';
        if (confirmationSection) confirmationSection.style.display = 'block';
    }

    hideConfirmation() {
        const confirmationSection = document.getElementById('confirmationSection');
        const customInputGroup = document.getElementById('customInputGroup');
        
        if (confirmationSection) confirmationSection.style.display = 'none';
        if (customInputGroup) customInputGroup.style.display = 'none';
        this.pendingTuneUp = null;
    }

    executeTuneUp(tuneUp) {
        this.zoltans -= tuneUp.cost;
        this.currentHp += tuneUp.hpToRestore;
        
        console.log(`${tuneUp.type} Tune Up: Spent ${tuneUp.cost}Z to restore ${tuneUp.hpToRestore} HP`);
        this.updateStats();
        this.hideConfirmation();
        
        alert(`${tuneUp.type} Tune Up complete!\nRestored ${tuneUp.hpToRestore} HP for ${tuneUp.cost}Z`);
    }

    toggleUpgradeMode() {
        const upgradeGridBtn = document.getElementById('upgradeGridBtn');
        const gridContainer = document.getElementById('fullGridContainer');
        
        this.upgradeMode = !this.upgradeMode;
        
        if (this.upgradeMode) {
            if (gridContainer) gridContainer.classList.add('upgrade-mode');
            if (upgradeGridBtn) {
                upgradeGridBtn.classList.add('active');
                upgradeGridBtn.textContent = 'Exit Upgrade Mode';
            }
            this.showExpansionCells();
        } else {
            if (gridContainer) gridContainer.classList.remove('upgrade-mode');
            if (upgradeGridBtn) {
                upgradeGridBtn.classList.remove('active');
                upgradeGridBtn.innerHTML = `Upgrade Grid (<span id="upgradePointsBtn">${this.upgradePoints}</span> points)`;
            }
            this.hideExpansionCells();
        }
    }

    showExpansionCells() {
        if (this.upgradePoints <= 0) return;
        
        // Recreate grid with expansion cells visible
        this.createFullGrid();
    }

    hideExpansionCells() {
        // Just recreate the grid without expansion cells
        this.createFullGrid();
    }

    expandSingleCell(x, y) {
        if (this.upgradePoints <= 0 || !this.isCellExpandable(x, y)) {
            return;
        }
        
        // Add single cell to expanded cells set
        this.expandedCells.add(`${x},${y}`);
        this.upgradePoints--;
        
        // Update display
        this.createFullGrid();
        this.updateDisplay();
        this.updateStats();
        this.updateGridStatistics();
        
        if (this.upgradeMode) {
            this.showExpansionCells();
        }
        
        console.log(`Grid expanded by 1 cell at (${x},${y}). Total expanded: ${this.expandedCells.size}`);
    }

    getEmptySlots() {
        let emptyCount = 0;
        
        // Count empty cells in base active area
        for (let y = this.activeStartY; y < this.activeStartY + this.baseActiveHeight; y++) {
            for (let x = this.activeStartX; x < this.activeStartX + this.baseActiveWidth; x++) {
                if (!this.fullGrid[y][x]) emptyCount++;
            }
        }
        
        // Count empty expanded cells
        for (const cellKey of this.expandedCells) {
            const [x, y] = cellKey.split(',').map(Number);
            if (!this.fullGrid[y][x]) emptyCount++;
        }
        
        return emptyCount;
    }

    getUsedSlots() {
        return this.getTotalActiveSlots() - this.getEmptySlots();
    }

    getTotalActiveSlots() {
        // Base area + expanded cells
        return (this.baseActiveWidth * this.baseActiveHeight) + this.expandedCells.size;
    }
    
    updateDisplay() {
        // Clear all piece-related classes from cells but keep active/inactive
        document.querySelectorAll('.grid-cell').forEach(cell => {
            const x = parseInt(cell.dataset.x);
            const y = parseInt(cell.dataset.y);
            
            // Reset classes but keep active/inactive/expansion state
            cell.classList.remove('piece', 'anchor', 'selected', 'drop-zone');
            cell.classList.remove('stat-hp', 'stat-attack', 'stat-defense', 'stat-speed');
            cell.textContent = '';
            
            // Restore basic state
            if (this.isCellActive(x, y)) {
                cell.classList.add('active');
            } else {
                cell.classList.add('inactive');
            }
        });
        
        // Render pieces
        for (let y = 0; y < this.maxGridSize; y++) {
            for (let x = 0; x < this.maxGridSize; x++) {
                const cell = this.fullGrid[y][x];
                if (cell) {
                    const piece = this.pieces[cell.pieceId];
                    const gridCell = document.querySelector(`[data-x="${x}"][data-y="${y}"]`);
                    
                    if (gridCell) {
                        gridCell.classList.add('piece');
                        gridCell.classList.add(`stat-${this.getStatType(piece)}`);
                        
                        if (cell.isAnchor) {
                            gridCell.classList.add('anchor');
                            gridCell.textContent = '+';
                        }
                        
                        // Highlight all cells of selected piece
                        if (cell.pieceId === this.selectedPiece) {
                            gridCell.classList.add('selected');
                        }
                    }
                }
            }
        }
    }
    
    getStatType(piece) {
        const stats = piece.stats;
        const maxStat = Math.max(stats.hp, stats.attack, stats.defense, stats.speed);
        if (stats.hp === maxStat) return 'hp';
        if (stats.attack === maxStat) return 'attack';
        if (stats.defense === maxStat) return 'defense';
        return 'speed';
    }
    
    updateStats() {
        const totals = { hp: 0, attack: 0, defense: 0, speed: 0 };
        let placedCount = 0;
        
        Object.values(this.pieces).forEach(piece => {
            if (piece.placed) {
                totals.hp += piece.stats.hp;
                totals.attack += piece.stats.attack;
                totals.defense += piece.stats.defense;
                totals.speed += piece.stats.speed;
                placedCount++;
            }
        });
        
        // Update max HP and current HP if needed
        this.maxHp = totals.hp;
        if (this.currentHp === 0 || this.currentHp > this.maxHp) {
            this.currentHp = this.maxHp; // Start with full HP or cap if over
        }
        
        // Update stats with null checks
        const hpStat = document.getElementById('hpStat');
        const attackStat = document.getElementById('attackStat');
        const defenseStat = document.getElementById('defenseStat');
        const speedStat = document.getElementById('speedStat');
        const pieceCount = document.getElementById('pieceCount');
        const zoltansStat = document.getElementById('zoltansStat');
        
        if (hpStat) hpStat.textContent = totals.hp;
        if (attackStat) attackStat.textContent = totals.attack;
        if (defenseStat) defenseStat.textContent = totals.defense;
        if (speedStat) speedStat.textContent = totals.speed;
        if (pieceCount) pieceCount.textContent = placedCount;
        if (zoltansStat) zoltansStat.textContent = this.zoltans;
        
        this.updateHpBar();
        this.updateLaunchStatus();
        this.updateGridStatistics();
    }

    updateGridStatistics() {
        const totalActiveCells = this.getTotalActiveSlots();
        const usedCells = this.getUsedSlots();
        const availableCells = this.getEmptySlots();
        const fillRate = totalActiveCells > 0 ? ((usedCells / totalActiveCells) * 100).toFixed(1) : 0;
        const installedUpgrades = this.expandedCells.size; // Each expanded cell is an upgrade
        
        // Update grid statistics with null checks
        const totalCellsEl = document.getElementById('totalCells');
        const installedUpgradesEl = document.getElementById('installedUpgrades');
        const availableUpgradesEl = document.getElementById('availableUpgrades');
        const fillRateEl = document.getElementById('fillRate');
        
        if (totalCellsEl) totalCellsEl.textContent = totalActiveCells;
        if (installedUpgradesEl) installedUpgradesEl.textContent = `${installedUpgrades} upgrades`;
        if (availableUpgradesEl) availableUpgradesEl.textContent = `${availableCells} cells`;
        if (fillRateEl) fillRateEl.textContent = `${fillRate}%`;
        
        // Update upgrade points display
        const upgradePointsBtn = document.getElementById('upgradePointsBtn');
        if (upgradePointsBtn) {
            upgradePointsBtn.textContent = this.upgradePoints;
        }
    }
    
    loadSamplePieces() {
        // Sample pieces with SINGLE stat rule
        const samplePieces = [
            {
                id: 'piece1',
                name: 'HP Fragment',
                pattern: '+ 2 3\n4 5 .\n6 . .',
                stats: { hp: 600, attack: 0, defense: 0, speed: 0 }  // 6 blocks, HP only
            },
            {
                id: 'piece2',
                name: 'Attack Core',
                pattern: '+ 2\n3 4',
                stats: { hp: 0, attack: 400, defense: 0, speed: 0 }  // 4 blocks, Attack only
            },
            {
                id: 'piece3',
                name: 'Defense Wall',
                pattern: '1 + 3\n4 5 6',
                stats: { hp: 0, attack: 0, defense: 600, speed: 0 }  // 6 blocks, Defense only
            }
        ];
        
        samplePieces.forEach(pieceData => {
            this.pieces[pieceData.id] = {
                ...pieceData,
                shape: parsePattern(pieceData.pattern),
                placed: false
            };
        });
        
        this.updatePieceLibrary();
    }

    setupFilters() {
        const statTypeFilter = document.getElementById('statTypeFilter');
        const hpRangeFilter = document.getElementById('hpRangeFilter');
        const blockCountFilter = document.getElementById('blockCountFilter');
        const resetFiltersBtn = document.getElementById('resetFiltersBtn');
        
        const hpRangeDisplay = document.getElementById('hpRangeDisplay');
        const blockCountDisplay = document.getElementById('blockCountDisplay');
        
        if (!statTypeFilter || !hpRangeFilter || !blockCountFilter || !resetFiltersBtn) return;
        
        // Stat type filter
            statTypeFilter.addEventListener('change', () => {
                this.filters.statType = statTypeFilter.value;
                this.updatePieceLibrary();
            });
        
        // HP range filter
            hpRangeFilter.addEventListener('input', () => {
                this.filters.maxHp = parseInt(hpRangeFilter.value);
            if (hpRangeDisplay) hpRangeDisplay.textContent = this.filters.maxHp;
                this.updatePieceLibrary();
            });
        
        // Block count filter  
            blockCountFilter.addEventListener('input', () => {
                this.filters.maxBlockCount = parseInt(blockCountFilter.value);
            if (blockCountDisplay) blockCountDisplay.textContent = this.filters.maxBlockCount;
                this.updatePieceLibrary();
            });
        
        // Reset filters
            resetFiltersBtn.addEventListener('click', () => {
            this.filters = { statType: 'all', maxHp: 500, maxBlockCount: 10 };
            statTypeFilter.value = 'all';
            hpRangeFilter.value = 500;
            blockCountFilter.value = 10;
            if (hpRangeDisplay) hpRangeDisplay.textContent = '500';
            if (blockCountDisplay) blockCountDisplay.textContent = '10';
            this.updatePieceLibrary();
        });
    }

    filterPieces(pieces) {
        return pieces.filter(piece => {
            // Stat type filter
            if (this.filters.statType !== 'all') {
                const dominantStat = this.getStatType(piece);
                if (dominantStat !== this.filters.statType) return false;
            }
            
            // HP range filter
            if (piece.stats.hp > this.filters.maxHp) return false;
            
            // Block count filter
            if (piece.shape.length > this.filters.maxBlockCount) return false;
            
            return true;
        });
    }
    
    updatePieceLibrary() {
        const library = document.getElementById('pieceLibrary');
        if (!library) return;
        
        library.innerHTML = '';
        
        const allPieces = Object.values(this.pieces);
        const filteredPieces = this.filterPieces(allPieces);
        
        filteredPieces.forEach(piece => {
            const element = this.createPieceElement(piece);
            library.appendChild(element);
        });

        // Also update floating library if active (floating library shows all pieces, no filters)
        this.updateFloatingLibrary();
    }
    
    createPieceElement(piece, isFloating = false) {
        const element = document.createElement('div');
        element.className = 'piece-item';
        
        if (this.activePiece === piece) {
            element.classList.add('selected');
        }
        
        element.innerHTML = `
            <div class="piece-name">${piece.name}</div>
            <div class="piece-stats">${this.getActiveStatText(piece.stats)}</div>
        `;
        
        const preview = this.createPiecePreview(piece, isFloating);
        element.appendChild(preview);
        
        element.addEventListener('click', () => {
            if (this.activePiece === piece) {
                this.clearActivePiece();
            } else {
                this.setActivePiece(piece);
            }
        });
        
        return element;
    }
    
    createPiecePreview(piece, isFloating = false) {
        const preview = document.createElement('div');
        preview.className = 'piece-preview';
        
        const shape = piece.shape || piece.pattern; // Handle both formats
        
        if (!shape || !Array.isArray(shape)) {
            console.warn('Invalid shape data:', shape);
            return preview;
        }
        
        // Convert shape to coordinate format if it's a boolean array
        const coordinates = this.convertShapeToCoordinates(shape);
        
        // Find the bounding box of the shape
        const minX = Math.min(...coordinates.map(([x, y]) => x));
        const maxX = Math.max(...coordinates.map(([x, y]) => x));
        const minY = Math.min(...coordinates.map(([x, y]) => y));
        const maxY = Math.max(...coordinates.map(([x, y]) => y));
        
        const width = maxX - minX + 1;
        const height = maxY - minY + 1;
        
        const grid = document.createElement('div');
        grid.className = 'piece-grid';
        grid.style.gridTemplateColumns = `repeat(${width}, 1fr)`;
        grid.style.gridTemplateRows = `repeat(${height}, 1fr)`;
        
        // Smaller cells for floating library
        if (isFloating) {
            grid.style.transform = 'scale(0.7)';
            grid.style.transformOrigin = 'center';
        }
        
        // Create a 2D array to represent the shape
        const shapeGrid = Array(height).fill().map(() => Array(width).fill(false));
        
        // Mark occupied positions
        coordinates.forEach(([dx, dy]) => {
            const x = dx - minX;
            const y = dy - minY;
            if (x >= 0 && x < width && y >= 0 && y < height) {
                shapeGrid[y][x] = true;
            }
        });
        
        // Create cells
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const cell = document.createElement('div');
                cell.className = 'piece-cell';
                
                if (shapeGrid[y][x]) {
                    cell.classList.add('filled');
                    // Apply stat color based on piece's primary stat
                    const statType = this.getStatType(piece);
                    cell.classList.add(`stat-${statType}`);
                    
                    // Mark the anchor point (0,0 relative to shape)
                    const originalX = x + minX;
                    const originalY = y + minY;
                    if (originalX === 0 && originalY === 0) {
                        cell.textContent = '+';
                    }
                }
                
                grid.appendChild(cell);
            }
        }
        
        preview.appendChild(grid);
        return preview;
    }
    
    convertShapeToCoordinates(shape) {
        // If shape is already in coordinate format [[x, y], [x, y], ...]
        if (shape.length > 0 && Array.isArray(shape[0]) && shape[0].length === 2 && typeof shape[0][0] === 'number') {
            return shape;
        }
        
        // If shape is in boolean array format [[true, false], [true, true], ...]
        if (shape.length > 0 && Array.isArray(shape[0]) && typeof shape[0][0] === 'boolean') {
            const coordinates = [];
            for (let y = 0; y < shape.length; y++) {
                for (let x = 0; x < shape[y].length; x++) {
                    if (shape[y][x]) {
                        coordinates.push([x, y]);
                    }
                }
            }
            return coordinates;
        }
        
        // Fallback: assume it's already in coordinate format
        return shape;
    }
    
    setupControls() {
        const rotateBtn = document.getElementById('rotateBtn');
        const removeBtn = document.getElementById('removeBtn');
        const clearBtn = document.getElementById('clearBtn');
        const launchBtn = document.getElementById('launchBtn');
        
        if (rotateBtn) {
            rotateBtn.addEventListener('click', () => {
                if (this.selectedPiece) {
                    this.rotatePiece(this.selectedPiece);
            }
        });
    }

        if (removeBtn) {
            removeBtn.addEventListener('click', () => {
                if (this.selectedPiece) {
                    this.removePiece(this.selectedPiece);
                    this.clearSelection();
                    this.updateDisplay();
                    this.updateStats();
                }
            });
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                Object.keys(this.pieces).forEach(id => {
                    this.removePiece(id);
                });
                this.clearSelection();
                this.clearActivePiece();
                this.updateDisplay();
                this.updateStats();
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' || e.key === 'R') {
                if (this.selectedPiece) {
                    this.rotatePiece(this.selectedPiece);
                }
            } else if (e.key === 'Delete' || e.key === 'Backspace') {
                if (this.selectedPiece) {
                    this.removePiece(this.selectedPiece);
                    this.clearSelection();
                    this.updateDisplay();
                    this.updateStats();
                }
            } else if (e.key === 'Escape') {
                this.clearActivePiece();
                this.clearSelection();
            }
        });

        // Launch button
        if (launchBtn) {
            launchBtn.addEventListener('click', () => {
                this.attemptLaunch();
            });
        }
    }

    canLaunch() {
        // Must have current HP > 0 to launch
        return this.currentHp > 0;
    }

    updateLaunchStatus() {
        const launchBtn = document.getElementById('launchBtn');
        const tuneUpFullBtn = document.getElementById('tuneUpFullBtn');
        const tuneUpCustomBtn = document.getElementById('tuneUpCustomBtn');
        
        if (launchBtn) {
            launchBtn.disabled = !this.canLaunch();
        }
        
        // Update tune-up button states
        const needsHeal = this.currentHp < this.maxHp;
        if (tuneUpFullBtn) tuneUpFullBtn.disabled = !needsHeal;
        if (tuneUpCustomBtn) tuneUpCustomBtn.disabled = !needsHeal;
    }

    attemptLaunch() {
        if (!this.canLaunch()) {
            alert('Cannot launch with 0 HP! Use Tune Up to restore health first.');
            return;
        }
        
        // Hide launch button and show sequence
        const launchBtn = document.getElementById('launchBtn');
        const launchSequence = document.getElementById('launchSequence');
        
        if (launchBtn) launchBtn.style.display = 'none';
        if (launchSequence) launchSequence.style.display = 'block';
        
        this.startLaunchSequence();
    }

    startLaunchSequence() {
        const loadingDots = document.getElementById('loadingDots');
        const systemCheck = document.getElementById('systemCheck');
        const engageBtn = document.getElementById('engageBtn');
        
        // Animate loading dots
        let dotCount = 0;
        const loadingInterval = setInterval(() => {
            dotCount++;
            if (loadingDots) loadingDots.textContent = '.'.repeat(dotCount % 12);
        }, 150);
        
        // After 3 seconds, show system ready
        setTimeout(() => {
            clearInterval(loadingInterval);
            if (loadingDots) loadingDots.textContent = ' COMPLETE';
            if (systemCheck) systemCheck.style.display = 'block';
            
            // After another 1 second, show engage button
            setTimeout(() => {
                if (engageBtn) {
                engageBtn.style.display = 'block';
                    
                    // Add engage button listener
                    engageBtn.addEventListener('click', () => {
                        this.finalLaunch();
                    });
                }
            }, 1000);
        }, 3000);
    }

    finalLaunch() {
        console.log(`MECHA LAUNCHED! HP: ${this.currentHp}/${this.maxHp}, ATK: ${document.getElementById('attackStat')?.textContent}, DEF: ${document.getElementById('defenseStat')?.textContent}, SPD: ${document.getElementById('speedStat')?.textContent}`);
        
        // Here we would submit to backend/battle system
        alert(`MECHA DEPLOYED TO COMBAT!\n\nFinal Stats:\nHP: ${this.currentHp}/${this.maxHp}\nATK: ${document.getElementById('attackStat')?.textContent}\nDEF: ${document.getElementById('defenseStat')?.textContent}\nSPD: ${document.getElementById('speedStat')?.textContent}\n\nBattle sequence initiated!`);
        
        // Reset launch UI
        const launchSequence = document.getElementById('launchSequence');
        const launchBtn = document.getElementById('launchBtn');
        const systemCheck = document.getElementById('systemCheck');
        const engageBtn = document.getElementById('engageBtn');
        
        if (launchSequence) launchSequence.style.display = 'none';
        if (launchBtn) launchBtn.style.display = 'block';
        if (systemCheck) systemCheck.style.display = 'none';
        if (engageBtn) engageBtn.style.display = 'none';
    }

    // ===== AUTHENTICATION METHODS =====
    
    setupAuthentication() {
        this.checkAuthStatus();
        this.setupAuthButtons();
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();
            
            if (data.authenticated) {
                this.authenticated = true;
                this.currentUserId = data.user_id;
                this.currentUsername = data.username;
                this.updateAuthUI();
            } else {
                this.authenticated = false;
                this.currentUserId = null;
                this.currentUsername = null;
                this.updateAuthUI();
            }
        } catch (error) {
            console.error('Auth status check failed:', error);
            this.authenticated = false;
            this.updateAuthUI();
        }
    }

    setupAuthButtons() {
        const loginBtn = document.getElementById('loginBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        
        if (loginBtn) {
            loginBtn.addEventListener('click', () => {
                window.location.href = '/login';
            });
        }
        
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                window.location.href = '/logout';
            });
        }
    }

    updateAuthUI() {
        const authUsername = document.getElementById('authUsername');
        const loginBtn = document.getElementById('loginBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        
        if (this.authenticated) {
            if (authUsername) authUsername.textContent = `Discord: ${this.currentUsername}`;
            if (loginBtn) loginBtn.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'inline-block';
            // Load shop items when authenticated
            this.loadShopItems();
        } else {
            if (authUsername) authUsername.textContent = 'Not authenticated';
            if (loginBtn) loginBtn.style.display = 'inline-block';
            if (logoutBtn) logoutBtn.style.display = 'none';
        }
    }

    // ===== SHOP SYSTEM =====
    
    async loadShopItems() {
        try {
            const response = await fetch('/api/player/shop');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const shopData = await response.json();
            this.displayShopItems(shopData.items || []);
        } catch (error) {
            console.error('Failed to load shop items:', error);
            this.displayShopItems([]);
        }
    }

    getActiveStatDisplay(stats) {
        // Return only the active stat (non-zero value)
        if (stats.hp > 0) return `<p>HP: ${stats.hp}</p>`;
        if (stats.attack > 0) return `<p>ATK: ${stats.attack}</p>`;
        if (stats.defense > 0) return `<p>DEF: ${stats.defense}</p>`;
        if (stats.speed > 0) return `<p>SPD: ${stats.speed}</p>`;
        return '<p>No stats</p>';
    }
    
    getActiveStatText(stats) {
        // Return only the active stat as text (for library display)
        if (stats.hp > 0) return `HP: ${stats.hp}`;
        if (stats.attack > 0) return `ATK: ${stats.attack}`;
        if (stats.defense > 0) return `DEF: ${stats.defense}`;
        if (stats.speed > 0) return `SPD: ${stats.speed}`;
        return 'No stats';
    }

    displayShopItems(items) {
        const shopContainer = document.getElementById('shopItems');
        if (!shopContainer) return;
        
        shopContainer.innerHTML = '';

        if (items.length === 0) {
            shopContainer.innerHTML = '<p>No items available in shop today.</p>';
            return;
        }

        items.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'shop-item';
            itemElement.innerHTML = `
                <h4>${item.name}</h4>
                <div class="shop-item-preview">
                    <div class="piece-preview" data-pattern='${JSON.stringify(item.pattern)}'></div>
                </div>
                <div class="shop-item-stats">
                    ${this.getActiveStatDisplay(item.stats)}
                </div>
                <div class="shop-item-price">
                    <p>Price: ${item.price} Zoltans</p>
                </div>
                <button class="shop-buy-btn" data-piece-id="${item.piece_id}">Buy</button>
            `;
            
            // Render piece preview
            this.renderPiecePreview(itemElement.querySelector('.piece-preview'), item.pattern);
            
            // Add buy button listener
            const buyBtn = itemElement.querySelector('.shop-buy-btn');
            buyBtn.addEventListener('click', () => this.buyShopItem(item.piece_id, item.name));
            
            shopContainer.appendChild(itemElement);
        });
    }

    async buyShopItem(pieceId, pieceName) {
        try {
            const response = await fetch('/api/player/shop/buy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ piece_id: pieceId })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Purchase failed');
            }
            
            const result = await response.json();
            alert(`Successfully purchased ${pieceName}!`);
            
            // Refresh shop and library
            this.loadShopItems();
            this.loadSamplePieces();
            
            // Update Zoltans display
            const zoltansElement = document.getElementById('zoltansStat');
            if (zoltansElement && result.player_zoltans !== undefined) {
                zoltansElement.textContent = result.player_zoltans;
            }
            
        } catch (error) {
            console.error('Purchase failed:', error);
            alert(`Purchase failed: ${error.message}`);
        }
    }

    // ===== FLOATING LIBRARY SYSTEM =====
    
    setupFloatingLibrary() {
        const toggleBtn = document.getElementById('libraryToggleBtn');
        const floatingLibrary = document.getElementById('floatingLibrary');
        const header = document.getElementById('floatingLibraryHeader');
        
        if (!toggleBtn || !floatingLibrary || !header) return;

        // Toggle floating library
        toggleBtn.addEventListener('click', () => {
            this.toggleFloatingLibrary();
        });

        // Close floating library - set up once and don't change
        this.setupFloatingLibraryCloseButton();

        // Make floating library draggable - ensure it's properly set up
        setTimeout(() => {
            this.makeDraggable(floatingLibrary, header);
        }, 100);
    }

    toggleFloatingLibrary() {
        const toggleBtn = document.getElementById('libraryToggleBtn');
        const floatingLibrary = document.getElementById('floatingLibrary');
        const pieceLibrary = document.querySelector('.piece-library');
        
        if (!toggleBtn || !floatingLibrary || !pieceLibrary) return;
        
        this.floatingLibraryActive = !this.floatingLibraryActive;
        
        if (this.floatingLibraryActive) {
            floatingLibrary.classList.add('active');
            pieceLibrary.classList.add('floating-active');
            toggleBtn.textContent = 'Dock Library';
            this.updateFloatingLibrary();
        } else {
            floatingLibrary.classList.remove('active');
            pieceLibrary.classList.remove('floating-active');
            toggleBtn.textContent = 'Float Library';
        }
    }

    setupFloatingLibraryCloseButton() {
        const closeBtn = document.getElementById('floatingLibraryClose');
        if (!closeBtn) return;
        
        // Remove any existing listeners and add fresh one
        closeBtn.replaceWith(closeBtn.cloneNode(true));
        const newCloseBtn = document.getElementById('floatingLibraryClose');
        
        if (newCloseBtn) {
            newCloseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Close button clicked!');
                this.closeFloatingLibrary();
            });
            
            // Also add touch event for mobile
            newCloseBtn.addEventListener('touchend', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Close button touched!');
                this.closeFloatingLibrary();
            });
        }
    }

    closeFloatingLibrary() {
        console.log('Closing floating library...');
        const toggleBtn = document.getElementById('libraryToggleBtn');
        const floatingLibrary = document.getElementById('floatingLibrary');
        const pieceLibrary = document.querySelector('.piece-library');
        
        if (!toggleBtn || !floatingLibrary || !pieceLibrary) return;
        
        this.floatingLibraryActive = false;
        floatingLibrary.classList.remove('active');
        pieceLibrary.classList.remove('floating-active');
        toggleBtn.textContent = 'Float Library';
        this.updatePieceLibrary();
        console.log('Floating library closed!');
    }

    makeDraggable(element, handle) {
        if (!element || !handle) return;
        
        let isDragging = false;
        let startX, startY, initialX, initialY;

        // Remove any existing listeners first
        if (this.startDragHandler) {
            handle.removeEventListener('mousedown', this.startDragHandler);
            handle.removeEventListener('touchstart', this.startDragHandler);
        }

        this.startDragHandler = (e) => {
            isDragging = true;
            
            const clientX = e.type === 'mousedown' ? e.clientX : e.touches[0].clientX;
            const clientY = e.type === 'mousedown' ? e.clientY : e.touches[0].clientY;
            
            startX = clientX;
            startY = clientY;
            
            const rect = element.getBoundingClientRect();
            initialX = rect.left;
            initialY = rect.top;

            const dragHandler = (e) => {
                if (!isDragging) return;
                
                const clientX = e.type === 'mousemove' ? e.clientX : e.touches[0].clientX;
                const clientY = e.type === 'mousemove' ? e.clientY : e.touches[0].clientY;
                
                const deltaX = clientX - startX;
                const deltaY = clientY - startY;
                
                const newX = Math.max(0, Math.min(window.innerWidth - element.offsetWidth, initialX + deltaX));
                const newY = Math.max(0, Math.min(window.innerHeight - element.offsetHeight, initialY + deltaY));
                
                element.style.left = newX + 'px';
                element.style.top = newY + 'px';
            };

            const stopDragHandler = () => {
                isDragging = false;
                document.removeEventListener('mousemove', dragHandler);
                document.removeEventListener('mouseup', stopDragHandler);
                document.removeEventListener('touchmove', dragHandler);
                document.removeEventListener('touchend', stopDragHandler);
            };

            document.addEventListener('mousemove', dragHandler);
            document.addEventListener('mouseup', stopDragHandler);
            document.addEventListener('touchmove', dragHandler);
            document.addEventListener('touchend', stopDragHandler);
        };

        handle.addEventListener('mousedown', this.startDragHandler);
        handle.addEventListener('touchstart', this.startDragHandler);
    }

    updateFloatingLibrary() {
        if (!this.floatingLibraryActive) return;
        
        const floatingContent = document.getElementById('floatingLibraryContent');
        if (!floatingContent) return;
        
        floatingContent.innerHTML = '';
        
        Object.values(this.pieces).forEach(piece => {
            const element = this.createPieceElement(piece, true); // true = floating version
            floatingContent.appendChild(element);
        });
    }

    // ===== NAME EDITING SYSTEM =====

    setupNameEditing() {
        const editOperatorBtn = document.getElementById('editOperatorBtn');
        const editMechaBtn = document.getElementById('editMechaBtn');
        
        if (!editOperatorBtn || !editMechaBtn) return;
        
        editOperatorBtn.addEventListener('click', () => {
            this.openNameEditModal('operator', this.operatorName);
        });
        
        editMechaBtn.addEventListener('click', () => {
            this.openNameEditModal('mecha', this.mechaName);
        });
        
        // Setup modal event listeners
        const saveBtn = document.getElementById('saveNameBtn');
        const cancelBtn = document.getElementById('cancelNameBtn');
        const modal = document.getElementById('editNameModal');
        
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveNameEdit();
            });
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.closeNameEditModal();
            });
        }
        
        // Close modal on background click
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target.id === 'editNameModal') {
                    this.closeNameEditModal();
                }
            });
        }
    }

    openNameEditModal(type, currentName) {
        this.editingNameType = type;
        const modal = document.getElementById('editNameModal');
        const title = document.getElementById('editNameTitle');
        const input = document.getElementById('editNameInput');
        
        if (!modal || !title || !input) return;
        
        title.textContent = type === 'operator' ? 'Edit Operator Name' : 'Edit Mecha Name';
        input.value = currentName;
        input.placeholder = type === 'operator' ? 'Enter Operator Name' : 'Enter Mecha Name';
        
        modal.classList.add('active');
        setTimeout(() => input.focus(), 100);
        
        // Add enter key listener
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.saveNameEdit();
            }
        });
    }

    closeNameEditModal() {
        const modal = document.getElementById('editNameModal');
        if (modal) {
            modal.classList.remove('active');
        }
        this.editingNameType = null;
    }

    saveNameEdit() {
        const input = document.getElementById('editNameInput');
        if (!input) return;
        
        const newName = input.value.trim();
        
        if (!newName) {
            alert('Name cannot be empty!');
            return;
        }
        
            if (this.editingNameType === 'operator') {
                this.operatorName = newName;
                localStorage.setItem('operatorName', newName);
        } else if (this.editingNameType === 'mecha') {
                this.mechaName = newName;
                localStorage.setItem('mechaName', newName);
        }
        
        this.updateHeaderNames();
        this.closeNameEditModal();
    }

    updateHeaderNames() {
        const operatorElement = document.getElementById('operatorName');
        const mechaElement = document.getElementById('mechaName');
        
        if (operatorElement) {
            operatorElement.textContent = this.operatorName || 'Unknown';
        }
        if (mechaElement) {
            mechaElement.textContent = this.mechaName || 'Unnamed';
        }
    }

    // ===== DEVELOPMENT HELPERS =====

    resetFirstTimeSetup() {
        localStorage.removeItem('operatorName');
        localStorage.removeItem('mechaName');
        console.log('First-time setup reset! Reload the page to see the setup sequence.');
        alert('First-time setup reset! Reload the page to see the setup sequence.');
    }

    startFirstTimeSetup() {
        // Show the first-time setup overlay
        const setupElement = document.getElementById('firstTimeSetup');
        if (setupElement) {
            setupElement.style.display = 'flex';
            this.renderSetupStep(1);
        } else {
            console.error('First-time setup element not found, skipping to main UI');
            this.skipSetup();
        }
    }
    
    renderSetupStep(step) {
        const content = document.getElementById('setupContent');
        if (!content) return;
        
        switch(step) {
            case 1:
                content.innerHTML = `
                    <div class="setup-step">
                        <h2>WELCOME TO DREAM MECHA</h2>
                        <p>Enter your operator name:</p>
                        <input type="text" id="operatorNameInput" placeholder="Operator" maxlength="20">
                        <div class="setup-buttons">
                            <button onclick="window.mechaGrid.nextSetupStep(2)">NEXT</button>
                        </div>
                    </div>
                `;
                break;
            case 2:
                const operatorName = document.getElementById('operatorNameInput')?.value || 'Operator';
                content.innerHTML = `
                    <div class="setup-step">
                        <h2>NAME YOUR MECHA</h2>
                        <p>Choose a name for your mecha:</p>
                        <input type="text" id="mechaNameInput" placeholder="Dream Mecha" maxlength="30">
                        <div class="setup-buttons">
                            <button onclick="window.mechaGrid.prevSetupStep(1)">BACK</button>
                            <button onclick="window.mechaGrid.completeSetup()">START GAME</button>
                        </div>
                    </div>
                `;
                break;
        }
    }
    
    nextSetupStep(step) {
        this.renderSetupStep(step);
    }
    
    prevSetupStep(step) {
        this.renderSetupStep(step);
    }
    
    completeSetup() {
        // Get names from inputs
        const operatorName = document.getElementById('operatorNameInput')?.value || 'Operator';
        const mechaName = document.getElementById('mechaNameInput')?.value || 'Dream Mecha';
        
        // Save to localStorage
        this.operatorName = operatorName;
        this.mechaName = mechaName;
        localStorage.setItem('operatorName', operatorName);
        localStorage.setItem('mechaName', mechaName);
        localStorage.setItem('setup_completed', 'true');
        
        // Hide setup and start game
        const setupElement = document.getElementById('firstTimeSetup');
        if (setupElement) {
            setupElement.style.display = 'none';
        }
        
        this.isFirstTime = false;
        this.initializeMainUI();
        
        console.log(`Setup completed! Operator: ${operatorName}, Mecha: ${mechaName}`);
    }

    skipSetup() {
        // Set default names and skip to main UI
        this.operatorName = 'Operator';
        this.mechaName = 'Dream Mecha';
        localStorage.setItem('operatorName', this.operatorName);
        localStorage.setItem('mechaName', this.mechaName);
        localStorage.setItem('setup_completed', 'true');
        
        // Hide setup and initialize main UI
        const setupElement = document.getElementById('firstTimeSetup');
        if (setupElement) {
            setupElement.style.display = 'none';
        }
        this.isFirstTime = false;
        this.initializeMainUI();
        
        console.log('Setup skipped! Using default names.');
    }

    // ===== FLOATING COMBAT LOG SYSTEM =====
    
    setupCombatLog() {
        const combatLogBtn = document.getElementById('combatLogBtn');
        if (combatLogBtn) {
            combatLogBtn.addEventListener('click', () => this.toggleCombatLog());
        }
    }

    toggleCombatLog() {
        const combatLogBtn = document.getElementById('combatLogBtn');
        const floatingCombatLog = document.getElementById('floatingCombatLog');
        
        if (!combatLogBtn || !floatingCombatLog) return;
        
        if (floatingCombatLog.classList.contains('active')) {
            floatingCombatLog.classList.remove('active');
            combatLogBtn.textContent = 'Combat Log';
        } else {
            floatingCombatLog.classList.add('active');
            combatLogBtn.textContent = 'Hide Log';
            this.loadCombatLog();
            this.setupCombatLogDrag();
        }
    }

    async loadCombatLog() {
        try {
            const response = await fetch('/api/player/combat/log');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const combatData = await response.json();
            this.displayCombatLog(combatData);
        } catch (error) {
            console.error('Failed to load combat log:', error);
            this.displayCombatLog({ combat_log: [] });
        }
    }

    displayCombatLog(combatData) {
        const combatLogContent = document.getElementById('floatingCombatLogContent');
        if (!combatLogContent) return;
        
        combatLogContent.innerHTML = '';

        const logEntries = combatData.combat_log || [];
        const lastCombatResult = combatData.last_combat_result;

        // Display combat summary if available
        if (lastCombatResult) {
            const summaryElement = document.createElement('div');
            summaryElement.className = 'combat-summary';
            
            const isVictory = lastCombatResult.enemies_remaining === 0;
            const summaryHTML = `
                <div class="combat-summary-header ${isVictory ? 'victory' : 'defeat'}">
                    <h3>${isVictory ? '🎉 VICTORY' : '💀 DEFEAT'}</h3>
                </div>
                <div class="combat-summary-stats">
                    <div class="stat-item">
                        <span class="stat-label">Enemies Defeated:</span>
                        <span class="stat-value">${lastCombatResult.enemies_defeated || 0}/${lastCombatResult.total_enemies || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Mechas Downed:</span>
                        <span class="stat-value">${lastCombatResult.mechas_downed || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Voidstate:</span>
                        <span class="stat-value">${lastCombatResult.voidstate_change || 0}</span>
                    </div>
                </div>
            `;
            
            summaryElement.innerHTML = summaryHTML;
            combatLogContent.appendChild(summaryElement);
        }

        // Display current combat status
        const statusElement = document.createElement('div');
        statusElement.className = 'combat-status';
        statusElement.innerHTML = `
            <div class="status-item">
                <span class="status-label">State:</span>
                <span class="status-value">${combatData.state || 'preparing'}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Mechas Launched:</span>
                <span class="status-value">${combatData.mechas_launched || 0}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Enemies Remaining:</span>
                <span class="status-value">${combatData.enemies_remaining || 0}</span>
            </div>
        `;
        combatLogContent.appendChild(statusElement);

        // Display combat log entries
        if (logEntries.length === 0) {
            const noActivityElement = document.createElement('div');
            noActivityElement.className = 'combat-log-entry no-activity';
            noActivityElement.innerHTML = '<p>No combat activity recorded.</p>';
            combatLogContent.appendChild(noActivityElement);
            return;
        }

        const logHeader = document.createElement('div');
        logHeader.className = 'combat-log-header';
        logHeader.innerHTML = '<h4>Combat Log</h4>';
        combatLogContent.appendChild(logHeader);

        logEntries.forEach(entry => {
            const entryElement = document.createElement('div');
            entryElement.className = 'combat-log-entry';
            
            // Determine entry type for styling
            if (entry.includes('attacks')) {
                entryElement.classList.add('attack');
            } else if (entry.includes('damage')) {
                entryElement.classList.add('damage');
            } else if (entry.includes('destroyed')) {
                entryElement.classList.add('destroyed');
            } else if (entry.includes('downed')) {
                entryElement.classList.add('downed');
            } else if (entry.includes('HP:')) {
                entryElement.classList.add('status');
            }
            
            entryElement.innerHTML = `
                <div class="combat-log-timestamp">${new Date().toLocaleTimeString()}</div>
                <div class="combat-log-message">${entry}</div>
            `;
            
            combatLogContent.appendChild(entryElement);
        });

        // Scroll to bottom to show latest entries
        combatLogContent.scrollTop = combatLogContent.scrollHeight;
    }

    setupCombatLogDrag() {
        const combatLog = document.getElementById('floatingCombatLog');
        const header = document.getElementById('floatingCombatLogHeader');
        const closeBtn = document.getElementById('floatingCombatLogClose');
        
        if (!combatLog || !header || !closeBtn) return;
        
        // Setup close button
        closeBtn.addEventListener('click', () => {
            combatLog.classList.remove('active');
            const combatLogBtn = document.getElementById('combatLogBtn');
            if (combatLogBtn) {
                combatLogBtn.textContent = 'Combat Log';
            }
        });
        
        // Make draggable using existing method
        this.makeDraggable(combatLog, header);
    }

    // ===== PIECE PREVIEW RENDERING =====

    renderPiecePreview(container, shape) {
        if (!container || !shape) return;
        
        const size = 4;
        let html = '<div class="piece-preview-grid">';
        
        for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
                const isActive = shape.some(([dx, dy]) => dx === x && dy === y);
                html += `<div class="preview-cell ${isActive ? 'active' : ''}"></div>`;
            }
        }
        
        html += '</div>';
        container.innerHTML = html;
    }

    createPiecePreview(piece, isFloating = false) {
        const preview = document.createElement('div');
        preview.className = 'piece-preview';
        
        const shape = piece.shape || piece.pattern; // Handle both formats
        
        if (!shape || !Array.isArray(shape)) {
            console.warn('Invalid shape data:', shape);
            return preview;
        }
        
        // Find the bounding box of the shape
        const minX = Math.min(...shape.map(([x, y]) => x));
        const maxX = Math.max(...shape.map(([x, y]) => x));
        const minY = Math.min(...shape.map(([x, y]) => y));
        const maxY = Math.max(...shape.map(([x, y]) => y));
        
        const width = maxX - minX + 1;
        const height = maxY - minY + 1;
        
        const grid = document.createElement('div');
        grid.className = 'piece-grid';
        grid.style.gridTemplateColumns = `repeat(${width}, 1fr)`;
        grid.style.gridTemplateRows = `repeat(${height}, 1fr)`;
        
        // Smaller cells for floating library
        if (isFloating) {
            grid.style.transform = 'scale(0.7)';
        }
        
        // Create cells for the piece
        for (let y = minY; y <= maxY; y++) {
            for (let x = minX; x <= maxX; x++) {
                const cell = document.createElement('div');
                cell.className = 'piece-cell';
                
                // Check if this coordinate is part of the shape
                if (shape.some(([px, py]) => px === x && py === y)) {
                    cell.classList.add('filled');
                }
                
                grid.appendChild(cell);
            }
        }
        
        preview.appendChild(grid);
        return preview;
}

// Initialize when page loads
    static initialize() {
    console.log('>>> DREAM MECHA NEURAL INTERFACE INITIALIZED <<<');
    console.log('>>> Press CTRL+SHIFT+R to reset first-time setup (for testing)');
    console.log('>>> Blockmaker integration: FIXED - now uses real algorithms');
    
    window.mechaGrid = new MechaGrid();
    
    // Development shortcut to reset first-time setup
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'R') {
            e.preventDefault();
            window.mechaGrid.resetFirstTimeSetup();
        }
    });
    }
    
    // ===== FORTRESS SYSTEM =====
    
    async loadFortressStatus() {
        try {
            const response = await fetch('/api/fortress/status');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.updateFortressDisplay(data.fortress);
                }
            }
        } catch (error) {
            console.warn('Failed to load fortress status:', error);
        }
    }
    
    updateFortressDisplay(fortressData) {
        // Update HP display
        const currentHPElement = document.getElementById('fortressCurrentHP');
        const maxHPElement = document.getElementById('fortressMaxHP');
        const hpFillElement = document.getElementById('fortressHPFill');
        
        if (currentHPElement && maxHPElement && hpFillElement) {
            currentHPElement.textContent = fortressData.current_hp.toLocaleString();
            maxHPElement.textContent = fortressData.max_hp.toLocaleString();
            
            // Update HP bar
            const hpPercent = fortressData.hp_percentage;
            hpFillElement.style.width = hpPercent + '%';
            
            // Update HP bar color based on health
            hpFillElement.classList.remove('healthy', 'warning', 'critical');
            if (hpPercent > 70) {
                hpFillElement.classList.add('healthy');
            } else if (hpPercent > 30) {
                hpFillElement.classList.add('warning');
            } else {
                hpFillElement.classList.add('critical');
            }
        }
        
        // Update stats
        const totalDamageElement = document.getElementById('fortressTotalDamage');
        const daysAttackedElement = document.getElementById('fortressDaysAttacked');
        const lastAttackElement = document.getElementById('fortressLastAttack');
        
        if (totalDamageElement) {
            totalDamageElement.textContent = fortressData.total_damage_taken.toLocaleString();
        }
        if (daysAttackedElement) {
            daysAttackedElement.textContent = fortressData.days_under_attack;
        }
        if (lastAttackElement) {
            lastAttackElement.textContent = fortressData.last_attack_date || 'Never';
        }
        
        // Update status indicator
        const statusIndicator = document.getElementById('fortressStatusIndicator');
        const statusText = statusIndicator?.querySelector('.status-text');
        
        if (statusText) {
            if (fortressData.current_hp <= 0) {
                statusText.textContent = '💀 FORTRESS FALLEN';
                statusIndicator.classList.add('fortress-under-attack');
            } else if (fortressData.days_under_attack > 0) {
                statusText.textContent = '⚠️ UNDER SIEGE';
                statusIndicator.classList.add('fortress-under-attack');
            } else {
                statusText.textContent = '🛡️ FORTRESS SECURE';
                statusIndicator.classList.remove('fortress-under-attack');
            }
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    MechaGrid.initialize();
});