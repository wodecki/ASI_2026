# BigData Analysis: pandas vs DuckDB Performance Comparison

## Overview

This module demonstrates the performance differences between **pandas** and **DuckDB** when processing large-scale datasets (100 million to 1 billion records). Students will learn:

- How different libraries handle big data processing
- Resource consumption patterns (memory, disk, CPU)
- When to use pandas vs DuckDB
- Practical big data processing techniques

## Learning Objectives

1. **Understand scalability limits** of traditional data processing libraries (pandas)
2. **Experience modern big data tools** (DuckDB) designed for analytical workloads
3. **Monitor resource consumption** during data processing operations
4. **Apply SQL-based data processing** as an alternative to DataFrame operations
5. **Make informed technology choices** based on dataset size and constraints

## Dataset Specifications

### Temperature Data Files

| File | Records | Size |
|------|---------|------|
| `medium_dataset.csv` | 100 million | ~1.3 GB |
| `large_dataset.csv` | 1 billion | ~13 GB |

**Format:** Semicolon-delimited CSV, no header (`station_name;measurement`)
```
London;23.1
Tokyo;15.6
Wrocław;-2.6
```

**Data Source:** synthetic, generated locally by `generate_data.py` (the files are too large to keep in git).
Each measurement is drawn from a normal distribution (sd = 10 °C) around the station's mean temperature
listed in `stations.csv` (49 stations), in the style of the *One Billion Row Challenge*.
The same row count always produces the same data, so everyone gets identical results.

```bash
uv run python generate_data.py --rows 100000000 --output medium_dataset.csv
uv run python generate_data.py --rows 1000000000 --output large_dataset.csv
```

`bigdata_pandas_vs_duckdb.py` runs these automatically for any file that is missing.

## Files in This Module

```
1. pandas_vs_duckdb/
├── bigdata_pandas_vs_duckdb.py    # Main Python script for analysis
├── generate_data.py               # Generates the synthetic datasets with DuckDB
├── stations.csv                   # Station names and mean temperatures used by the generator
├── pyproject.toml                 # uv dependency configuration
├── uv.lock                        # Locked dependency versions
├── medium_dataset.csv             # 100M records dataset (~1.3 GB)
├── large_dataset.csv              # 1B records dataset (~13 GB)
└── README.md                      # This file
```

## Requirements

### Installing uv Package Manager

**REQUIRED: This project uses `uv` for package management.**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip (one-time)
pip install uv
```

### Python Dependencies

```bash
# Install all dependencies from pyproject.toml
uv sync

# Or install specific packages
uv add pandas duckdb pyarrow

```

### System Requirements

- **For 100M records:**
  - RAM: 8 GB minimum, 16 GB recommended
  - Disk: 5 GB free space
  - CPU: Multi-core recommended

- **For 1B records:**
  - RAM: 32 GB minimum (64 GB for pandas)
  - Disk: 30 GB free space
  - CPU: 4+ cores recommended

## Usage Instructions

### Running the Analysis Script

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Open `bigdata_pandas_vs_duckdb.py` and uncomment desired sections at the bottom:

   ```python
   # Step 1: Generate data (run once)
   generate_temperature_data()

   # Step 2: Analyze 100M records
   analyze_100m_with_pandas()
   analyze_100m_with_duckdb()

   # Step 3: Analyze 1B records (DuckDB only)
   analyze_1b_with_duckdb()
   ```

3. Run the script using uv:
   ```bash
   uv run python bigdata_pandas_vs_duckdb.py
   ```

4. Monitor system resources using your OS tools:
   - **macOS:** Activity Monitor
   - **Linux:** `htop`, `top`, or `glances`
   - **Windows:** Task Manager

## Expected Performance Results

Measured in September 2026 on a laptop with 8 CPU cores and 16 GB RAM (pandas 2.3.3, DuckDB 1.5.6).
Your numbers will differ - the ratio is what matters.

### 100M Records (~1.3 GB)

| Library | Time | Memory Peak | Notes |
|---------|------|-------------|-------|
| **pandas** | ~12 sec | ~4.2 GB | Loads the whole file into memory, single-threaded aggregation |
| **DuckDB** | ~1.6 sec | ~0.26 GB | Parallel, streaming CSV scan |

**Speedup:** DuckDB is about **7x faster** and uses about **15x less memory**

### 1B Records (~13 GB)

| Library | Time | Memory Peak | Notes |
|---------|------|-------------|-------|
| **pandas** | minutes, or out-of-memory | > RAM on a 16 GB machine | Not recommended |
| **DuckDB** | ~22 sec | a few GB | Handles data larger than RAM |

**Recommendation:** **Only use DuckDB** for billion-record datasets

## Key Concepts Explained

### Why is DuckDB Faster?

1. **Parallel Processing:**
   - DuckDB reads CSV files in parallel across multiple CPU cores
   - pandas reads sequentially (single-threaded)

2. **Columnar Storage:**
   - DuckDB stores data in columns (better for analytics)
   - pandas uses row-oriented DataFrames (general-purpose)

3. **Lazy Evaluation:**
   - DuckDB optimizes the entire query before execution
   - pandas executes operations immediately

4. **Memory Efficiency:**
   - DuckDB can process data larger than RAM (out-of-core processing)
   - pandas loads entire dataset into memory

### When to Use Each Tool?

**Use pandas when:**
- Dataset fits comfortably in memory (< 1 GB)
- You need rich data manipulation APIs
- Integrating with Python ML libraries (scikit-learn, etc.)
- Exploratory data analysis with frequent transformations

**Use DuckDB when:**
- Dataset is large (> 5 GB)
- Performing aggregations (GROUP BY, JOIN)
- SQL-familiar team
- Need production-grade performance
- Processing data larger than available RAM

## Exercises for Students

### Exercise 1: Baseline Performance (Easy)

1. Generate `medium_dataset.csv`
2. Process with both pandas and DuckDB
3. Record execution times and peak memory
4. **Question:** What is the speedup ratio?

### Exercise 2: Resource Monitoring (Medium)

1. Run the 100M analysis while monitoring system resources
2. Take screenshots of resource usage for both libraries
3. **Question:** At what point does memory usage peak?

### Exercise 3: Query Optimization (Medium)

Modify the DuckDB query to:
1. Filter for stations where `mean_measurement > 20.0`
2. Return only the top 10 hottest stations
3. **Question:** How does filtering affect execution time?

### Exercise 4: Scalability Analysis (Advanced)

1. Generate `large_dataset.csv`
2. Process with DuckDB only
3. Compare execution time to the 100M dataset
4. **Question:** Is the processing time linear with data size? Why or why not?

### Exercise 5: Custom Dataset (Advanced)

Create your own large dataset:
```python
import random

