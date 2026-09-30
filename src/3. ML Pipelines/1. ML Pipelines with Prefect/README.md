# ML Pipelines with Prefect

This module teaches workflow orchestration for ML pipelines using [Prefect](https://www.prefect.io/). Through progressive examples, you'll learn how to build observable, resilient, and production-ready ML workflows.

## Learning Objectives

By completing this module, you will:

1. Understand the value of workflow orchestration vs. plain Python scripts
2. Build pipelines using Prefect's `@task` and `@flow` decorators
3. Manage data artifacts and pipeline checkpoints
4. Compose complex pipelines from reusable subflows
5. Implement conditional routing for ML decision-making
6. Handle failures with retries and fallback patterns
7. Optimize performance with task caching

## Prerequisites

- Python 3.10+
- Basic understanding of Python functions and decorators
- Familiarity with pandas DataFrames

## Installation

```bash
cd "src/3. ML Pipelines/1. ML Pipelines with Prefect"
uv sync
```

## Quick Start

### 1. Start the Prefect Server

The Prefect server provides a UI for monitoring your pipelines.

```bash
# Terminal 1: Start server
uv run prefect server start

# Terminal 2: Configure API URL (one-time setup)
uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

Open http://127.0.0.1:4200 to view the Prefect dashboard.

### 2. Run Your First Flow

```bash
cd 01_basics
uv run python 1.py
```

## Module Structure

The module is organized into 6 progressive sub-modules, each answering a key question:

| Module | Question | Key Concepts |
|--------|----------|--------------|
| [01_basics](#01_basics---tasks-and-flows) | What are tasks and flows? | `@task`, `@flow`, `.map()` |
| [02_artifacts](#02_artifacts---data-management) | How do I manage pipeline data? | Data layers, UI artifacts |
| [03_flows](#03_flows---pipeline-composition) | How do I compose complex pipelines? | Subflows, ETL patterns |
| [04_routing](#04_routing---conditional-logic) | How do I make decisions in pipelines? | If/else, multi-branch, ML thresholds |
| [05_retries](#05_retries---failure-handling) | How do I handle failures? | Retries, backoff, fallbacks |
| [06_caching](#06_caching---efficiency) | How do I avoid re-computation? | Cache policies, expiration |

Each sub-module includes:
- `0.py` - Plain Python baseline (no Prefect) for comparison
- `1.py`, `2.py`, `3.py` - Progressive Prefect examples
- `README.md` - Detailed documentation
- `data/` - Sample datasets (where applicable)

---

## 01_basics - Tasks and Flows

**Question:** What are tasks and flows?

### Core Concepts

**@task** - A single unit of work that Prefect tracks:
```python
@task
def load_data() -> pd.DataFrame:
    return pd.read_csv("data.csv")
```

**@flow** - An orchestrator that calls tasks:
```python
@flow
def my_pipeline():
    data = load_data()      # Task call
    result = process(data)  # Another task
    return result
```

**.map()** - Parallel execution across items:
```python
@flow
def parallel_flow():
    items = [1, 2, 3, 4, 5]
    futures = process_item.map(items)  # Runs in parallel
    results = [f.result() for f in futures]
```

### Scripts

| Script | Description |
|--------|-------------|
| `0.py` | Plain Python baseline (no Prefect) |
| `1.py` | Basic `@task` and `@flow` |
| `2.py` | Parallel execution with `.map()` |

### Running

```bash
cd 01_basics
uv run python 0.py   # Plain Python - baseline
uv run python 1.py   # Basic tasks and flows
uv run python 2.py   # Parallel execution
```

---

## 02_artifacts - Data Management

**Question:** How do I manage data between pipeline steps?

### Core Concepts

**Data Layers** (Kedro-inspired pattern):
```
data/
├── 01_input/        # Raw source data (immutable)
├── 02_intermediate/ # Transformed data (checkpoints)
└── 03_output/       # Final results
```

**File-Based Artifacts** - Save checkpoints as parquet:
```python
@task
def transform(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["total"] = result["price"] * result["quantity"]
    result.to_parquet("data/02_intermediate/transformed.parquet")
    return result
```

**Prefect UI Artifacts** - Display results in the dashboard:
```python
from prefect.artifacts import create_table_artifact, create_markdown_artifact

@task
def create_report(df: pd.DataFrame):
    create_table_artifact(
        key="output-table",
        table=df.to_dict(orient="records")
    )
    create_markdown_artifact(
        key="report",
        markdown="# Summary\n**Rows:** 100"
    )
```

### Scripts

| Script | Description |
|--------|-------------|
| `0.py` | Plain Python ETL baseline |
| `1.py` | File-based ETL with parquet checkpoints |
| `2.py` | Prefect UI artifacts (table + markdown) |

### Running

```bash
cd 02_artifacts
uv run python 0.py   # Plain Python ETL
uv run python 1.py   # File-based artifacts
uv run python 2.py   # Prefect UI artifacts

# Cleanup intermediate files
./clean_up.sh
```

---

## 03_flows - Pipeline Composition

**Question:** How do I compose complex pipelines?

### Core Concepts

**Subflows** - Flows can call other flows:
```python
@flow
def extract_flow():
    return load_data()

@flow
def transform_flow(data):
    return process(data)

@flow
def etl():
    raw = extract_flow()       # Subflow call
    clean = transform_flow(raw)
    return clean
```

**Partial Pipeline Execution** - Run specific steps:
```python
@flow
def partial_pipeline(start=1, end=5, data=None):
    steps = {1: step_1, 2: step_2, 3: step_3, 4: step_4, 5: step_5}
    for i in range(start, end + 1):
        data = steps[i](data)
    return data

# Run only steps 2-4
partial_pipeline(start=2, end=4, data=checkpoint)
```

### Scripts

| Script | Description |
|--------|-------------|
| `0.py` | Plain Python composition baseline |
| `1.py` | Basic subflows (flow calling flow) |
| `2.py` | ETL pattern with subflows |
| `3.py` | Partial pipeline execution |

### Running

```bash
cd 03_flows
uv run python 0.py   # Plain Python baseline
uv run python 1.py   # Basic subflows
uv run python 2.py   # ETL pattern
uv run python 3.py   # Partial execution
```

---

## 04_routing - Conditional Logic

**Question:** How do I make decisions in pipelines?

### Core Concepts

**Basic If/Else Routing**:
```python
@flow
def routing_pipeline(data):
    quality = check_quality(data)

    if quality["is_valid"]:
        return process_valid(data)
    else:
        return process_invalid(data)
```

**Multi-Branch Routing** (dispatch pattern):
```python
@flow
def multi_branch(order):
    priority = calculate_priority(order)

    handlers = {
        "critical": handle_critical,
        "high": handle_high,
        "medium": handle_medium,
        "low": handle_low,
    }

    return handlers[priority](order)
```

**ML Threshold Routing**:
```python
@flow
def ml_pipeline(models, deploy_threshold=0.85, review_threshold=0.75):
    best = train_and_select_best(models)

    if best["f1"] >= deploy_threshold:
        return deploy_model(best)
    elif best["f1"] >= review_threshold:
        return request_review(best)
    else:
        return trigger_retrain(best)
```

### Scripts

| Script | Description |
|--------|-------------|
| `0.py` | Plain Python routing baseline |
| `1.py` | Basic if/else routing |
| `2.py` | Multi-branch routing (4+ destinations) |
| `3.py` | ML threshold routing (deploy/review/retrain) |

### Running

```bash
cd 04_routing
uv run python 0.py   # Plain Python baseline
uv run python 1.py   # Basic routing
uv run python 2.py   # Multi-branch
uv run python 3.py   # ML thresholds
```

---

## 05_retries - Failure Handling

**Question:** How do I handle failures in pipelines?

### Core Concepts

**Basic Retries**:
```python
@task(retries=3)
def flaky_task():
    # Will retry up to 3 times on failure
    call_unreliable_api()
```

**Exponential Backoff** - For rate limits:
```python
@task(retries=3, retry_delay_seconds=[1, 10, 60])
def rate_limited_task():
    # Retry delays: 1s, 10s, 60s
    call_throttled_api()
```

**Fallback Pattern** - Cascading alternatives:
```python
@flow
def with_fallback(endpoint):
    try:
        return primary_api(endpoint)
    except Exception:
        pass

    try:
        return backup_api(endpoint)
    except Exception:
        pass

    return use_cached_data()
```

### Scripts

| Script | Description |
|--------|-------------|
| `1.py` | Basic retries (`retries=3`) |
| `2.py` | Exponential backoff (`retry_delay_seconds=[1, 10, 60]`) |
| `3.py` | Fallback patterns (primary -> backup -> cache) |

### Running

```bash
cd 05_retries
uv run python 1.py   # Basic retries
uv run python 2.py   # Exponential backoff
uv run python 3.py   # Fallback patterns
```

---

## 06_caching - Efficiency

**Question:** How do I avoid re-running expensive computations?

### Core Concepts

**Basic Caching** - Cache by input values:
```python
from prefect.cache_policies import INPUTS

@task(cache_policy=INPUTS)
def expensive_task(x, y):
    # Cached by input values
    return compute(x, y)
```

**Cache Expiration** - Time-based invalidation:
```python
from datetime import timedelta

@task(
    cache_policy=INPUTS,
    cache_expiration=timedelta(hours=1)
)
def fetch_data():
    # Cache valid for 1 hour
    return get_from_api()
```

**Force Refresh** - Bypass cache when needed:
```python
@flow
def pipeline(force_refresh=False):
    if force_refresh:
        result = my_task.with_options(refresh_cache=True)(data)
    else:
        result = my_task(data)
```

### Scripts

| Script | Description |
|--------|-------------|
| `1.py` | Basic caching (`cache_policy=INPUTS`) |
| `2.py` | Cache expiration (`timedelta(hours=1)`) |
| `3.py` | Force refresh (`refresh_cache=True`) |

### Running

```bash
cd 06_caching
uv run python 1.py   # Basic caching
uv run python 2.py   # Cache expiration
uv run python 3.py   # Force refresh
```

---

## Sample Data

All modules use the same simple dataset:

**products.csv**:
```csv
id,price,category
1,10,A
2,20,B
```

**sales.csv**:
```csv
id,quantity,region
1,5,North
2,3,South
```

## Why Prefect?

Comparing plain Python vs. Prefect:

| Feature | Plain Python | Prefect |
|---------|-------------|---------|
| Execution tracking | Manual logging | Automatic |
| UI dashboard | None | Built-in |
| Retry on failure | Manual try/except | `@task(retries=3)` |
| Result caching | Manual implementation | `cache_policy=INPUTS` |
| Parallel execution | Manual threading | `.map()` |
| Pipeline composition | Function calls | Subflows with tracking |
| Artifacts | Manual file I/O | UI-visible artifacts |

## Prefect Server Commands

```bash
# Start the server
uv run prefect server start

# Configure API URL
uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api

# View configuration
uv run prefect config view

# Stop the server (Ctrl+C in terminal)
```

## Dependencies

```toml
dependencies = [
    "prefect",
    "prefect-cloud",
    "pandas",
    "tabulate",
    "pyarrow>=22.0.0",
]
```

## Resources

- [Prefect Documentation](https://docs.prefect.io/)
- [Prefect Concepts](https://docs.prefect.io/concepts/)
- [Prefect Examples](https://github.com/PrefectHQ/prefect/tree/main/src/prefect/examples)
