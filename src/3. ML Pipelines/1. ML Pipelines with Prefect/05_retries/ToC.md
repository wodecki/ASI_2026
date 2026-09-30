# 05_retries - Table of Contents

## Scripts

### 1.py - Basic Task Retries
- `@task(retries=3)` decorator
- Automatic retry on exception
- Total attempts = 1 initial + N retries

### 2.py - Exponential Backoff
- `retry_delay_seconds=2` - fixed delay
- `retry_delay_seconds=[1, 5, 30]` - exponential
- Ideal for rate limits and throttling

### 3.py - Fallback Patterns
- Try primary with retries
- Fall back to backup source
- Last resort: cached/default data

## Key Patterns

```python
# Basic retry
@task(retries=3)
def my_task(): ...

# Fixed delay
@task(retries=3, retry_delay_seconds=5)
def my_task(): ...

# Exponential backoff
@task(retries=3, retry_delay_seconds=[1, 10, 60])
def my_task(): ...

# Fallback flow
@flow
def with_fallback():
    try:
        return primary()
    except:
        return fallback()
```
