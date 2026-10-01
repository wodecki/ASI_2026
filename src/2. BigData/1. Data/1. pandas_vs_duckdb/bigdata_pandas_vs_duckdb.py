"""
Big Data Analysis: pandas vs DuckDB Performance Comparison

This script demonstrates the performance differences between pandas and DuckDB
when processing large-scale temperature datasets (100M and 1B records).

SETUP INSTRUCTIONS:
    # Install uv (if not already installed)
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Install dependencies
    uv sync

    # Run the script
    uv run python bigdata_pandas_vs_duckdb.py

Educational Focus:
- Processing 100M+ records efficiently
- DuckDB parallel processing vs pandas
- Resource monitoring (memory, disk)
- Data aggregation patterns

Dataset Details:
- Source: synthetic, generated locally by generate_data.py (station list in stations.csv)
- Format: Semicolon-delimited (station_name;measurement), no header
- Size: 100M records (~1.3 GB), 1B records (~13 GB)
"""

import pandas as pd
import duckdb
import time
from pathlib import Path

from generate_data import generate


# =============================================================================
# SECTION 1: Data Generation
# =============================================================================

def generate_temperature_data():
    """Generate the synthetic temperature datasets locally (only if not already present).

    The files are produced by generate_data.py with DuckDB - see that script for details.
    """

    datasets = [
        (Path("medium_dataset.csv"), 100_000_000),   # 100M records: ~1.3 GB
        (Path("large_dataset.csv"), 1_000_000_000),  # 1B records: ~13 GB
    ]

    for path, rows in datasets:
        if path.exists():
            print(f"✓ {path.name} already exists, skipping generation")
        else:
            generate(rows, path)


# =============================================================================
# SECTION 2: 100M Records Analysis with pandas
# =============================================================================

def analyze_100m_with_pandas():
    """
    Process 100 million temperature records using pandas

    Demonstrates:
    - CSV reading with custom separators and column names
    - GroupBy aggregation (min/mean/max)
    - Performance timing
    - Memory consumption patterns
    """

    # Preview: Load first 10 records to understand data structure
    sample = pd.read_csv(
        "medium_dataset.csv",
        sep=";",
        header=None,
        names=["station_name", "measurement"],
        nrows=10
    )
    print("Sample data:")
    print(sample.head())
    print()

    # Full processing with timing
    # TIP: Monitor resource usage in your environment's resource monitor
    print("Processing 100M records with pandas...")
    start_time = time.time()

    # Load and aggregate in a single pipeline
    df = (
        pd.read_csv(
            "medium_dataset.csv",
            sep=";",
            header=None,
            names=["station_name", "measurement"]
        )
        .groupby("station_name")
        .agg(["min", "mean", "max"])
    )

    # Flatten multi-level column index
    df.columns = df.columns.get_level_values(level=1)
    df = df.reset_index()
    df.columns = ["station_name", "min_measurement", "mean_measurement", "max_measurement"]
    df = df.sort_values("station_name")

    end_time = time.time()

    # Format output: {station1=min/mean/max, station2=min/mean/max, ...}
    print("{", end="")
    for row in df.itertuples(index=False):
        print(
            f"{row.station_name}={row.min_measurement:.1f}/{row.mean_measurement:.1f}/{row.max_measurement:.1f}",
            end=", "
        )
    print("\b\b} ")
    print(f"Data processed in {end_time - start_time:.2f} seconds.")
    print()


# =============================================================================
# SECTION 3: 100M Records Analysis with DuckDB
# =============================================================================

