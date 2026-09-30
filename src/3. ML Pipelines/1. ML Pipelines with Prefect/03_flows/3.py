"""
Partial Pipeline Execution

Demonstrates how to run only specific steps of a pipeline:
- Call individual subflows directly
- Run from step X to step Y
- Useful for testing, debugging, and checkpoint recovery

Question: How do I run only part of my pipeline?
"""

from prefect import flow
from typing import Optional


# --- Pipeline Steps (each is a subflow) ---

@flow
def step_1_ingest() -> dict:
    """Step 1: Data ingestion"""
    print("Step 1: Data ingestion")
    return {"raw": [1, 2, 3, 4, 5]}


@flow
def step_2_validate(data: dict) -> dict:
    """Step 2: Validation"""
    print("Step 2: Validation")
    data["validated"] = True
    return data


@flow
def step_3_transform(data: dict) -> dict:
    """Step 3: Transform"""
    print("Step 3: Transform")
    data["transformed"] = [x * 2 for x in data["raw"]]
    return data


@flow
def step_4_enrich(data: dict) -> dict:
    """Step 4: Enrich"""
    print("Step 4: Enrich")
    data["enriched"] = [x + 10 for x in data["transformed"]]
    return data


@flow
def step_5_export(data: dict) -> dict:
    """Step 5: Export"""
    print("Step 5: Export")
    data["exported"] = True
    return data


# --- Full Pipeline ---

@flow
def full_pipeline() -> dict:
    """Run all steps 1 through 5"""
    data = step_1_ingest()
    data = step_2_validate(data)
    data = step_3_transform(data)
    data = step_4_enrich(data)
    data = step_5_export(data)
    return data


# --- Partial Pipeline ---

@flow
def partial_pipeline(
    start: int = 1,
    end: int = 5,
    initial_data: Optional[dict] = None
) -> dict:
    """
    Run pipeline from step `start` to step `end` (inclusive).

    Args:
        start: First step to run (1-5)
        end: Last step to run (1-5)
        initial_data: Input data (required if start > 1)

    Examples:
        partial_pipeline(start=2, end=4, initial_data={"raw": [1,2,3]})
    """
    steps = {
        1: step_1_ingest,
        2: step_2_validate,
        3: step_3_transform,
        4: step_4_enrich,
        5: step_5_export,
    }

    # Validation
    if start < 1 or end > 5 or start > end:
        raise ValueError(f"Invalid range: {start} to {end}")
    if start > 1 and initial_data is None:
        raise ValueError(f"initial_data required when starting from step {start}")

    # Execute steps
    data = initial_data
    for step_num in range(start, end + 1):
        step_fn = steps[step_num]
        if step_num == 1:
            data = step_fn()
        else:
            data = step_fn(data)

    return data


if __name__ == "__main__":
    print("=" * 50)
    print("Example 1: Run single subflow directly")
    print("=" * 50)
    result = step_3_transform({"raw": [10, 20]})
    print(f"Result: {result}\n")

    print("=" * 50)
    print("Example 2: Run steps 2-4 only")
    print("=" * 50)
    checkpoint = {"raw": [100, 200, 300]}  # Simulated checkpoint
    result = partial_pipeline(start=2, end=4, initial_data=checkpoint)
    print(f"Result: {result}\n")

    print("=" * 50)
    print("Example 3: Run full pipeline")
    print("=" * 50)
    result = full_pipeline()
    print(f"Result: {result}")
