import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

# Read the dataset
df = pd.read_csv("data/iowa_sales.csv")
df.head()

# Transform the date column to timestamp
df['date'] = pd.to_datetime(df['date'])

# Set 'date' as the index of the DataFrame
df.set_index('date', inplace=True)
df.sort_index(inplace=True)

# Prepare the train and test datasets
# First, let's determine the exact dates we have at the end of the dataset
all_dates = df.index.unique().sort_values()  # Get all unique dates sorted
last_7_dates = all_dates[-7:]  # Take the last 7 unique dates

# Now set up the train and test datasets accordingly
test_df = df.reset_index()  # train_df + extra 7 days
train_df = df[~df.index.isin(last_7_dates)].reset_index()

train_data = TimeSeriesDataFrame.from_data_frame(
    train_df,
    id_column="item_name",
    timestamp_column="date"
)

test_data = TimeSeriesDataFrame.from_data_frame(
    test_df,
    id_column="item_name",
    timestamp_column="date"
)

# Train the model
predictor = TimeSeriesPredictor(
    freq="D",
    prediction_length=7,
    path="autogluon-iowa-daily",
    target="total_amount_sold",
    eval_metric="MASE",
)

predictor.fit(
    train_data,
    presets="medium_quality",
    time_limit=60,
    excluded_model_types=["RecursiveTabular", "DirectTabular"],
)

# Make predictions
predictions = predictor.predict(train_data)
predictions.head()

# Plot the predictions
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Create plots directory if it doesn't exist
os.makedirs("plots", exist_ok=True)

# Plot 4 randomly chosen time series and the respective forecasts
predictor.plot(test_data, predictions, quantile_levels=[0.1, 0.9], max_history_length=200, max_num_item_ids=4)

# Save the plot with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
plot_filename = f"plots/predictions_{timestamp}.png"
plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved to {plot_filename}")
plt.close()
