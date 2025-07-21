# 🧪 Test Guide - Xaryxis Heart System

## Quick Reference

### Available Tests

| Test File | Duration | Purpose | Best For |
|-----------|----------|---------|----------|
| `quick_test.py` | 10 seconds | Basic learning demo | Quick demonstration |
| `simple_learning_test.py` | 30 seconds | Learning limits analysis | Understanding plateaus |
| `test_learning_limits.py` | 60 seconds | Comprehensive analysis | Deep learning study |
| `test_solar_core.py` | 15 seconds | Solar core functionality | Energy system testing |
| `test_xaryxis_heart.py` | 30 seconds | Full AI system demo | Complete system overview |

## 🚀 Quick Start

### Basic Learning Demo
```bash
python quick_test.py
```
**Shows:** Learning rate progression, decision making, pattern recognition

### Learning Limits Test
```bash
python simple_learning_test.py
```
**Shows:** How learning plateaus, maximum potential analysis

### Full System Test
```bash
python test_xaryxis_heart.py
```
**Shows:** Complete AI behavior, adaptive responses, memory system

## 📊 What Each Test Demonstrates

### `quick_test.py`
- **Learning Rate Growth**: 0.500 → 0.584 (16.8% improvement)
- **Decision Making**: 91 decisions with increasing confidence
- **Pattern Recognition**: Detects energy consumption patterns
- **Memory Storage**: 93 memories collected

### `simple_learning_test.py`
- **Learning Plateaus**: Shows when learning slows down
- **Maximum Potential**: Analyzes achievable vs theoretical limits
- **Performance Metrics**: Success rates and decision quality
- **Optimal Range**: Identifies 75-85% as sweet spot

### `test_learning_limits.py`
- **Extended Learning**: 60-second comprehensive analysis
- **Learning Velocity**: Measures rate of improvement over time
- **Decision Quality**: Analyzes high-confidence decisions
- **System Behavior**: Shows how system adapts at peak learning

### `test_solar_core.py`
- **Energy Generation**: Infinite energy production
- **Node Creation**: Energy boost system with density
- **Shut-off Mechanism**: Deadly radiant damage system
- **Real-time Monitoring**: Live energy consumption tracking

### `test_xaryxis_heart.py`
- **Consciousness Integration**: Learning-based decision making
- **Adaptive Behavior**: System that improves over time
- **Memory System**: Experience-based learning
- **Emergent Intelligence**: Complex behavior from simple rules

## 🎯 Key Metrics to Watch

### Learning Rate
- **Start**: 0.500 (50%)
- **Optimal**: 0.75-0.85 (75-85%)
- **Maximum**: 1.0 (100%) - rarely reached

### Decision Confidence
- **Start**: 0.35
- **Peak**: 0.70+
- **Formula**: `learning_rate * adaptability_weight`

### Success Rate
- **Early**: 40-60%
- **Mid**: 60-75%
- **Peak**: 70-85%

### Memory Storage
- **Capacity**: 100 recent memories
- **Types**: Energy updates, reflections, decisions
- **Purpose**: Pattern recognition and learning

## 🔧 Test Configuration

### Environment Setup
```bash
# Create test energy nodes
solar_core.create_node("Test Node", 10.0, "test", (0,0,0), 1.0, 10.0)

# Monitor learning progress
status = xaryxis_heart.get_system_status()
print(f"Learning Rate: {status['learning_rate']:.3f}")
```

### Custom Test Scenarios
```python
# Low energy scenario
solar_core.create_node("Low Energy", 5.0, "test", (0,0,0), 1.0, 5.0)

# High energy scenario
solar_core.create_node("High Energy", 50.0, "test", (5,0,0), 2.0, 10.0)

# Crisis scenario
solar_core.create_node("Crisis", 100.0, "test", (0,0,0), 3.0, 15.0)
```

## 📈 Interpreting Results

### Learning Rate Progression
```
0-30s:   Rapid learning (0.500 → 0.600)
30-60s:  Moderate learning (0.600 → 0.750)
60s+:    Slow learning (0.750 → 0.850)
90%+:    Diminishing returns
```

### Plateau Detection
- **Learning velocity** drops below 20% of early rate
- **Success rate** stabilizes around 60-70%
- **New patterns** have minimal impact

### Optimal Performance Indicators
- **Learning Rate**: 75-85%
- **Decision Confidence**: 0.6+
- **Success Rate**: 70%+
- **Memory Count**: 50+ experiences

## 🎮 Game Integration Testing

### Player Interaction Tests
```python
# Test player shut-off attempt
result = solar_core.attempt_shut_off(player_distance=0.5)
print(f"Damage: {result['damage_taken']}, Success: {result['success']}")

# Test AI response to player actions
# (System automatically responds to energy changes)
```

### Environmental Response Tests
```python
# Create energy crisis
solar_core.create_node("Crisis", 100.0, "crisis", (0,0,0), 3.0, 15.0)

# Watch AI create emergency nodes
# Monitor learning rate increase
# Observe behavior weight adjustments
```

## 🔍 Troubleshooting

### Common Issues

**Learning Rate Not Increasing:**
- Check if energy nodes are being created
- Verify success rate calculation
- Ensure memory system is working

**High Failure Rate:**
- Reduce energy consumption in test nodes
- Check node creation parameters
- Monitor system state changes

**Memory Overflow:**
- System automatically keeps last 100 memories
- No manual intervention needed
- Old memories are automatically removed

### Debug Information
```python
# Get detailed system status
status = xaryxis_heart.get_system_status()
print(f"Learning Rate: {status['learning_rate']}")
print(f"Behavior Weights: {status['behavior_weights']}")
print(f"Patterns: {status['patterns']}")
print(f"Memories: {status['memories_count']}")

# Get recent decisions
recent_logs = xaryxis_heart.memory_logger.get_recent_logs(10)
for log in recent_logs:
    print(log['message'])
```

## 📚 Related Documentation

- **`LEARNING_LIMITS_DOCUMENTATION.md`** - Detailed learning analysis
- **`README_SOLAR_CORE.md`** - Solar core system documentation
- **`core/ai/xaryxis_heart.py`** - Main AI system implementation

---

**Last Updated**: July 8, 2025  
**Test Environment**: Python 3.10+, Windows 10  
**System Version**: Xaryxis Heart v1.0 