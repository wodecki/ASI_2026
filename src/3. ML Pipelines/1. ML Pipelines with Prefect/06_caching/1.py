"""
Basic Task Caching

Demonstrates result caching to avoid re-computation:
- cache_key_fn: Function to generate cache key
- task_input_hash: Built-in hasher for task inputs

Question: How do I avoid re-running expensive computations?
"""

from prefect import flow, task
from prefect.cache_policies import INPUTS
import time


@task(cache_policy=INPUTS)
def expensive_computation(x: int, y: int) -> int:
    """
    Expensive computation that caches based on inputs.

    If called with same inputs, returns cached result.
    """
    print(f"Computing {x} + {y}... (expensive!)")
    time.sleep(2)  # Simulate expensive work
    result = x + y
    print(f"Result: {result}")
    return result


@task(cache_policy=INPUTS)
def feature_engineering(data: list) -> list:
    """
    Feature engineering that caches results.

    Useful for ML pipelines where feature computation is expensive.
    """
    print(f"Engineering features for {len(data)} items...")
    time.sleep(1)  # Simulate work
    features = [x ** 2 + x for x in data]
    print(f"Features: {features}")
    return features


@flow
def caching_demo() -> dict:
    """
    Demonstrates task caching.

    Second call with same inputs uses cached result.
    """
    print("=" * 50)
    print("CACHING DEMO - Basic Task Caching")
    print("=" * 50)
    print()

    # First call - computes and caches
    print("[1] First call (will compute)")
    print("-" * 40)
    result1 = expensive_computation(5, 3)
    print()

    # Second call with SAME inputs - uses cache
    print("[2] Second call, SAME inputs (should use cache)")
    print("-" * 40)
    result2 = expensive_computation(5, 3)
    print()

    # Third call with DIFFERENT inputs - computes new
    print("[3] Third call, DIFFERENT inputs (will compute)")
    print("-" * 40)
    result3 = expensive_computation(10, 20)
    print()

    # Feature engineering example
    print("[4] Feature engineering (first call)")
    print("-" * 40)
    features1 = feature_engineering([1, 2, 3])
    print()

    print("[5] Feature engineering (same data - cached)")
    print("-" * 40)
    features2 = feature_engineering([1, 2, 3])
    print()

    print("=" * 50)
    print("Flow complete!")
    print("=" * 50)

    return {
        "results": [result1, result2, result3],
        "features": features1
    }


if __name__ == "__main__":
    result = caching_demo()
    print(f"\nFinal result: {result}")
