"""
File-Based Artifacts (Data Layers)

Demonstrates the data engineering convention (inspired by Kedro):
- 01_input/       -> Raw source data (immutable)
- 02_intermediate/ -> Transformed data (checkpoints)
- 03_output/      -> Final results

Question: How do I manage data between pipeline steps?
"""

import os
import pandas as pd
from prefect import flow, task

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")


# --- EXTRACT ---

@task
def extract_products() -> pd.DataFrame:
    """Extract products from raw input layer"""
    path = os.path.join(DATA_DIR, "01_input", "products.csv")
    df = pd.read_csv(path)
    print(f"[EXTRACT] Products from {path}:")
    print(df)
    print()
    return df


@task
def extract_sales() -> pd.DataFrame:
    """Extract sales from raw input layer"""
    path = os.path.join(DATA_DIR, "01_input", "sales.csv")
    df = pd.read_csv(path)
    print(f"[EXTRACT] Sales from {path}:")
    print(df)
    print()
    return df


# --- TRANSFORM ---

@task
def transform(products: pd.DataFrame, sales: pd.DataFrame) -> pd.DataFrame:
    """
    Transform: merge and compute derived columns.
    Saves intermediate result for debugging/checkpointing.
    """
    # Merge on id
    merged = pd.merge(products, sales, on="id")
    print("[TRANSFORM] Merged dataframes:")
    print(merged)
    print()

    # Compute total revenue
    merged["total"] = merged["price"] * merged["quantity"]
    print("[TRANSFORM] Added 'total' column:")
    print(merged)
    print()

    # Save intermediate artifact (checkpoint) as parquet for efficiency
    intermediate_path = os.path.join(DATA_DIR, "02_intermediate", "merged.parquet")
    merged.to_parquet(intermediate_path, index=False)
    print(f"[TRANSFORM] Saved checkpoint: {intermediate_path}")
    print()

    return merged


# --- LOAD ---

@task
def load(df: pd.DataFrame) -> str:
    """Load final output to 03_output layer"""
    summary = df[["id", "category", "region", "total"]]

    output_path = os.path.join(DATA_DIR, "03_output", "summary.csv")
    summary.to_csv(output_path, index=False)

    print("[LOAD] Final output:")
    print(summary)
    print()
    print(f"[LOAD] Saved to: {output_path}")

    return output_path


# --- FLOW ---

@flow
def etl_pipeline() -> str:
    """
    ETL Pipeline demonstrating data layers:
    01_input -> 02_intermediate -> 03_output
    """
    print("=" * 50)
    print("ETL PIPELINE - File-Based Artifacts Demo")
    print("=" * 50)
    print()

    # Extract
    products = extract_products()
    sales = extract_sales()

    # Transform (saves intermediate)
    transformed = transform(products, sales)

    # Load (saves final output)
    output_path = load(transformed)

    print()
    print("=" * 50)
    print("Pipeline complete!")
    print("=" * 50)

    return output_path


if __name__ == "__main__":
    result = etl_pipeline()
    print(f"\nFinal artifact: {result}")
