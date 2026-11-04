import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from autogluon.tabular import TabularPredictor

# Use case C (see ../ANALYSIS.md): predict a new SKU's first-year sales from what is known 8 weeks after launch.
# Reads the public table directly - no fetch step, no CSV. Each run scans ~4.2 GB in BigQuery.

load_dotenv(override=True)
PROJECT_ID = os.getenv("PROJECT_ID")
if not PROJECT_ID or PROJECT_ID == "your-gcp-project-id":
    raise ValueError("Set PROJECT_ID in .env (copy .env.example) to the GCP project billed for the BigQuery query")

# One row per SKU first ordered since 2017 (a "launch"), with at least 8 weeks of data:
#   product attributes + adoption in the first 8 weeks (features) + sales in the first 52 weeks (outcome)
# Note: a new item_number can also be an existing product in a new size or package.
QUERY = """
WITH bounds AS (
  SELECT MAX(date) AS end_date FROM `bigquery-public-data.iowa_liquor_sales.sales`
),
lines AS (
  SELECT item_number, item_description, category_name, vendor_name, bottle_volume_ml, pack,
    state_bottle_retail, store_number, date, bottles_sold, sale_dollars,
    MIN(date) OVER (PARTITION BY item_number) AS first_date
  FROM `bigquery-public-data.iowa_liquor_sales.sales`
  WHERE bottles_sold > 0                               -- returns (RINV lines) are not demand
)
SELECT
  item_number,
  ANY_VALUE(item_description) AS item_description,
  ANY_VALUE(UPPER(TRIM(category_name))) AS category,
  ANY_VALUE(UPPER(TRIM(vendor_name))) AS vendor,
  ANY_VALUE(bottle_volume_ml) AS bottle_volume_ml,
  ANY_VALUE(pack) AS pack,
  MIN(first_date) AS launch_date,
  EXTRACT(MONTH FROM MIN(first_date)) AS launch_month,
  APPROX_QUANTILES(IF(date < DATE_ADD(first_date, INTERVAL 56 DAY), state_bottle_retail, NULL), 2)[OFFSET(1)] AS bottle_price,
  COUNT(DISTINCT IF(date < DATE_ADD(first_date, INTERVAL 56 DAY), store_number, NULL)) AS stores_8w,
  COUNT(DISTINCT IF(date < DATE_ADD(first_date, INTERVAL 56 DAY), CONCAT(store_number, '|', CAST(date AS STRING)), NULL)) AS store_orders_8w,
  COUNT(DISTINCT IF(date < DATE_ADD(first_date, INTERVAL 56 DAY), date, NULL)) AS order_days_8w,
  SUM(IF(date < DATE_ADD(first_date, INTERVAL 56 DAY), bottles_sold, 0)) AS bottles_8w,
  SUM(IF(date < DATE_ADD(first_date, INTERVAL 56 DAY), sale_dollars, 0)) AS dollars_8w,
  SUM(IF(date < DATE_ADD(first_date, INTERVAL 364 DAY), sale_dollars, 0)) AS dollars_52w,
  ANY_VALUE(end_date) AS end_date
FROM lines, bounds
GROUP BY item_number
HAVING launch_date >= '2017-01-01'                           -- earlier years miss business days
   AND launch_date <= DATE_SUB(end_date, INTERVAL 56 DAY)    -- at least 8 weeks of data
"""

print("Querying the public Iowa Liquor Sales table...")
client = bigquery.Client(project=PROJECT_ID)
df = client.query(QUERY).to_dataframe()
df["launch_date"] = pd.to_datetime(df["launch_date"])
end_date = pd.to_datetime(df["end_date"]).max()  # last date in the table
# BigQuery returns integers as pandas nullable Int64, which AutoGluon silently drops: use plain floats
int_columns = df.select_dtypes("Int64").columns
df[int_columns] = df[int_columns].astype(float)
print(f"Downloaded {len(df)} launches from {df['launch_date'].min().date()} to {df['launch_date'].max().date()}")

# Only launches whose whole first year is in the data have a known outcome (the rest are scored by 2. predict.py)
done = df[df["launch_date"] <= end_date - pd.DateOffset(days=364)].copy()
done["log_dollars_52w"] = np.log1p(done["dollars_52w"])  # first-year sales span several orders of magnitude

# Split by launch date, not at random: train on older launches, test on the latest year of launches
test_start = done["launch_date"].max() - pd.DateOffset(years=1)
train = done[done["launch_date"] <= test_start]
test = done[done["launch_date"] > test_start]
print(f"Train: {len(train)} launches up to {test_start.date()}; test: {len(test)} later launches")

FEATURES = [
    "item_description", "category", "vendor", "bottle_volume_ml", "pack", "launch_month", "bottle_price",
    "stores_8w", "store_orders_8w", "order_days_8w", "bottles_8w", "dollars_8w",
]
LABEL = "log_dollars_52w"

# Train the model
predictor = TabularPredictor(
    label=LABEL,
    path="autogluon-iowa-launch",
    eval_metric="root_mean_squared_error",  # on log sales: errors are relative, so a $1k and a $1M launch count alike
)

predictor.fit(
    train[FEATURES + [LABEL]],
    presets="medium_quality",
    time_limit=120,
    excluded_model_types=["NN_TORCH", "FASTAI"],  # neural nets need torch; tree models are enough for ~7k rows
)
# AutoGluon logs "Failed to import torch or check CUDA availability!" a few times during fit:
# harmless here - torch is not installed on purpose, and the tree models train on CPU without it.

# Score every model on the test launches (AutoGluon prints RMSE with a minus sign: higher is better)
print(predictor.leaderboard(test[FEATURES + [LABEL]])[["model", "score_test", "score_val", "fit_time_marginal"]])

# Business view: how well does the model rank launches, compared with simply ranking by sales in the first 8 weeks?
test = test.assign(predicted_dollars_52w=np.expm1(predictor.predict(test[FEATURES])))
n_top = len(test) // 10
print(f"\nRank correlation with real first-year sales (Spearman): "
      f"model {test['predicted_dollars_52w'].corr(test['dollars_52w'], method='spearman'):.3f}, "
      f"first-8-week sales {test['dollars_8w'].corr(test['dollars_52w'], method='spearman'):.3f}")
for name, column in [("model", "predicted_dollars_52w"), ("first-8-week sales", "dollars_8w"), ("perfect ranking", "dollars_52w")]:
    share = test.nlargest(n_top, column)["dollars_52w"].sum() / test["dollars_52w"].sum()
    print(f"Top 10% of test launches by {name}: {share:.0%} of the cohort's first-year sales")

# Feature importance (permutation): which signals drive the prediction
print(predictor.feature_importance(test[FEATURES + [LABEL]], silent=True)["importance"].round(3))
