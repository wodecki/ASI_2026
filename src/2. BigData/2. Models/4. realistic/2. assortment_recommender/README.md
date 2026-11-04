# B. Assortment-gap recommender: "stores like yours sell X"

## 🎯 What it is for

A typical Iowa liquor store orders about 150 of the ~5,000 SKUs on offer, and stores of the same type order similar ranges. This project learns those patterns from the store × SKU order history and answers two questions:

1. **For a retailer:** which SKUs do stores like mine order that I don't?
2. **For a vendor's sales rep:** which stores are most likely to start ordering my SKU?

Getting a product into more stores is the main way a spirits brand grows, so a good target list is worth money. The reasons for this design are in [`../ANALYSIS.md`](../ANALYSIS.md), section 5B.

Unlike the other two folders, this one is not AutoGluon. It is a classic recommender built with scikit-learn (matrix factorisation with `TruncatedSVD`), so it needs no torch and installs quickly.

## 📁 What's inside

```
2. assortment_recommender/
├── 1. train.py           # query BigQuery → backtest vs popularity baseline → save the model
├── 2. predict.py         # recommendations for one store and one SKU (no BigQuery needed)
├── .env.example          # template for .env (PROJECT_ID, used by 1. train.py only)
├── pyproject.toml        # dependencies (scikit-learn, scipy, BigQuery client)
└── uv.lock
```

Training creates `recommender-iowa-assortment.joblib` (gitignored). It holds the model, the store × SKU matrix and the store and SKU names.

## 🚀 How to run

**Prerequisites** (for training only):
- A GCP project with billing enabled. The data is the public table `bigquery-public-data.iowa_liquor_sales.sales`, but the query is billed to your project.
- Application Default Credentials: `gcloud auth application-default login`.

```bash
cp .env.example .env              # set PROJECT_ID to your GCP project ID
uv sync
uv run python "1. train.py"       # ~2 min, mostly downloading ~760k rows
uv run python "2. predict.py"     # instant, reads the saved model
```

- **Cost:** `1. train.py` scans about **3 GB** in BigQuery (≈ $0.02 at on-demand rates, or free within the 1 TB monthly tier). `2. predict.py` doesn't touch BigQuery at all.
- To get recommendations for another store or SKU, edit `STORE_NUMBER` and `SKU_NUMBER` at the top of `2. predict.py`.

## 📊 What the code does

### `1. train.py`

1. **Query BigQuery once** for every store × SKU pair ordered in the last 18 months (returns excluded). Each pair gets three numbers, relative to the last date in the table:

   | Column | Window | Used for |
   |---|---|---|
   | `bottles_history` | 18 to 6 months ago | Training data for the backtest model |
   | `weeks_holdout` | Last 6 months | Number of weeks the store ordered the SKU: did it start carrying it? |
   | `bottles_recent` | Last 12 months | Training data for the final model |

2. **Build a store × SKU matrix** with a 1 where the store ordered the SKU in the window. Quantities are ignored, because the question is "does the store carry it?". In a quick comparison, this binary version did slightly better than log-scaled bottle counts.
3. **Backtest.**
   - Fit `TruncatedSVD(n_components=50)` on the history window. The 50 factors are hidden "tastes" shared by stores and SKUs.
   - Score every SKU for every store, hide the SKUs the store already orders, and keep the top 10.
   - Compare with a **popularity baseline**: the SKUs most stores carry, minus the ones this store already has.
   - Grade both against reality. A hit is a SKU the store had not ordered in the history window and then ordered in **at least 2 different weeks** of the holdout, meaning it tried the SKU and reordered. SKUs launched during the holdout are left out; they belong to `3. launch_success`.
4. **Final model.** Refit the same SVD on the last 12 months and save it together with the matrix and the names.

### `2. predict.py`

1. **For a store** (default: `5102`, Wilkie Liquors, an independent store in Mount Vernon):
   - It projects the store's row onto the SVD factors.
   - It scores every SKU and hides the ones the store already orders.
   - It prints the 10 best, with the number of stores that already order each.
2. **For a SKU** (default: `88296`, Patron Silver 750 ml):
   - It scores every store for that SKU and hides the stores that already order it.
   - It prints the 10 best, with the size of each store's current range.

## 📈 Understanding the output

Results from the run on 2026-11-03 (data up to 2026-04-30). Numbers will change as the public table is updated.

```
Downloaded 761044 store x SKU pairs: 2332 stores, 5650 SKUs
17549 new store x SKU pairs in the last 6 months, in 1775 stores
Popularity baseline    precision@10 0.070   recall@10 0.130   stores with >= 1 hit 43%
Matrix factorisation   precision@10 0.101   recall@10 0.213   stores with >= 1 hit 59%
✓ Model for 2273 stores x 4927 SKUs saved to recommender-iowa-assortment.joblib
```

- **precision@10:** the share of the 10 recommendations the store actually started ordering in the next 6 months. 0.101 means about 1 in 10. That sounds low, but the model is predicting stores' own future decisions with no other information, and it is **44% better than recommending best-sellers**.
- **recall@10:** the share of a store's real new SKUs that were among its top 10, here 21% vs 13% for the baseline.
- **stores with ≥ 1 hit:** for 59% of stores, at least one of the 10 suggestions came true.

Sample from `2. predict.py`:

```
WILKIE LIQUORS orders 982 SKUs. Ten more to consider:
item_number                                 sku  score  stores_ordering
      27783               JIM BEAM APPLE 750 ml  0.866              756
      17916                 ELIJAH CRAIG 750 ml  0.850              594
      ...
PATRON SILVER 750 ml is ordered by 1185 of 2273 stores. Ten stores to pitch:
store_number                             store  score  skus_ordered
        5958                BP FUEL / WATERLOO  1.048           331
        4285 FAREWAY STORES #922 / NEW HAMPTON  1.009           347
        ...
```

`score` is the SVD's reconstructed value for that store–SKU cell, roughly "how much this cell looks like a 1". Use it to rank recommendations, not as a probability.

## ⚠️ Limitations and next steps

- **Correlation is not cause.** A store may skip a SKU because its customers don't want it, and the model can't tell.
- **Chains decide centrally.** Hy-Vee, Casey's and Fareway set ranges at head office, so for them it would make more sense to recommend per chain.
- **The saved matrix is a snapshot.** `2. predict.py` scores the last 12 months as they were at training time. Retrain to pick up new orders and new stores.
- **Simple model.** The next steps from `../ANALYSIS.md` are:
  - a baseline within each store segment (chain × size × region);
  - a LightGBM ranker with store and SKU features such as size, chain, price tier and what nearby stores sell;
  - an online test of how often recommendations are taken up.
