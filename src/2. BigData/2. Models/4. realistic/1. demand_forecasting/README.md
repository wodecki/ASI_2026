# A. Demand forecasting: weekly SKU forecasts for supply planning

## 🎯 What it is for

The Iowa Alcoholic Beverages Division (ABD) is the only spirits wholesaler in Iowa. Every week it has to decide how many bottles of each product (SKU) to order from vendors and how much safety stock to keep. This project forecasts the next **13 weeks** of orders for each of about **1,550 SKUs**, which together account for 88% of revenue. Each forecast comes with a range:

- **P50** is the expected demand.
- **P90** is a stock level that covers demand in 9 weeks out of 10.

Adding up the SKU forecasts gives a statewide forecast.

This is the realistic version of the forecast in `1. minimal` to `3. advanced`:

| | `1. minimal` | `1. demand_forecasting` |
|---|---|---|
| Series | 5 hand-picked product names (bottle sizes merged) | ~1,550 SKUs (`item_number`), chosen by a rule |
| Frequency, horizon | Daily, 7 days | Weekly, 13 weeks |
| Data | CSV fetched by a separate script | Queried live from the public BigQuery table |
| Output | Point forecast + plot | P10/P50/P90 forecasts, a backtest leaderboard and statewide accuracy |

The reasons behind these choices are in [`../ANALYSIS.md`](../ANALYSIS.md), section 5A. For example, the forecast is weekly because stores order about once a week, and at store × SKU × day level the data is almost all zeros.

## 📁 What's inside

```
1. demand_forecasting/
├── 1. train.py           # query BigQuery → backtest → save the model → plot
├── 2. predict.py         # query the latest data → forecast the next 13 weeks
├── .env.example          # template for .env (PROJECT_ID)
├── pyproject.toml        # dependencies (AutoGluon time series, BigQuery client)
└── uv.lock
```

Training creates the following; both are gitignored:

- `autogluon-iowa-weekly/`: the saved model.
- `plots/`: the forecast plot.

## 🚀 How to run

**Prerequisites:**
- A GCP project with billing enabled. The data is the public table `bigquery-public-data.iowa_liquor_sales.sales`, but the queries are billed to your project.
- Application Default Credentials: `gcloud auth application-default login`.

```bash
cp .env.example .env              # set PROJECT_ID to your GCP project ID
uv sync
uv run python "1. train.py"       # ~1-2 min to download, ~100 s to train
uv run python "2. predict.py"
```

| Script | BigQuery scan per run | Cost (on-demand) |
|---|---|---|
| `1. train.py` | ~0.8 GB | well under $0.01 |
| `2. predict.py` | ~1.9 GB (it also reads the SKU names) | about $0.01 |

Both fit easily in the free tier (1 TB a month). If `PROJECT_ID` is missing, both scripts stop with an error saying what to set.

The Chronos2 and Toto2 foundation models download their weights from Hugging Face on first use. The warning about unauthenticated Hugging Face requests is harmless.

## 📊 What the code does

### `1. train.py`

1. **Query BigQuery for weekly bottles per SKU.**
   - SKUs: those ordered statewide on at least 150 days in the last year.
   - History: weekly totals since 2017. Earlier years are skipped because they are missing business days.
   - Returns (negative `RINV` lines) are excluded because they are not demand.
   - The last, incomplete week is dropped.
2. **Fill in the zeros.** A week without orders is a real zero, not a missing value. Each SKU gets a row for every week from its first order to the end of the data.
3. **Hold out the last 13 weeks** with `train_test_split(prediction_length=13)` to compare the forecast with what really happened.
4. **Train `TimeSeriesPredictor`** with these settings:
   - `freq="W-MON"`, `prediction_length=13`;
   - `eval_metric="WQL"`, `quantile_levels=[0.1, 0.5, 0.9]`;
   - preset `medium_quality`, `time_limit=600`.

   Two settings differ from `1. minimal`:
   - The **tabular models stay in**. With ~1,550 series, a global LightGBM model (`DirectTabular`) learns patterns shared across SKUs.
   - **ETS is left out**, because it diverges on a few short or intermittent series.
