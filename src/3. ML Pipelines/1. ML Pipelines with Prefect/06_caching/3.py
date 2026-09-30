"""
Cache Refresh Pattern

Demonstrates how to force re-computation when needed:
- refresh_cache=True: Ignore cache and recompute
- Useful for retraining, data refresh, etc.

Question: How do I force re-computation when needed?
"""

from prefect import flow, task
from prefect.cache_policies import INPUTS
import time


@task(cache_policy=INPUTS)
def train_model(config: dict) -> dict:
    """
    Train a model (cached by config).

    In production, you might want to force retraining
    even with the same config.
    """
    print(f"Training model with config: {config}")
    time.sleep(2)  # Simulate training

    model = {
        "config": config,
        "accuracy": 0.95,
        "trained_at": time.time()
    }
    print(f"Model trained at {model['trained_at']:.0f}")
    return model


@task(cache_policy=INPUTS)
def compute_features(data: list) -> list:
    """Feature computation (cached)"""
    print(f"Computing features for {len(data)} items...")
    time.sleep(1)
    return [x * 2 for x in data]


@flow
def training_pipeline(
    config: dict,
    force_retrain: bool = False
) -> dict:
    """
    Training pipeline with optional cache refresh.

    Args:
        config: Model configuration
        force_retrain: If True, ignore cache and retrain
    """
    print(f"Force retrain: {force_retrain}")
    print()

    # Compute features (use cache if available)
    features = compute_features([1, 2, 3, 4, 5])
    print()

    # Train model (optionally force refresh)
    if force_retrain:
        # Call with refresh_cache=True to bypass cache
        model = train_model.with_options(refresh_cache=True)(config)
    else:
        model = train_model(config)

    return {"features": features, "model": model}


@flow
def refresh_demo() -> None:
    """
    Demonstrates cache refresh pattern.
    """
    print("=" * 50)
    print("CACHING DEMO - Cache Refresh Pattern")
    print("=" * 50)
    print()

    config = {"layers": 3, "units": 64}

    # First run - trains model
    print("[1] First training run")
    print("-" * 40)
    result1 = training_pipeline(config, force_retrain=False)
    print(f"Model trained at: {result1['model']['trained_at']:.0f}")
    print()

    # Second run - uses cached model
    print("[2] Second run (should use cached model)")
    print("-" * 40)
    result2 = training_pipeline(config, force_retrain=False)
    print(f"Model trained at: {result2['model']['trained_at']:.0f}")
    print()

    # Third run - force retrain
    print("[3] Third run with force_retrain=True")
    print("-" * 40)
    result3 = training_pipeline(config, force_retrain=True)
    print(f"Model trained at: {result3['model']['trained_at']:.0f}")
    print()

    # Verify timestamps
    print("=" * 50)
    print("Summary:")
    print(f"  Run 1 timestamp: {result1['model']['trained_at']:.0f}")
    print(f"  Run 2 timestamp: {result2['model']['trained_at']:.0f} (same = cached)")
    print(f"  Run 3 timestamp: {result3['model']['trained_at']:.0f} (different = retrained)")
    print("=" * 50)


if __name__ == "__main__":
    refresh_demo()
