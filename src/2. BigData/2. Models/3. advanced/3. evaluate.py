import logging
import pandas as pd
import json
import os
import sys
from datetime import datetime
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
import matplotlib.pyplot as plt
import numpy as np

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
test_size_days = config['training']['test_size_days']
evaluation_report_file = config['output']['evaluation_report']
metrics_to_calculate = config['evaluation'].get('metrics', ['MASE', 'RMSE', 'MAE'])
generate_plots = config['evaluation'].get('generate_plots', True)

# Load model
logger.info(f"Loading trained model from {model_path}/")
try:
    predictor = TimeSeriesPredictor.load(model_path)
    logger.info("✓ Model loaded successfully")
except Exception as e:
    logger.error(f"ERROR: Failed to load model from {model_path}/")
    logger.error("Did you run '1. train.py' first?")
    raise

# Load data
logger.info(f"Loading data from {data_file}")
if not os.path.exists(data_file):
    logger.error(f"ERROR: Data file not found: {data_file}")
    raise FileNotFoundError(f"Missing {data_file}")

df = pd.read_csv(data_file)
df[date_column] = pd.to_datetime(df[date_column])
logger.info(f"✓ Loaded {len(df)} rows")

# Set date as index
df.set_index(date_column, inplace=True)
df.sort_index(inplace=True)

# Split into train/test (same as training)
logger.info(f"Splitting data for evaluation (last {test_size_days} days for testing)...")
all_dates = df.index.unique().sort_values()
last_n_dates = all_dates[-test_size_days:]

test_df = df[df.index.isin(last_n_dates)].reset_index()
train_df = df[~df.index.isin(last_n_dates)].reset_index()

logger.info(f"  Training samples: {len(train_df)}")
logger.info(f"  Test samples: {len(test_df)}")

# Convert to TimeSeriesDataFrame
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

# Generate predictions on test data
logger.info("Generating predictions on test set...")
predictions = predictor.predict(train_data)
logger.info("✓ Predictions generated")

# Calculate evaluation metrics
logger.info("\nCalculating evaluation metrics...")

def calculate_metrics(actuals, predictions, product_name):
    """Calculate multiple evaluation metrics"""
    # Merge actuals and predictions
    merged = actuals.merge(
        predictions,
        left_index=True,
        right_index=True,
        suffixes=('_actual', '_pred')
    )

    if 'mean' in merged.columns:
        pred_col = 'mean'
    else:
        logger.warning(f"No 'mean' column found for {product_name}")
        return None

    y_true = merged[target_column]
    y_pred = merged[pred_col]

    # Remove any NaN values
    mask = ~(y_true.isna() | y_pred.isna())
    y_true = y_true[mask]
    y_pred = y_pred[mask]

    if len(y_true) == 0:
        logger.warning(f"No valid data for {product_name}")
        return None

    metrics = {}

    # RMSE (Root Mean Squared Error)
    if 'RMSE' in metrics_to_calculate:
        metrics['RMSE'] = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

    # MAE (Mean Absolute Error)
    if 'MAE' in metrics_to_calculate:
        metrics['MAE'] = float(np.mean(np.abs(y_true - y_pred)))

    # MAPE (Mean Absolute Percentage Error)
    if 'MAPE' in metrics_to_calculate:
        # Avoid division by zero
        mask_nonzero = y_true != 0
        if mask_nonzero.sum() > 0:
            metrics['MAPE'] = float(np.mean(np.abs((y_true[mask_nonzero] - y_pred[mask_nonzero]) / y_true[mask_nonzero])) * 100)
        else:
            metrics['MAPE'] = None

    # MASE (Mean Absolute Scaled Error) - AutoGluon's metric
    if 'MASE' in metrics_to_calculate:
        # Simple naive forecast baseline (last value)
        naive_error = np.mean(np.abs(y_true.diff().dropna()))
        if naive_error > 0:
            metrics['MASE'] = float(metrics['MAE'] / naive_error)
        else:
            metrics['MASE'] = None

    return metrics

# Calculate metrics for each product
logger.info("="*60)
logger.info("Evaluation Results by Product:")
logger.info("="*60)

