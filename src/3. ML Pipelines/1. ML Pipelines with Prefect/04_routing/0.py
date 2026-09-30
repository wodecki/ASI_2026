"""
Plain Python Conditional Routing (No Prefect)

This script demonstrates conditional routing WITHOUT Prefect.
Compare to 1.py to see what Prefect adds:

What you DON'T get without Prefect:
- No visibility into which branch was taken
- No tracking of routing decisions over time
- No UI to analyze routing patterns
- No execution history for different paths
- Manual logging of decisions

Purpose: Baseline to understand Prefect's value for conditional routing.
"""


def check_data_quality(data: list) -> dict:
    """Analyze data quality"""
    missing = sum(1 for x in data if x is None)
    total = len(data)
    score = (total - missing) / total if total > 0 else 0

    return {
        "score": score,
        "missing": missing,
        "is_valid": score >= 0.8  # 80% threshold
    }


def process_valid_data(data: list) -> str:
    """Process valid data"""
    print(f"[VALID] Processing {len(data)} clean records")
    return f"Processed {len(data)} records"


def process_invalid_data(data: list) -> str:
    """Handle invalid data"""
    cleaned = [x for x in data if x is not None]
    print(f"[INVALID] Cleaned {len(data) - len(cleaned)} bad records")
    return f"Cleaned to {len(cleaned)} records"


def routing_pipeline(data: list) -> str:
    """
    Plain Python routing - no orchestration.

    This works, but consider:
    - How do you track which branch was taken?
    - How do you analyze routing patterns over time?
    - How do you debug why a specific path was chosen?

    Prefect tracks all routing decisions in the UI.
    """
    print("=" * 50)
    print("ROUTING PIPELINE - Plain Python (No Prefect)")
    print("=" * 50)
    print()

    # Check quality
    quality = check_data_quality(data)
    print(f"Quality score: {quality['score']:.0%}")
    print(f"Missing values: {quality['missing']}")
    print()

    # Route based on quality
    if quality["is_valid"]:
        print("-> Routing to: VALID data pipeline")
        result = process_valid_data(data)
    else:
        print("-> Routing to: INVALID data pipeline")
        result = process_invalid_data(data)

    print()
    print("=" * 50)
    print("Routing complete!")
    print("=" * 50)

    return result


if __name__ == "__main__":
    print("\n--- Test 1: Good data (90% valid) ---\n")
    good_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, None]
    result = routing_pipeline(good_data)
    print(f"Result: {result}")

    print("\n--- Test 2: Bad data (40% valid) ---\n")
    bad_data = [1, None, None, None, 5, None, 7, None, None, 10]
    result = routing_pipeline(bad_data)
    print(f"Result: {result}")
