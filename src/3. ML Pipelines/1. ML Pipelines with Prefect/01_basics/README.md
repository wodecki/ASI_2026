# 01_basics - Tasks and Flows

## Question
**What are tasks and flows?**

## Core Concepts

### @task - A Unit of Work
```python
@task
def load_data() -> pd.DataFrame:
    return pd.read_csv("data.csv")
```

Tasks are the smallest unit of work in Prefect. They:
- Execute a single piece of logic
- Are tracked by Prefect (start time, duration, status)
- Can be retried, cached, and configured

### @flow - The Orchestrator
```python
@flow
def my_pipeline():
    data = load_data()      # Call tasks
    result = process(data)  # Like regular functions
    return result
```

Flows are containers that orchestrate tasks. They:
- Call tasks and other flows
- Define the execution order
- Provide observability into the pipeline

### .map() - Parallel Execution
```python
@task
def process_item(item):
    return item * 2

@flow
def parallel_flow():
    items = [1, 2, 3, 4, 5]
    results = process_item.map(items)  # Runs in parallel
```

The `.map()` method applies a task to each item in a list, potentially in parallel.

## Scripts

| Script | Concept | Description |
|--------|---------|-------------|
| `0.py` | Plain Python (no Prefect) | Baseline to show Prefect's value |
| `1.py` | Basic @task and @flow | Sequential task execution |
| `2.py` | Parallel with .map() | Process items in parallel |

## Running

### Start Prefect Server (if not running)

```bash
# Terminal 1: Start server
uv run prefect server start

# Terminal 2: Configure API URL
uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

View runs at http://127.0.0.1:4200

### Run Scripts

```bash
uv run 0.py   # Plain Python (no Prefect) - baseline
uv run 1.py   # Basic tasks and flows
uv run 2.py   # Parallel execution
```

## Data
Uses the same products/sales CSVs as all modules:
- `data/01_input/products.csv`
- `data/01_input/sales.csv`
