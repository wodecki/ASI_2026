import logging
import pandas as pd
import json
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
id_column = config['data']['id_column']
model_path = config['model']['path']
metadata_file = config['output']['metadata_file']

# Load model
logger.info(f"Loading trained model from {model_path}/")
try:
    predictor = TimeSeriesPredictor.load(model_path)
    logger.info("✓ Model loaded successfully")
except Exception as e:
    logger.error(f"ERROR: Failed to load model from {model_path}/")
    logger.error(f"Error details: {e}")
    logger.error("\nTroubleshooting:")
    logger.error("1. Did you run '1. train.py' first?")
    logger.error("2. Check that the model_path in config/config.toml is correct")
    logger.error("3. Verify the model directory exists and contains trained model files")
    raise

# Load and display model metadata
if os.path.exists(metadata_file):
    logger.info(f"\nLoading model metadata from {metadata_file}")
    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    logger.info("="*60)
    logger.info("Model Information:")
    logger.info(f"  Trained at: {metadata['trained_at']}")
    logger.info(f"  Training time: {metadata['training_time_seconds']} seconds")
    logger.info(f"  Best model: {metadata['model_performance']['best_model']}")
    logger.info(f"  Number of models: {metadata['model_performance']['num_models_trained']}")
    logger.info(f"  Data samples: {metadata['data_summary']['num_samples']}")
    logger.info(f"  Products: {metadata['data_summary']['num_products']}")
    logger.info("="*60 + "\n")
else:
    logger.warning(f"Metadata file not found: {metadata_file}")
    logger.warning("Model information not available")

# Load data
logger.info(f"Loading data from {data_file}")
if not os.path.exists(data_file):
    logger.error(f"ERROR: Data file not found: {data_file}")
    logger.error("Run '0. fetch_data.py' to download the data")
    raise FileNotFoundError(f"Missing {data_file}")

df = pd.read_csv(data_file)
logger.info(f"✓ Loaded {len(df)} rows")

# Transform date column
df[date_column] = pd.to_datetime(df[date_column])

# Convert to TimeSeriesDataFrame
train_data = TimeSeriesDataFrame.from_data_frame(
    df,
    id_column=id_column,
    timestamp_column=date_column
)

# Make predictions
logger.info("Generating predictions...")
predictions = predictor.predict(train_data)
logger.info(f"✓ Predictions generated for {predictions.index.nunique()} products")

# Example: Get specific prediction for BLACK VELVET
logger.info("\nExample Prediction (BLACK VELVET):")
logger.info("-" * 60)

try:
    black_velvet_predictions = predictions.loc['BLACK VELVET']
    max_timestamp = black_velvet_predictions.index.max()
    mean_value = black_velvet_predictions.loc[max_timestamp, 'mean']

    logger.info(f"Product: BLACK VELVET")
    logger.info(f"Forecast date: {max_timestamp}")
    logger.info(f"Predicted sales (mean): {mean_value:.2f}")

    # Show quantile predictions (uncertainty)
    if '0.1' in black_velvet_predictions.columns and '0.9' in black_velvet_predictions.columns:
        q10 = black_velvet_predictions.loc[max_timestamp, '0.1']
        q90 = black_velvet_predictions.loc[max_timestamp, '0.9']
        logger.info(f"Prediction interval (80%): [{q10:.2f}, {q90:.2f}]")

except KeyError:
    logger.warning("BLACK VELVET not found in predictions")

logger.info("-" * 60)

# Display all products
logger.info("\nPredictions Summary (all products):")
logger.info("-" * 60)
for product in predictions.index.unique():
    product_preds = predictions.loc[product]
    # Handle both single and multiple prediction cases
    if isinstance(product_preds, pd.Series):
        latest_pred = product_preds['mean']
    else:
        latest_pred = product_preds.iloc[-1]['mean']
    logger.info(f"  {product}: {latest_pred:.2f}")
logger.info("-" * 60)

# Future forecasting example (3 months ahead)
logger.info("\nGenerating future forecasts (3 months ahead)...")
df_future = df.copy()
df_future[date_column] = df_future[date_column] + pd.DateOffset(months=3)

future_data = TimeSeriesDataFrame.from_data_frame(
    df_future,
    id_column=id_column,
    timestamp_column=date_column
)

future_predictions = predictor.predict(future_data)
logger.info("✓ Future predictions generated")

# Show future prediction example
try:
    black_velvet_future = future_predictions.loc['BLACK VELVET']
    max_future_timestamp = black_velvet_future.index.max()
    mean_future_value = black_velvet_future.loc[max_future_timestamp, 'mean']

    logger.info(f"\nFuture Forecast Example (BLACK VELVET):")
    logger.info(f"  Future date: {max_future_timestamp}")
    logger.info(f"  Predicted sales: {mean_future_value:.2f}")
except KeyError:
    logger.warning("BLACK VELVET not found in future predictions")

logger.info("\n" + "="*60)
logger.info("Prediction complete!")
logger.info("To make predictions with different parameters:")
logger.info("1. Edit config/config.toml")
logger.info("2. Re-run this script")
logger.info("="*60)
