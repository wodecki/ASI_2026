# 06_caching - Efficiency

## Question
**How do I avoid re-running expensive computations?**

## Core Concepts

### Basic Caching
```python
from prefect.cache_policies import INPUTS

@task(cache_policy=INPUTS)
def expensive_task(x, y):
    # Cached by input values
    return compute(x, y)
```

### Cache Expiration
```python
from datetime import timedelta

@task(
    cache_policy=INPUTS,
    cache_expiration=timedelta(hours=1)
)
def fetch_data():
    # Cache valid for 1 hour
    return get_from_api()
```

### Force Refresh
```python
@flow
def pipeline(force_refresh=False):
    if force_refresh:
        result = my_task.with_options(refresh_cache=True)(data)
    else:
        result = my_task(data)
```

## Scripts

| Script | Concept | Description |
|--------|---------|-------------|
| `1.py` | Basic caching | `cache_policy=INPUTS` |
| `2.py` | Cache expiration | `cache_expiration=timedelta(...)` |
| `3.py` | Force refresh | `refresh_cache=True` |

## Running

### Start Prefect Server (if not running)

```bash
# Terminal 1: Start server
uv run prefect server start

# Terminal 2: Configure API URL
uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

View runs at http://127.0.0.1:4200

### Run Scripts

```bash
uv run 1.py   # Basic caching
uv run 2.py   # Cache expiration
uv run 3.py   # Force refresh pattern
```

## ML Use Cases

- **Feature engineering**: Cache computed features
- **Model training**: Cache trained models by config
- **Data loading**: Cache loaded datasets
- **API calls**: Cache external API responses
