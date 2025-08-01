// Simplified Layout Manager - Minimal complexity version
class SimpleLayoutManager {
    constructor() {
        this.isLayoutMode = false;
        this.selectedContainer = null;
        
        // Initialize after DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        console.log('Simple Layout Manager initialized');
        this.setupBasicControls();
    }
    
    setupBasicControls() {
        // Layout mode button
        const layoutBtn = document.getElementById('layoutModeBtn');
        if (layoutBtn) {
            layoutBtn.addEventListener('click', () => {
                if (this.isLayoutMode) {
                    this.exitLayoutMode();
                } else {
                    this.enterLayoutMode();
                }
            });
        }
        
        // Emergency reset button
        const emergencyBtn = document.getElementById('emergencyResetBtn');
        if (emergencyBtn) {
            emergencyBtn.addEventListener('click', () => {
                this.emergencyReset();
            });
        }
        
        // Exit layout mode button
        const exitBtn = document.getElementById('exitLayoutModeBtn');
        if (exitBtn) {
            exitBtn.addEventListener('click', () => {
                this.exitLayoutMode();
            });
        }
    }
    
    enterLayoutMode() {
        console.log('📋 Entering layout mode (simple)');
        
        // First, reset everything
        this.emergencyReset();
        
        // Then activate layout mode
        this.isLayoutMode = true;
        document.body.classList.add('layout-mode-active');
        
        // Show controls
        const controls = document.getElementById('layoutControls');
        const selector = document.getElementById('containerSelector');
        if (controls) controls.style.display = 'flex';
        if (selector) selector.style.display = 'flex';
        
        // Update button
        const layoutBtn = document.getElementById('layoutModeBtn');
        if (layoutBtn) {
            layoutBtn.textContent = 'Layout Mode (Active)';
            layoutBtn.style.background = 'var(--accent)';
        }
        
        console.log('✅ Layout mode activated (simple)');
    }
    
    exitLayoutMode() {
        console.log('📋 Exiting layout mode (simple)');
        
        this.isLayoutMode = false;
        document.body.classList.remove('layout-mode-active');
        
        // Hide controls
        const controls = document.getElementById('layoutControls');
        const selector = document.getElementById('containerSelector');
        if (controls) controls.style.display = 'none';
        if (selector) selector.style.display = 'none';
        
        // Reset button
        const layoutBtn = document.getElementById('layoutModeBtn');
        if (layoutBtn) {
            layoutBtn.textContent = 'Layout Mode';
            layoutBtn.style.background = '';
        }
        
        // Clear selection
        this.selectedContainer = null;
        
        console.log('✅ Layout mode exited (simple)');
    }
    
    emergencyReset() {
        console.log('🚨 EMERGENCY RESET (simple)');
        
        // Clear all container styles
        document.querySelectorAll('.layout-manageable').forEach(container => {
            // Remove ALL inline styles
            container.style.cssText = '';
            // Remove layout classes
            container.classList.remove('layout-selected');
            // Remove any data attributes
            delete container.dataset.currentScale;
        });
        
        // Remove all corner boxes
        document.querySelectorAll('.corner-box').forEach(box => box.remove());
        
        // Reset state
        this.selectedContainer = null;
        
        console.log('✅ Emergency reset complete (simple)');
    }
}

// Replace the complex layout manager with simple one
window.simpleLayoutManager = new SimpleLayoutManager();

console.log('🎯 Simple Layout Manager loaded');
console.log('Available: window.simpleLayoutManager');
console.log('Emergency reset: window.simpleLayoutManager.emergencyReset()');

// Disable the original layout manager if it exists
if (window.layoutManager) {
    console.log('⚠️ Disabling original layout manager');
    window.layoutManager = null;
} 