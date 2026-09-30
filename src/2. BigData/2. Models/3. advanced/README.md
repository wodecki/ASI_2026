# 3. Advanced - Pre-Production Polish

## 🎯 Learning Objectives

This is the **most sophisticated** local implementation before deployment. It builds on `2. production_ready/` by adding:
- Separate evaluation script (train ≠ evaluate ≠ predict)
- Data quality reports (comprehensive data profiling)
- Query result caching (avoid repeated BigQuery costs)
- Batch prediction support (process all products efficiently)
- API-ready JSON output (prep for Module 3 deployment)

## 📁 What's Inside

```
3. advanced/
├── 0. fetch_data.py              # Enhanced: caching + quality reports
├── 1. train.py                   # Enhanced: model comparison logging
├── 2. predict.py                 # Enhanced: batch + API-ready JSON
├── 3. evaluate.py                # NEW: Separate evaluation script
├── config/
│   └── config.toml               # Enhanced: caching + evaluation settings
├── data/
│   ├── iowa_sales.csv            # Cached training data
│   └── data_quality_report.json  # Generated: data profiling
├── model_metadata.json           # Generated: training metadata
├── predictions.json              # Generated: API-ready predictions
├── evaluation_report.json        # Generated: model performance metrics
├── pyproject.toml                # Dependencies (+ numpy for metrics)
└── README.md                     # This file
```

## 🚀 How to Run

### Full Workflow

```bash
# Install dependencies
uv sync

# 1. Fetch data with quality checks (runs only if cached data is stale)
uv run python "0. fetch_data.py"

# 2. Train model
uv run python "1. train.py"

# 3. Evaluate model performance
uv run python "3. evaluate.py"

# 4. Make predictions (batch + API format)
uv run python "2. predict.py"
```

### Quick Start (Use Cached Data)

```bash
uv sync
uv run python "1. train.py"
uv run python "3. evaluate.py"
uv run python "2. predict.py"
```

## 🆕 What's New vs `2. production_ready/`

### ✅ 1. Separate Evaluation Script

**Why it matters:** In production, training and evaluation are separate processes.

**Before (production_ready):**
```python
# 1. train.py does everything: train + evaluate + predict
predictor.fit(train_data)
predictions = predictor.predict(train_data)
# Evaluation mixed with training
```

**After (advanced):**
```python
# 1. train.py - Train only
predictor.fit(train_data)

# 3. evaluate.py - Evaluate separately
metrics = calculate_metrics(actuals, predictions)
# Generate comprehensive evaluation report

# 2. predict.py - Predict only
predictions = predictor.predict(new_data)
```

**Benefits:**
- Clear separation of concerns (train ≠ evaluate ≠ predict)
- Can evaluate without retraining
- Can compare multiple model versions
- Closer to production MLOps patterns

### ✅ 2. Data Quality Reports

**Before (production_ready):**
```python
# Basic validation only
assert len(df) > 0
assert not df.isna().any()
```

**After (advanced):**
```json
// data/data_quality_report.json (auto-generated)
{
  "basic_stats": {
    "num_rows": 1781,
    "num_products": 5,
    "date_range": {"start": "2023-07-07", "end": "2024-04-05"}
  },
  "data_quality": {
    "missing_values": {"date": 0, "item_name": 0, "total_amount_sold": 0},
    "duplicates": 0,
    "negative_values": 0
  },
  "sales_statistics": {
    "total_sales": 5234567,
    "mean_daily_sales_per_product": 2938.45,
    "min_sales": 0, "max_sales": 12345
  },
  "per_product_stats": {
    "BLACK VELVET": {
      "total_sales": 1234567,
      "mean_sales": 3430.19
    }
  }
}
```

**Benefits:**
- Comprehensive data profiling
- Detect outliers and anomalies
- Track data distribution changes over time
- Foundation for data drift detection (Module 9)

### ✅ 3. Query Result Caching

**Before (production_ready):**
```python
# Always fetch from BigQuery (costs money every time)
df = client.query(QUERY).to_dataframe()
```

