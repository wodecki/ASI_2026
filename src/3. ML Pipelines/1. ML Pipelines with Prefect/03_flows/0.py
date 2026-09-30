"""
Plain Python Pipeline Composition (No Prefect)

This script demonstrates pipeline composition WITHOUT Prefect.
Compare to 1.py to see what Prefect adds:

What you DON'T get without Prefect:
- No visibility into parent/child flow relationships
- No tracking of which subflow ran when
- No execution history for individual components
- No UI to visualize flow hierarchy
- Manual orchestration of dependencies

Purpose: Baseline to understand Prefect's value for pipeline composition.
"""


def prepare_data() -> list[str]:
    """Prepare customer IDs"""
    print("[STEP] Preparing data...")
    customers = ["customer_1", "customer_2", "customer_3"]
    print(f"[STEP] Found {len(customers)} customers")
    return customers


def process_customer(customer_id: str) -> dict:
    """Process a single customer"""
    print(f"[STEP] Processing {customer_id}...")
    return {
        "customer": customer_id,
        "status": "processed"
    }


def master_pipeline() -> list[dict]:
    """
    Plain Python pipeline - no orchestration.

    This works, but consider:
    - How do you track which function ran when?
    - How do you visualize the execution hierarchy?
    - How do you monitor long-running pipelines?

    Prefect subflows solve these problems.
    """
    print("=" * 50)
    print("MASTER PIPELINE - Plain Python (No Prefect)")
    print("=" * 50)
    print()

    # Get data
    customer_ids = prepare_data()
    print()

    # Process each customer
    results = []
    for customer_id in customer_ids:
        result = process_customer(customer_id)
        results.append(result)

    print()
    print("[MASTER] All results:")
    for r in results:
        print(f"  - {r}")

    print()
    print("=" * 50)
    print("Master pipeline complete!")
    print("=" * 50)

    return results


if __name__ == "__main__":
    master_pipeline()
