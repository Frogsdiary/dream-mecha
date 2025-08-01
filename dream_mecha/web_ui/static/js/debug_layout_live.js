// Live Layout Debug System
// Run this in the browser console to get real-time debugging

console.log('🔍 LIVE LAYOUT DEBUGGER STARTED');

// Override console.log to track layout operations
const originalLog = console.log;
let logBuffer = [];

console.log = function(...args) {
    logBuffer.push(args.join(' '));
    if (logBuffer.length > 50) logBuffer.shift(); // Keep last 50 logs
    originalLog.apply(console, args);
};

// Function to show current state
window.debugLayoutState = function() {
    console.log('=== LAYOUT STATE DEBUG ===');
    
    // Check layout manager
    const lm = window.layoutManager;
    if (lm) {
        console.log('Layout Manager exists:');
        console.log('  isLayoutMode:', lm.isLayoutMode);
        console.log('  selectedContainer:', lm.selectedContainer?.dataset?.containerId);
        console.log('  draggedElement:', lm.draggedElement?.dataset?.containerId);
        console.log('  resizeElement:', lm.resizeElement?.dataset?.containerId);
    } else {
        console.log('❌ Layout Manager not found');
    }
    
    // Check all containers
    const containers = document.querySelectorAll('.layout-manageable');
    console.log(`Found ${containers.length} containers:`);
    
    containers.forEach((container, i) => {
        const id = container.dataset.containerId;
        const rect = container.getBoundingClientRect();
        const style = getComputedStyle(container);
        
        console.log(`  ${i+1}. ${id}:`);
        console.log(`     Position: ${style.position}`);
        console.log(`     Left/Top: ${style.left}/${style.top}`);
        console.log(`     Size: ${Math.round(rect.width)}x${Math.round(rect.height)}`);
        console.log(`     Classes: ${container.className}`);
        if (container.style.cssText) {
            console.log(`     Inline: ${container.style.cssText}`);
        }
    });
    
    // Check for event listeners
    console.log('Recent layout operations:', logBuffer.slice(-10));
};

// Function to completely reset everything
window.emergencyReset = function() {
    console.log('🚨 EMERGENCY RESET TRIGGERED');
    
    // Stop all event propagation temporarily
    const stopEvents = (e) => {
        e.stopPropagation();
        e.preventDefault();
    };
    
    document.addEventListener('click', stopEvents, true);
    document.addEventListener('mousedown', stopEvents, true);
    document.addEventListener('mousemove', stopEvents, true);
    
    setTimeout(() => {
        // Remove all layout classes and styles
        document.querySelectorAll('.layout-manageable').forEach(container => {
            container.style.cssText = '';
            container.classList.remove('layout-selected');
            container.removeAttribute('data-current-scale');
        });
        
        // Remove all corner boxes
        document.querySelectorAll('.corner-box').forEach(box => box.remove());
        
        // Reset body class
        document.body.classList.remove('layout-mode-active');
        
        // Hide controls
        const controls = document.getElementById('layoutControls');
        const selector = document.getElementById('containerSelector');
        if (controls) controls.style.display = 'none';
        if (selector) selector.style.display = 'none';
        
        // Reset layout manager if it exists
        if (window.layoutManager) {
            window.layoutManager.isLayoutMode = false;
            window.layoutManager.selectedContainer = null;
            window.layoutManager.draggedElement = null;
            window.layoutManager.resizeElement = null;
        }
        
        // Re-enable events
        document.removeEventListener('click', stopEvents, true);
        document.removeEventListener('mousedown', stopEvents, true);
        document.removeEventListener('mousemove', stopEvents, true);
        
        console.log('✅ Emergency reset complete');
    }, 100);
};

// Monitor for unexpected positioning changes
const originalSetProperty = CSSStyleDeclaration.prototype.setProperty;
CSSStyleDeclaration.prototype.setProperty = function(property, value, priority) {
    if (property === 'position' && value === 'absolute') {
        console.log('⚠️ Setting position:absolute on:', this.parentElement?.dataset?.containerId || this.parentElement?.className);
        console.trace(); // Show stack trace
    }
    return originalSetProperty.call(this, property, value, priority);
};

console.log('🎯 Debug functions available:');
console.log('  window.debugLayoutState() - Show current state');
console.log('  window.emergencyReset() - Force reset everything');
console.log('  Click tracking and position monitoring active');

// Auto-debug on container clicks
document.addEventListener('click', (e) => {
    if (e.target.closest('.layout-manageable')) {
        const container = e.target.closest('.layout-manageable');
        console.log(`🖱️ Clicked container: ${container.dataset.containerId}`);
        setTimeout(() => window.debugLayoutState(), 100);
    }
}, true); 