# 🌞 Solar Core System - Silver Void Energy Source

## Overview

The Solar Core System is an infinite energy source designed for the Silver Void game environment. It provides centralized energy distribution, real-time monitoring, and a deadly shut-off mechanism accessible to players.

## 🎯 Key Features

### **Infinite Energy Generation**
- Unlimited energy production
- Real-time energy distribution
- Priority-based consumer management

### **Deadly Shut-Off Mechanism**
- Accessible to players but extremely dangerous
- Distance-based radiant damage calculation
- Core can be restarted after shut-off

### **Real-Time Monitoring**
- Live energy consumption tracking
- Consumer status monitoring
- GUI interface for system management

### **Modular Architecture**
- Easy integration with game systems
- Thread-safe operation
- Callback-based monitoring system

## 🏗️ Architecture

### Core Components

```
core/managers/solar_core_manager.py  # Main energy management system
gui/solar_monitor.py                 # Real-time monitoring interface
test_solar_core.py                   # System testing and demonstration
```

### Energy Priority System

1. **CRITICAL** - Life support, core systems
2. **HIGH** - Navigation, communication, AI processing
3. **MEDIUM** - Environmental controls, lighting
4. **LOW** - Decorative systems, luxury features

## 🚀 Quick Start

### 1. Basic Usage

```python
from core.managers.solar_core_manager import get_solar_core, EnergyPriority

# Get the solar core instance
solar_core = get_solar_core()

# Register energy consumers
solar_core.register_consumer("Life Support", EnergyPriority.CRITICAL, 10.0)
solar_core.register_consumer("Navigation", EnergyPriority.HIGH, 5.0)

# Check energy status
status = solar_core.get_energy_status()
print(f"Current consumption: {status['current_consumption']} units/sec")
```

### 2. Real-Time Monitoring

```python
def energy_callback(status):
    print(f"Energy update: {status['current_consumption']} units/sec")

solar_core.add_monitoring_callback(energy_callback)
```

### 3. Shut-Off Mechanism

```python
# Player attempts to shut off the core
result = solar_core.attempt_shut_off(player_distance=0.5)

if result['success']:
    print("Core shut off - but player took massive damage!")
    print(f"Damage: {result['damage_taken']}")
```

## 🎮 Game Integration

### Player Interaction

- **Distance 0-1 units**: Can shut off core, takes 1000 radiant damage
- **Distance 1-5 units**: Takes 500 radiant damage, cannot shut off
- **Distance 5+ units**: No damage, cannot access shut-off

### Energy Consumers

Systems can register as energy consumers:

```python
# Example: Lighting system
solar_core.register_consumer("Ambient Lighting", EnergyPriority.MEDIUM, 2.0)

# Example: AI system
solar_core.register_consumer("AI Processing", EnergyPriority.HIGH, 8.0)
```

## 📊 Monitoring Interface

Run the GUI monitor:

```bash
python gui/solar_monitor.py
```

Features:
- Real-time energy consumption display
- Consumer status table
- Emergency shut-off controls
- System restart functionality

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_solar_core.py
```

Tests cover:
- Energy generation and distribution
- Consumer registration
- Shut-off mechanics
- Real-time monitoring
- Thread safety

## 🔧 Configuration

### Energy Generation
- **Infinite**: Set to `float('inf')` for unlimited energy
- **Finite**: Modify `_energy_generation_rate` for limited energy

### Radiant Damage
- **Threshold**: 1000 damage per second at core
- **Distance scaling**: Linear reduction with distance
- **Accessibility**: Configurable via `_shut_off_accessible`

### Monitoring
- **Update frequency**: 10 FPS (0.1 second intervals)
- **Callback system**: Real-time notifications
- **Thread safety**: Daemon threads for background operation

## 🎯 Integration with Sharkman

The Solar Core System integrates seamlessly with the existing Sharkman architecture:

- Uses established manager patterns
- Follows modular design principles
- Compatible with existing GUI framework
- Thread-safe operation

## 🔮 Future Enhancements

### Phase 2: Environment Systems
- Gravity control systems
- Atmospheric regulation
- Temperature management
- Communication networks

### Phase 3: Advanced Features
- Energy efficiency optimization
- Backup power systems
- Energy crisis management
- Predictive consumption modeling

## 🛡️ Safety Features

- **Thread-safe operation**: All operations are thread-safe
- **Error handling**: Graceful error recovery
- **Resource management**: Proper cleanup on shutdown
- **Distance validation**: Safe shut-off mechanics

## 📝 API Reference

### SolarCoreManager

#### Methods
- `register_consumer(name, priority, rate)` - Register energy consumer
- `unregister_consumer(name)` - Remove energy consumer
- `set_consumer_active(name, active)` - Activate/deactivate consumer
- `get_energy_status()` - Get current energy status
- `attempt_shut_off(distance)` - Attempt core shut-off
- `restart_core()` - Restart after shut-off
- `add_monitoring_callback(callback)` - Add monitoring callback

#### Properties
- `is_active` - Core operational status
- `total_energy_generated` - Cumulative energy production
- `current_consumption` - Current consumption rate
- `consumers` - Registered consumer list

## 🎮 Game Design Notes

### Silver Void Integration
- The solar core serves as the central power source
- Players can attempt to shut it off for dramatic effect
- Energy distribution affects game mechanics
- Real-time monitoring provides immersion

### Balance Considerations
- Infinite energy prevents resource management
- Shut-off mechanism provides risk/reward
- Priority system allows strategic energy allocation
- Distance-based damage creates tension

---

**Status**: ✅ Core system operational  
**Version**: 1.0.0  
**Compatibility**: Python 3.10+, PyQt5  
**Architecture**: Modular, thread-safe, real-time 