with open("custom_data.txt", "w") as f:
    stations = ["Station_A", "Station_B", "Station_C", "Station_D", "Station_E"]
    for _ in range(50_000_000):  # 50 million records
        station = random.choice(stations)
        temp = random.uniform(-10, 40)
        f.write(f"{station};{temp:.1f}\n")
```

Process it with both tools and compare results:
```bash
uv run python bigdata_pandas_vs_duckdb.py
```

## Troubleshooting

### Issue: "Memory Error" with pandas

**Solution:**
- Reduce dataset size for pandas (use `nrows` parameter)
- Use DuckDB instead
- Increase system swap space (not recommended for production)

### Issue: "File not found"

**Solution:**
- Ensure you're in the module directory: `src/2. BigData/1. Data/1. pandas_vs_duckdb/`
- Re-run the generation step (`generate_data.py`)

### Issue: Not enough disk space

**Solution:**
- The 1B-record file needs ~13 GB; generate only `medium_dataset.csv` and skip Step 3

### Issue: DuckDB query returns no results

**Solution:**
- Check file path in SQL query (use absolute paths if needed)
- Verify delimiter is set to `;` not `,`
- Ensure `parallel=true` is enabled

## Architecture Patterns Demonstrated

### pandas Pattern

```python
# Load → Transform → Aggregate pipeline
df = (
    pd.read_csv("file.txt", sep=";", names=["col1", "col2"])
    .groupby("col1")
    .agg(["min", "mean", "max"])
)
```

**Characteristics:**
- Imperative, step-by-step processing
- In-memory operations
- Python API

### DuckDB Pattern

```python
# Declarative SQL query
with duckdb.connect() as conn:
    results = conn.sql("""
        SELECT col1, MIN(col2), AVG(col2), MAX(col2)
        FROM read_csv('file.txt', delim=';', parallel=true)
        GROUP BY col1
    """).fetchall()
```

**Characteristics:**
- Declarative, SQL-based
- Query optimization
- Parallel execution

## Integration with Course Modules

This demo serves as **Module 1** in the BigData curriculum:

```
Module 1 (Current): Data Processing Benchmarking
    ↓
Module 2: Model Training (AutoGluon)
    ↓
Module 3: Deployment (FastAPI + Docker)
    ↓
Module 4: Performance Testing (Locust)
    ↓
Module 5: Advanced Applications (LLM Integration)
```

**Key Takeaway:** Understanding data processing performance is foundational for building scalable ML systems.

## Additional Resources

- **DuckDB Documentation:** https://duckdb.org/docs/
- **pandas Documentation:** https://pandas.pydata.org/docs/
- **Performance Comparison Study:** https://h2oai.github.io/db-benchmark/

## Questions for Discussion

1. Why doesn't pandas automatically parallelize CSV reading?
2. What are the trade-offs between SQL and DataFrame APIs?
3. How would you process a 10 TB dataset with limited resources?
4. When would you choose pandas despite slower performance?
5. How does DuckDB achieve out-of-core processing?

## Quick Start Commands

```bash
# 1. Install uv (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install dependencies
uv sync

# 3. Run the analysis script
uv run python bigdata_pandas_vs_duckdb.py
```

## Next Steps

After completing this module, proceed to:
- **Module 2:** Time series forecasting with AutoGluon
- **Module 3:** Deploying ML models with FastAPI and Docker
- **Containerization:** Learn to package this demo in Docker (Module 6)

---

**Course:** ASI 2026 - Machine Learning Operations
**Module:** 2. BigData / 1. Data Processing
**Difficulty:** Intermediate
**Time Required:** 2-3 hours
**Package Manager:** uv (mandatory)
