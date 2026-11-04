# Iowa Liquor Sales: dataset analysis and ML use cases

Source: `bigquery-public-data.iowa_liquor_sales.sales` (Google Cloud Marketplace, *Iowa Liquor Sales*), queried on 2026-11-03. Every number below comes from the queries in [`eda/`](eda/) (see [Reproducing](#reproducing)).

## Summary

- **The data records wholesale orders, not consumer sales.** Iowa is an alcohol control state: the Alcoholic Beverages Division (ABD) is the only spirits wholesaler, and each row is one line of an order a licensed retailer placed with ABD. There are 34.0M lines from 2012-01-03 to 2026-04-30, worth $5.06B, from 3,431 stores, covering 15.6k SKUs and 852 vendors.
- **Volume is shrinking while prices rise.** Liters peaked in 2021 and fell 10% by 2025. $/liter rose from 13.6 (2012) to 19.2 (2025). 2025 brought the first fall in dollar sales (−5%), and Jan–Apr 2026 is down a further 3.8% on Jan–Apr 2025. Only tequila and specialty/gift packs still grow in liters.
- **Demand is very skewed and very sparse.** 1% of SKUs bring in 33% of revenue. The store × SKU matrix is 5.5% filled. A typical store–SKU pair is ordered in only 2 weeks of the year.
- **Prices hardly move.** The state markup is exactly 1.5× cost, and retail prices change in only 2.6% of item-months. This rules out price-elasticity and promotion use cases.
- **Top 3 ML use cases:**
  1. Hierarchical demand forecasting for ABD supply planning.
  2. An assortment-gap recommender ("stores like yours sell X").
  3. Prediction of whether a new product will succeed.

  These three follow the life of a product: decide whether to **list** it, get it **placed** in the right stores, and keep it **stocked**.

## 1. What the dataset is (and is not)

| Column group | Columns | Notes |
|---|---|---|
| Order line | `invoice_and_item_number`, `date` | IDs look like `INV-` or `RINV-` followed by 11 digits; the last 5 digits are the line number. Removing them gives the invoice ID, and each invoice has exactly one store and one date (0 exceptions in 2025). `RINV` marks a return (negative quantity). |
| Store | `store_number`, `store_name`, `address`, `city`, `zip_code`, `store_location` (GEOGRAPHY), `county_number`, `county` | Gives the licensee and where it is. There are no other store attributes: no size, format, or opening hours. |
| Product | `item_number`, `item_description`, `category`, `category_name`, `vendor_number`, `vendor_name`, `pack`, `bottle_volume_ml` | `item_number` identifies a product *in one bottle size*. For example, *TITOS HANDMADE VODKA* exists as three SKUs: 1750, 1000 and 750 ml. |
| Money and volume | `state_bottle_cost`, `state_bottle_retail`, `bottles_sold`, `sale_dollars`, `volume_sold_liters`, `volume_sold_gallons` | `state_bottle_retail` is what the store pays ABD. It is not the shelf price consumers pay. |

What follows from this:

- **The demand signal is store orders.** For ABD that is exactly the demand it has to meet. For consumer demand it is only a delayed, lumpy proxy: stores order in batches, usually weekly.
- **Inventory, stock-outs, shelf prices, promotions and marketing spend are all missing.** Demand is therefore censored. If ABD ran out of a product, the data simply shows fewer orders.
- **Any join to external data has to be done by us.** That includes census population and income by county or ZIP, the holiday calendar, local events (college football, the State Fair) and weather.

## 2. Dataset profile

### Scale

| | Value |
|---|---|
| Rows (order lines) | 34,016,839 |
| Date range | 2012-01-03 to 2026-04-30 |
| Net sales / bottles / liters | $5.06B / 374.9M / 310.1M |
| Stores / SKUs / vendors (all time) | 3,431 / 15,633 / 852 |
| Active in 2025: stores / SKUs / vendors | 2,243 / 5,048 / 268 |
| Invoices in 2025 | 120.6k (≈54 per store). The median invoice has 14 lines and is worth $1,640. The 90th percentile is 46 lines and $7.5k. The largest is $763k. |

### Trend

| Year | Net sales $M | Liters M | $/liter | Active stores | Active SKUs | Invoices |
|---|---:|---:|---:|---:|---:|---:|
| 2012 | 255.2 | 18.76 | 13.61 | 1,226 | 3,146 | 53,145 |
| 2016 | 299.5 | 20.30 | 14.75 | 1,462 | 3,724 | 65,240 |
| 2019 | 349.2 | 22.30 | 15.66 | 1,748 | 4,008 | 74,717 |
| 2020 | 396.7 | 24.21 | 16.38 | 1,878 | 4,176 | 86,500 |
| 2021 | 428.1 | **24.76** | 17.29 | 1,948 | 4,472 | 100,992 |
| 2023 | 446.1 | 23.73 | 18.80 | 2,110 | 5,231 | 114,597 |
| 2024 | **447.2** | 23.31 | 19.19 | 2,162 | 5,211 | 125,180 |
| 2025 | 425.0 | 22.19 | 19.15 | 2,243 | 5,048 | 122,800 |

- Dollar sales grew 4–6% a year from 2014 to 2019. They jumped 13.6% in the COVID year 2020, slowed to 0–4% a year from 2022 to 2024, and fell 5.0% in 2025.
- The number of stores rose 83% between 2012 and 2025, so volume per store is falling.
- Each year about 160–210 stores place their first order and 80–110 place their last. 181 stores have not ordered since some point in 2025.

### Seasonality and calendar

- **Months:** sales are 20% above an average month in December and 14% above in October, as stores stock up for the holidays. They are 19% below in January and 14% below in February. (Index of each month against the yearly mean, averaged over 2016–2025.)
- **Weekdays:** Monday to Friday each account for 18–21% of sales. Saturday and Sunday together account for 3%. Weekend order days became more common after 2021: 31–56 per year, up from 1–10.
- **Daily volatility:** an average weekday in 2023–2025 brings $1.64M, with a coefficient of variation of 0.22.

### Concentration

- **SKUs:** 133 SKUs make 50% of 2025 revenue, 641 make 80%, and 1,869 make 95%. The top 1% of SKUs make 33% and the top 10% make 76%. The biggest SKUs are Tito's 1.75 L ($11.4M), Tito's 1 L, Black Velvet 1.75 L, Captain Morgan Spiced 1.75 L, Tito's 750 ml and Fireball 50 ml minis.
- **Stores:** 138 stores make 50% of 2025 revenue and 632 make 80%. The median store spent $68k and the 99th-percentile store $2.1M. The largest stores are Hy-Vee #3 / BDI and Central City 2 (both Des Moines, about $13M each).
- **Chains** (matched by store name, so approximate):

  | Chain | Stores | Share of 2025 revenue |
  |---|---:|---:|
  | Independents and other | 1,051 | 36% |
  | Hy-Vee | 193 | 30% |
  | Casey's | 552 | 8% |
  | Fareway | 120 | 6% |
  | Walmart | 60 | 5% |
  | Sam's Club | 11 | 5% |

- **Vendors:** Diageo has 20% and Sazerac 18%. The top 5 have 57%, the top 10 have 77%, and the HHI is about 950.
- **Geography:** the top 5 counties (Polk, Linn, Scott, Johnson, Black Hawk) make 48% of revenue.

### Category mix (families grouped by keywords in `category_name`)

| Family | Share 2016 | Share 2025 | $ CAGR 2016–25 | Liters CAGR 2021–25 |
|---|---:|---:|---:|---:|
| Whiskey | 36.7% | 38.3% | +4.5% | −3.2% |
| Vodka | 24.5% | 21.5% | +2.5% | −1.0% |
| Tequila / Mezcal | 5.6% | **10.4%** | **+11.3%** | **+1.6%** |
| Liqueur / Cordial | 9.9% | 9.5% | +3.5% | −4.3% |
| Rum | 12.3% | 8.0% | −1.0% | −5.7% |
| Specialty / temporary packages | 1.1% | 4.2% | +20.7% | +2.1% |
| Brandy | 4.4% | 2.9% | −1.0% | −9.5% |
| RTD / cocktails | 1.6% | 2.2% | +7.4% | −4.2% |
| Gin | 2.6% | 2.1% | +1.7% | −5.2% |

By bottle size, 750 ml takes 42% of revenue, 1.75 L 23%, 1 L 16%, 375 ml 8% and 50 ml minis 7%.

### Prices

- The markup `state_bottle_retail / state_bottle_cost` is 1.50 for every SKU (1.499–1.502 between the 1st and 99th percentiles). It is a fixed state markup.
- Between 2023 and 2025 the median SKU had **one** retail price. For 90% of SKUs the highest price was within 14% of the lowest.
- Among the top 200 SKUs, the monthly price changed in 2.6% of item-months, almost always upward (median +3.9%). There was 1 temporary price reduction in four years.

### Sparsity: what level of detail a model can work at

- **Store × SKU, 2025:** 627k pairs were ordered at least once. That is 5.5% of the 2,243 × 5,048 possible pairs. The median pair was ordered in **2 weeks** of the year. 42% of pairs were ordered in a single week, and only 1.2% in 26 weeks or more.
- **Statewide SKU, 2025** (out of 311 order days):
  - 569 SKUs were ordered on ≥250 days; they make 71% of revenue.
  - 1,555 SKUs were ordered on ≥150 days; they make 88%.
  - 2,634 SKUs were ordered on ≥50 days; they make 95%.
- **Store order cadence:** the median active store ordered on 37 days in 2025 and the 75th percentile on 52, so weekly ordering is the norm for the larger half of stores.

Conclusion: statewide **SKU × week** is a good level to forecast. Store × SKU × day is almost all zeros. At that level it is a question of *whether a store will order*, not *how much*.

### Data quality issues to handle

| Issue | Size | Handling |
|---|---|---|
| Category codes stored both as integers and as floats (`1031100` vs `1031100.0`) | 185 codes for 103 names | Normalise the code, or key on `UPPER(TRIM(category_name))` |
| Case variants in place names | 100 county names for 99 counties; 505 city names | Uppercase and map to the official lists |
| Missing `store_location` | 2.52M rows (7.4%), across 705 stores | Geocode from address/ZIP, or fill from the store's other rows |
| Missing `county` / `category` | 162k / 17k rows | Fill from the store's or SKU's other rows |
| Returns (`RINV`, negative quantities) | Present since 2022: 1.1k–3.7k lines a year, $0.2–0.6M a year | Decide on net vs gross; returns are not demand |
| Names drift over time | 2,392 SKUs with >1 description; 456 stores with >1 name; 93 vendor numbers with >1 name | Key on numbers, not names. The current `2. Models` variants filter on `item_description`, which merges bottle sizes. |
| Business days with no data in early years | 17–42 days a year in 2012–2016; ≤7 a year from 2017 | Train from 2017 onwards, or mark the gaps as missing (not zero) |
| Left-censored first year | All 1,226 stores and 3,146 SKUs appear "new" in 2012 | Ignore 2012 when counting launches or openings |
| Freshness | The BigQuery copy ends on 2026-04-30, although the table was last modified on 2026-10-25 | Check the source's update schedule before relying on the data in production |

## 3. Possible ML use cases

The users are ABD (wholesaler and regulator), retailers, vendors, and outside parties such as investors, site-selection teams and public-health researchers.

| # | Use case | Primary user → decision | ML formulation | Data fit |
|---|---|---|---|---|
| A | **SKU-level demand forecasting (hierarchical)** | ABD → purchase orders to vendors, safety stock, warehouse labour | Probabilistic forecast of SKU × week bottles, reconciled to category and state totals | High: 1.5k regular series cover 88% of revenue, with 14 years of history |
| B | **Assortment-gap recommender** | Vendor sales reps and retailers → which SKUs to add in which store | Implicit-feedback recommendation / ranking on the store × SKU matrix | High: 627k observed pairs, 5.5% filled, clear store segments |
| C | **New-product success prediction** | ABD → list or not, initial buy, delisting; vendors → launch decisions | Cold-start regression/classification (52-week sales, survival), updated after 4–8 weeks of sales | Medium–high: about 1.1k launches a year with known outcomes |
| D | State revenue forecast | Budget office → fiscal planning | Monthly aggregate time series | High, but it is the top level of A, and simple models already do well |
| E | Store-level suggested orders | Retailers → what to put on the next order | Predict which SKUs (and how many) go on a store's next order | Low: the median pair has 2 order-weeks a year, and the store's own sales and stock are unknown |
| F | Store churn / closure | Vendors, ABD → protect distribution, plan routes | Survival / classification on order cadence | Medium: 80–180 exits a year, but no reason for closing is recorded |
| G | Store segmentation | Feeds B, C and F → better targeting | Clustering on mix, size and cadence | High, but has no value on its own |
| H | Category and brand trend intelligence | Vendors → portfolio, growth bets | Trend and change-point detection, share forecasting | Medium: mostly BI; ML adds little |
| I | Order anomaly / compliance monitoring | ABD → audits (diversion, data errors) | Unsupervised anomaly detection on store × SKU volumes against peers | Low–medium: no labels, so it cannot be validated |
| J | Price elasticity / promotion optimisation | Vendors, ABD → pricing | Causal demand models | **Very low:** fixed 1.5× markup, prices change in 2.6% of item-months, no promotions recorded |
| K | White-space and new-store site selection | Chains, investors → where to open | Predict store revenue from location and demographics | Low–medium: needs census data; 7% of rows lack a location; customers cross county lines |
| L | Entity resolution / data cleaning | Data team → reliable product and store master data | Fuzzy matching of descriptions, names and categories | High, but it supports the other use cases rather than delivering value itself |
| M | Per-capita consumption monitoring | Public health → where to intervene | Small-area estimation with census data | Medium: measures where liquor is bought, not where it is drunk |

## 4. Selection

Each use case is scored 1–5 on four criteria:

- **Value (V):** size of the decision × how much ML improves on current practice. It counts double.
- **Data fit (D):** can *this* dataset carry the use case without external data?
- **Measurability (M):** is there a clean offline backtest that can be repeated?
- **Feasibility (F):** time to a first useful version.

The scores are judgement calls; the reasoning is in the last column.

| # | Use case | V×2 | D | M | F | Total | Comment |
|---|---|---:|---:|---:|---:|---:|---|
| A | Demand forecasting | 10 | 5 | 5 | 4 | **24** | Large decision, rich history, clean rolling backtest |
| B | Assortment-gap recommender | 8 | 5 | 4 | 4 | **21** | Getting into more stores is the main growth lever for a spirits brand |
| C | New-product success | 8 | 4 | 4 | 3 | **19** | About 1.1k launches a year with outcomes that vary hugely |
| D | Revenue forecast | 4 | 5 | 5 | 5 | 19 | Comes free as the top of the A hierarchy |
| F | Store churn | 6 | 4 | 3 | 4 | 17 | Useful, but less money depends on it |
| H | Trend intelligence | 6 | 4 | 3 | 4 | 17 | Mostly descriptive |
| G, L | Segmentation, entity resolution | 4 | 5 | 2–3 | 4–5 | 15–16 | Inputs to A–C |
| E | Store suggested orders | 8 | 2 | 3 | 2 | 15 | Store sales and stock are unobserved |
| I, K | Anomaly, site selection | 6 | 2–3 | 1–3 | 2–3 | 13 | Need labels or external data |
| J, M | Price elasticity, per-capita consumption | 4–6 | 1–3 | 2 | 3 | 12 | Data cannot support them |

D scores the same as C, but it is the top level of A, so it is not a separate pick. The three use cases selected are **A, B and C**.

## 5. The top 3 in detail

### A. Hierarchical demand forecasting for ABD supply planning

**Decision.** Each week, ABD decides how many units of each SKU to order from vendors and how much safety stock to keep. Daily case volume also drives warehouse staffing. The total of the hierarchy is the state's revenue forecast (use case D).

**Why this use case.** 2025 net sales were $425M, which at the 1.5× markup is about $283M of goods at cost. One week of stock is therefore worth about $5.4M at cost. *This is an illustration only:* ABD's actual stock levels and lead times are not in the data. Every week of safety stock that better forecasts let ABD drop frees roughly that much working capital. Fewer stock-outs also protect revenue during the October and December peaks, which are 14–20% above an average month.

**Formulation.**
- Target: weekly net bottles per `item_number`, statewide. Optionally split by region (county groups or delivery zones).
- Horizon: 1–13 weeks. Set it from procurement lead times.
- Output: P50 and P90 quantiles. The P90 sets safety stock.
- Hierarchy: SKU → category → vendor → state, reconciled bottom-up or with MinT.

**Why weekly.**
- Larger stores order about once a week (the median store ordered on 37 days in 2025, the 75th percentile on 52).
- 97% of revenue falls on weekdays.
- Holidays move orders from one day to another, which adds noise to daily data without changing weekly demand.

**Scope.**
- The ~1,550 SKUs ordered on ≥150 days (88% of revenue) get their own model.
- The long tail uses intermittent-demand methods (Croston/TSB) or a category forecast split down by recent shares.
- New SKUs get forecasts from use case C.

**Features.**
- Calendar: holidays, the length of the Q4 run-up.
- Product: SKU age and lifecycle stage, category, bottle size, price level.
- Announced price changes. These are rare but known in advance.
- Distribution: number of stores ordering the SKU over the last 8 weeks.
- External, if available: events and weather.

**Models**, from simplest to most complex:
1. Seasonal-naive and ETS/Theta per series.
2. A global gradient-boosted model on lags and features.
3. AutoGluon TimeSeries, as in `1.`–`3.`, including the Chronos-2 foundation model.

**Evaluation.**
- Rolling-origin backtest over 2024–2025, cutting weekly.
- Metrics: revenue-weighted WAPE and MASE at SKU level, bias, and P90 coverage.
- Business test: simulate an order-up-to policy driven by each forecast against actual orders, and compare fill rate with average stock.

**Risks.**
- Censored demand: stock-outs show up as low sales.
- New SKUs replace old ones (new size, repackaged), so products need a lineage mapping.
- Structural drift: volume is falling while prices rise, and tastes are moving toward tequila. Monitoring has to catch this.
- The BigQuery copy is about six months behind.

### B. Assortment-gap recommender ("stores like yours sell X")

**Decision.** A vendor's sales rep decides which stores to pitch which SKU. A retailer, or a chain's head office, decides what to add to its range. The same model can be run the other way: for a given SKU, rank the stores most likely to take it on.

**Why this use case.** Most sales come from a narrow range: 10% of SKUs make 76% of revenue. Yet the median store carries only 153 SKUs, and the store × SKU matrix is 5.5% filled. Stores also fall into clear groups: 552 Casey's convenience stores, 193 Hy-Vee supermarkets and 1,051 independents order very differently. That is the pattern collaborative filtering exploits: the store's peers sell a product that the store itself does not stock.

**Formulation.**
- Input: a store × SKU matrix of trailing 12-month bottles or dollars, treated as implicit feedback.
- Label: a store–SKU pair the store had never ordered before, which it orders in the next quarter **and reorders at least twice**. Requiring reorders filters out one-off trials.
- Output: a ranked top-N list per store.
- SKUs launched inside the label window are left out; they belong to use case C.

**Models.**
- Baseline: the best-selling SKUs within the store's segment (chain × size band × region) that the store does not carry yet.
- Then: item-kNN, ALS matrix factorisation, and a LightGBM ranker. Ranker features include store size, chain, county, range depth, category, bottle size, price tier, how fast the SKU is spreading, and what nearby stores sell.

**Evaluation.**
- Temporal holdout: train on data to 2024-12-31 and label on 2025 H1.
- Metrics: precision@10, recall@20 and NDCG, plus "revenue captured": the 2025 revenue of the recommended pairs that were actually taken up.
- Online: the share of recommendations reps or retailers act on, in an A/B test.

**Risks.**
- Correlation is not cause: a store may skip an SKU because its customers don't want it.
- Chains decide their range at head office, so recommendations for chains should be made at chain level.
- A new SKU can take sales from existing ones.
- A recommender run by one vendor will lean toward that vendor's products.

### C. New-product success prediction

**Decision.** ABD decides which new SKUs to list, how much to buy at launch, and when to delist. Vendors decide whether to launch at all and how much stock to allocate to Iowa.

**Why this use case.** ABD sees 1,000–1,200 new SKUs every year (1,209 in 2023). Of the SKUs launched in 2023, only **41% (495) were still being ordered in 2025**. Their median lifetime sales were $6.4k, and the best 10% took 70% of the whole 2023 cohort's revenue. Most launches fail, and a few carry the year, so ranking launches early is valuable. SKUs launched in 2024–2025 already make 8.8% of 2025 revenue. Gift and specialty packs (+21% a year since 2016) are an important and predictable subgroup, launched seasonally with a short life.

**Formulation.** Two stages:

1. **At listing**, before any sales:
   - Predict 52-week sales (regression on log sales) and whether the SKU survives a year (classification).
   - Inputs: category; vendor and the vendor's launch record; bottle size; price compared with its category; words in the description (flavour, "mini", "gift", "RTD"); whether it extends an existing brand, linked to that brand's history; launch month.
2. **Early read**, after 4–8 weeks:
   - Add adoption features: how many stores ordered, what kinds of stores, the reorder rate, and how fast it is spreading. These update the forecast in a Bass-diffusion-like way.

**Models.**
- Gradient boosting on attributes plus text embeddings of `item_description`.
- An "analog" k-nearest-neighbours baseline that predicts from the most similar past launches. Planners find it easy to interpret.

**Evaluation.**
- Split by launch cohort: train on 2017–2022, validate on 2023, test on 2024.
- Metrics: Spearman correlation between predicted and actual 52-week sales; AUC for survival; WAPE on the top quartile.
- Decision curve: how much cohort revenue would be kept by listing or stocking only the top-k% of predictions.

**Risks.**
- A "new `item_number`" is often an existing product in a new size or package. 2,392 SKUs have more than one description, so products need a lineage mapping.
- Inputs are thin: no marketing spend, shelf price or distributor push.
- Some categories have few launches.

## 6. What this means for `4. realistic`

`1. minimal` to `3. advanced` forecast five hand-picked `item_description`s (which merge bottle sizes) as statewide daily series. Use case A is the realistic next step. It uses the same AutoGluon tooling, but:

- it is keyed on `item_number` and covers about 1,500 series;
- it forecasts weekly, with quantiles and hierarchical reconciliation;
- it handles returns and the gaps in early years;
- it is judged by rolling backtests and a simulated inventory policy.

## 7. Code

Each use case has its own folder and `uv` project, with scripts in the style of `1. minimal`. `1. train.py` queries the public table directly (there is no fetch step and no CSV), trains, backtests and saves the model. `2. predict.py` loads the model and produces recommendations or forecasts.

| Folder | Model | Backtest (run on 2026-11-03, data to 2026-04-30) |
|---|---|---|
| [`1. demand_forecasting`](1.%20demand_forecasting/) | AutoGluon `TimeSeriesPredictor`: 1,543 SKUs, weekly, 13 weeks ahead, P10/P50/P90 | On the last 13 weeks: Chronos2 WQL 0.161 vs 0.390 for seasonal naive. Statewide total (sum of SKU forecasts): 4.3% WAPE. Training takes about 100 s. |
| [`2. assortment_recommender`](2.%20assortment_recommender/) | Truncated SVD (50 factors) on the store × SKU "orders it" matrix | Trained on months 18–6 before the end of the data and tested on the last 6 (17.5k new store × SKU pairs). Precision@10: 0.101 vs 0.070 for the popularity baseline. Recall@10: 0.213 vs 0.130. |
| [`3. launch_success`](3.%20launch_success/) | AutoGluon `TabularPredictor` on 8-week adoption features and product attributes, predicting log first-year sales | Trained on 6.9k launches from 2017 to 2024-05 and tested on the 1.1k after. Spearman 0.953 vs 0.925 for ranking by first-8-week sales. The top 10% of launches hold 59% of the cohort's sales by the model's ranking, 58% by the baseline's and 63% under a perfect ranking. |

These are first versions and simpler than section 5:
- A has no regional split and no reconciliation: the statewide total is the sum of SKU forecasts.
- B uses neither the segment baseline nor the LightGBM ranker. Its label is "ordered in ≥2 weeks of the holdout".
- C implements only the 8-week early read, not the before-listing model. Early sales already rank launches well, so the model adds only a little over that simple rule.

```bash
cd "1. demand_forecasting"            # or "2. assortment_recommender", "3. launch_success"
cp .env.example .env                  # set PROJECT_ID: the GCP project billed for the queries
uv sync
uv run python "1. train.py"
uv run python "2. predict.py"
```

BigQuery scans per run:

| Folder | `1. train.py` | `2. predict.py` |
|---|---|---|
| `1. demand_forecasting` | 0.8 GB | 1.9 GB |
| `2. assortment_recommender` | 3.0 GB | none (it reads the saved model) |
| `3. launch_success` | 4.2 GB | 4.2 GB |

## Reproducing

The queries are in [`eda/`](eda/), and each one reads the public table directly. Run them from this directory with the project you want billed:

```bash
bq query --use_legacy_sql=false --project_id="$PROJECT_ID" --format=prettyjson < "eda/01_overview.sql"
```

The table has no partitioning or clustering, so every query scans the full width of the columns it reads. All ten together scan about 25 GB (`--dry_run` shows the figure per query). Queries 08 and 09 return arrays, so use `--format=prettyjson` for them rather than CSV. Shares, Pareto counts and growth rates were computed from the query outputs in pandas.
