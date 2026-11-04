import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from autogluon.tabular import TabularPredictor

# Score the latest launches: SKUs first ordered 8 to 52 weeks ago, whose first year is not over yet.
# Each run scans ~4.2 GB in BigQuery.

load_dotenv(override=True)
PROJECT_ID = os.getenv("PROJECT_ID")
if not PROJECT_ID or PROJECT_ID == "your-gcp-project-id":
    raise ValueError("Set PROJECT_ID in .env (copy .env.example) to the GCP project billed for the BigQuery query")

# Same query as in 1. train.py
QUERY = """
WITH bounds AS (
  SELECT MAX(date) AS end_date FROM `bigquery-public-data.iowa_liquor_sales.sales`
),
lines AS (
  SELECT item_number, item_description, category_name, vendor_name, bottle_volume_ml, pack,
    state_bottle_retail, store_number, date, bottles_sold, sale_dollars,
    MIN(date) OVER (PARTITION BY item_number) AS first_date
  FROM `bigquery-public-data.iowa_liquor_sales.sales`
  WHERE bottles_sold > 0
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
HAVING launch_date >= '2017-01-01'
   AND launch_date <= DATE_SUB(end_date, INTERVAL 56 DAY)
"""

print("Querying the public Iowa Liquor Sales table...")
client = bigquery.Client(project=PROJECT_ID)
df = client.query(QUERY).to_dataframe()
df["launch_date"] = pd.to_datetime(df["launch_date"])
end_date = pd.to_datetime(df["end_date"]).max()  # last date in the table
# BigQuery returns integers as pandas nullable Int64, which AutoGluon silently drops: use plain floats
int_columns = df.select_dtypes("Int64").columns
df[int_columns] = df[int_columns].astype(float)

# Launches still inside their first year: the outcome is not known yet
new = df[df["launch_date"] > end_date - pd.DateOffset(days=364)].copy()
print(f"{len(new)} launches between {new['launch_date'].min().date()} and {new['launch_date'].max().date()} to score")

predictor = TabularPredictor.load("autogluon-iowa-launch")
new["predicted_dollars_52w"] = np.expm1(predictor.predict(new[predictor.features()])).round()

columns = ["item_number", "item_description", "category", "bottle_volume_ml", "launch_date", "stores_8w", "dollars_8w", "predicted_dollars_52w"]
new = new.sort_values("predicted_dollars_52w", ascending=False)
print("\nTop 10 launches (stock up, support with distribution):")
print(new[columns].head(10).to_string(index=False))
print("\nBottom 10 launches (candidates to delist or not reorder):")
print(new[columns].tail(10).to_string(index=False))