def analyze_100m_with_duckdb():
    """
    Process 100 million temperature records using DuckDB

    Demonstrates:
    - SQL-based data processing
    - Parallel CSV reading
    - In-memory analytical database performance
    - Resource-efficient aggregation
    """

    print("Processing 100M records with DuckDB...")

    with duckdb.connect() as conn:
        start_time = time.time()

        # Execute SQL query with parallel CSV reading
        # Note: DuckDB processes CSV files in parallel automatically
        data = conn.sql("""
            SELECT
                station_name,
                MIN(measurement) AS min_measurement,
                CAST(AVG(measurement) AS DECIMAL(8, 1)) AS mean_measurement,
                MAX(measurement) AS max_measurement
            FROM read_csv(
                'medium_dataset.csv',
                header=false,
                columns={'station_name': 'varchar', 'measurement': 'decimal(8, 1)'},
                delim=';',
                parallel=true
            )
            GROUP BY station_name
            ORDER BY station_name
        """)

        results = data.fetchall()
        end_time = time.time()

        # Format output
        print("{", end="")
        for row in sorted(results):
            print(f"{row[0]}={row[1]}/{row[2]}/{row[3]}", end=", ")
        print("\b\b} ")
        print(f"Query executed in {end_time - start_time:.2f} seconds.")
    print()


# =============================================================================
# SECTION 4: 1B Records Analysis with pandas (NOT RECOMMENDED)
# =============================================================================

def analyze_1b_with_pandas():
    """
    Attempt to process 1 billion records using pandas

    WARNING: This will likely cause memory issues on most systems.
    This function demonstrates pandas limitations with very large datasets.

    Educational Note:
    - pandas loads entire dataset into memory
    - 1B records can exceed available RAM
    - Use PyArrow engine for better performance, but still limited
    """

    print("WARNING: Processing 1B records with pandas (not recommended)...")
    print("This may cause memory issues. Consider skipping this step.")

    # Uncomment to run (at your own risk):
    start_time = time.time()
    
    df = (
        pd.read_csv(
            "large_dataset.csv",
            sep=";",
            header=None,
            names=["station_name", "measurement"],
            engine="pyarrow"
        )
        .groupby("station_name")
        .agg(["min", "mean", "max"])
    )
    
    df.columns = df.columns.get_level_values(level=1)
    df = df.reset_index()
    df.columns = ["station_name", "min_measurement", "mean_measurement", "max_measurement"]
    df = df.sort_values("station_name")
    
    end_time = time.time()
    
    print("{", end="")
    for row in df.itertuples(index=False):
        print(
            f"{row.station_name}={row.min_measurement:.1f}/{row.mean_measurement:.1f}/{row.max_measurement:.1f}",
            end=", "
        )
    print("\b\b} ")
    print(f"Data processed in {end_time - start_time:.2f} seconds.")


# =============================================================================
# SECTION 5: 1B Records Analysis with DuckDB (RECOMMENDED)
# =============================================================================

def analyze_1b_with_duckdb():
    """
    Process 1 billion temperature records using DuckDB

    Demonstrates:
    - Efficient handling of datasets larger than RAM
    - DuckDB's columnar storage advantages
    - Parallel processing at scale
    - Production-ready big data processing
    """

    print("Processing 1B records with DuckDB...")

    with duckdb.connect() as conn:
        start_time = time.time()

        data = conn.sql("""
            SELECT
                station_name,
                MIN(measurement) AS min_measurement,
                CAST(AVG(measurement) AS DECIMAL(8, 1)) AS mean_measurement,
                MAX(measurement) AS max_measurement
            FROM read_csv(
                'large_dataset.csv',
                header=false,
                columns={'station_name': 'varchar', 'measurement': 'decimal(8, 1)'},
                delim=';',
                parallel=true
            )
            GROUP BY station_name
            ORDER BY station_name
        """)

        results = data.fetchall()
        end_time = time.time()

        print("{", end="")
        for row in sorted(results):
            print(f"{row[0]}={row[1]}/{row[2]}/{row[3]}", end=", ")
        print("\b\b} ")
        print(f"Query executed in {end_time - start_time:.2f} seconds.")
    print()


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

# Uncomment sections as needed:

# Step 1: Generate data (run once)
generate_temperature_data()

# Step 2: Analyze 100M records
analyze_100m_with_pandas()
analyze_100m_with_duckdb()

# Step 3: Analyze 1B records (DuckDB only recommended)
analyze_1b_with_pandas()  # WARNING: Not recommended
analyze_1b_with_duckdb()

# Compare the performance results and resource consumption between pandas and DuckDB!
