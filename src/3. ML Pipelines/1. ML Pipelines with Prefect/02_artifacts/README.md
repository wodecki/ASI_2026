# 02_artifacts - Data Management

## Question
**How do I manage data between pipeline steps?**

## Core Concepts

### Data Layers (Kedro-inspired)
```
data/
├── 01_input/        # Raw source data (immutable)
├── 02_intermediate/ # Transformed data (checkpoints)
└── 03_output/       # Final results
```

This pattern enables:
- **Clear data lineage**: Know where data comes from
- **Checkpoint recovery**: Resume from intermediate state
- **Debugging**: Inspect data at each stage

### File-Based Artifacts
```python
@task
def transform(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["total"] = result["price"] * result["quantity"]

    # Save checkpoint as parquet (efficient binary format)
    result.to_parquet("data/02_intermediate/transformed.parquet")
    return result
```

### Prefect UI Artifacts
```python
from prefect.artifacts import create_table_artifact, create_markdown_artifact

@task
def create_artifacts(df: pd.DataFrame):
    # Table artifact (shows data in UI)
    create_table_artifact(
        key="output-table",
        table=df.to_dict(orient="records")
    )

    # Markdown artifact (shows report in UI)
    create_markdown_artifact(
        key="report",
        markdown="# Summary\n**Rows:** 100"
    )
```

## Scripts

| Script | Concept | Description |
|--------|---------|-------------|
| `0.py` | Plain Python (no Prefect) | Baseline ETL to show Prefect's value |
| `1.py` | File-based artifacts | ETL with data layers (parquet checkpoints) |
| `2.py` | Prefect UI artifacts | Table and markdown artifacts |

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
uv run 0.py   # Plain Python ETL (no Prefect) - baseline
uv run 1.py   # File-based ETL with parquet checkpoints
uv run 2.py   # Prefect UI artifacts (requires server for viewing)
```

## Cleanup

```bash
./clean_up.sh   # Remove intermediate and output files
```

## Data
- `data/01_input/` - Source data (preserved by clean_up.sh)
- `data/02_intermediate/` - Transform checkpoints (parquet format)
- `data/03_output/` - Final results
