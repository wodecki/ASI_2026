import os
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

# Use case A (see ../ANALYSIS.md): weekly demand forecast per SKU for ABD supply planning.
# Reads the public table directly - no fetch step, no CSV. Each run scans ~0.8 GB in BigQuery.

load_dotenv(override=True)
PROJECT_ID = os.getenv("PROJECT_ID")
if not PROJECT_ID or PROJECT_ID == "your-gcp-project-id":
    raise ValueError("Set PROJECT_ID in .env (copy .env.example) to the GCP project billed for the BigQuery query")

QUERY = """
WITH bounds AS (
  SELECT MAX(date) AS end_date FROM `bigquery-public-data.iowa_liquor_sales.sales`
),
-- SKUs ordered statewide on at least 150 days in the last year (~1,550 SKUs, ~88% of revenue)
skus AS (
  SELECT item_number
  FROM `bigquery-public-data.iowa_liquor_sales.sales`, bounds
  WHERE date > DATE_SUB(end_date, INTERVAL 1 YEAR)
  GROUP BY item_number
  HAVING COUNT(DISTINCT date) >= 150
)
SELECT
  item_number,
  DATE_TRUNC(date, WEEK(MONDAY)) AS week,
  SUM(bottles_sold) AS bottles
FROM `bigquery-public-data.iowa_liquor_sales.sales`, bounds
WHERE date >= '2017-01-02'                                              -- earlier years miss business days
  AND date < DATE_TRUNC(DATE_ADD(end_date, INTERVAL 1 DAY), WEEK(MONDAY))  -- drop the last, incomplete week
  AND bottles_sold > 0                                                  -- returns (RINV lines) are not demand
  AND item_number IN (SELECT item_number FROM skus)
GROUP BY item_number, week
"""

print("Querying the public Iowa Liquor Sales table...")
client = bigquery.Client(project=PROJECT_ID)
df = client.query(QUERY).to_dataframe()
df["week"] = pd.to_datetime(df["week"])
print(f"Downloaded {len(df)} rows: {df['item_number'].nunique()} SKUs, weeks {df['week'].min().date()} to {df['week'].max().date()}")

# A week without orders is a real zero, not a missing value:
# give every SKU a row for every week from its first order to the end of the data
weeks = pd.date_range(df["week"].min(), df["week"].max(), freq="W-MON")
grid = pd.MultiIndex.from_product([df["item_number"].unique(), weeks], names=["item_number", "week"])
df = df.set_index(["item_number", "week"]).reindex(grid, fill_value=0).reset_index()
first_week = df[df["bottles"] > 0].groupby("item_number")["week"].min()
df = df[df["week"] >= df["item_number"].map(first_week)]

data = TimeSeriesDataFrame.from_data_frame(
    df,
    id_column="item_number",
    timestamp_column="week"
)

# Hold out the last 13 weeks to compare the forecast with what really happened
train_data, test_data = data.train_test_split(prediction_length=13)

# Train the model
predictor = TimeSeriesPredictor(
    freq="W-MON",
    prediction_length=13,             # one quarter ahead: the procurement horizon
    path="autogluon-iowa-weekly",
    target="bottles",
    eval_metric="WQL",                # weighted quantile loss: big SKUs weigh more, and P10/P90 are scored too
    quantile_levels=[0.1, 0.5, 0.9],  # P90 is the stock level that covers demand in 9 weeks out of 10
)

# Unlike ../../1. minimal, the tabular models stay in: with ~1,550 series,
# a global LightGBM model learns patterns shared across SKUs.
# ETS is left out: on a few short or intermittent series it diverges (WQL in the millions).
predictor.fit(
    train_data,
    presets="medium_quality",
    time_limit=600,
    excluded_model_types=["ETS"],
)

# Score every model on the 13 held-out weeks (AutoGluon prints WQL with a minus sign: higher is better)
print(predictor.leaderboard(test_data)[["model", "score_test", "score_val", "fit_time_marginal"]])

# Make predictions for the held-out weeks
predictions = predictor.predict(train_data)

# Top of the hierarchy: statewide bottles per week, forecast vs actual
forecast = predictions.groupby(level="timestamp")["mean"].sum()
actual = test_data.groupby(level="timestamp")["bottles"].sum().loc[forecast.index]
print(pd.DataFrame({"actual": actual, "forecast": forecast.round()}))
print(f"Statewide error over the 13 held-out weeks: {(forecast - actual).abs().sum() / actual.sum():.1%} WAPE")

# Plot the predictions
import matplotlib.pyplot as plt
from datetime import datetime

# Create plots directory if it doesn't exist
os.makedirs("plots", exist_ok=True)

# Plot four well-known SKUs: Tito's 1.75 L, Black Velvet 1.75 L, Fireball 50 ml minis, Patron Silver 750 ml
predictor.plot(test_data, predictions, quantile_levels=[0.1, 0.9], max_history_length=104,
               item_ids=["38178", "11788", "65013", "88296"])

# Save the plot with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
plot_filename = f"plots/predictions_{timestamp}.png"
plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
print(f"✓ Plot saved to {plot_filename}")
plt.close()
