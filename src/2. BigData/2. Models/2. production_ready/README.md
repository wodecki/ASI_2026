# 2. Production Ready - MLOps Fundamentals

## 🎯 Learning Objectives

This is a **production-ready** implementation that builds on `1. minimal/` by adding MLOps best practices:
- Configuration-driven development (TOML files, not hardcoded values)
- Structured logging (visibility into training process)
- Data validation (fail fast on bad data)
- Model metadata (track what was trained, when, and how)
- Error handling (helpful troubleshooting messages)

## 📁 What's Inside

```
2. production_ready/
├── 0. fetch_data.py           # Config-driven BigQuery data fetch
├── 1. train.py                # Enhanced training with logging & validation
├── 2. predict.py              # Enhanced predictions with error handling
├── config/
│   └── config.toml            # Central configuration file
├── data/
│   └── iowa_sales.csv         # Pre-downloaded data (fallback)
├── model_metadata.json        # Generated: training metadata
├── pyproject.toml             # Dependencies (+ tomli for TOML support)
└── README.md                  # This file
```

## 🚀 How to Run

### Quick Start (Use Pre-Downloaded Data)

```bash
# Install dependencies
uv sync

# Train model
uv run python "1. train.py"

# Make predictions
uv run python "2. predict.py"
```

### Full Workflow (Fetch from BigQuery)

```bash
# Install dependencies
uv sync

# Download fresh data from BigQuery
uv run python "0. fetch_data.py"

# Train model
uv run python "1. train.py"

# Make predictions
uv run python "2. predict.py"
```

## 🆚 What Improved vs `1. minimal/`

### ✅ 1. Configuration-Driven Development

**Before (minimal):**
```python
# Hardcoded in code - must edit script to change
PROJECT_ID = "asi2025"
prediction_length = 7
time_limit = 60
```

**After (production_ready):**
```toml
# config/config.toml - change without touching code
[model]
prediction_length = 7
time_limit_seconds = 60
preset = "medium_quality"
```

**Benefits:**
- Experiment with different settings without code changes
- Easy to compare configurations (just copy config files)
- Prevents accidental code bugs when changing parameters
- Can version control configurations separately

### ✅ 2. Structured Logging

**Before (minimal):**
```python
print("Downloading data...")
print(f"Downloaded {len(df)} rows")
```

**After (production_ready):**
```python
logger.info("Fetching data from BigQuery project: asi2025")
logger.info(f"✓ Downloaded {len(df)} rows")
logger.error("ERROR: Data file not found")
```

**Benefits:**
- Timestamps on every log message
- Log levels (INFO, WARNING, ERROR) for filtering
- Easier to debug when things go wrong
- Can redirect logs to files for later analysis

### ✅ 3. Data Validation

**Before (minimal):**
```python
df = pd.read_csv("data/iowa_sales.csv")  # Assumes data is perfect
```

**After (production_ready):**
```python
assert not df['date'].isna().any(), "ERROR: Missing dates found"
assert (df['total_amount_sold'] >= 0).all(), "ERROR: Negative sales values"
assert len(df) > 100, "ERROR: Dataset too small"
logger.info("✓ Data validation passed")
```

**Benefits:**
- Catch data quality issues immediately
- Fail fast with clear error messages
- Prevents training on corrupted data
- Documents data assumptions

### ✅ 4. Model Metadata

**Before (minimal):**
```python
# No metadata saved
# Can't remember: when was this trained? with what data?
```

**After (production_ready):**
```json
// model_metadata.json (auto-generated)
{
  "trained_at": "2024-10-30T14:23:15",
  "training_time_seconds": 58.42,
  "data_summary": {
    "num_samples": 1781,
    "num_products": 5
  },
  "best_model": "WeightedEnsemble",
  "leaderboard": [...]
}
```

**Benefits:**
- Track experiment history
- Reproduce results later
- Compare model versions
- Debugging (know exactly what data was used)

### ✅ 5. Error Handling

**Before (minimal):**
```python
predictor = TimeSeriesPredictor.load("autogluon-iowa-daily")
# Cryptic error if model doesn't exist
```

**After (production_ready):**
```python
try:
    predictor = TimeSeriesPredictor.load(model_path)
except Exception as e:
    logger.error(f"ERROR: Failed to load model")
    logger.error("Troubleshooting:")
    logger.error("1. Did you run '1. train.py' first?")
    logger.error("2. Check model_path in config.toml")
    raise
```

