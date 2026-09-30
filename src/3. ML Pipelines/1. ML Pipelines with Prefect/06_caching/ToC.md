# 06_caching - Table of Contents

## Scripts

### 1.py - Basic Task Caching
- `cache_policy=INPUTS` for input-based caching
- Cache hit vs miss demonstration
- Feature engineering example

### 2.py - Cache Expiration
- `cache_expiration=timedelta(seconds=5)` - short expiration
- `cache_expiration=timedelta(hours=1)` - long expiration
- Different expiration for different data types

### 3.py - Force Cache Refresh
- `task.with_options(refresh_cache=True)()`
- Pattern for forced retraining
- Combining cached and refreshed tasks

## Key Patterns

```python
from prefect.cache_policies import INPUTS
from datetime import timedelta

# Basic caching
@task(cache_policy=INPUTS)
def my_task(x): ...

# With expiration
@task(
    cache_policy=INPUTS,
    cache_expiration=timedelta(hours=1)
)
def my_task(x): ...

# Force refresh
result = my_task.with_options(refresh_cache=True)(data)
```
