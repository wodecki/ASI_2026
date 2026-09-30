"""
Fallback Patterns

Demonstrates fallback strategies when retries are exhausted:
- Try/except around task calls
- Fallback to alternative flow/data source
- Graceful degradation

Question: What happens when retries are exhausted?
"""

from prefect import flow, task
import random


@task(retries=2, retry_delay_seconds=1)
def primary_api(endpoint: str) -> dict:
    """Primary API - fast but unreliable"""
    print(f"[PRIMARY] Calling {endpoint}...")

    if random.random() < 0.8:  # 80% failure rate
        print(f"[PRIMARY] Failed!")
        raise ConnectionError("Primary API unavailable")

    return {"source": "primary", "data": [1, 2, 3]}


@task(retries=1)
def backup_api(endpoint: str) -> dict:
    """Backup API - slower but more reliable"""
    print(f"[BACKUP] Calling {endpoint}...")

    if random.random() < 0.2:  # 20% failure rate
        print(f"[BACKUP] Failed!")
        raise ConnectionError("Backup API unavailable")

    return {"source": "backup", "data": [1, 2, 3]}


@task
def use_cached_data() -> dict:
    """Last resort: use cached/default data"""
    print("[CACHE] Using cached fallback data")
    return {"source": "cache", "data": [0, 0, 0]}


@flow
def fetch_with_fallback(endpoint: str) -> dict:
    """
    Fetch data with cascading fallback:
    1. Try primary API (with retries)
    2. Fall back to backup API (with retries)
    3. Fall back to cached data
    """
    # Try primary
    try:
        return primary_api(endpoint)
    except Exception as e:
        print(f"Primary exhausted: {e}")

    # Try backup
    try:
        return backup_api(endpoint)
    except Exception as e:
        print(f"Backup exhausted: {e}")

    # Last resort: cached data
    return use_cached_data()


@flow
def fallback_demo() -> dict:
    """
    Demonstrates fallback pattern for resilient data fetching.
    """
    print("=" * 50)
    print("RETRY DEMO - Fallback Patterns")
    print("=" * 50)
    print()

    random.seed(42)

    result = fetch_with_fallback("https://api.example.com/data")

    print()
    print(f"Data source used: {result['source']}")
    print()
    print("=" * 50)
    print("Flow complete!")
    print("=" * 50)

    return result


if __name__ == "__main__":
    # Run multiple times to see different outcomes
    for i in range(3):
        print(f"\n{'#'*60}")
        print(f"# RUN {i+1}")
        print(f"{'#'*60}\n")
        random.seed(i * 10)  # Different seed each run
        result = fallback_demo()
        print(f"\nResult: {result}")
