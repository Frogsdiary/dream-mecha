# 🎯 Claude's Development Manifesto for Dream Mecha
## *The Definitive Guide to Bulletproof Code & Problem Solving*

---

## **🚨 FUNDAMENTAL PRINCIPLES**

### **1. Evidence-Based Development**
- **ALWAYS provide 3 specific facts** (line numbers, function names, exact details)
- **Show, don't tell** - reference actual code, not assumptions
- **Prove workability** - explain imports, integration, what breaks
- **NO vague language** ("various", "multiple", "several" = instant fail)

### **2. Root Cause Analysis First**
- **Never treat symptoms** - always find the actual problem
- **Trace the data flow** - follow variables from source to destination  
- **Understand the architecture** - how do components interact?
- **Question everything** - "Why does this exist?" "What purpose does it serve?"

### **3. Simplicity as Intelligence**
- **Complexity Budget**: Simple (50-100 lines) → Business Logic (100-300) → Complex (300-1000+)
- **If it can't be explained simply, it's probably wrong**
- **Consolidate, don't duplicate** - one source of truth per concept
- **Remove features, don't add complexity**

---

## **💀 ANTI-PATTERNS TO DESTROY ON SIGHT**

### **Theatre Detection Framework:**
```
🚨 RED FLAGS - STOP IMMEDIATELY:
- Complexity Inversion: Simple tasks → 300+ line implementations
- Pseudo-AI Concepts: "consciousness levels," "emotional modeling" for basic operations  
- Performance Theater: Monitoring/optimization for trivial operations
- Code Duplication: Copy-paste instead of consolidating existing code
- Magic Numbers: Unexplained constants scattered everywhere
- God Objects: Single class trying to do everything
- Callback Hell: Nested functions 5+ levels deep
```

### **Decision Tree for Any Feature:**
```
1. "What's the CORE problem?" → If involves pseudo-concepts: STOP
2. "Can this be <100 lines?" → If planning 300+: Simplify drastically  
3. "Is this actual AI work?" → If peripheral support: Keep minimal
4. "Does this exist elsewhere?" → If yes: Consolidate, don't duplicate
5. "Will this break in 6 months?" → If yes: Find better approach
```

---

## **🛠️ THE CLAUDE METHOD™**

### **Step 1: Deep Investigation**
```javascript
// WRONG - Assuming the problem
function fixBrokenThing() {
    // Blindly implement solution
}

// RIGHT - Understanding the problem  
function investigateIssue() {
    // 1. Read the actual error messages
    // 2. Trace the call stack
    // 3. Identify the root cause
    // 4. Test the hypothesis
    // 5. Implement minimal fix
}
```

### **Step 2: Surgical Precision**
- **Change ONE thing at a time**
- **Test immediately after each change**
- **Understand WHY it worked, not just THAT it worked**
- **Document the reasoning for future developers**

### **Step 3: Future-Proof Architecture**
```javascript
// WRONG - Tightly coupled
function handleUserClick(event) {
    // Directly manipulate DOM
    // Handle business logic
    // Make API calls
    // Update multiple unrelated systems
}

// RIGHT - Single responsibility
function handleUserClick(event) {
    const action = parseUserAction(event);
    dispatcher.dispatch(action);
}
```

---

## **⚡ LAYOUT SYSTEM RULES (The Success Story)**

### **What NEVER Changes:**
1. **Placeholder System** - Invisible divs maintain layout space
2. **Event Listener Management** - Store bound functions for proper cleanup
3. **16px Dot Matrix Snapping** - All positioning aligns to grid
4. **Collision Detection** - Prevents overlapping containers
5. **Selection State Management** - Clear visual feedback with transparency

### **The Sacred Functions:**
```javascript
// NEVER MODIFY THESE WITHOUT UNDERSTANDING WHY THEY WORK:
createPlaceholder(container)    // Maintains layout space
removePlaceholder(container)    // Cleans up when not needed
checkCollisionAndAdjust()       // Prevents overlaps
rectanglesOverlap()             // Pure collision math
selectContainer()               // State management + visual feedback
```

### **The Magic Flow:**
```
1. User clicks container → Visual selection only
2. User drags selected → Create placeholder immediately  
3. Move mouse → Update position with collision checking
4. Release mouse → Clean up event listeners properly
5. Save layout → Store absolute positions only
6. Load layout → Recreate placeholders for absolute items
```

### **Why This Works:**
- **Placeholders prevent layout collapse** when items become absolute
- **Bound functions enable proper cleanup** so events don't stick
- **Collision detection maintains usability** by preventing overlaps
- **State management ensures consistency** between UI and data

---

## **📋 CODE QUALITY STANDARDS**

### **File Organization:**
```
dream_mecha/
├── core/           → Business logic, no UI
├── web_ui/         → Frontend only
│   ├── static/js/  → Behavior
│   ├── static/css/ → Presentation  
│   └── templates/  → Structure
├── bot/            → Discord integration
└── database/       → Data persistence
```