**Benefits:**
- Helpful error messages
- Troubleshooting guidance
- Faster debugging
- Better student experience

## 📊 Configuration File Explained

### `config/config.toml` Structure

```toml
[bigquery]
project_id = "asi2025"           # Your GCP project
dataset = "iowa"                 # BigQuery dataset
table = "sales"                  # BigQuery table

[data]
input_file = "data/iowa_sales.csv"   # Local data file
products = ["BLACK VELVET", ...]      # Products to forecast

[data.date_range]
start = "2023-01-01"                  # Training data start
end = "2024-05-30"                    # Training data end

[model]
path = "autogluon-iowa-production"    # Model save location
prediction_length = 7                 # Forecast horizon (days)
preset = "medium_quality"             # Training quality
time_limit_seconds = 60               # Max training time

[training]
test_size_days = 7                    # Validation split

[output]
metadata_file = "model_metadata.json" # Metadata location
predictions_file = "predictions.csv"  # Predictions output
```

### How to Experiment

Want to forecast 14 days instead of 7?
```bash
# Edit config/config.toml
[model]
prediction_length = 14

# Re-run training
uv run python "1. train.py"
```

Want to use different products?
```bash
# Edit config/config.toml
[data]
products = ["CAPTAIN MORGAN SPICED RUM", "JAGERMEISTER"]

# Fetch fresh data
uv run python "0. fetch_data.py"

# Train new model
uv run python "1. train.py"
```

## 📈 Understanding the Output

### During Training (`1. train.py`)

```
2024-10-30 14:23:10 - INFO - Loading configuration from config/config.toml
2024-10-30 14:23:10 - INFO - Loading data from data/iowa_sales.csv
2024-10-30 14:23:10 - INFO - ✓ Loaded 1781 rows
2024-10-30 14:23:11 - INFO - ✓ Data validation passed
2024-10-30 14:23:11 - INFO -   Products: 5
2024-10-30 14:23:11 - INFO -   Total samples: 1781
2024-10-30 14:23:12 - INFO - Starting model training with preset='medium_quality'
2024-10-30 14:24:10 - INFO - ✓ Training completed in 58.42 seconds
2024-10-30 14:24:10 - INFO - ✓ Best model: WeightedEnsemble
2024-10-30 14:24:11 - INFO - ✓ Model metadata saved to model_metadata.json
```

**What you learn:**
- See exactly what's happening at each step
- Timestamps help identify slow operations
- Checkmarks (✓) confirm success
- Clear summary at the end

### During Prediction (`2. predict.py`)

```
2024-10-30 14:25:00 - INFO - Loading trained model from autogluon-iowa-production/
2024-10-30 14:25:01 - INFO - ✓ Model loaded successfully
============================================================
Model Information:
  Trained at: 2024-10-30T14:23:15
  Best model: WeightedEnsemble
  Number of models: 7
  Data samples: 1781
============================================================

Example Prediction (BLACK VELVET):
------------------------------------------------------------
Product: BLACK VELVET
Forecast date: 2024-04-05
Predicted sales (mean): 3036.51
Prediction interval (80%): [2145.23, 3927.79]
------------------------------------------------------------
```

**What you learn:**
- Model metadata displayed automatically
- Predictions include uncertainty (prediction intervals)
- Clear formatting makes output easy to read

## 🚫 What's Still Missing for TRUE Production

This code is **ready for local development** but NOT production deployment. Here's what's missing:

### ❌ Experiment Tracking
- **What's missing:** MLflow, WandB, or TensorBoard integration
- **Why it matters:** Compare 100+ experiments, visualize training curves
- **Where to learn:** → **Module 8: Experiment Tracking**

### ❌ Containerization
- **What's missing:** Docker images, reproducible environments
- **Why it matters:** "Works on my machine" → "Works everywhere"
- **Where to learn:** → **Module 6: Containerization**

### ❌ API Deployment
- **What's missing:** FastAPI endpoints, Streamlit dashboards
- **Why it matters:** Serve predictions to applications
- **Where to learn:** → **Module 3: Deployment**

### ❌ Model Monitoring
- **What's missing:** Data drift detection, performance tracking
- **Why it matters:** Know when models degrade over time
- **Where to learn:** → **Module 9: Data and Model Drift**