5. **Print the backtest:** the leaderboard on the held-out weeks, and the statewide weekly total, forecast vs actual.
6. **Save a plot** of four well-known SKUs to `plots/predictions_<timestamp>.png`: Tito's 1.75 L, Black Velvet 1.75 L, Fireball 50 ml minis and Patron Silver 750 ml.

### `2. predict.py`

1. Runs the same query (plus a readable SKU name) to get the latest data.
2. Loads `autogluon-iowa-weekly/` and forecasts the 13 weeks after the last complete week.
3. Prints three tables:
   - the weekly P10 / mean / P90 for **Tito's Handmade Vodka 1.75 L** (`38178`);
   - a **next-quarter plan for the top 10 SKUs**: expected bottles (sum of the weekly means) and a conservative level (sum of the weekly P90s). The sum of weekly P90s is higher than the true P90 of the quarter, hence "conservative";
   - the **statewide weekly forecast**, the sum over all modelled SKUs.

## 📈 Understanding the output

Results from the run on 2026-11-03 (data up to 2026-04-30). Numbers will change as the public table is updated.

```
Downloaded 582024 rows: 1543 SKUs, weeks 2017-01-02 to 2026-04-20
Training complete. Models trained: ['SeasonalNaive', 'RecursiveTabular', 'DirectTabular', 'Theta', 'Chronos2', 'Toto2', 'WeightedEnsemble']

              model  score_test  score_val
0          Chronos2   -0.160853  -0.160612
1  WeightedEnsemble   -0.161698  -0.159215
2             Toto2   -0.169373  -0.171690
3     DirectTabular   -0.193831  -0.180480
4             Theta   -0.211738  -0.212036
5  RecursiveTabular   -0.289638  -0.279824
6     SeasonalNaive   -0.390025  -0.375634

Statewide error over the 13 held-out weeks: 4.3% WAPE
```

- **WQL (weighted quantile loss)** measures the P10, P50 and P90 forecasts together, scaled by sales volume, so big SKUs count more. Lower is better.
  - AutoGluon prints it with a minus sign so that higher is better. The `-0.161` for Chronos2 means WQL = 0.161.
  - That is **59% lower than the seasonal-naive baseline** (0.390).
- **`score_val`** comes from AutoGluon's internal validation window and **`score_test`** from the 13 held-out weeks. Their values are close, so the validation score is a fair guide.
- **WeightedEnsemble** mixes the best models (Chronos2 0.76, DirectTabular 0.12 and Toto2 0.12 in this run). It is the model `predict()` uses by default.
- **Statewide WAPE of 4.3%:** summed over all SKUs, the weekly forecast was on average 4.3% away from actual orders. Errors on individual SKUs are much larger, because a single store's bulk order can triple a SKU's week. You can see this in the Tito's 1.75 L plot.

## ⚠️ Limitations and next steps

- **No reconciliation or regional split.** The statewide forecast is a plain sum of SKU forecasts, and there is no county or warehouse-zone level yet.
- **Long tail not modelled.** SKUs ordered on fewer than 150 days a year (~12% of revenue) are left out. They need intermittent-demand methods or a category-level forecast.
- **Censored demand.** When ABD runs out of stock, orders look lower than real demand, and the model learns that.
- **Product lineage.** When a product is relaunched under a new `item_number` (new size or packaging), it starts as a new, short series.
- **Data freshness.** The public BigQuery copy currently ends on 2026-04-30, so the "next 13 weeks" forecast starts at the end of April 2026, not today.
- **Business test missing.** The next step is to simulate an order-up-to inventory policy driven by the P90 forecasts and compare fill rate with stock held. See `../ANALYSIS.md`, section 5A.