evaluation_results = {
    "evaluated_at": datetime.now().isoformat(),
    "test_size_days": test_size_days,
    "metrics_calculated": metrics_to_calculate,
    "per_product_metrics": {},
    "overall_metrics": {}
}

all_metrics = {metric: [] for metric in metrics_to_calculate}

for product in test_df[id_column].unique():
    logger.info(f"\n{product}:")
    logger.info("-" * 60)

    # Get actuals for this product
    product_actuals = test_df[test_df[id_column] == product]
    product_actuals = product_actuals.set_index(date_column)[[target_column]]

    # Get predictions for this product
    try:
        product_predictions = predictions.loc[product]

        # Calculate metrics
        metrics = calculate_metrics(product_actuals, product_predictions, product)

        if metrics:
            for metric_name, value in metrics.items():
                if value is not None:
                    logger.info(f"  {metric_name}: {value:.4f}")
                    all_metrics[metric_name].append(value)
                else:
                    logger.info(f"  {metric_name}: N/A")

            evaluation_results["per_product_metrics"][product] = metrics
        else:
            logger.warning(f"  Could not calculate metrics")

    except KeyError:
        logger.warning(f"  Predictions not found")

# Calculate overall metrics (average across products)
logger.info("\n" + "="*60)
logger.info("Overall Metrics (averaged across products):")
logger.info("="*60)

for metric_name, values in all_metrics.items():
    if len(values) > 0:
        avg_value = np.mean(values)
        std_value = np.std(values)
        logger.info(f"{metric_name}: {avg_value:.4f} (±{std_value:.4f})")

        evaluation_results["overall_metrics"][metric_name] = {
            "mean": float(avg_value),
            "std": float(std_value),
            "min": float(np.min(values)),
            "max": float(np.max(values))
        }

logger.info("="*60)

# Interpretation guide
logger.info("\nMetric Interpretation Guide:")
logger.info("-" * 60)
if 'MASE' in metrics_to_calculate:
    logger.info("MASE (Mean Absolute Scaled Error):")
    logger.info("  < 1.0: Model is better than naive baseline ✓")
    logger.info("  = 1.0: Model is equal to naive baseline")
    logger.info("  > 1.0: Model is worse than naive baseline ✗")
if 'RMSE' in metrics_to_calculate:
    logger.info("RMSE (Root Mean Squared Error):")
    logger.info("  Lower is better (in units of target variable)")
if 'MAE' in metrics_to_calculate:
    logger.info("MAE (Mean Absolute Error):")
    logger.info("  Lower is better (in units of target variable)")
if 'MAPE' in metrics_to_calculate:
    logger.info("MAPE (Mean Absolute Percentage Error):")
    logger.info("  Lower is better (percentage)")
    logger.info("  < 10%: Excellent, 10-20%: Good, 20-50%: Acceptable, >50%: Poor")
logger.info("-" * 60)

# Save evaluation report
with open(evaluation_report_file, 'w') as f:
    json.dump(evaluation_results, f, indent=2)

logger.info(f"\n✓ Evaluation report saved to {evaluation_report_file}")

# Generate plots if configured
if generate_plots:
    logger.info("\nGenerating evaluation plots...")

    # Plot predictions vs actuals for each product
    try:
        predictor.plot(
            test_data,
            predictions,
            quantile_levels=[0.1, 0.5, 0.9],
            max_history_length=100,
            max_num_item_ids=5
        )
        logger.info("✓ Prediction plots generated")
    except Exception as e:
        logger.warning(f"Could not generate plots: {e}")

logger.info("\n" + "="*60)
logger.info("Evaluation complete!")
logger.info(f"Report saved to: {evaluation_report_file}")
logger.info("\nKey insights:")
if 'MASE' in evaluation_results.get('overall_metrics', {}):
    mase = evaluation_results['overall_metrics']['MASE']['mean']
    if mase < 1.0:
        logger.info(f"✓ Model performance is GOOD (MASE = {mase:.4f} < 1.0)")
    else:
        logger.info(f"⚠ Model needs improvement (MASE = {mase:.4f} > 1.0)")
logger.info("="*60)
