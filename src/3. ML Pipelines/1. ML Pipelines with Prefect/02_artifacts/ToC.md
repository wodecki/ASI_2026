# 02_artifacts - Table of Contents

## Scripts

### 0.py - Plain Python ETL (No Prefect)
- Baseline ETL pipeline without Prefect
- Same logic as 1.py but no decorators
- Shows what you miss: no tracking, no UI artifacts, no run history

### 1.py - File-Based Artifacts (Data Layers)
- Extract from `01_input/`
- Transform and save to `02_intermediate/` (parquet format)
- Load to `03_output/`
- Checkpoint-based workflow

### 2.py - Prefect UI Artifacts
- `create_table_artifact()` for tabular data
- `create_markdown_artifact()` for reports
- Viewing artifacts in Prefect UI

## Key Patterns

```python
# File-based checkpoint (parquet for efficiency)
df.to_parquet("data/02_intermediate/checkpoint.parquet")

# Prefect table artifact
create_table_artifact(
    key="my-table",
    table=df.to_dict(orient="records")
)

# Prefect markdown artifact
create_markdown_artifact(
    key="my-report",
    markdown="# Report\n**Rows:** 100"
)
```

## Data Layer Convention

```
01_input/       <- Raw, immutable
02_intermediate/ <- Checkpoints, can be deleted
03_output/      <- Final results
```
