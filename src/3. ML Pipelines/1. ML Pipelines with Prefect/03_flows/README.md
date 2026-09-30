# 03_flows - Pipeline Composition

## Question
**How do I compose complex pipelines?**

## Core Concepts

### Subflows (Flow Calling Flow)
```python
@flow
def child_flow():
    return "data"

@flow
def parent_flow():
    result = child_flow()  # Subflow call
    return result
```

Subflows enable:
- **Modularity**: Reusable pipeline components
- **Visibility**: Track execution in Prefect UI
- **Organization**: Logical grouping of steps

### ETL Pattern with Subflows
```python
@flow
def extract_flow():
    return load_data()

@flow
def transform_flow(data):
    return process(data)

@flow
def load_flow(data):
    save(data)

@flow
def etl():
    raw = extract_flow()
    clean = transform_flow(raw)
    load_flow(clean)
```

### Partial Pipeline Execution
```python
@flow
def partial_pipeline(start=1, end=5, data=None):
    steps = {1: step_1, 2: step_2, 3: step_3, ...}
    for i in range(start, end + 1):
        data = steps[i](data)
    return data

# Run only steps 2-4
partial_pipeline(start=2, end=4, data=checkpoint)
```

## Scripts

| Script | Concept | Description |
|--------|---------|-------------|
| `0.py` | Plain Python (no Prefect) | Baseline to show Prefect's value |
| `1.py` | Basic subflows | Flow calling flow |
| `2.py` | ETL with subflows | Extract/Transform/Load architecture |
| `3.py` | Partial execution | Run steps X to Y |

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
uv run 1.py   # Basic subflows
uv run 2.py   # ETL pattern
uv run 3.py   # Partial pipeline execution
```

## Use Cases

1. **Modular pipelines**: Break large flows into focused subflows
2. **Reusability**: Share subflows across multiple pipelines
3. **Testing**: Run individual subflows in isolation
4. **Recovery**: Resume from checkpoint using partial execution
