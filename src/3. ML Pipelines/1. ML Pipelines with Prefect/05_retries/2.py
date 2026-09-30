"""
Exponential Backoff

Demonstrates retry delays for rate limiting and backpressure:
- retry_delay_seconds: Fixed delay between retries
- retry_delay_seconds=[1, 10, 60]: Exponential backoff pattern

Question: How do I handle rate limits and backpressure?
"""

from prefect import flow, task
import random


@task(retries=3, retry_delay_seconds=2)
def fixed_delay_task(item: str) -> str:
    """
    Task with fixed retry delay.

    Waits 2 seconds between each retry attempt.
    """
    print(f"Processing {item}...")

    if random.random() < 0.5:
        print(f"  -> Failed! (will retry in 2s)")
        raise RuntimeError(f"Failed to process {item}")

    print(f"  -> Success!")
    return f"done:{item}"


@task(retries=3, retry_delay_seconds=[1, 5, 30])
def exponential_backoff_task(endpoint: str) -> dict:
    """
    Task with exponential backoff.

    Retry delays:
    - 1st retry: wait 1 second
    - 2nd retry: wait 5 seconds
    - 3rd retry: wait 30 seconds

    This pattern is ideal for:
    - API rate limits (429 responses)
    - Database connection limits
    - External service throttling
    """
    print(f"Calling {endpoint}...")

    # Simulate rate limiting (high failure initially, decreases over time)
    if random.random() < 0.7:
        print(f"  -> Rate limited! (backing off)")
        raise ConnectionError(f"Rate limited by {endpoint}")

    print(f"  -> Success!")
    return {"endpoint": endpoint, "status": "ok"}


@flow
def backoff_demo() -> dict:
    """
    Demonstrates different retry delay strategies.
    """
    print("=" * 50)
    print("RETRY DEMO - Exponential Backoff")
    print("=" * 50)
    print()

    random.seed(123)

    print("[1] Fixed delay (2s between retries)")
    print("-" * 40)
    result1 = fixed_delay_task("item_a")
    print()

    print("[2] Exponential backoff (1s, 5s, 30s)")
    print("-" * 40)
    result2 = exponential_backoff_task("https://api.example.com")
    print()

    print("=" * 50)
    print("Flow complete!")
    print("=" * 50)

    return {"fixed": result1, "exponential": result2}


if __name__ == "__main__":
    result = backoff_demo()
    print(f"\nFinal result: {result}")
