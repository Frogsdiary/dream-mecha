# Debug Steps for Layout Issues

## 🚨 **Current Issue**: Layout gets "messed up" when clicking containers

Based on your console logs showing continuous drag operations, something is triggering unwanted drag events.

## 🔍 **Step 1: Load Debug Tools**

1. **Open browser console** (F12)
2. **Copy and paste** the content of `debug_layout_live.js` into console
3. **Press Enter** - you should see "🔍 LIVE LAYOUT DEBUGGER STARTED"

## 🔍 **Step 2: Check Current State**

In console, run:
```javascript
window.debugLayoutState()
```

This will show:
- Layout manager state
- All container positions
- Any inline styles applied

## 🚨 **Step 3: Emergency Reset**

In console, run:
```javascript
window.emergencyReset()
```

This should immediately fix the layout. **Tell me what happens!**

## 🔍 **Step 4: Load Simple Layout Manager**

1. **Copy and paste** the content of `layout_simple.js` into console
2. This replaces the complex layout manager with a minimal version
3. Try clicking "Layout Mode" - it should just show boundaries, nothing else

## 🔍 **Step 5: Reproduce the Issue**

Now try to reproduce the problem:
1. Click "Layout Mode"
2. Click on a container (like stats in top-left)
3. **Watch the console** - any messages?
4. **Tell me exactly what happens visually**

## 🎯 **Questions for You**

Please answer these to help me debug:

1. **When you run `window.emergencyReset()`** - does it fix the layout?
2. **When you click a container in layout mode** - do you see console messages?
3. **What browser are you using?** (Chrome, Firefox, etc.)
4. **Are there any JavaScript errors** in the console (red text)?
5. **When you run `window.debugLayoutState()`** - what does it show?

## 🔧 **Emergency Commands**

Copy/paste these in console for immediate help:

```javascript
// Complete reset
document.querySelectorAll('.layout-manageable').forEach(el => el.style.cssText = '');
document.body.classList.remove('layout-mode-active');
document.querySelectorAll('.corner-box').forEach(el => el.remove());

// Check for rogue event listeners
console.log('Event listeners on body:', getEventListeners(document.body));

// Check container positions
document.querySelectorAll('.layout-manageable').forEach((el, i) => {
    console.log(`${i}: ${el.dataset.containerId} - Position: ${getComputedStyle(el).position}`);
});
```

## 🎯 **What I Need From You**

1. **Run the debug tools** and tell me what you see
2. **Try the emergency reset** and tell me if it fixes things
3. **Copy/paste the console output** when the issue happens
4. **Tell me the exact steps** that cause the problem

The difference between "Emergency Reset" and normal "Reset Layout":
- **Emergency Reset**: Stops ALL events, clears ALL styles, forces everything back to normal
- **Reset Layout**: Only clears saved layout data, doesn't fix broken state

Let's solve this step by step! 🎯 