"""
Basic Tasks and Flows

Demonstrates the fundamental Prefect building blocks:
- @task: A single unit of work
- @flow: An orchestrator that calls tasks

Question: What are tasks and flows?
"""

import os
import pandas as pd
from prefect import flow, task

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")


@task
def load_products() -> pd.DataFrame:
    """Task: Load products from CSV"""
    path = os.path.join(DATA_DIR, "01_input", "products.csv")
    df = pd.read_csv(path)
    print(f"[TASK] Loaded {len(df)} products")
    return df


@task
def load_sales() -> pd.DataFrame:
    """Task: Load sales from CSV"""
    path = os.path.join(DATA_DIR, "01_input", "sales.csv")
    df = pd.read_csv(path)
    print(f"[TASK] Loaded {len(df)} sales")
    return df


@task
def compute_revenue(products: pd.DataFrame, sales: pd.DataFrame) -> pd.DataFrame:
    """Task: Merge data and compute total revenue"""
    merged = pd.merge(products, sales, on="id")
    merged["total"] = merged["price"] * merged["quantity"]
    print(f"[TASK] Computed revenue for {len(merged)} rows")
    return merged


@flow
def basic_pipeline() -> pd.DataFrame:
    """
    Flow: Orchestrates tasks in sequence

    Tasks are called just like regular Python functions,
    but Prefect tracks their execution and dependencies.
    """
    print("=" * 50)
    print("BASIC PIPELINE - Tasks & Flows Demo")
    print("=" * 50)
    print()

    # Call tasks (Prefect tracks these)
    products = load_products()
    sales = load_sales()
    result = compute_revenue(products, sales)

    print()
    print("[FLOW] Result:")
    print(result)
    print()
    print("=" * 50)
    print("Pipeline complete!")
    print("=" * 50)

    return result


if __name__ == "__main__":
    basic_pipeline()