**After (advanced):**
```python
# Check if cached data is fresh
if os.path.exists(data_file):
    age_days = calculate_age(data_file)
    if age_days < cache_max_age_days:
        logger.info("✓ Using cached data")
        exit(0)

# Only fetch if cache is stale
df = client.query(QUERY).to_dataframe()
```

**Configuration:**
```toml
[data]
cache_max_age_days = 7  # Re-fetch if older than 7 days
```

**Benefits:**
- Reduce BigQuery costs (queries aren't free!)
- Faster development iteration
- Configurable cache policy
- Teaches caching patterns for production

### ✅ 4. Batch Predictions + API-Ready JSON

**Before (production_ready):**
```python
# Single product example
predictions = predictor.predict(train_data)
black_velvet = predictions.loc['BLACK VELVET']
print(black_velvet)
```

**After (advanced):**
```python
# Batch process all products
predictions = predictor.predict(train_data)

# Export in API-ready format
results = []
for product in predictions.index.unique():
    results.append({
        "item_name": product,
        "predictions": [...forecast...],
        "num_predictions": 7
    })

# Save as JSON
with open("predictions.json", "w") as f:
    json.dump({"results": results}, f)
```

**Output format (`predictions.json`):**
```json
{
  "generated_at": "2024-10-30T14:30:00",
  "num_products": 5,
  "results": [
    {
      "item_name": "BLACK VELVET",
      "predictions": [
        {
          "timestamp": "2024-04-06",
          "mean": 3036.51,
          "quantile_0.1": 2145.23,
          "quantile_0.9": 3927.79
        }
      ],
      "num_predictions": 7
    }
  ]
}
```

**Benefits:**
- Ready for FastAPI integration (Module 3)
- Standard REST API format
- Includes uncertainty (quantiles)
- Easy to consume by frontend applications

### ✅ 5. Model Comparison Logging

**Before (production_ready):**
```python
logger.info(f"Best model: {best_model}")
logger.info(f"Models trained: {len(leaderboard)}")
```

**After (advanced):**
```
============================================================
Model Performance Comparison (Leaderboard):
============================================================
Model Name                     Score           Fit Time (s)
------------------------------------------------------------
WeightedEnsemble              -0.2367          0.45
SeasonalNaive                 -0.3012          0.12
ETS                           -0.3456          2.34
RecursiveTabular              -0.4123          8.67
DirectTabular                 -0.4567          7.89
Theta                         -0.5012          1.23
Naive                         0.0000           0.05
============================================================
Best model: WeightedEnsemble
Evaluation metric: MASE (lower is better)
============================================================
```

**Benefits:**
- See why ensemble wins
- Understand model trade-offs (accuracy vs speed)
- Identify fast models for production
- Educational: learn about different time series models

### ✅ 6. Comprehensive Evaluation Metrics

**New script: `3. evaluate.py`**

Calculates multiple metrics:
- **MASE** (Mean Absolute Scaled Error) - AutoGluon's metric
- **RMSE** (Root Mean Squared Error) - Penalizes large errors
- **MAE** (Mean Absolute Error) - Average error magnitude
- **MAPE** (Mean Absolute Percentage Error) - Percentage error

**Output (`evaluation_report.json`):**
```json
{
  "per_product_metrics": {
    "BLACK VELVET": {
      "MASE": 0.2367,
      "RMSE": 456.78,
      "MAE": 345.12,
      "MAPE": 12.34
    }
  },
  "overall_metrics": {
    "MASE": {
      "mean": 0.2845,
      "std": 0.0512,
      "min": 0.2367,
      "max": 0.3456
    }
  }
}
```

**Benefits:**
- Multiple perspectives on model performance
- Per-product and overall metrics
- Interpretation guide (what's a "good" MASE?)
- Comparable across experiments

### ✅ 7. Dry-Run Mode for BigQuery

**Configuration:**
```toml
[bigquery]
dry_run = true  # Preview query without executing
```

**Usage:**
```bash
uv run python "0. fetch_data.py"

============================================================
DRY RUN MODE - Query Preview:
============================================================
SELECT
  date,
  item_description AS item_name,
  SUM(bottles_sold) AS total_amount_sold
FROM iowa.sales
WHERE date BETWEEN '2023-01-01' AND '2024-05-30'
  AND item_description IN (...)
GROUP BY date, item_name
ORDER BY date
============================================================
Set dry_run = false to execute query
============================================================
```

**Benefits:**
- Preview query before spending money
- Catch SQL errors early
- Validate query logic
- Teaching tool (understand what's happening)

## 📊 Configuration File Enhancements

### New Settings in `config/config.toml`

```toml
[bigquery]
dry_run = false              # NEW: Preview queries without executing

[data]
cache_max_age_days = 7       # NEW: Data freshness threshold

[evaluation]
metrics = ["MASE", "RMSE", "MAE", "MAPE"]  # NEW: Metrics to calculate
generate_plots = true                       # NEW: Create evaluation plots

[output]
data_quality_report = "data/data_quality_report.json"  # NEW
evaluation_report = "evaluation_report.json"           # NEW
predictions_file = "predictions.json"                  # Changed to JSON
```

## 📈 Understanding the Outputs

### 1. Data Quality Report (`data/data_quality_report.json`)

Generated by `0. fetch_data.py`:
- Basic statistics (rows, products, date range)
- Data quality checks (missing values, duplicates, negatives)
- Sales statistics (total, mean, median, std dev)
- Per-product breakdown

### 2. Model Metadata (`model_metadata.json`)

Generated by `1. train.py`:
- Training timestamp and duration
- Data summary (samples, products, dates)
- Model configuration (prediction length, preset, time limit)
- Model performance (best model, leaderboard)
- Educational notes (cross-validation, ensemble strategy)

### 3. Evaluation Report (`evaluation_report.json`)

Generated by `3. evaluate.py`:
- Per-product metrics (MASE, RMSE, MAE, MAPE)
- Overall metrics (mean, std, min, max)
- Metric interpretation guide

### 4. Predictions (`predictions.json`)

Generated by `2. predict.py`:
- API-ready JSON format
- Batch predictions for all products
- Includes uncertainty (quantiles)
- Ready for FastAPI integration

## 🧪 Advanced Experiments

### Experiment 1: Dry-Run Query Preview

```bash
# Edit config/config.toml
[bigquery]
dry_run = true

# Preview query
uv run python "0. fetch_data.py"
# Output: SQL query without execution

# Execute query
[bigquery]
dry_run = false

uv run python "0. fetch_data.py"
```

### Experiment 2: Cache Policy Testing

```bash
# Fresh fetch
uv run python "0. fetch_data.py"

# Immediate re-run (uses cache)
uv run python "0. fetch_data.py"

# Force refresh by shortening cache age
[data]
cache_max_age_days = 0

uv run python "0. fetch_data.py"
```

### Experiment 3: Model Comparison

```bash
# Train with medium quality
[model]
preset = "medium_quality"

uv run python "1. train.py"
# Note the leaderboard

# Train with best quality
[model]
preset = "best_quality"

uv run python "1. train.py"
# Compare leaderboards - which models improved?
```

### Experiment 4: Multiple Metrics

```bash
# Edit config/config.toml
[evaluation]
metrics = ["MASE", "RMSE", "MAE", "MAPE"]

# Run evaluation
uv run python "3. evaluate.py"

# Check evaluation_report.json
# Which metric tells you the most about model quality?
```

## 🚫 What's Still Missing for True Production

This is the **bridge** between local development and production deployment. Still missing:

### ❌ Experiment Tracking
- **What's missing:** MLflow, WandB integration
- **Where to learn:** → **Module 8: Experiment Tracking**
- **Why deferred:** Module 8 teaches this comprehensively

### ❌ Containerization
- **What's missing:** Docker images, docker-compose
- **Where to learn:** → **Module 6: Containerization**
- **Why deferred:** Module 6 has complete Docker curriculum

### ❌ API Serving
- **What's missing:** FastAPI endpoints, Streamlit UI
- **Where to learn:** → **Module 3: Deployment**
- **Why deferred:** JSON format is ready, Module 3 adds serving

### ❌ Model Monitoring
- **What's missing:** Data drift detection, performance alerts
- **Where to learn:** → **Module 9: Data and Model Drift**
- **Why deferred:** Module 9 teaches monitoring patterns

### ❌ CI/CD Pipelines
- **What's missing:** GitHub Actions, automated testing
- **Where to learn:** → **Module 11: AI Architecture Design**
- **Why deferred:** Requires containerization first

### ❌ Unit Tests
- **What's missing:** pytest for data loading, predictions, metrics
- **Why deferred:** Can be added as exercise, or in Module 4 (Software Engineering)

## 📚 Key Takeaways

### What You Learned

1. **Separation of Concerns**
   - Train, evaluate, and predict are distinct processes
   - Each script has a single responsibility
   - Easier to test, debug, and maintain

2. **Data Profiling**
   - Comprehensive quality reports
   - Foundation for drift detection
   - Document data assumptions

3. **Cost Optimization**
   - Query result caching
   - Configurable cache policies
   - Dry-run mode to preview queries

4. **Production Patterns**
   - API-ready JSON outputs
   - Batch processing
   - Multiple evaluation metrics
   - Model comparison logging

5. **Bridge to Deployment**
   - This code is **deployment-ready** (just needs infrastructure)
   - JSON format works with FastAPI
   - Evaluation reports inform production decisions

### When to Use This Approach

✅ **Use `3. advanced/` for:**
- Final local development before deployment
- Model comparison and selection
- Preparing for Module 3 (Deployment)
- Learning pre-production patterns
- Team projects with code reviews

❌ **Don't use yet for:**
- Production deployment (needs Module 3, 6)
- Real-time serving (needs FastAPI)
- Experiment tracking (needs Module 8)
- Monitoring (needs Module 9)

## ➡️ Next Steps

### Ready for Deployment?

👉 **Module 3: Deployment**
- Use `predictions.json` as API response format
- Wrap `2. predict.py` in FastAPI endpoints
- Add Streamlit frontend
- Deploy to GCP Cloud Run

### Want Containers?

👉 **Module 6: Containerization**
- Create Dockerfile for this project
- Use docker-compose for multi-container setup
- Learn volume management for model persistence

### Want Experiment Tracking?

👉 **Module 8: Experiment Tracking**
- Integrate WandB
- Track hyperparameters and metrics
- Compare 100+ experiments
- Model registry

### Want Monitoring?

👉 **Module 9: Data and Model Drift**
- Use `data_quality_report.json` as baseline
- Implement drift detection
- Set up alerts
- Performance monitoring

## 🔄 Comparison Table

| Feature | 1. minimal/ | 2. production_ready/ | 3. advanced/ |
|---------|------------|---------------------|--------------|
| Configuration | Hardcoded | TOML file | TOML + caching |
| Logging | print() | logging | logging + structured |
| Validation | None | Assertions | Assertions + reports |
| Evaluation | Mixed with training | Mixed with training | **Separate script** |
| Data quality | None | Basic checks | **Comprehensive reports** |
| Caching | No | No | **Yes (configurable)** |
| Predictions | Single example | Per product | **Batch + API JSON** |
| Metrics | MASE only | MASE only | **4 metrics** |
| Model comparison | Basic | Basic | **Detailed leaderboard** |
| Dry-run | No | No | **Yes** |
| API-ready | No | No | **Yes (JSON format)** |
| Code lines | 60 | 120 | 180 |
| Production-ready | ❌ | ⚠️ (local only) | ✅ (needs infra) |

## 🤔 Questions This Code Answers

✅ How do I avoid repeated BigQuery costs? → **Caching**
✅ How do I evaluate models properly? → **Separate evaluation script**
✅ How do I profile my data? → **Data quality reports**
✅ How do I prepare for API deployment? → **JSON output format**
✅ How do I compare model performance? → **Multiple metrics + leaderboard**
✅ How do I preview queries safely? → **Dry-run mode**

## 🎓 Educational Value

This module teaches the **transition from development to production**:

1. **Local development** (1. minimal) → Quick prototyping
2. **MLOps fundamentals** (2. production_ready) → Best practices
3. **Pre-production** (3. advanced) → Deployment preparation
4. **Production** (Modules 3, 6, 8, 9) → Infrastructure & monitoring

**You've learned the complete local ML workflow!**

---

**Next:** Continue to **Module 3 (Deployment)** to deploy this model as a REST API with FastAPI and Streamlit.
