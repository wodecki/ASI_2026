"""
Parallel Execution with .map()

Demonstrates how to process multiple items in parallel:
- task.map(items): Apply a task to each item in a list

Question: How do I run tasks in parallel?
"""

import os
import pandas as pd
from prefect import flow, task

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")


@task
def load_products() -> pd.DataFrame:
    """Load products from CSV"""
    path = os.path.join(DATA_DIR, "01_input", "products.csv")
    return pd.read_csv(path)


@task
def process_product(row: dict) -> dict:
    """
    Process a single product row.

    This task will be mapped across all products.
    Each invocation runs potentially in parallel.
    """
    product_id = row["id"]
    price = row["price"]
    category = row["category"]

    # Simulate some processing
    adjusted_price = price * 1.1 if category == "A" else price * 1.2

    result = {
        "id": product_id,
        "original_price": price,
        "adjusted_price": round(adjusted_price, 2),
        "category": category
    }

    print(f"[TASK] Processed product {product_id}: ${price} -> ${adjusted_price:.2f}")
    return result


@flow
def parallel_pipeline() -> list[dict]:
    """
    Flow: Process products in parallel using .map()

    The .map() method:
    - Takes an iterable of inputs
    - Creates one task run per item
    - Returns a list of results (preserves order)
    """
    print("=" * 50)
    print("PARALLEL PIPELINE - .map() Demo")
    print("=" * 50)
    print()

    # Load data
    products = load_products()

    # Convert to list of dicts for mapping
    product_rows = products.to_dict(orient="records")
    print(f"[FLOW] Processing {len(product_rows)} products in parallel...")
    print()

    # Map task across all products (parallel execution)
    # .map() returns PrefectConcurrentFuture objects, call .result() to get values
    futures = process_product.map(product_rows)
    results = [f.result() for f in futures]

    print()
    print("[FLOW] All results:")
    for r in results:
        print(f"  - Product {r['id']}: ${r['adjusted_price']}")

    print()
    print("=" * 50)
    print("Pipeline complete!")
    print("=" * 50)

    return results


if __name__ == "__main__":
    parallel_pipeline()
