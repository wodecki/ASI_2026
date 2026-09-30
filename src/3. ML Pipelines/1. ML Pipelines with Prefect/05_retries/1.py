"""
Basic Task Retries

Demonstrates automatic retry on task failure:
- @task(retries=N): Retry N times on failure
- Prefect handles retry logic automatically

Question: How do I make tasks retry on failure?
"""

from prefect import flow, task
import random


@task(retries=3)
def flaky_api_call(endpoint: str) -> dict:
    """
    Simulates an unreliable API that fails randomly.

    With retries=3, Prefect will attempt up to 4 times total
    (1 initial + 3 retries).
    """
    print(f"Calling API: {endpoint}")

    # Simulate 60% failure rate
    if random.random() < 0.6:
        print("  -> API failed!")
        raise ConnectionError(f"Failed to connect to {endpoint}")

    print("  -> API succeeded!")
    return {"status": "ok", "endpoint": endpoint}


@task(retries=2)
def process_data(data: dict) -> str:
    """
    Process data with retry capability.

    Even internal processing can benefit from retries
    for transient errors.
    """
    print(f"Processing: {data}")

    # Simulate occasional processing failure
    if random.random() < 0.3:
        print("  -> Processing error!")
        raise RuntimeError("Transient processing error")

    print("  -> Processing succeeded!")
    return f"processed:{data['endpoint']}"


@flow
def retry_demo() -> str:
    """
    Flow demonstrating task retries.

    Each task will automatically retry on failure
    without any explicit try/except.
    """
    print("=" * 50)
    print("RETRY DEMO - Basic Task Retries")
    print("=" * 50)
    print()

    # Set random seed for reproducibility in demo
    random.seed(42)

    # Both tasks have automatic retries
    data = flaky_api_call("https://api.example.com/data")
    result = process_data(data)

    print()
    print("=" * 50)
    print("Flow complete!")
    print("=" * 50)

    return result


if __name__ == "__main__":
    result = retry_demo()
    print(f"\nFinal result: {result}")
