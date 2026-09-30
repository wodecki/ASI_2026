"""
ETL Pattern with Subflows

Demonstrates a clean ETL architecture using subflows:
- extract_flow: Load raw data
- transform_flow: Process and enrich
- load_flow: Save results

Question: How do I structure an ETL pipeline with subflows?
"""

import os
import pandas as pd
from prefect import flow, task

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")


# --- EXTRACT SUBFLOW ---

@task
def read_csv(filename: str) -> pd.DataFrame:
    """Task: Read a CSV file"""
    path = os.path.join(DATA_DIR, "01_input", filename)
    return pd.read_csv(path)


@flow
def extract_flow() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Subflow: Extract all source data"""
    print("[EXTRACT] Loading source data...")

    products = read_csv("products.csv")
    sales = read_csv("sales.csv")

    print(f"[EXTRACT] Loaded {len(products)} products, {len(sales)} sales")
    return products, sales


# --- TRANSFORM SUBFLOW ---

@task
def merge_data(products: pd.DataFrame, sales: pd.DataFrame) -> pd.DataFrame:
    """Task: Merge products and sales"""
    return pd.merge(products, sales, on="id")


@task
def add_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Task: Add revenue column"""
    df = df.copy()
    df["total"] = df["price"] * df["quantity"]
    return df


@flow
def transform_flow(products: pd.DataFrame, sales: pd.DataFrame) -> pd.DataFrame:
    """Subflow: Transform and enrich data"""
    print("[TRANSFORM] Processing data...")

    merged = merge_data(products, sales)
    enriched = add_revenue(merged)

    print(f"[TRANSFORM] Result: {len(enriched)} rows")
    print(enriched)
    return enriched


# --- LOAD SUBFLOW ---

@task
def save_output(df: pd.DataFrame, filename: str) -> str:
    """Task: Save DataFrame to output"""
    os.makedirs(os.path.join(DATA_DIR, "03_output"), exist_ok=True)
    path = os.path.join(DATA_DIR, "03_output", filename)
    df.to_csv(path, index=False)
    return path


@flow
def load_flow(df: pd.DataFrame) -> str:
    """Subflow: Load data to destination"""
    print("[LOAD] Saving output...")

    path = save_output(df, "etl_result.csv")
    print(f"[LOAD] Saved to: {path}")
    return path


# --- MAIN ETL FLOW ---

@flow
def etl_pipeline() -> str:
    """
    ETL Pipeline using subflows.

    Flow hierarchy:
    - etl_pipeline (orchestrator)
      - extract_flow
      - transform_flow
      - load_flow
    """
    print("=" * 50)
    print("ETL PIPELINE - Subflows Architecture")
    print("=" * 50)
    print()

    # E - Extract
    products, sales = extract_flow()
    print()

    # T - Transform
    result = transform_flow(products, sales)
    print()

    # L - Load
    output_path = load_flow(result)

    print()
    print("=" * 50)
    print("ETL complete!")
    print("=" * 50)

    return output_path


if __name__ == "__main__":
    etl_pipeline()
