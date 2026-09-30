"""
Basic Subflows

Demonstrates how flows can call other flows (subflows):
- A flow can call another flow just like a function
- Prefect tracks both parent and child flows
- Useful for modular, reusable pipeline components

Question: How do I compose flows from smaller flows?
"""

from prefect import flow


@flow
def prepare_data() -> list[str]:
    """Subflow: Prepare customer IDs"""
    print("[SUBFLOW] Preparing data...")
    customers = ["customer_1", "customer_2", "customer_3"]
    print(f"[SUBFLOW] Found {len(customers)} customers")
    return customers


@flow
def process_customer(customer_id: str) -> dict:
    """Subflow: Process a single customer"""
    print(f"[SUBFLOW] Processing {customer_id}...")
    return {
        "customer": customer_id,
        "status": "processed"
    }


@flow
def master_flow() -> list[dict]:
    """
    Master flow that calls subflows.

    Flow hierarchy:
    - master_flow (parent)
      - prepare_data (child)
      - process_customer (child, called multiple times)
    """
    print("=" * 50)
    print("MASTER FLOW - Subflows Demo")
    print("=" * 50)
    print()

    # Call subflow to get data
    customer_ids = prepare_data()
    print()

    # Call subflow for each customer
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
    print("Master flow complete!")
    print("=" * 50)

    return results


if __name__ == "__main__":
    master_flow()
