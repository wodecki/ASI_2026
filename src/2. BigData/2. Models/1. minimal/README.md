# 1. Minimal - Basic AutoML Time Series Forecasting

## 🎯 Learning Objectives

This is the **simplest possible** implementation of time series forecasting with AutoGluon. The goal is to:
- Understand AutoML basics (AutoGluon trains multiple models automatically)
- Learn time series prediction workflow: load data → train → predict
- Experience the **limitations** of minimal code (no logging, validation, or configuration)

## 📁 What's Inside

```
1. minimal/
├── 0. fetch_data.py      # Optional: Download data from BigQuery
├── 1. train.py           # Train AutoGluon time series model
├── 2. predict.py         # Make predictions with trained model
├── data/
│   └── iowa_sales.csv    # Pre-downloaded training data (fallback)
├── pyproject.toml        # Python dependencies
└── README.md             # This file
```

## 🚀 How to Run

### Option A: Use Pre-Downloaded Data (Faster - Recommended for First Try)

```bash
# Install dependencies
uv sync

# Train model (takes ~60 seconds)
uv run python "1. train.py"

# Make predictions
uv run python "2. predict.py"
```

### Option B: Fetch Fresh Data from BigQuery (Learn Cloud Workflow)

**Prerequisites:**
- GCP account with billing enabled
- BigQuery dataset created (see `src/2. BigData/1. Data/2. BigQuery Iowa Transfer/`)
- Application Default Credentials configured:
  ```bash
  gcloud auth application-default login
  ```

**Workflow:**
```bash
# Install dependencies
uv sync

# First set PROJECT_ID in "0. fetch_data.py" (placeholder: your-gcp-project-id)

# Download fresh data from BigQuery
uv run python "0. fetch_data.py"

# Train model
uv run python "1. train.py"

# Make predictions
uv run python "2. predict.py"
```

## 📊 What the Code Does

### `0. fetch_data.py` - Download Training Data

Downloads Iowa alcohol sales data from BigQuery:
- **Dataset:** `your-gcp-project-id.iowa.sales` (created in Module 1)
- **Products:** 5 top-selling alcohol items
- **Date range:** 2023-01-01 to 2024-05-30
- **Output:** `data/iowa_sales.csv` (~1800 rows)

### `1. train.py` - Train Forecasting Model

1. Loads Iowa sales data (5 products, daily sales)
2. Splits data: last 7 days for testing, rest for training
3. Trains multiple time series models with AutoGluon:
   - Naive baseline
   - SeasonalNaive
   - ETS (Exponential Smoothing)
   - Theta method
   - RecursiveTabular (ML-based)
   - DirectTabular (ML-based)
   - WeightedEnsemble (combines all models)
4. Saves trained model to `autogluon-iowa-daily/`
5. Plots predictions vs actual values

**Training time:** ~60 seconds on modern laptop

### `2. predict.py` - Make Future Predictions

1. Loads the trained model from `autogluon-iowa-daily/`
2. Generates 7-day forecasts for all products
3. Shows specific prediction for "BLACK VELVET" product
4. Demonstrates future forecasting (3 months ahead)

## 📈 Understanding the Output

When you run `1. train.py`, AutoGluon will show:

```
Fitting timeseries model...
Model trained in 60.23s
Best model: WeightedEnsemble
MASE score: -0.2367 (lower is better)
```

**MASE (Mean Absolute Scaled Error):**
- Measures forecast accuracy
- MASE < 1.0 = Better than naive baseline
- MASE = -0.24 means the model is excellent!

## ⚠️ Limitations of This Approach

This code is **intentionally minimal** to teach AutoML basics. In real projects, you need:

### ❌ No Configuration
- All parameters are hardcoded (project ID, dates, products, model settings)
- Changing anything requires editing the code
- **Problem:** Can't experiment with different settings easily

### ❌ No Logging
- Uses `print()` statements only
- No visibility into what's happening during long training runs
- **Problem:** Hard to debug when something goes wrong

### ❌ No Data Validation
- Assumes data is perfect (no missing values, no outliers)
- No checks for data quality
- **Problem:** Silent failures if data is corrupted

### ❌ No Error Handling
- Scripts crash with cryptic error messages
- No helpful troubleshooting guidance
- **Problem:** Frustrating debugging experience

### ❌ No Model Metadata
- Don't know when model was trained or with what data
- Can't reproduce results later
- **Problem:** Not production-ready

### ❌ No Experiment Tracking
- Can't compare different model versions
- No history of what you tried
- **Problem:** Difficult to improve iteratively

## 🧪 Try Breaking It!

To understand the limitations, try these experiments:

1. **Delete the CSV file:**
   ```bash
   rm data/iowa_sales.csv
   uv run python "1. train.py"
   ```
   ❌ Unhelpful error: `FileNotFoundError: [Errno 2] No such file or directory`

2. **Run predict before training:**
   ```bash
   uv run python "2. predict.py"
   ```
   ❌ Confusing error about missing model directory

3. **Corrupt the data:**
   - Add some missing values to `iowa_sales.csv`
   - Run training
   ❌ Fails silently or produces bad predictions

4. **Change model parameters:**
   - Want to forecast 14 days instead of 7?
   - Must edit code directly (error-prone)

## ➡️ Next Steps

**Congratulations!** You've trained your first AutoML time series model. But you've also experienced the limitations of minimal code.

### Ready to Improve?

👉 **See `../2. production_ready/`** to learn how to add:
- ✅ Configuration files (change parameters without editing code)
- ✅ Structured logging (see what's happening)
- ✅ Data validation (catch errors early)
- ✅ Model metadata (track what you trained)
- ✅ Better error messages (helpful troubleshooting)

### What About Deployment?

This module focuses on **training and prediction only**. For deployment:
- **Module 3:** FastAPI + Streamlit deployment
- **Module 6:** Docker containerization
- **Module 8:** Experiment tracking with WandB
- **Module 9:** Model monitoring and drift detection

## 🤔 Questions This Code Doesn't Answer

- How do I know if my model is actually good?
- What if I want to use different products or date ranges?
- How do I compare multiple model versions?
- What happens if the data changes over time?
- How do I deploy this to production?

👉 These questions are answered in `2. production_ready/` and `3. advanced/`

## 📚 Key Takeaways

1. **AutoML is powerful** - AutoGluon trains 7+ models automatically
2. **Minimal code works** - But only for initial experimentation
3. **Production requires more** - Logging, validation, configuration, error handling
4. **Progression matters** - Start simple, add complexity as needed

**Remember:** This is a teaching example. Real ML projects need the patterns from `2. production_ready/` and `3. advanced/`.

---

**Next:** Open `../2. production_ready/README.md` to see how to improve this code for real-world use.
