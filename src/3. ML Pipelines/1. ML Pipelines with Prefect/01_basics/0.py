"""
Plain Python Pipeline (No Prefect)

This script performs the same operations as 1.py but WITHOUT Prefect.
Compare this to 1.py to see what Prefect adds:

What you DON'T get without Prefect:
- No automatic execution tracking (start time, duration, status)
- No visibility in a UI dashboard
- No automatic retry capability
- No caching of results
- No logging of function calls
- No dependency graph visualization

Purpose: Baseline to understand Prefect's value proposition.
"""

import os
import pandas as pd

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")


def load_products() -> pd.DataFrame:
    """Load products from CSV"""
    path = os.path.join(DATA_DIR, "01_input", "products.csv")
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} products")
    return df


def load_sales() -> pd.DataFrame:
    """Load sales from CSV"""
    path = os.path.join(DATA_DIR, "01_input", "sales.csv")
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} sales")
    return df


def compute_revenue(products: pd.DataFrame, sales: pd.DataFrame) -> pd.DataFrame:
    """Merge data and compute total revenue"""
    merged = pd.merge(products, sales, on="id")
    merged["total"] = merged["price"] * merged["quantity"]
    print(f"Computed revenue for {len(merged)} rows")
    return merged


def basic_pipeline() -> pd.DataFrame:
    """
    Plain Python pipeline - no orchestration.

    This works fine for simple scripts, but as pipelines grow:
    - How do you know if a step failed last night?
    - How long did each step take?
    - Can you retry just the failed step?
    - Can you see the execution history?

    Prefect answers all these questions.
    """
    print("=" * 50)
    print("BASIC PIPELINE - Plain Python (No Prefect)")
    print("=" * 50)
    print()

    # Call functions (no tracking, no retries, no caching)
    products = load_products()
    sales = load_sales()
    result = compute_revenue(products, sales)

    print()
    print("Result:")
    print(result)
    print()
    print("=" * 50)
    print("Pipeline complete!")
    print("=" * 50)

    return result


if __name__ == "__main__":
    basic_pipeline()
