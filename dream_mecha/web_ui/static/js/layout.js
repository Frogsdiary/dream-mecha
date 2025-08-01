// ===== NATIVE LAYOUT SYSTEM =====
// Simple, clean, and actually works

class LayoutManager {
    constructor() {
        this.isLayoutMode = false;
        this.selectedContainer = null;
        this.dotSize = 16; // 4px dot matrix
    }
    
    init() {
        this.setupLayoutControls();
        this.setupContainerInteraction();
        
        // Load appropriate layout based on screen size
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            this.loadMobileLayout();
        } else {
            this.loadLayout(); // Auto-load saved layout on page load
        }
        
        console.log('Native Layout Manager initialized');
    }

    // ===== LAYOUT MODE TOGGLE =====
    
    enterLayoutMode() {
        this.isLayoutMode = true;
        document.body.classList.add('layout-mode-active');
        
        // Show layout controls and container selector
        const controls = document.getElementById('layoutControls');
        const selector = document.getElementById('containerSelector');
        if (controls) controls.style.display = 'flex';
        if (selector) selector.style.display = 'flex';
        
        // Check if mobile (debug with more info)
        const isMobile = window.innerWidth <= 768;
        console.log('Screen width:', window.innerWidth, 'Is mobile:', isMobile);
        console.log('User agent:', navigator.userAgent);
        
        if (isMobile) {
            this.enterMobileReorderMode();
        } else {
            this.enterDesktopDragMode();
        }
        
        console.log(isMobile ? 'Mobile reorder mode activated' : 'Desktop drag mode activated');
    }
    
    enterDesktopDragMode() {
        // Desktop mode: just make containers draggable, no extra UI
        // The layout mode should be "invisible" - UI looks the same but with drag functionality
        this.makeContainersDraggable();
    }
    
    enterMobileReorderMode() {
        // Show mobile reorder interface
        this.showMobileReorderInterface();
        
        // Make containers reorderable instead of draggable
        this.makeContainersReorderable();
    }
    
    exitLayoutMode() {
        this.isLayoutMode = false;
        document.body.classList.remove('layout-mode-active');
        
        // Hide layout controls and container selector
        const controls = document.getElementById('layoutControls');
        const selector = document.getElementById('containerSelector');
        if (controls) controls.style.display = 'none';
        if (selector) selector.style.display = 'none';
        
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            // Hide mobile interface
            this.hideMobileReorderInterface();
        }
        
        // Remove draggable functionality
        this.removeDraggable();
        
        // Deselect container
        this.deselectContainer();
        
        console.log('Layout mode deactivated');
    }

    // ===== SIMPLE DRAG SYSTEM =====
    
    makeContainersDraggable() {
        const containers = document.querySelectorAll('.layout-manageable');
        containers.forEach(container => {
            // Click to select - use the container itself, not the clicked target
            container.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectContainer(container);
            });
            
            // Mouse drag - only start if container is already selected
            container.addEventListener('mousedown', (e) => {
                if (this.selectedContainer === container) {
                    this.startDrag(e, container);
                }
            });
            
            // Touch drag for mobile - only start if container is already selected
            container.addEventListener('touchstart', (e) => {
                if (this.selectedContainer === container) {
                    // Prevent default touch behavior
                    e.preventDefault();
                    this.startTouchDrag(e, container);
                }
            }, { passive: false });
        });
    }
    
    removeDraggable() {
        const containers = document.querySelectorAll('.layout-manageable');
        containers.forEach(container => {
            container.classList.remove('selected');
        });
        
        // Clean up any active drag listeners
        if (this.boundHandleDrag) {
            document.removeEventListener('mousemove', this.boundHandleDrag);
            document.removeEventListener('mouseup', this.boundStopDrag);
            this.boundHandleDrag = null;
            this.boundStopDrag = null;
        }
        
        if (this.boundHandleTouchDrag) {
            document.removeEventListener('touchmove', this.boundHandleTouchDrag);
            document.removeEventListener('touchend', this.boundStopTouchDrag);
            this.boundHandleTouchDrag = null;
            this.boundStopTouchDrag = null;
        }
    }
    
    selectContainer(container) {
        if (!this.isLayoutMode) return;
        
        // Deselect previous
        this.deselectContainer();
        
        // Select new container
        this.selectedContainer = container;
        container.classList.add('selected');
        
        const containerId = container.dataset.containerId;
        
        // Make all other containers semi-transparent
        const allContainers = document.querySelectorAll('.layout-manageable');
        allContainers.forEach(c => {
            if (c !== container) {
                c.style.opacity = '0.3';
            } else {
                c.style.opacity = '1';
            }
        });
        
        // Highlight the corresponding button in container selector
        const buttons = document.querySelectorAll('#containerSelector button');
        buttons.forEach(btn => {
            if (btn.dataset.container === containerId) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }
        });
        
        console.log('Container selected:', containerId);
    }
    
    startDrag(e, container) {
        if (!this.isLayoutMode || this.selectedContainer !== container) return;
        
        e.preventDefault();
        
        // Calculate initial offset
        const rect = container.getBoundingClientRect();
        this.dragOffset = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        
        // Store initial position but DON'T set absolute yet
        this.initialRect = rect;
        this.hasMoved = false;
        
        // Store bound functions so we can remove them later
        this.boundHandleDrag = (e) => this.handleDrag(e, container);
        this.boundStopDrag = () => this.stopDrag(container);
        
        // Add drag listeners
        document.addEventListener('mousemove', this.boundHandleDrag);
        document.addEventListener('mouseup', this.boundStopDrag);
        
        console.log('Drag started');
    }
    
    handleDrag(e, container) {
        if (!this.isLayoutMode) return;
        
        // Only set absolute positioning when user actually moves
        if (!this.hasMoved) {
            // Create a placeholder to maintain layout space
            this.createPlaceholder(container);
            
            container.style.position = 'absolute';
            container.style.left = this.initialRect.left + 'px';
            container.style.top = this.initialRect.top + 'px';
            container.style.zIndex = 1000;
            this.hasMoved = true;
        }
        
        let newX = e.clientX - this.dragOffset.x;
        let newY = e.clientY - this.dragOffset.y;
        
        // Snap to 16px dot matrix
        newX = Math.round(newX / 16) * 16;
        newY = Math.round(newY / 16) * 16;
        
        // Prevent overlaps - check collision with other containers
        const validPosition = this.checkCollisionAndAdjust(container, newX, newY);
        
        container.style.left = validPosition.x + 'px';
        container.style.top = validPosition.y + 'px';
    }
    
    stopDrag(container) {
        // Remove drag listeners properly
        document.removeEventListener('mousemove', this.boundHandleDrag);
        document.removeEventListener('mouseup', this.boundStopDrag);
        
        // Clear bound functions
        this.boundHandleDrag = null;
        this.boundStopDrag = null;
        
        console.log('Drag ended');
    }
    
    // ===== MOBILE TOUCH DRAG SYSTEM =====
    
    startTouchDrag(e, container) {
        if (!this.isLayoutMode || this.selectedContainer !== container) return;
        
        const touch = e.touches[0];
        
        // Calculate initial offset
        const rect = container.getBoundingClientRect();
        this.dragOffset = {
            x: touch.clientX - rect.left,
            y: touch.clientY - rect.top
        };
        
        // Store initial position but DON'T set absolute yet
        this.initialRect = rect;
        this.hasMoved = false;
        
        // Store bound functions for touch events
        this.boundHandleTouchDrag = (e) => this.handleTouchDrag(e, container);
        this.boundStopTouchDrag = () => this.stopTouchDrag(container);
        
        // Add touch listeners
        document.addEventListener('touchmove', this.boundHandleTouchDrag, { passive: false });
        document.addEventListener('touchend', this.boundStopTouchDrag);
        
        console.log('Touch drag started');
    }
    
    handleTouchDrag(e, container) {
        if (!this.isLayoutMode) return;
        
        e.preventDefault(); // Prevent scrolling
        const touch = e.touches[0];
        
        // Only set absolute positioning when user actually moves
        if (!this.hasMoved) {
            // Create placeholder to maintain layout space
            this.createPlaceholder(container);
        
        container.style.position = 'absolute';
            container.style.left = this.initialRect.left + 'px';
            container.style.top = this.initialRect.top + 'px';
            container.style.zIndex = 1000;
            this.hasMoved = true;
        }
        
        let newX = touch.clientX - this.dragOffset.x;
        let newY = touch.clientY - this.dragOffset.y;
        
        // Snap to 16px dot matrix
        newX = Math.round(newX / 16) * 16;
        newY = Math.round(newY / 16) * 16;
        
        // Prevent overlaps - check collision with other containers
        const validPosition = this.checkCollisionAndAdjust(container, newX, newY);
        
        container.style.left = validPosition.x + 'px';
        container.style.top = validPosition.y + 'px';
    }
    
    stopTouchDrag(container) {
        // Remove touch listeners properly
        document.removeEventListener('touchmove', this.boundHandleTouchDrag);
        document.removeEventListener('touchend', this.boundStopTouchDrag);
        
        // Clear bound functions
        this.boundHandleTouchDrag = null;
        this.boundStopTouchDrag = null;
        
        console.log('Touch drag ended');
    }
    
    // ===== MOBILE REORDER SYSTEM =====
    
    makeContainersReorderable() {
        const containers = document.querySelectorAll('.layout-manageable');
        this.containerOrder = Array.from(containers).map(c => c.dataset.containerId);
        
        containers.forEach(container => {
            // Add reorder controls to each container
            this.addReorderControls(container);
        });
    }
    
    addReorderControls(container) {
        // Remove existing controls
        const existing = container.querySelector('.mobile-reorder-controls');
        if (existing) existing.remove();
        
        // Create reorder controls
        const controls = document.createElement('div');
        controls.className = 'mobile-reorder-controls';
        controls.innerHTML = `
            <button class="reorder-btn up-btn" data-direction="up">▲</button>
            <button class="reorder-btn down-btn" data-direction="down">▼</button>
        `;
        
        // Add to container
        container.style.position = 'relative';
        container.appendChild(controls);
        
        // Add event listeners
        controls.querySelector('.up-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.moveContainer(container, 'up');
        });
        
        controls.querySelector('.down-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.moveContainer(container, 'down');
        });
    }
    
    moveContainer(container, direction) {
        const containerId = container.dataset.containerId;
        const currentIndex = this.containerOrder.indexOf(containerId);
        
        if (direction === 'up' && currentIndex > 0) {
            // Swap with previous
            [this.containerOrder[currentIndex], this.containerOrder[currentIndex - 1]] = 
            [this.containerOrder[currentIndex - 1], this.containerOrder[currentIndex]];
            this.applyMobileOrder();
        } else if (direction === 'down' && currentIndex < this.containerOrder.length - 1) {
            // Swap with next
            [this.containerOrder[currentIndex], this.containerOrder[currentIndex + 1]] = 
            [this.containerOrder[currentIndex + 1], this.containerOrder[currentIndex]];
            this.applyMobileOrder();
        }
    }
    
    applyMobileOrder() {
        const mainContent = document.querySelector('.main-content');
        if (!mainContent) return;
        
        // Create ordered array of containers
        const orderedContainers = this.containerOrder.map(id => 
            document.querySelector(`[data-container-id="${id}"]`)
        ).filter(c => c);
        
        // Reorder DOM elements
        orderedContainers.forEach(container => {
            mainContent.appendChild(container);
        });
        
        // Update visual feedback
        this.updateOrderIndicators();
        
        console.log('Mobile order updated:', this.containerOrder);
    }
    
    updateOrderIndicators() {
        const containers = document.querySelectorAll('.layout-manageable');
        containers.forEach((container, index) => {
            // Update up/down button states
            const upBtn = container.querySelector('.up-btn');
            const downBtn = container.querySelector('.down-btn');
            
            if (upBtn) upBtn.disabled = index === 0;
            if (downBtn) downBtn.disabled = index === containers.length - 1;
        });
    }
    
    showMobileReorderInterface() {
        console.log('Creating mobile reorder interface...');
        
        // Remove existing interface if it exists
        const existing = document.getElementById('mobileReorderInterface');
        if (existing) {
            existing.remove();
        }
        
        // Create mobile-specific interface
        const mobileInterface = document.createElement('div');
        mobileInterface.id = 'mobileReorderInterface';
        mobileInterface.className = 'mobile-reorder-interface';
        mobileInterface.style.cssText = `
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            background: rgba(0, 0, 0, 0.95) !important;
            border-bottom: 2px solid #fff !important;
            padding: 16px !important;
            z-index: 99999 !important;
            text-align: center !important;
            display: block !important;
        `;
        mobileInterface.innerHTML = `
            <div class="mobile-header">
                <h3 style="color: #fff; margin: 0 0 8px 0; font-size: 18px;">Reorder Menu Items</h3>
                <p style="color: #ccc; margin: 0 0 16px 0; font-size: 14px;">Use ▲▼ buttons to arrange your layout</p>
            </div>
            <div class="mobile-controls" style="display: flex; gap: 8px; justify-content: center;">
                <button id="saveMobileLayoutBtn" class="mobile-btn primary">Save Layout</button>
                <button id="resetMobileLayoutBtn" class="mobile-btn">Reset</button>
                <button id="exitMobileLayoutBtn" class="mobile-btn">Exit</button>
            </div>
        `;
        
        document.body.appendChild(mobileInterface);
        console.log('Mobile interface added to DOM');
        
        // Add event listeners
        document.getElementById('saveMobileLayoutBtn').addEventListener('click', () => this.saveMobileLayout());
        document.getElementById('resetMobileLayoutBtn').addEventListener('click', () => this.resetMobileLayout());
        document.getElementById('exitMobileLayoutBtn').addEventListener('click', () => this.exitLayoutMode());
        
        console.log('Mobile interface event listeners added');
    }
    
    hideMobileReorderInterface() {
        const mobileInterface = document.getElementById('mobileReorderInterface');
        if (mobileInterface) mobileInterface.remove();
        
        // Remove reorder controls from containers
        document.querySelectorAll('.mobile-reorder-controls').forEach(controls => {
            controls.remove();
        });
    }
    
    saveMobileLayout() {
        // Save the mobile order to localStorage
        localStorage.setItem('dream_mecha_mobile_order', JSON.stringify(this.containerOrder));
        
        // Show feedback
        const btn = document.getElementById('saveMobileLayoutBtn');
        const originalText = btn.textContent;
        btn.textContent = 'Saved!';
        btn.style.background = 'var(--success, #0f0)';
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
        }, 1500);
        
        console.log('Mobile layout saved:', this.containerOrder);
    }
    
    resetMobileLayout() {
        // Reset to original order
        this.containerOrder = ['stats', 'controls', 'grid', 'fortress', 'inventory', 'shop'];
        this.applyMobileOrder();
        localStorage.removeItem('dream_mecha_mobile_order');
        
        console.log('Mobile layout reset');
    }
    
    loadMobileLayout() {
        const saved = localStorage.getItem('dream_mecha_mobile_order');
        if (saved) {
            try {
                this.containerOrder = JSON.parse(saved);
                this.applyMobileOrder();
                console.log('Mobile layout loaded:', this.containerOrder);
            } catch (e) {
                console.error('Failed to load mobile layout:', e);
            }
        }
    }
    
    createPlaceholder(container) {
        // Remove any existing placeholder for this container
        this.removePlaceholder(container);
        
        // Create invisible placeholder that maintains the space
        const placeholder = document.createElement('div');
        placeholder.className = 'layout-placeholder';
        placeholder.dataset.placeholderFor = container.dataset.containerId;
        
        // Copy dimensions to maintain space
        const rect = container.getBoundingClientRect();
        placeholder.style.width = rect.width + 'px';
        placeholder.style.height = rect.height + 'px';
        placeholder.style.visibility = 'hidden';
        placeholder.style.pointerEvents = 'none';
        
        // Insert placeholder in the same position
        container.parentNode.insertBefore(placeholder, container);
    }
    
    removePlaceholder(container) {
        const containerId = container.dataset.containerId;
        const existingPlaceholder = document.querySelector(`[data-placeholder-for="${containerId}"]`);
        if (existingPlaceholder) {
            existingPlaceholder.remove();
        }
    }
    
    checkCollisionAndAdjust(draggedContainer, newX, newY) {
        const draggedRect = {
            left: newX,
            top: newY,
            right: newX + draggedContainer.offsetWidth,
            bottom: newY + draggedContainer.offsetHeight
        };
        
        // Check against all other absolute positioned containers
        const otherContainers = document.querySelectorAll('.layout-manageable');
        
        for (const container of otherContainers) {
            if (container === draggedContainer) continue;
            if (container.style.position !== 'absolute') continue;
            
            const containerRect = container.getBoundingClientRect();
            const otherRect = {
                left: parseInt(container.style.left),
                top: parseInt(container.style.top),
                right: parseInt(container.style.left) + container.offsetWidth,
                bottom: parseInt(container.style.top) + container.offsetHeight
            };
            
            // Check if rectangles overlap
            if (this.rectanglesOverlap(draggedRect, otherRect)) {
                // Find nearest non-overlapping position
                return this.findNearestValidPosition(draggedContainer, newX, newY, otherRect);
            }
        }
        
        return { x: newX, y: newY };
    }
    
    rectanglesOverlap(rect1, rect2) {
        return !(rect1.right <= rect2.left || 
                rect1.left >= rect2.right || 
                rect1.bottom <= rect2.top || 
                rect1.top >= rect2.bottom);
    }
    
    findNearestValidPosition(container, originalX, originalY, obstacleRect) {
        const containerWidth = container.offsetWidth;
        const containerHeight = container.offsetHeight;
        
        // Try positions around the obstacle (snapped to 16px grid)
        const positions = [
            // Right of obstacle
            { x: Math.ceil(obstacleRect.right / 16) * 16, y: originalY },
            // Left of obstacle  
            { x: Math.floor((obstacleRect.left - containerWidth) / 16) * 16, y: originalY },
            // Below obstacle
            { x: originalX, y: Math.ceil(obstacleRect.bottom / 16) * 16 },
            // Above obstacle
            { x: originalX, y: Math.floor((obstacleRect.top - containerHeight) / 16) * 16 }
        ];
        
        // Find the closest valid position
        let bestPosition = { x: originalX, y: originalY };
        let bestDistance = Infinity;
        
        for (const pos of positions) {
            // Ensure position is within viewport
            if (pos.x >= 0 && pos.y >= 0 && 
                pos.x + containerWidth <= window.innerWidth && 
                pos.y + containerHeight <= window.innerHeight) {
                
                const distance = Math.sqrt(
                    Math.pow(pos.x - originalX, 2) + Math.pow(pos.y - originalY, 2)
                );
                
                if (distance < bestDistance) {
                    bestDistance = distance;
                    bestPosition = pos;
                }
            }
        }
        
        return bestPosition;
    }

    // ===== CONTAINER SELECTION =====
    
    deselectContainer() {
        if (this.selectedContainer) {
            this.selectedContainer.classList.remove('selected');
            this.selectedContainer = null;
        }
        
        // Clear transparency from all containers
        const allContainers = document.querySelectorAll('.layout-manageable');
        allContainers.forEach(c => {
            c.style.opacity = '1';
        });
        
        // Clear button highlights
        const buttons = document.querySelectorAll('#containerSelector button');
        buttons.forEach(btn => btn.classList.remove('selected'));
    }

    // ===== LAYOUT PERSISTENCE =====
    
    saveLayout() {
        const containers = document.querySelectorAll('.layout-manageable');
        const layout = {};
        
        containers.forEach(container => {
            const id = container.dataset.containerId;
            if (id && container.style.position === 'absolute') {
                layout[id] = {
                    left: container.style.left,
                    top: container.style.top,
                    width: container.style.width,
                    height: container.style.height
                };
            }
        });
        
        localStorage.setItem('dream_mecha_layout', JSON.stringify(layout));
        console.log('Layout saved:', layout);
    }
    
    loadLayout() {
        const saved = localStorage.getItem('dream_mecha_layout');
        if (!saved) return;
        
        try {
            const layout = JSON.parse(saved);
            Object.entries(layout).forEach(([id, pos]) => {
                const container = document.querySelector(`[data-container-id="${id}"]`);
                if (container) {
                    // Create placeholder before making absolute
                    this.createPlaceholder(container);
                    
                    container.style.position = 'absolute';
                    container.style.left = pos.left;
                    container.style.top = pos.top;
                    if (pos.width) container.style.width = pos.width;
                    if (pos.height) container.style.height = pos.height;
                }
            });
            console.log('Layout loaded:', layout);
        } catch (e) {
            console.error('Failed to load layout:', e);
        }
    }
    
    resetLayout() {
        localStorage.removeItem('dream_mecha_layout');
        
        const containers = document.querySelectorAll('.layout-manageable');
        containers.forEach(container => {
            container.style.position = '';
            container.style.left = '';
            container.style.top = '';
            container.style.width = '';
            container.style.height = '';
            container.classList.remove('selected');
            
            // Remove any placeholders
            this.removePlaceholder(container);
        });
        
        console.log('Layout reset');
    }

    // ===== CONTROLS =====
    // Controls removed - layout mode is now "invisible" with just drag functionality

    // ===== EVENT SETUP =====
    
    setupLayoutControls() {
        const layoutBtn = document.getElementById('layoutModeBtn');
        const saveBtn = document.getElementById('saveLayoutBtn');
        const resetBtn = document.getElementById('resetLayoutBtn');
        const exitBtn = document.getElementById('exitLayoutModeBtn');
        
        if (layoutBtn) {
            console.log('Layout button found, adding listener');
            layoutBtn.addEventListener('click', () => {
                console.log('Layout button clicked! isLayoutMode:', this.isLayoutMode);
                if (this.isLayoutMode) {
                    this.exitLayoutMode();
                } else {
                    this.enterLayoutMode();
                }
            });
        } else {
            console.error('Layout button not found!');
        }
        
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveLayout());
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetLayout());
        }
        
        if (exitBtn) {
            exitBtn.addEventListener('click', () => this.exitLayoutMode());
        }
        
        // Container selector
        const selector = document.getElementById('containerSelector');
        if (selector) {
            const buttons = selector.querySelectorAll('button');
            buttons.forEach(button => {
                button.addEventListener('click', () => {
                    const containerId = button.dataset.container;
                    if (containerId) {
                        this.selectContainerById(containerId);
                    }
                });
            });
        }
    }
    
    selectContainerById(containerId) {
        const container = document.querySelector(`[data-container-id="${containerId}"]`);
        if (container) {
            this.selectContainer(container);
        }
    }
    
    setupContainerInteraction() {
        // Click outside to deselect
        document.addEventListener('click', (e) => {
            if (!this.isLayoutMode) return;
            
            const isLayoutElement = e.target.closest('.layout-manageable, .layout-controls, .container-selector');
            if (!isLayoutElement) {
                this.deselectContainer();
            }
        });
    }
}

// Initialize
let layoutManager;
document.addEventListener('DOMContentLoaded', () => {
    layoutManager = new LayoutManager();
    layoutManager.init();
}); 