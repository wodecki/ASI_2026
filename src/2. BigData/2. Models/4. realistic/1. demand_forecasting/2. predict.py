import os
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

# Forecast the next 13 weeks for every SKU, starting from the latest data in the public table.
# Each run scans ~1.9 GB in BigQuery (more than training: it also reads the SKU names).

load_dotenv(override=True)
PROJECT_ID = os.getenv("PROJECT_ID")
if not PROJECT_ID or PROJECT_ID == "your-gcp-project-id":
    raise ValueError("Set PROJECT_ID in .env (copy .env.example) to the GCP project billed for the BigQuery query")

# Same query as in 1. train.py, plus a readable SKU name
QUERY = """
WITH bounds AS (
  SELECT MAX(date) AS end_date FROM `bigquery-public-data.iowa_liquor_sales.sales`
),
skus AS (
  SELECT item_number
  FROM `bigquery-public-data.iowa_liquor_sales.sales`, bounds
  WHERE date > DATE_SUB(end_date, INTERVAL 1 YEAR)
  GROUP BY item_number
  HAVING COUNT(DISTINCT date) >= 150
)
SELECT
  item_number,
  ANY_VALUE(CONCAT(item_description, ' ', CAST(bottle_volume_ml AS STRING), ' ml')) AS sku_name,
  DATE_TRUNC(date, WEEK(MONDAY)) AS week,
  SUM(bottles_sold) AS bottles
FROM `bigquery-public-data.iowa_liquor_sales.sales`, bounds
WHERE date >= '2017-01-02'
  AND date < DATE_TRUNC(DATE_ADD(end_date, INTERVAL 1 DAY), WEEK(MONDAY))
  AND bottles_sold > 0
  AND item_number IN (SELECT item_number FROM skus)
GROUP BY item_number, week
"""

print("Querying the public Iowa Liquor Sales table...")
client = bigquery.Client(project=PROJECT_ID)
df = client.query(QUERY).to_dataframe()
df["week"] = pd.to_datetime(df["week"])
sku_names = df.groupby("item_number")["sku_name"].first()
print(f"Latest complete week in the data: {df['week'].max().date()}")

# Weeks without orders are zeros (same as in 1. train.py)
weeks = pd.date_range(df["week"].min(), df["week"].max(), freq="W-MON")
grid = pd.MultiIndex.from_product([df["item_number"].unique(), weeks], names=["item_number", "week"])
df = df[["item_number", "week", "bottles"]].set_index(["item_number", "week"]).reindex(grid, fill_value=0).reset_index()
first_week = df[df["bottles"] > 0].groupby("item_number")["week"].min()
df = df[df["week"] >= df["item_number"].map(first_week)]

data = TimeSeriesDataFrame.from_data_frame(
    df,
    id_column="item_number",
    timestamp_column="week"
)

predictor = TimeSeriesPredictor.load("autogluon-iowa-weekly")
predictions = predictor.predict(data)

# Forecast for one SKU: TITOS HANDMADE VODKA 1750 ml (item 38178)
print(f"\nNext 13 weeks for {sku_names['38178']} (bottles; P10 / mean / P90):")
print(predictions.loc["38178"][["0.1", "mean", "0.9"]].round())

# Next-quarter plan for the 10 SKUs with the most expected bottles.
# Summing the weekly P90s gives a conservative upper level, not the P90 of the quarter.
plan = predictions.groupby(level="item_id").agg(expected=("mean", "sum"), conservative=("0.9", "sum")).round()
plan.insert(0, "sku", plan.index.map(sku_names))
print("\nNext 13 weeks, top 10 SKUs (bottles):")
print(plan.sort_values("expected", ascending=False).head(10))

# Top of the hierarchy: statewide bottles per week (sum of the SKU forecasts)
print("\nStatewide forecast (bottles per week, modelled SKUs):")
print(predictions.groupby(level="timestamp")["mean"].sum().round())