### ❌ CI/CD Pipelines
- **What's missing:** Automated testing, deployment workflows
- **Why it matters:** Deploy safely and frequently
- **Where to learn:** → **Module 11: AI Architecture Design**

### ❌ Unit Tests
- **What's missing:** pytest tests for data loading, validation, predictions
- **Why it matters:** Prevent regressions, catch bugs early
- **Where to learn:** (Future module or `3. advanced/`)

### ❌ Model Versioning
- **What's missing:** Semantic versioning (v1.0.0, v1.1.0)
- **Why it matters:** Roll back to previous versions, A/B testing
- **Where to learn:** → **Module 8: Experiment Tracking**

## 🧪 Try These Experiments

### Experiment 1: Change Forecast Horizon

```bash
# Edit config/config.toml
[model]
prediction_length = 14  # Changed from 7 to 14

# Re-train
uv run python "1. train.py"
```

**Observe:**
- Does training time change?
- How does model performance compare?
- Check `model_metadata.json` to see the difference

### Experiment 2: Change Training Quality

```bash
# Edit config/config.toml
[model]
preset = "best_quality"  # Changed from "medium_quality"

# Re-train (will take longer!)
uv run python "1. train.py"
```

**Observe:**
- Training takes 5-10x longer
- Does accuracy improve?
- Compare leaderboards in metadata files

### Experiment 3: Add New Products

```bash
# Edit config/config.toml
[data]
products = [
    "BLACK VELVET",
    "CAPTAIN MORGAN SPICED RUM",  # New!
    "JAGERMEISTER"                # New!
]

# Fetch fresh data
uv run python "0. fetch_data.py"

# Train new model
uv run python "1. train.py"
```

**Observe:**
- Data validation catches any issues
- Model trains on new products automatically
- Metadata tracks the change

## 📚 Key Takeaways

### What You Learned

1. **Configuration > Hardcoding**
   - Separate code from parameters
   - Easy experimentation
   - Version control configurations

2. **Logging > Print Statements**
   - Structured, timestamped logs
   - Log levels for filtering
   - Better debugging experience

3. **Validation > Assumptions**
   - Check data quality early
   - Fail fast with clear messages
   - Document data requirements

4. **Metadata > Amnesia**
   - Track what you trained
   - Reproduce experiments
   - Compare model versions

5. **Error Handling > Cryptic Crashes**
   - Helpful error messages
   - Troubleshooting guidance
   - Better user experience

### When to Use This Approach

✅ **Use `2. production_ready/` for:**
- Local development and experimentation
- Team projects (shared configurations)
- Learning MLOps fundamentals
- Preparing for deployment (Module 3+)

❌ **Don't use yet for:**
- Production deployment (needs Module 3, 6, 8, 9)
- Real-time predictions (needs FastAPI)
- Large-scale training (needs cloud infrastructure)
- Model monitoring (needs drift detection)

## ➡️ Next Steps

### Want More Polish?

👉 **See `../3. advanced/`** for:
- ✅ Separate evaluation script (train ≠ evaluate)
- ✅ Data quality reports
- ✅ Query result caching (avoid repeated BigQuery costs)
- ✅ Batch prediction support
- ✅ API-ready output format

### Ready for Deployment?

👉 **Continue to Module 3** for:
- FastAPI backend serving
- Streamlit frontend
- Docker containerization
- GCP Cloud Run deployment

### Want Experiment Tracking?

👉 **Jump to Module 8** for:
- WandB integration
- Experiment comparison
- Hyperparameter tracking
- Model registry

## 🤔 Questions This Code Answers

✅ How do I change parameters without editing code? → **config.toml**
✅ How do I see what's happening during training? → **Logging**
✅ How do I know if my data is valid? → **Data validation**
✅ How do I track what models I've trained? → **Metadata files**
✅ How do I get helpful error messages? → **Error handling**

## 🔄 Comparison Table

| Feature | 1. minimal/ | 2. production_ready/ | Difference |
|---------|------------|---------------------|------------|
| Configuration | Hardcoded | TOML file | Easy experimentation |
| Logging | print() | logging module | Structured, timestamped |
| Validation | None | Assertions | Catch errors early |
| Metadata | None | JSON file | Track experiments |
| Error handling | Basic | Detailed | Helpful messages |
| Code length | 60 lines | 120 lines | 2x longer but 10x better |

**The extra 60 lines add 10x value for real-world projects.**

---

**Next:** Open `../3. advanced/README.md` for additional improvements before deployment.
