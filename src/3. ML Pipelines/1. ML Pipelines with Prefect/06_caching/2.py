"""
Cache Expiration

Demonstrates time-based cache expiration:
- cache_expiration: How long cached results are valid

Question: How do I invalidate stale cached data?
"""

from prefect import flow, task
from prefect.cache_policies import INPUTS
from datetime import timedelta
import time


@task(
    cache_policy=INPUTS,
    cache_expiration=timedelta(seconds=5)
)
def fetch_market_data(symbol: str) -> dict:
    """
    Fetch market data with 5-second cache expiration.

    Real market data changes frequently, so cache expires quickly.
    """
    print(f"Fetching market data for {symbol}...")
    time.sleep(1)  # Simulate API call

    # Simulated data with timestamp
    data = {
        "symbol": symbol,
        "price": 100.0 + (time.time() % 10),  # Changes over time
        "timestamp": time.time()
    }
    print(f"Data: price=${data['price']:.2f}")
    return data


@task(
    cache_policy=INPUTS,
    cache_expiration=timedelta(hours=1)
)
def load_model_weights(model_name: str) -> dict:
    """
    Load model weights with 1-hour cache expiration.

    Model weights change infrequently, so longer cache is appropriate.
    """
    print(f"Loading weights for {model_name}...")
    time.sleep(2)  # Simulate loading

    weights = {
        "model": model_name,
        "version": "1.0",
        "params": 1000000
    }
    print(f"Loaded: {weights['params']} parameters")
    return weights


@flow
def expiration_demo() -> None:
    """
    Demonstrates cache expiration behavior.
    """
    print("=" * 50)
    print("CACHING DEMO - Cache Expiration")
    print("=" * 50)
    print()

    # Market data - short expiration
    print("[1] Fetch market data (5s expiration)")
    print("-" * 40)
    data1 = fetch_market_data("ACME")
    print()

    print("[2] Immediate re-fetch (should use cache)")
    print("-" * 40)
    data2 = fetch_market_data("ACME")
    print()

    print("[3] Waiting 6 seconds for cache to expire...")
    time.sleep(6)
    print()

    print("[4] Re-fetch after expiration (should compute)")
    print("-" * 40)
    data3 = fetch_market_data("ACME")
    print()

    # Model weights - long expiration
    print("[5] Load model weights (1h expiration)")
    print("-" * 40)
    weights1 = load_model_weights("classifier_v1")
    print()

    print("[6] Re-load (should use cache - valid for 1h)")
    print("-" * 40)
    weights2 = load_model_weights("classifier_v1")
    print()

    print("=" * 50)
    print("Flow complete!")
    print("=" * 50)


if __name__ == "__main__":
    expiration_demo()
