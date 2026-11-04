import joblib
import numpy as np
import pandas as pd

# Recommend from the saved model - no BigQuery needed: the model keeps the store x SKU matrix it learned from.
model = joblib.load("recommender-iowa-assortment.joblib")
svd, matrix = model["svd"], model["matrix"]
stores, skus = pd.Index(model["stores"]), pd.Index(model["skus"])

# 1) For a retailer: SKUs that stores like this one order, but this one does not (yet)
STORE_NUMBER = "5102"  # WILKIE LIQUORS / MOUNT VERNON, an independent liquor store

row = stores.get_loc(STORE_NUMBER)
scores = (svd.transform(matrix[row]) @ svd.components_).ravel()
scores[matrix[row].indices] = -np.inf  # leave out what the store already orders
top = np.argsort(-scores)[:10]

print(f"{model['store_names'][STORE_NUMBER]} orders {matrix[row].nnz} SKUs. Ten more to consider:")
print(pd.DataFrame({
    "item_number": skus[top],
    "sku": model["sku_names"][skus[top]].values,
    "score": scores[top].round(3),
    "stores_ordering": np.asarray(matrix[:, top].sum(axis=0)).ravel().astype(int),
}).to_string(index=False))

# 2) For a vendor's sales rep: stores most likely to take a SKU they do not order yet
SKU_NUMBER = "88296"  # PATRON SILVER 750 ml

col = skus.get_loc(SKU_NUMBER)
store_scores = svd.transform(matrix) @ svd.components_[:, col]
store_scores[matrix[:, col].nonzero()[0]] = -np.inf  # leave out stores that already order it
top_stores = np.argsort(-store_scores)[:10]

print(f"\n{model['sku_names'][SKU_NUMBER]} is ordered by {matrix[:, col].nnz} of {len(stores)} stores. Ten stores to pitch:")
print(pd.DataFrame({
    "store_number": stores[top_stores],
    "store": model["store_names"][stores[top_stores]].values,
    "score": store_scores[top_stores].round(3),
    "skus_ordered": matrix[top_stores].getnnz(axis=1),
}).to_string(index=False))
