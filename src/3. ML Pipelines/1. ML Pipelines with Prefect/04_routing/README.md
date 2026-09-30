# 04_routing - Conditional Logic

## Question
**How do I make decisions in pipelines?**

## Core Concepts

### Basic If/Else Routing
```python
@flow
def routing_pipeline(data):
    quality = check_quality(data)

    if quality["is_valid"]:
        return process_valid(data)
    else:
        return process_invalid(data)
```

### Multi-Branch Routing
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

### ML Threshold Routing
```python
@flow
def ml_pipeline(models, deploy_threshold=0.85):
    best = train_and_select_best(models)

    if best["f1"] >= deploy_threshold:
        return deploy_model(best)
    elif best["f1"] >= 0.75:
        return request_review(best)
    else:
        return trigger_retrain(best)
```

## Scripts

| Script | Concept | Description |
|--------|---------|-------------|
| `0.py` | Plain Python (no Prefect) | Baseline to show Prefect's value |
| `1.py` | Basic if/else | Route based on data quality |
| `2.py` | Multi-branch | Route to 4+ destinations |
| `3.py` | ML thresholds | Deploy/review/retrain based on metrics |

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
uv run 1.py   # Basic routing
uv run 2.py   # Multi-branch routing
uv run 3.py   # ML threshold routing
```

## ML Use Cases

- **Model deployment**: Deploy if accuracy > 0.9
- **A/B testing**: Route traffic based on experiment
- **Data quality**: Skip processing if data is invalid
- **Alerting**: Escalate based on severity
