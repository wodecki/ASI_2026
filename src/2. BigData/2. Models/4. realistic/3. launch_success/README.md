# C. New-product success: predict first-year sales from the first 8 weeks

## 🎯 What it is for

Iowa's state wholesaler (ABD) sees about **1,100 new SKUs a year**. Most fail: of the 2023 launches, only 41% were still being ordered in 2025. A few carry the year: the best 10% of a year's launches bring in about 70% of that group's sales.

This project predicts a new SKU's **first-year (52-week) sales** from what is known **8 weeks after launch**:
- how many stores ordered it;
- how often they reordered;
- its early sales;
- the product's category, vendor, size and price.

ABD can use the prediction to decide what to restock and promote, and what to delist. The reasons for this design are in [`../ANALYSIS.md`](../ANALYSIS.md), section 5C.

This is a **tabular** problem (one row per launch), so it uses AutoGluon's `TabularPredictor` rather than the time-series predictor used in `1. minimal` and `1. demand_forecasting`.

## 📁 What's inside

```
3. launch_success/
├── 1. train.py           # query BigQuery → train on older launches → test on the latest year
├── 2. predict.py         # score launches still inside their first year
├── .env.example          # template for .env (PROJECT_ID)
├── pyproject.toml        # dependencies (AutoGluon tabular with LightGBM/CatBoost/XGBoost, BigQuery client)
└── uv.lock
```

Training creates `autogluon-iowa-launch/` (gitignored), which holds the saved model.

## 🚀 How to run

**Prerequisites:**
- A GCP project with billing enabled. The data is the public table `bigquery-public-data.iowa_liquor_sales.sales`, but the queries are billed to your project.
- Application Default Credentials: `gcloud auth application-default login`.

```bash
cp .env.example .env              # set PROJECT_ID to your GCP project ID
uv sync
uv run python "1. train.py"       # ~1-2 min (time_limit=120)
uv run python "2. predict.py"
```

- **Cost:** each script scans about **4.2 GB** in BigQuery (≈ $0.03 at on-demand rates, or free within the 1 TB monthly tier).
- **Torch warnings:** during training AutoGluon logs `Failed to import torch or check CUDA availability!` a few times. This is harmless: torch is deliberately not installed, and the tree models don't need it.

## 📊 What the code does

### `1. train.py`

1. **Query BigQuery for one row per launch.** A launch is a SKU whose first order was in 2017 or later and that has at least 8 weeks of data. Each row has:

   | Group | Columns |
   |---|---|
   | Product | `item_description`, `category`, `vendor`, `bottle_volume_ml`, `pack`, `launch_month`, `bottle_price` |
   | First 8 weeks | `stores_8w` (stores that ordered it), `store_orders_8w` (store-days with an order; this minus `stores_8w` counts reorders), `order_days_8w`, `bottles_8w`, `dollars_8w` |
   | Outcome | `dollars_52w`: sales in the first 52 weeks |

2. **Convert integer columns to floats.** BigQuery returns integers as pandas nullable `Int64`, which AutoGluon would otherwise silently drop.
3. **Keep launches whose first year is complete** (they are at least 52 weeks old). The label is `log(1 + dollars_52w)`, because first-year sales span several orders of magnitude.
4. **Split by launch date, not at random.** The last year of complete launches is the test set, and everything older is training data. This mimics real use: train on the past, predict the next launches.
5. **Train `TabularPredictor`.** It uses RMSE on the log label, preset `medium_quality` and `time_limit=120`. Neural nets are excluded because they would need torch; the tree models are LightGBM, CatBoost, XGBoost, random forest and extra trees.
6. **Print the evaluation:**
   - the leaderboard on the test launches;
   - the rank correlation with real first-year sales, compared with simply ranking launches by `dollars_8w`;
   - the share of the cohort's sales captured by the top 10% of predicted launches;
   - permutation feature importance.

### `2. predict.py`

1. Runs the same query, which gives the latest data.
2. Selects the launches **still inside their first year**, those between 8 and 52 weeks old, whose outcome is not known yet.
3. Predicts their first-year sales and prints two lists:
   - the **top 10**: stock up and support with distribution;
   - the **bottom 10**: candidates to delist or not reorder.

## 📈 Understanding the output

Results from the run on 2026-11-03 (data up to 2026-04-30). Numbers will change as the public table is updated.

```
Downloaded 8862 launches from 2017-01-03 to 2026-03-05
Train: 6917 launches up to 2024-05-01; test: 1143 later launches
                 model  score_test  score_val
0  WeightedEnsemble_L2   -0.553215  -0.596357
1             CatBoost   -0.560511  -0.600445
2        LightGBMLarge   -0.569411  -0.620437
...
Rank correlation with real first-year sales (Spearman): model 0.953, first-8-week sales 0.925
Top 10% of test launches by model: 59% of the cohort's first-year sales
Top 10% of test launches by first-8-week sales: 58% of the cohort's first-year sales
Top 10% of test launches by perfect ranking: 63% of the cohort's first-year sales
```

- **RMSE 0.553 on log sales** (printed with a minus sign: higher is better). An error of 0.553 in log space is a factor of e^0.553 ≈ 1.7, so a typical prediction is within about ×1.7 of actual first-year sales.
- **Spearman 0.953:** how well the model *orders* launches from best to worst, where 1.0 is a perfect ranking.
- **Top 10% capture:**
  - Backing the model's top 10% of launches covers 59% of the cohort's first-year sales, against 63% for a perfect ranking.
  - Be honest about this one: ranking by first-8-week sales alone already gets 58%.
  - The model's gain is in ordering the whole cohort better (Spearman 0.953 vs 0.925), not in finding the few big winners, which early sales already reveal.
- **Feature importance:** `dollars_8w` dominates (1.26), followed by `order_days_8w` (0.23), `bottles_8w`, `store_orders_8w` and `stores_8w`. Product attributes (description, category, vendor, price) add a little on top.

Sample from `2. predict.py`, scoring 802 launches between 2025-05-05 and 2026-03-05 (some columns trimmed):

```
Top 10 launches (stock up, support with distribution):
item_number      item_description                      category  launch_date  stores_8w  dollars_8w  predicted_dollars_52w
      10779 CROWN ROYAL CHOCOLATE TEMPORARY & SPECIALTY PACKAGES   2025-08-20      989.0   824880.64              1720649.0
      11356   CROWN ROYAL MARQUIS             CANADIAN WHISKIES   2025-12-02      605.0   285924.66               746288.0
      ...
Bottom 10 launches (candidates to delist or not reorder):
     978245         SWEET REVENGE  AMERICAN CORDIALS & LIQUEURS   2025-10-29        1.0      132.12                  221.0
      ...
```

## ⚠️ Limitations and next steps

- **Only the 8-week check.** The model needs 8 weeks of sales. Predicting *before* listing, from product attributes alone (the first stage in `../ANALYSIS.md`), is a separate and harder model that isn't built yet.
- **What counts as "new".** A new `item_number` is often an existing product in a new size or package, so some "launches" are really line extensions with a known track record. A product-lineage mapping would separate them.
- **The label includes the first 8 weeks.** `dollars_52w` contains `dollars_8w`, which partly explains why early sales are so predictive. Predicting only the remaining 44 weeks is a stricter alternative.
- **The newest cohort is not in the final model.** The model is trained on launches up to a year before the latest complete cohort, and the test year is not added back. Refitting on all complete launches before deployment is a small next step.
- **Thin inputs.** There is no marketing spend, shelf price or distributor push, all of which drive real launches.
