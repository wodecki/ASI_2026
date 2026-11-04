import os
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD

# Use case B (see ../ANALYSIS.md): "stores like yours sell X" - recommend SKUs a store does not order yet.
# Reads the public table directly - no fetch step, no CSV. Each run scans ~3 GB in BigQuery.

load_dotenv(override=True)
PROJECT_ID = os.getenv("PROJECT_ID")
if not PROJECT_ID or PROJECT_ID == "your-gcp-project-id":
    raise ValueError("Set PROJECT_ID in .env (copy .env.example) to the GCP project billed for the BigQuery query")

# One row per store x SKU, with three time windows relative to the last date in the table:
#   bottles_history - 18 to 6 months ago: what the backtest model learns from
#   weeks_holdout   - last 6 months: in how many weeks the store ordered the SKU (did it start carrying it?)
#   bottles_recent  - last 12 months: what the final model learns from
QUERY = """
WITH bounds AS (
  SELECT MAX(date) AS end_date FROM `bigquery-public-data.iowa_liquor_sales.sales`
)
SELECT
  store_number,
  ANY_VALUE(store_name) AS store_name,
  item_number,
  ANY_VALUE(CONCAT(item_description, ' ', CAST(bottle_volume_ml AS STRING), ' ml')) AS sku_name,
  SUM(IF(date <= DATE_SUB(end_date, INTERVAL 6 MONTH), bottles_sold, 0)) AS bottles_history,
  COUNT(DISTINCT IF(date > DATE_SUB(end_date, INTERVAL 6 MONTH), DATE_TRUNC(date, WEEK(MONDAY)), NULL)) AS weeks_holdout,
  SUM(IF(date > DATE_SUB(end_date, INTERVAL 12 MONTH), bottles_sold, 0)) AS bottles_recent
FROM `bigquery-public-data.iowa_liquor_sales.sales`, bounds
WHERE date > DATE_SUB(end_date, INTERVAL 18 MONTH)
  AND bottles_sold > 0                                 -- returns (RINV lines) are not demand
GROUP BY store_number, item_number
"""

print("Querying the public Iowa Liquor Sales table...")
client = bigquery.Client(project=PROJECT_ID)
df = client.query(QUERY).to_dataframe()
print(f"Downloaded {len(df)} store x SKU pairs: {df['store_number'].nunique()} stores, {df['item_number'].nunique()} SKUs")


def carried_matrix(rows, column):
    """Store x SKU matrix with a 1 where the store ordered the SKU in the given window."""
    rows = rows[rows[column] > 0]
    stores = np.sort(rows["store_number"].unique())
    skus = np.sort(rows["item_number"].unique())
    r = pd.Index(stores).get_indexer(rows["store_number"])
    c = pd.Index(skus).get_indexer(rows["item_number"])
    return csr_matrix((np.ones(len(rows)), (r, c)), shape=(len(stores), len(skus))), stores, skus


def top_10(scores, carried):
    """The 10 highest-scoring SKUs per store, leaving out the SKUs the store already orders."""
    scores = np.asarray(scores, dtype=float).copy()
    scores[carried.nonzero()] = -np.inf
    return np.argsort(-scores, axis=1)[:, :10]


# 1) Backtest: learn from 18-6 months ago, check against what stores started ordering in the last 6 months
history, stores, skus = carried_matrix(df, "bottles_history")
svd = TruncatedSVD(n_components=50, random_state=42).fit(history)  # 50 "taste" factors shared by stores and SKUs
svd_top = top_10(svd.transform(history) @ svd.components_, history)

# Baseline: the SKUs most stores carry, which this store does not carry yet
popularity = np.asarray(history.sum(axis=0)).ravel()
popular_top = top_10(np.tile(popularity, (history.shape[0], 1)), history)

# A new SKU for a store: not ordered in the history window, then ordered in >= 2 different weeks
# of the holdout (tried and reordered). SKUs launched in the holdout are left out - that is use case C.
new = df[(df["bottles_history"] == 0) & (df["weeks_holdout"] >= 2)
         & df["store_number"].isin(stores) & df["item_number"].isin(skus)]
new_pairs = set(zip(pd.Index(stores).get_indexer(new["store_number"]), pd.Index(skus).get_indexer(new["item_number"])))
new_per_store = pd.Series([s for s, _ in new_pairs]).value_counts().sort_index()
stores_with_new, n_new = new_per_store.index, new_per_store.values
print(f"{len(new_pairs)} new store x SKU pairs in the last 6 months, in {len(stores_with_new)} stores")

for name, top in [("Popularity baseline", popular_top), ("Matrix factorisation", svd_top)]:
    hits = np.array([sum((s, c) in new_pairs for c in top[s]) for s in stores_with_new])
    print(f"{name:22s} precision@10 {hits.mean() / 10:.3f}   recall@10 {(hits / n_new).mean():.3f}   "
          f"stores with >= 1 hit {(hits > 0).mean():.0%}")

# 2) Final model: learn from the last 12 months
matrix, stores, skus = carried_matrix(df, "bottles_recent")
svd = TruncatedSVD(n_components=50, random_state=42).fit(matrix)

# Save the model, the store x SKU matrix it scores, and readable names
model = {
    "svd": svd,
    "matrix": matrix,
    "stores": stores,
    "skus": skus,
    "store_names": df.groupby("store_number")["store_name"].first(),
    "sku_names": df.groupby("item_number")["sku_name"].first(),
}
joblib.dump(model, "recommender-iowa-assortment.joblib")
print(f"✓ Model for {len(stores)} stores x {len(skus)} SKUs saved to recommender-iowa-assortment.joblib")
