import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

df = pd.read_csv("data/iowa_sales.csv")

# Transform the date column to timestamp
df['date'] = pd.to_datetime(df['date'])

train_data = TimeSeriesDataFrame.from_data_frame(
    df,
    id_column="item_name",
    timestamp_column="date"
)

predictor = TimeSeriesPredictor.load("autogluon-iowa-daily")
predictions = predictor.predict(train_data)

# Get "mean" for the max value of timestamp in df for item_id = "BLACK VELVET"

# Filter the predictions for 'BLACK VELVET'
black_velvet_predictions = predictions.loc['BLACK VELVET']

# Find the maximum timestamp for 'BLACK VELVET'
max_timestamp = black_velvet_predictions.index.max()
# Get the 'mean' value for the maximum timestamp
mean_value = black_velvet_predictions.loc[max_timestamp, 'mean']
print("Mean prediction for BLACK VELVET on the maximum timestamp (", max_timestamp, "):", mean_value)

# Create a df_future by shifting date in df by 3 months
df_future = df.copy()
df_future['date'] = df_future['date'] + pd.DateOffset(months=3)

future_data = TimeSeriesDataFrame.from_data_frame(
    df_future,
    id_column="item_name",
    timestamp_column="date"
)

future_predictions = predictor.predict(future_data)
future_predictions.head()