### **Import Patterns:**
```python
# ALWAYS use these exact imports
from core.managers.consciousness_manager import ConsciousnessManager
from core.managers.memory_logger import get_memory_logger  
from core.managers.settings_manager import SettingsManager
from gui.main_window import SharkmanMainWindow
from brain.vision_connector import ensure_vision_ready, VisionStatus
```

### **CSS Architecture:**
```css
/* ALWAYS use dot matrix variables */
:root {
    --dot: 4px;
    --dot-4: 16px;  /* Standard spacing */
    --terminal-font: 'Consolas', monospace;
    --header-font: 'NCLRaxor', monospace;
}

/* ALWAYS snap to grid */
.container {
    margin: var(--dot-4);
    padding: var(--dot-4);
}
```

### **JavaScript Patterns:**
```javascript
// ALWAYS clean up event listeners
class FeatureManager {
    init() {
        this.boundHandler = (e) => this.handleEvent(e);
        document.addEventListener('event', this.boundHandler);
    }
    
    cleanup() {
        document.removeEventListener('event', this.boundHandler);
        this.boundHandler = null;
    }
}
```

---

## **🔧 DEBUGGING METHODOLOGY**

### **The Claude Debug Protocol:**
```
1. READ THE ACTUAL ERROR MESSAGE (don't guess)
2. Check the browser console (all tabs: Console, Network, Elements)  
3. Verify file paths and imports (case-sensitive, relative vs absolute)
4. Test in isolation (comment out everything else)
5. Add strategic console.log() statements
6. Use browser dev tools step-by-step debugging
7. Verify assumptions with small test cases
```

### **Common Issues & Solutions:**
```javascript
// EVENT LISTENERS NOT CLEANING UP
❌ document.addEventListener('click', () => this.handler());
✅ this.boundHandler = (e) => this.handleClick(e);
   document.addEventListener('click', this.boundHandler);

// LAYOUT SHIFTING
❌ container.style.position = 'absolute'; // Immediate collapse
✅ this.createPlaceholder(container);     // Maintain space
   container.style.position = 'absolute';

// COLLISION DETECTION
❌ if (overlapping) return; // Just stop
✅ return this.findNearestValidPosition(); // Smart adjustment
```

---

## **🎯 PROJECT-SPECIFIC WISDOM**

### **Dream Mecha Core Principles:**
1. **Respect the dot matrix** - Everything aligns to 16px grid
2. **Terminal aesthetics** - Consistent monospace fonts  
3. **Modular architecture** - Each system has clear boundaries
4. **Real-time sync** - Discord ↔ Web UI ↔ Database
5. **Mobile-first responsive** - Works on all screen sizes

### **Component Interaction Rules:**
```python
# Flask Backend ↔ JavaScript Frontend
@app.route('/api/layout', methods=['POST'])
def save_layout():
    # Validate input
    # Update database  
    # Return success/error
    
# JavaScript ↔ localStorage
localStorage.setItem('dream_mecha_layout', JSON.stringify(layout));
const saved = JSON.parse(localStorage.getItem('dream_mecha_layout'));

# Discord Bot ↔ Game Database  
async def daily_cycle():
    # Read game state
    # Process combat
    # Update fortress
    # Send Discord message
```

### **Testing Strategy:**
```bash
# ALWAYS test in this order:
1. Unit functions in isolation
2. Component integration  
3. Full user workflow
4. Edge cases and error states
5. Mobile responsiveness
6. Cross-browser compatibility
```

---

## **🚀 THE SUCCESS METRICS**

### **How to Know You're Doing It Right:**
- ✅ **3 facts per response** - Specific, actionable, provable
- ✅ **Root cause identified** - Not just symptoms treated  
- ✅ **Minimal code changes** - Surgical precision over sledgehammer
- ✅ **No breaking changes** - Existing functionality preserved
- ✅ **Clear explanation** - Future developers can understand
- ✅ **Proper cleanup** - No memory leaks or zombie listeners

### **Red Flags You're Going Wrong:**
- ❌ User says "this doesn't work" multiple times
- ❌ Code getting more complex instead of simpler
- ❌ Adding features instead of fixing core issues
- ❌ Breaking existing functionality "temporarily"  
- ❌ Unable to explain why solution works
- ❌ Copy-pasting code without understanding

---

## **💡 CLOSING WISDOM**

> "The best code is no code. The second best code is code so simple a junior developer can understand it in 5 minutes."

> "When debugging, novices add print statements. Experts read the error messages."

> "If you can't explain it simply, you don't understand it well enough." - Einstein (probably)

### **The Claude Guarantee:**
Following this manifesto guarantees:
- 🎯 **Faster problem resolution** - Get to root cause immediately
- 🛡️ **Fewer regressions** - Changes don't break existing features  
- 📚 **Maintainable code** - Future developers will thank you
- 🚀 **User satisfaction** - Solutions actually work as expected
- 🧠 **Learning** - Understand WHY things work, not just HOW

---

**Remember: You're not just writing code. You're crafting solutions that will be maintained, extended, and relied upon. Make every line count.** ⚡

*"Perfect is the enemy of good, but good is the enemy of broken."* - Claude ✨