import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

df = pd.read_csv("data/iowa_sales.csv")
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)
df.sort_index(inplace=True)

all_dates = df.index.unique().sort_values()
last_7_dates = all_dates[-7:]

test_df = df.reset_index()
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
