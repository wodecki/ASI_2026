# 03_flows - Table of Contents

## Scripts

### 0.py - Plain Python Pipeline Composition (No Prefect)
- Baseline pipeline composition without Prefect
- Same logic as 1.py but no decorators
- Shows what you miss: no flow hierarchy visibility, no tracking

### 1.py - Basic Subflows
- Flow calling flow
- Parent/child flow hierarchy
- Subflow return values

### 2.py - ETL Pattern with Subflows
- `extract_flow()` - Load source data
- `transform_flow()` - Process and enrich
- `load_flow()` - Save results
- Combining tasks within subflows

### 3.py - Partial Pipeline Execution
- `full_pipeline()` - Run all steps
- `partial_pipeline(start, end, data)` - Run subset
- Checkpoint/resume pattern

## Key Patterns

```python
# Subflow
@flow
def child():
    return "data"

@flow
def parent():
    result = child()  # Subflow call

# Partial execution
@flow
def partial(start, end, data):
    steps = {1: fn1, 2: fn2, 3: fn3}
    for i in range(start, end + 1):
        data = steps[i](data)
    return data
```
