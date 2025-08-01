// Debug script to diagnose layout issues
console.log('=== LAYOUT DEBUG SCRIPT ===');

// Check if layout mode is active
const body = document.body;
console.log('Body classes:', body.className);
console.log('Layout mode active:', body.classList.contains('layout-mode-active'));

// Check all layout-manageable containers
const containers = document.querySelectorAll('.layout-manageable');
console.log('Found containers:', containers.length);

containers.forEach((container, index) => {
    const containerId = container.dataset.containerId;
    const rect = container.getBoundingClientRect();
    const computedStyle = getComputedStyle(container);
    
    console.log(`Container ${index} (${containerId}):`);
    console.log('  Position:', computedStyle.position);
    console.log('  Left:', computedStyle.left);
    console.log('  Top:', computedStyle.top);
    console.log('  Width:', computedStyle.width);
    console.log('  Height:', computedStyle.height);
    console.log('  Transform:', computedStyle.transform);
    console.log('  BoundingRect:', {
        left: rect.left,
        top: rect.top,
        width: rect.width,
        height: rect.height
    });
    console.log('  Inline styles:', container.style.cssText);
    console.log('---');
});

// Check layout manager state
if (window.layoutManager) {
    console.log('Layout Manager state:');
    console.log('  isLayoutMode:', window.layoutManager.isLayoutMode);
    console.log('  selectedContainer:', window.layoutManager.selectedContainer);
    console.log('  layoutData:', window.layoutManager.layoutData);
} else {
    console.log('Layout Manager not found on window object');
}

// Check for any containers with absolute positioning
const absoluteContainers = Array.from(containers).filter(c => 
    getComputedStyle(c).position === 'absolute' || 
    getComputedStyle(c).position === 'fixed'
);
console.log('Containers with absolute/fixed positioning:', absoluteContainers.length);
absoluteContainers.forEach(c => {
    console.log('  Container:', c.dataset.containerId, 'Position:', getComputedStyle(c).position);
}); 