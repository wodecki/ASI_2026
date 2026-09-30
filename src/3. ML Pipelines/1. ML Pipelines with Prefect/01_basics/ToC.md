# 01_basics - Table of Contents

## Scripts

### 0.py - Plain Python (No Prefect)
- Baseline pipeline without Prefect
- Same logic as 1.py but no decorators
- Shows what you miss: no tracking, no retries, no caching, no UI

### 1.py - Basic Tasks and Flows
- `@task` decorator
- `@flow` decorator
- Sequential task execution
- Task return values

### 2.py - Parallel Execution with .map()
- `task.map(items)` for parallel processing
- Converting DataFrame to list of dicts
- Collecting mapped results

## Key Patterns

```python
# Basic task
@task
def my_task(x):
    return x * 2

# Basic flow
@flow
def my_flow():
    result = my_task(5)
    return result

# Parallel mapping
@flow
def parallel_flow():
    items = [1, 2, 3]
    results = my_task.map(items)  # [2, 4, 6]
```
