# 04_routing - Table of Contents

## Scripts

### 0.py - Plain Python Conditional Routing (No Prefect)
- Baseline conditional routing without Prefect
- Same logic as 1.py but no decorators
- Shows what you miss: no routing visibility, no decision tracking

### 1.py - Basic If/Else Routing
- `check_data_quality()` upstream flow
- `process_valid_data()` downstream A
- `process_invalid_data()` downstream B
- Simple if/else decision

### 2.py - Multi-Branch Routing
- Priority calculation (critical/high/medium/low)
- Dispatch dictionary pattern
- Four handler flows

### 3.py - ML Threshold Routing
- Train multiple models
- Select best by F1 score
- Route: deploy / review / retrain

## Key Patterns

```python
# If/else routing
if condition:
    return flow_a()
else:
    return flow_b()

# Multi-branch dispatch
handlers = {"a": fn_a, "b": fn_b, "c": fn_c}
result = handlers[key](data)

# Threshold routing
if metric >= high_threshold:
    deploy()
elif metric >= low_threshold:
    review()
else:
    retrain()
```
