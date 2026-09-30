import logging
import pandas as pd
import json
import time
import os
import sys
from datetime import datetime
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

# Import tomllib (Python 3.11+) or tomli (Python < 3.11)
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
logger.info("Loading configuration from config/config.toml")
with open("config/config.toml", "rb") as f:
    config = tomllib.load(f)

# Extract configuration
data_file = config['data']['input_file']
date_column = config['data']['date_column']
target_column = config['data']['target_column']
id_column = config['data']['id_column']
model_path = config['model']['path']
frequency = config['model']['frequency']
prediction_length = config['model']['prediction_length']
eval_metric = config['model']['eval_metric']
preset = config['model']['preset']
time_limit = config['model']['time_limit_seconds']
test_size_days = config['training']['test_size_days']

# Load data
logger.info(f"Loading data from {data_file}")
if not os.path.exists(data_file):
    logger.error(f"ERROR: Data file not found: {data_file}")
    logger.error("Did you run '0. fetch_data.py' first?")
    logger.error("Or check if the file path in config/config.toml is correct")
    raise FileNotFoundError(f"Missing {data_file}")

df = pd.read_csv(data_file)
logger.info(f"✓ Loaded {len(df)} rows")

# Data validation
logger.info("Validating data...")
assert not df[date_column].isna().any(), f"ERROR: Missing values in {date_column}"
assert not df[target_column].isna().any(), f"ERROR: Missing values in {target_column}"
assert (df[target_column] >= 0).all(), f"ERROR: Negative values found in {target_column}"
assert len(df) > 100, f"ERROR: Dataset too small ({len(df)} rows), need at least 100"

num_products = df[id_column].nunique()
logger.info(f"✓ Data validation passed")
logger.info(f"  Products: {num_products}")
logger.info(f"  Date range: {df[date_column].min()} to {df[date_column].max()}")
logger.info(f"  Total samples: {len(df)}")

# Transform date column to timestamp
df[date_column] = pd.to_datetime(df[date_column])

# Set date as index
df.set_index(date_column, inplace=True)
df.sort_index(inplace=True)

# Prepare train/test split
logger.info(f"Splitting data: holding out last {test_size_days} days for testing")
all_dates = df.index.unique().sort_values()
last_n_dates = all_dates[-test_size_days:]

test_df = df.reset_index()
train_df = df[~df.index.isin(last_n_dates)].reset_index()

logger.info(f"  Training samples: {len(train_df)}")
logger.info(f"  Test samples: {len(test_df)}")

# Convert to TimeSeriesDataFrame format
logger.info("Converting to AutoGluon TimeSeriesDataFrame format...")
train_data = TimeSeriesDataFrame.from_data_frame(
    train_df,
    id_column=id_column,
    timestamp_column=date_column
)

test_data = TimeSeriesDataFrame.from_data_frame(
    test_df,
    id_column=id_column,
    timestamp_column=date_column
)

# Train model
logger.info(f"Starting model training with preset='{preset}'")
logger.info(f"  Frequency: {frequency} (daily)")
logger.info(f"  Prediction length: {prediction_length} days")
logger.info(f"  Evaluation metric: {eval_metric}")
logger.info(f"  Time limit: {time_limit} seconds")
logger.info(f"  Model will be saved to: {model_path}/")
logger.info("\nThis may take up to 60 seconds...")

predictor = TimeSeriesPredictor(
    freq=frequency,
    prediction_length=prediction_length,
    path=model_path,
    target=target_column,
    eval_metric=eval_metric,
)

start_time = time.time()
predictor.fit(
    train_data,
    presets=preset,
    time_limit=time_limit,
    excluded_model_types=["RecursiveTabular", "DirectTabular"],
)
training_time = time.time() - start_time

logger.info(f"✓ Training completed in {training_time:.2f} seconds")

# Get model information
best_model = predictor.model_best
leaderboard = predictor.leaderboard()

logger.info(f"✓ Best model: {best_model}")
logger.info(f"✓ Models trained: {len(leaderboard)}")

# Make predictions on test data
logger.info("Generating predictions on test data...")
predictions = predictor.predict(train_data)
logger.info("✓ Predictions generated")

# Save model metadata
metadata = {
    "trained_at": datetime.now().isoformat(),
    "training_time_seconds": round(training_time, 2),
    "data_summary": {
        "num_samples": len(train_df),
        "num_products": num_products,
        "date_range": {
            "start": str(df.index.min()),
            "end": str(df.index.max())
        }
    },
    "model_config": {
        "frequency": frequency,
        "prediction_length": prediction_length,
        "eval_metric": eval_metric,
        "preset": preset,
        "time_limit_seconds": time_limit
    },
    "model_performance": {
        "best_model": best_model,
        "num_models_trained": len(leaderboard)
    },
    "leaderboard": leaderboard.to_dict('records')
}

metadata_file = config['output']['metadata_file']
with open(metadata_file, "w") as f:
    json.dump(metadata, f, indent=2)

logger.info(f"✓ Model metadata saved to {metadata_file}")

# Plot predictions
logger.info("Generating prediction plots...")
import matplotlib.pyplot as plt

# Create plots directory if it doesn't exist
os.makedirs("plots", exist_ok=True)

predictor.plot(
    test_data,
    predictions,
    quantile_levels=[0.1, 0.9],
    max_history_length=200,
    max_num_item_ids=4
)

# Save the plot with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
plot_filename = f"plots/predictions_{timestamp}.png"
plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
logger.info(f"✓ Plot saved to {plot_filename}")
plt.close()

logger.info("\n" + "="*60)
logger.info("Training complete!")
logger.info(f"Model saved to: {model_path}/")
logger.info(f"Metadata saved to: {metadata_file}")
logger.info("Next step: Run '2. predict.py' to make predictions")
logger.info("="*60)
