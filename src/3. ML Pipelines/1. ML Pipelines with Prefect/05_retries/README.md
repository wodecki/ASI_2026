# 05_retries - Failure Handling

## Question
**How do I handle failures in pipelines?**

## Core Concepts

### Basic Retries
```python
@task(retries=3)
def flaky_task():
    # Will retry up to 3 times on failure
    call_unreliable_api()
```

### Retry with Fixed Delay
```python
@task(retries=3, retry_delay_seconds=5)
def rate_limited_task():
    # Wait 5 seconds between retries
    call_api()
```

### Exponential Backoff
```python
@task(retries=3, retry_delay_seconds=[1, 10, 60])
def backoff_task():
    # Retry delays: 1s, 10s, 60s
    call_throttled_api()
```

### Fallback Pattern
```python
@flow
def with_fallback():
    try:
        return primary_task()
    except Exception:
        return fallback_task()
```

## Scripts

| Script | Concept | Description |
|--------|---------|-------------|
| `1.py` | Basic retries | `@task(retries=3)` |
| `2.py` | Exponential backoff | `retry_delay_seconds=[1, 10, 60]` |
| `3.py` | Fallback patterns | Try/except with alternatives |

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
uv run 1.py   # Basic retries
uv run 2.py   # Exponential backoff
uv run 3.py   # Fallback patterns
```

## ML Use Cases

- **API rate limits**: Backoff for external model APIs
- **Database connections**: Retry on transient failures
- **Training failures**: Retry on OOM with smaller batch
- **Data fetching**: Fallback to cached features
