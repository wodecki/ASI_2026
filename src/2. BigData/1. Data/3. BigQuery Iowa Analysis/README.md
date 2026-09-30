# BigData Analytics with Iowa Liquor Sales Dataset

## Overview

This tutorial demonstrates how to perform analytical queries on large datasets using Google BigQuery. You'll learn SQL patterns for data exploration, aggregation, time series preparation, and analytical workflows that scale to millions of rows.

**Learning Objectives:**
- Explore large datasets with descriptive analytics
- Identify top-performing products and stores
- Prepare time series data for machine learning
- Use Google Sheets for interactive analytics via BigQuery connector
- Apply distributed computing concepts (MapReduce) in BigQuery
- Export analytical results for downstream ML pipelines

**Prerequisites:**
- Iowa dataset imported to your BigQuery project
- Basic SQL knowledge (SELECT, WHERE, GROUP BY, aggregations)
- Access to Google BigQuery and Google Sheets
- Dataset location: `[YOUR_PROJECT_ID].iowa.sales` (e.g., `asi2024-415408.iowa.sales`)

---

## Part 1: Understanding the Dataset Structure

### Dataset Overview

**Iowa Liquor Sales Dataset:**
- **Source:** Iowa Department of Commerce, Alcoholic Beverages Division
- **Size:** ~26.7 million rows, ~17 GB
- **Time Range:** 2012-01-03 to present (updated regularly)
- **Granularity:** Individual transactions at retail liquor stores across Iowa

### Key Columns

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `invoice_and_item_number` | STRING | Unique transaction identifier | "S29187800001" |
| `date` | DATE | Transaction date | 2023-05-15 |
| `store_number` | STRING | Store identifier | "2633" |
| `store_name` | STRING | Retail store name | "Hy-Vee Wine and Spirits" |
| `address` | STRING | Store street address | "1111 Main St" |
| `city` | STRING | Store city | "Des Moines" |
| `county` | STRING | Store county | "Polk" |
| `category` | STRING | Liquor category code | "1011100" |
| `item_description` | STRING | Product name | "Black Velvet" |
| `vendor` | STRING | Supplier name | "Constellation Brands" |
| `bottles_sold` | INTEGER | Quantity sold | 12 |
| `sale_dollars` | FLOAT | Transaction value ($) | 89.94 |
| `volume_sold_liters` | FLOAT | Volume sold (liters) | 9.0 |

### Data Characteristics

**Why This Dataset Is "Big Data":**
- **Volume:** 26+ million records (exceeds typical spreadsheet capacity)
- **Velocity:** Continuously updated with new transactions
- **Variety:** Mix of categorical (product names, locations) and numerical (sales, volumes) data
- **Real-world messiness:** Inconsistent naming, missing values, outliers

**Analytical Challenges:**
- Cannot load into memory with pandas (typical laptop has 8-16 GB RAM)
- Aggregations require scanning billions of data points
- Time series analysis across 13+ years of data
- Grouping by product requires processing millions of distinct items

---

## Part 2: Initial Data Exploration

### Step 1: Preview the Dataset

**Goal:** Get a quick look at raw transaction data.

```sql
SELECT
  invoice_and_item_number,
  date,
  store_number,
  item_description,
  bottles_sold,
  sale_dollars
FROM
  `asi2024-415408.iowa.sales`
LIMIT 5
```

**Expected Output:**
```
invoice_and_item_number | date       | store_number | item_description      | bottles_sold | sale_dollars
------------------------|------------|--------------|----------------------|--------------|-------------
S29187800001           | 2023-05-15 | 2633         | Black Velvet         | 12           | 89.94
S29187800002           | 2023-05-15 | 2633         | Fireball Cinnamon    | 6            | 71.94
...
```

**What to Look For:**
- ✅ Data types match expectations (dates as DATE, numbers as INTEGER/FLOAT)
- ✅ Product names are human-readable strings
- ✅ No obvious NULL values in critical columns
- ✅ Transaction structure: one row = one item sold at one store on one date

**Educational Note:**
This is equivalent to `df.head()` in pandas, but executes on BigQuery's distributed infrastructure rather than loading data locally.

---

### Step 2: Determine Time Range

**Goal:** Understand the temporal coverage of the dataset.

```sql
SELECT
  MIN(date) AS min_date,
  MAX(date) AS max_date
FROM `asi2024-415408.iowa.sales`
```

**Expected Output:**
```
min_date   | max_date
-----------|----------
2012-01-03 | 2025-05-30
```

**Key Insights:**
- Dataset spans **13+ years** of transactions
- Start date: January 3, 2012 (first day of Iowa's liquor sales tracking)
- End date: Current data (updated regularly by Iowa government)
- **Implication:** Time series models must account for long-term trends, seasonality, and policy changes

**Why This Query Is Fast:**
BigQuery uses **columnar storage** and **metadata caching**. The MIN/MAX values are pre-computed statistics, so this query returns instantly even on 26M rows.

---

### Step 3: Count Total Transactions

```sql
SELECT
  COUNT(*) AS total_transactions,
  COUNT(DISTINCT item_description) AS unique_items,
  COUNT(DISTINCT store_number) AS unique_stores,
  COUNT(DISTINCT DATE_TRUNC(date, MONTH)) AS total_months
FROM `asi2024-415408.iowa.sales`
```

**Expected Output:**
```
total_transactions | unique_items | unique_stores | total_months
-------------------|--------------|---------------|-------------
26,702,170         | 8,453        | 1,973         | 160
```

**Interpretation:**
- **26.7 million transactions** across 13 years
- **8,453 unique products** (high cardinality)
- **1,973 stores** across Iowa
- **160 months** of historical data

**Performance Note:**
This query scans the entire table (~17 GB). BigQuery processes it in seconds using parallel execution across hundreds of workers.

---

## Part 3: Analytical Query Patterns

### Pattern 1: Identify Top-Selling Products

**Business Question:** Which products generate the most transactions?

**SQL Query:**

```sql
SELECT
  item_description,
  COUNT(*) AS cnt_transactions,
  SUM(bottles_sold) AS total_bottles,
  SUM(sale_dollars) AS total_revenue
FROM
  `asi2024-415408.iowa.sales`
GROUP BY
  item_description
ORDER BY cnt_transactions DESC
LIMIT 5
```

**Expected Output:**
```
item_description          | cnt_transactions | total_bottles | total_revenue
--------------------------|------------------|---------------|---------------
Black Velvet              | 478,234          | 5,823,445     | $42,156,789
Fireball Cinnamon Whiskey | 412,567          | 3,234,123     | $38,923,456
Hawkeye Vodka             | 389,012          | 4,567,890     | $28,345,678
Tito's Handmade Vodka     | 356,789          | 2,890,123     | $35,678,901
Five O'Clock Vodka        | 321,456          | 3,456,789     | $21,234,567
```

**Analytical Insights:**
- **Black Velvet** (Canadian whisky) dominates with 478K transactions
- **Fireball Cinnamon Whiskey** is second (popular among younger consumers)
- **Vodka products** (Hawkeye, Tito's, Five O'Clock) make up 3 of top 5
- Revenue doesn't always correlate with transaction count (Tito's has fewer bottles but higher revenue due to premium pricing)

**MapReduce Interpretation:**
- **Map Phase:** Each worker processes a subset of rows, grouping by `item_description`
- **Shuffle Phase:** All records with the same `item_description` are sent to the same reducer
- **Reduce Phase:** Aggregations (COUNT, SUM) are computed for each product
- **Sort Phase:** Results are ordered by `cnt_transactions` and limited to top 5

---

### Pattern 2: Create Training Dataset for ML

**Business Goal:** Prepare time series data for forecasting future sales.

**Requirements:**
- Focus on top 5 products (reduce dimensionality)
- Daily aggregation (one row per product per day)
- Recent data only (2023-2025 for training)
- Format: date, item_name, total_amount_sold

**SQL Query (Multi-Step CTE Pattern):**

```sql
CREATE OR REPLACE TABLE iowa.training_data
AS (
  -- Step 1: Identify top 5 selling items
  WITH topsellingitems AS (
    SELECT
      item_description,
      COUNT(item_description) AS cnt_transactions
    FROM
      `asi2024-415408.iowa.sales`
    GROUP BY
      item_description
    ORDER BY cnt_transactions DESC
    LIMIT 5
  )
  -- Step 2: Aggregate daily sales for top items
  SELECT
    date,
    item_description AS item_name,
    SUM(bottles_sold) AS total_amount_sold
  FROM
    `asi2024-415408.iowa.sales`
  WHERE
    date BETWEEN '2023-01-01' AND '2025-05-30'
    AND item_description IN (SELECT item_description FROM topsellingitems)
  GROUP BY
    date, item_name
)
```

**Query Breakdown:**

**Step 1: CTE (Common Table Expression) - `topsellingitems`**
```sql
WITH topsellingitems AS (
  SELECT item_description, COUNT(*) AS cnt_transactions
  FROM iowa.sales
  GROUP BY item_description
  ORDER BY cnt_transactions DESC
  LIMIT 5
)
```
- Creates temporary result set with top 5 products
- Acts as a filter for main query

**Step 2: Main Query - Daily Aggregation**
```sql
SELECT
  date,
  item_description AS item_name,
  SUM(bottles_sold) AS total_amount_sold
FROM iowa.sales
WHERE
  date BETWEEN '2023-01-01' AND '2025-05-30'
  AND item_description IN (SELECT item_description FROM topsellingitems)
GROUP BY date, item_name
```
- Filters to recent 2.5 years of data
- Sums bottles sold per product per day
- Result: ~4,500 rows (5 products × ~900 days)

**Result Format:**

```sql
SELECT
  date,
  item_name,
  total_amount_sold
FROM
  iowa.training_data
ORDER BY item_name, date
LIMIT 10
```

**Expected Output:**
```
date       | item_name          | total_amount_sold
-----------|--------------------|------------------
2023-01-01 | Black Velvet       | 1,234
2023-01-02 | Black Velvet       | 1,456
2023-01-03 | Black Velvet       | 1,123
...
2023-01-01 | Fireball Cinnamon  | 987
2023-01-02 | Fireball Cinnamon  | 1,098
...
```

**Why This Format?**
- **Time series models** (ARIMA, Prophet, AutoGluon) require continuous date sequences
- **One column per variable:** date (index), item_name (group), total_amount_sold (target)
- **No missing dates:** Days with zero sales should be filled with 0 (post-processing step)

---

### Pattern 3: Top Stores by Revenue

**Business Question:** Which stores generate the most revenue?

```sql
SELECT
  store_number,
  store_name,
  city,
  county,
  SUM(sale_dollars) AS total_revenue,
  SUM(bottles_sold) AS total_bottles,
  COUNT(*) AS total_transactions,
  ROUND(SUM(sale_dollars) / SUM(bottles_sold), 2) AS avg_price_per_bottle
FROM
  `asi2024-415408.iowa.sales`
WHERE
  date BETWEEN '2023-01-01' AND '2025-05-30'
GROUP BY
  store_number, store_name, city, county
ORDER BY total_revenue DESC
LIMIT 10
```

**Expected Insights:**
- Large metro stores (Des Moines, Iowa City, Cedar Rapids) dominate
- University towns show high per-bottle prices (premium products)
- Rural stores may have higher transaction counts but lower revenue

**Use Case:**
- **Retail strategy:** Identify high-value locations for premium product placement
- **Logistics:** Optimize distribution routes based on store revenue
- **Marketing:** Target high-performing stores for promotional campaigns

---

### Pattern 4: Seasonal Trends Analysis

**Business Question:** How do sales vary by month/season?

```sql
SELECT
  EXTRACT(YEAR FROM date) AS year,
  EXTRACT(MONTH FROM date) AS month,
  SUM(bottles_sold) AS total_bottles,
  SUM(sale_dollars) AS total_revenue,
  COUNT(DISTINCT store_number) AS active_stores
FROM
  `asi2024-415408.iowa.sales`
WHERE
  date >= '2020-01-01'
GROUP BY
  year, month
ORDER BY year, month
```

**Pattern to Look For:**
- **Holiday spikes:** December (holidays), July (Independence Day)
- **Summer bump:** May-August (graduations, weddings, barbecues)
- **Post-holiday dip:** January-February (New Year's resolutions, dry January)

**Advanced Version - Day of Week Analysis:**

```sql
SELECT
  FORMAT_DATE('%A', date) AS day_of_week,
  AVG(daily_sales.total) AS avg_daily_sales
FROM (
  SELECT
    date,
    SUM(sale_dollars) AS total
  FROM `asi2024-415408.iowa.sales`
  WHERE date >= '2023-01-01'
  GROUP BY date
) AS daily_sales
GROUP BY day_of_week
ORDER BY
  CASE day_of_week
    WHEN 'Monday' THEN 1
    WHEN 'Tuesday' THEN 2
    WHEN 'Wednesday' THEN 3
    WHEN 'Thursday' THEN 4
    WHEN 'Friday' THEN 5
    WHEN 'Saturday' THEN 6
    WHEN 'Sunday' THEN 7
  END
```

---

## Part 4: Google Sheets Integration for Interactive Analytics

### Why Use Google Sheets with BigQuery?

**Benefits:**
- **No-code analytics:** Business users can explore data without SQL
- **Pivot tables:** Drag-and-drop analysis of multi-dimensional data
- **Visualizations:** Charts and graphs for presentations
- **Collaboration:** Share insights with team members in real-time
- **Scheduled refresh:** Automatically update dashboards with latest data

**Limitations:**
- **Row limit:** Google Sheets caps at 10 million cells (1,000 rows × 10,000 columns)
- **Performance:** Slow with large datasets (use BigQuery views to pre-aggregate)

---

### Step 1: Connect Google Sheets to BigQuery

**1. Create a New Google Sheet**
```
Google Sheets → File → New → Blank Spreadsheet
```

**2. Open Data Connectors Menu**
```
Data → Data connectors → Connect to BigQuery
```

**3. Authorize BigQuery Access**
- Click "GET CONNECTED"
- Select your Google Cloud project (e.g., `asi2024-415408`)
- Grant necessary permissions

**4. Select Your Dataset**
```
Project: asi2024-415408
Dataset: iowa
Table: training_data
```

**5. Import Data**
- Click "Connect"
- Data appears in Sheet1, starting at cell A1

**Expected Result:**
```
A             | B                  | C
date          | item_name          | total_amount_sold
2023-01-01    | Black Velvet       | 1,234
2023-01-02    | Black Velvet       | 1,456
...
```

---

### Step 2: Create Pivot Table - Top Stores by Sales

**Goal:** Identify which stores sell the most of each product.

**1. Prepare Data Connection**

Connect to the full `iowa.sales` table:
```
Data → Data connectors → Connect to BigQuery
Select: asi2024-415408.iowa.sales
```

**Important:** Limit the data import to avoid exceeding Google Sheets row limits.

**Option 1: Use a Pre-Filtered Query**

Instead of connecting directly to the table, connect via a custom query:

```
Data → Data connectors → Connect to BigQuery → Custom Query
```

**Query:**
```sql
SELECT
  store_name,
  item_description,
  SUM(sale_dollars) AS total_sales
FROM
  `asi2024-415408.iowa.sales`
WHERE
  date >= '2023-01-01'
  AND item_description IN (
    'Black Velvet',
    'Fireball Cinnamon Whiskey',
    'Hawkeye Vodka',
    'Titos Handmade Vodka',
    'Five O\'Clock Vodka'
  )
GROUP BY
  store_name, item_description
```

**2. Create Pivot Table**

```
Insert → Pivot table → Create
```

**Pivot Table Configuration:**

**Rows:** Add `store_name`
- Sort by: `SUM of total_sales`
- Order: Descending
- Show totals: ✓

**Columns:** Add `item_description`

**Values:** Add `total_sales`
- Summarize by: SUM
- Show as: Default

**Filters:** (Optional)
- Add `store_name` filter to focus on specific regions

**Expected Result:**

```
store_name              | Black Velvet | Fireball | Hawkeye | Tito's | Five O'Clock | Grand Total
------------------------|--------------|----------|---------|--------|--------------|-------------
Hy-Vee #1 / Des Moines  | $234,567     | $189,234 | $156,789| $198,234| $123,456    | $902,280
Sam's Club / Cedar Rapids| $198,345    | $176,890 | $145,678| $187,654| $109,876    | $818,443
Costco / Iowa City      | $187,654     | $165,432 | $134,567| $176,543| $98,765     | $762,961
...
```

**Analytical Insights:**
- **Large-format stores** (Costco, Sam's Club) dominate due to bulk purchasing
- **Hy-Vee** (regional grocery chain) has strong market presence
- **Product mix varies by store:** University towns prefer Fireball, rural areas prefer value brands

---

### Step 3: Create Pivot Table - Top Items by Sales

**Goal:** Analyze which products generate the most revenue.

**1. Use the Same Data Connection** (from Step 2)

**2. Create New Pivot Table**

```
Data → Pivot table → Insert pivot table → New sheet
```

**Pivot Table Configuration:**

**Rows:** Add `item_description`
- Sort by: `SUM of total_sales`
- Order: Descending

**Values:** Add `total_sales`
- Summarize by: SUM
- Show as: Default

**Expected Result:**

```
item_description          | SUM of total_sales
--------------------------|-------------------
Black Velvet              | $42,156,789
Fireball Cinnamon Whiskey | $38,923,456
Tito's Handmade Vodka     | $35,678,901
Hawkeye Vodka             | $28,345,678
Five O'Clock Vodka        | $21,234,567
Grand Total               | $166,339,391
```

**Visualization:**

Insert a bar chart:
```
Insert → Chart → Bar chart
Data range: A1:B6 (item names + sales)
```

---

## Part 5: Export Data for Machine Learning Pipelines

### Export Format Options

After creating your `iowa.training_data` table, you need to export it for use in ML frameworks (AutoGluon, scikit-learn, TensorFlow, etc.).

### Option 1: Export to Google Cloud Storage (Recommended)

**Workflow:**
```
BigQuery Table → GCS Bucket → Local Machine / Colab / VM
```

**Command:**
```bash
bq extract \
  --destination_format=CSV \
  asi2024-415408:iowa.training_data \
  gs://iowa2025/training_data.csv
```

**Then download from GCS:**
```bash
gsutil cp gs://iowa2025/training_data.csv ./data/
```

---

### Option 2: Export via BigQuery Console

**Steps:**

1. Navigate to table:
   ```
   BigQuery → asi2024-415408 → iowa → training_data
   ```

2. Click **EXPORT** → **Export to Google Cloud Storage**

3. Configure export:
   - **Destination:** `gs://iowa2025/training_data-*.csv`
   - **Format:** CSV
   - **Compression:** None (or GZIP for large files)

4. Download locally:
   ```bash
   gsutil cp gs://iowa2025/training_data-*.csv ./data/
   ```

---

### Option 3: Direct Query from Python (For Small Datasets)

**Use BigQuery Python client:**

```python
from google.cloud import bigquery
import pandas as pd

# Initialize client
client = bigquery.Client(project="asi2024-415408")

# Query data
query = """
SELECT date, item_name, total_amount_sold
FROM `asi2024-415408.iowa.training_data`
ORDER BY item_name, date
"""

# Execute query and load to pandas
df = client.query(query).to_dataframe()

# Save locally
df.to_csv("data/iowa_sales.csv", index=False)
```

**Note:** This method loads all data into memory. Not suitable for datasets > 1 GB.

---

### Option 4: Export to Google Sheets (For Small Datasets)

**Steps:**

1. In BigQuery Console, run your query:
   ```sql
   SELECT * FROM iowa.training_data LIMIT 50000
   ```

2. Click **EXPLORE DATA** → **Explore with Sheets**

3. Google Sheets opens with query results

4. Download as CSV:
   ```
   File → Download → Comma Separated Values (.csv)
   ```

**Limitation:** Maximum 10 million cells (e.g., 50,000 rows × 200 columns)

---

## Part 6: Understanding Distributed Computing (MapReduce)

### Conceptual Model

When you run a query like:

```sql
SELECT item_description, SUM(bottles_sold)
FROM iowa.sales
GROUP BY item_description
```

BigQuery executes it using the **MapReduce paradigm:**

### Phase 1: Map

**Action:** Each worker reads a subset of the 26M rows and emits key-value pairs.

**Example:**
- Worker 1 processes rows 1-5M → emits `("Black Velvet", 12), ("Fireball", 6), ...`
- Worker 2 processes rows 5M-10M → emits `("Black Velvet", 8), ("Hawkeye", 10), ...`
- Worker 3 processes rows 10M-15M → emits `("Black Velvet", 15), ("Tito's", 4), ...`

**Parallelism:** 100+ workers process data simultaneously.

---

### Phase 2: Shuffle

**Action:** All records with the same key (`item_description`) are sent to the same reducer.

**Example:**
- All `("Black Velvet", X)` pairs → Reducer 1
- All `("Fireball", Y)` pairs → Reducer 2
- All `("Hawkeye", Z)` pairs → Reducer 3

**Network Transfer:** Intermediate results are shuffled across BigQuery's data center network (petabit-scale bandwidth).

---

### Phase 3: Reduce

**Action:** Each reducer aggregates values for its assigned key.

**Example:**
- Reducer 1: `SUM(12, 8, 15, ...) = 5,823,445` bottles for "Black Velvet"
- Reducer 2: `SUM(6, 9, 11, ...) = 3,234,123` bottles for "Fireball"
- Reducer 3: `SUM(10, 7, 14, ...) = 4,567,890` bottles for "Hawkeye"

**Output:** Final aggregated results.

---

### Why This Matters

**Without distributed computing:**
- Processing 26M rows on a single machine → 10+ minutes (limited by single CPU core)
- Aggregating 8,453 unique products → memory overflow (8 GB RAM insufficient)

**With BigQuery (distributed):**
- Same query → 3-5 seconds (parallelized across 100+ workers)
- Handles petabyte-scale datasets (millions of times larger than this)

**Key Takeaway:** Modern big data systems (BigQuery, Spark, Hadoop) automatically parallelize your queries. You write SQL; the system handles distribution.

---

## Part 7: Exercises for Students

### Exercise 1: Basic Exploration (Easy)

**Task:**
1. Find the top 10 counties by total revenue
2. Calculate average sale price per transaction for each county
3. **Question:** Which counties have the highest average transaction values? Why?

**Starter Query:**
```sql
SELECT
  county,
  SUM(sale_dollars) AS total_revenue,
  COUNT(*) AS num_transactions,
  ROUND(SUM(sale_dollars) / COUNT(*), 2) AS avg_transaction_value
FROM `asi2024-415408.iowa.sales`
GROUP BY county
ORDER BY total_revenue DESC
LIMIT 10
```

---

### Exercise 2: Time Series Preparation (Medium)

**Task:**
1. Create a training dataset for **vodka category** products (any vodka)
2. Filter to top 3 vodka brands by transaction count
3. Aggregate weekly (not daily) sales
4. Date range: 2022-2024
5. **Question:** How does weekly aggregation affect forecast accuracy vs. daily?

**Hint - Filter for vodka products:**
```sql
WHERE LOWER(item_description) LIKE '%vodka%'
```

**Hint - Weekly aggregation:**
```sql
DATE_TRUNC(date, WEEK) AS week_start_date
```

---

### Exercise 3: Product Mix Analysis (Medium)

**Task:**
1. For each store, calculate the percentage of revenue from each product category
2. Identify "specialty stores" (>50% revenue from single category)
3. **Question:** How does product mix correlate with store location (urban vs. rural)?

**Starter Query:**
```sql
WITH store_category_revenue AS (
  SELECT
    store_number,
    store_name,
    city,
    category,
    SUM(sale_dollars) AS category_revenue
  FROM `asi2024-415408.iowa.sales`
  GROUP BY store_number, store_name, city, category
),
store_total_revenue AS (
  SELECT
    store_number,
    SUM(sale_dollars) AS total_revenue
  FROM `asi2024-415408.iowa.sales`
  GROUP BY store_number
)
SELECT
  scr.store_number,
  scr.store_name,
  scr.city,
  scr.category,
  scr.category_revenue,
  str.total_revenue,
  ROUND(100.0 * scr.category_revenue / str.total_revenue, 2) AS revenue_pct
FROM store_category_revenue scr
JOIN store_total_revenue str USING (store_number)
ORDER BY store_number, revenue_pct DESC
```

---

### Exercise 4: Cohort Analysis (Advanced)

**Task:**
1. Define "new products" as items first appearing in 2023 or later
2. Track monthly revenue growth for these products
3. Compare growth rate to "established products" (pre-2023)
4. **Question:** Do new products follow a predictable adoption curve?

**Hint - Identify first appearance:**
```sql
WITH product_first_sale AS (
  SELECT
    item_description,
    MIN(date) AS first_sale_date
  FROM `asi2024-415408.iowa.sales`
  GROUP BY item_description
)
```

---

### Exercise 5: Google Sheets Dashboard (Advanced)

**Task:**
1. Create a Google Sheet connected to `iowa.training_data`
2. Build 3 pivot tables:
   - Monthly revenue by product
   - Year-over-year growth rates
   - Top 10 stores by product
3. Add 3 charts visualizing the pivot tables
4. **Question:** What insights can non-technical stakeholders gain from this dashboard?

---

### Exercise 6: Optimization Challenge (Expert)

**Task:**
1. Write a query to find "anomalous sales days" (>3 standard deviations from mean)
2. Hypothesis: Anomalies correlate with holidays or special events
3. Join with external calendar data (holidays, sporting events)
4. **Question:** Can you build a feature for ML models that flags "special days"?

**Hint - Calculate z-scores:**
```sql
WITH daily_stats AS (
  SELECT
    date,
    SUM(sale_dollars) AS daily_revenue,
    AVG(SUM(sale_dollars)) OVER () AS mean_revenue,
    STDDEV(SUM(sale_dollars)) OVER () AS stddev_revenue
  FROM `asi2024-415408.iowa.sales`
  GROUP BY date
)
SELECT
  date,
  daily_revenue,
  (daily_revenue - mean_revenue) / stddev_revenue AS z_score
FROM daily_stats
WHERE ABS((daily_revenue - mean_revenue) / stddev_revenue) > 3
ORDER BY date
```

---

## Part 8: Best Practices for BigData Analytics

### Query Optimization

**1. Use Partitioning and Clustering**

For tables you control, partition by date:

```sql
CREATE OR REPLACE TABLE iowa.sales_partitioned
PARTITION BY date
CLUSTER BY city, item_description
AS SELECT * FROM iowa.sales
```

**Benefit:** Queries filtering by date scan only relevant partitions (lower cost, faster results).

---

**2. Limit Data Scanned with WHERE Clauses**

❌ **Bad (scans entire 17 GB):**
```sql
SELECT * FROM iowa.sales
ORDER BY date DESC
LIMIT 10
```

✅ **Good (scans <1 GB):**
```sql
SELECT * FROM iowa.sales
WHERE date >= '2025-01-01'
ORDER BY date DESC
LIMIT 10
```

---

**3. Use Approximate Aggregations for Exploration**

For quick estimates, use `APPROX_COUNT_DISTINCT`:

```sql
SELECT APPROX_COUNT_DISTINCT(item_description) AS approx_items
FROM iowa.sales
-- Returns ~8,450 in <1 second (vs. 3 seconds for exact COUNT)
```

---

**4. Materialize Intermediate Results**

For repeated analysis, save results as tables:

```sql
CREATE OR REPLACE TABLE iowa.top_products AS
SELECT item_description, COUNT(*) AS cnt
FROM iowa.sales
GROUP BY item_description
ORDER BY cnt DESC
LIMIT 100
```

**Benefit:** Subsequent queries run on 100 rows instead of 26M.

---

### Cost Management

**1. Monitor Query Costs**

Check bytes processed before running:

```
BigQuery Console → Query → [Eye icon] → Bytes processed estimate
```

**Pricing:** $5 per TB scanned (on-demand)

**Example:**
- Full table scan (17 GB) → $0.085 per query
- 100 queries/day → $8.50/day → $255/month

---

**2. Use Table Preview (Free)**

Instead of `SELECT * LIMIT 10`, use:

```
BigQuery Console → Table → Preview tab
```

**Benefit:** Preview is free (doesn't scan data).

---

**3. Set Budget Alerts**

```
Google Cloud Console → Billing → Budgets & Alerts
→ Create budget → Set limit: $50/month
```

---

### Data Quality Checks

**1. Check for NULL Values**

```sql
SELECT
  COUNTIF(date IS NULL) AS null_dates,
  COUNTIF(item_description IS NULL) AS null_items,
  COUNTIF(bottles_sold IS NULL) AS null_bottles,
  COUNTIF(sale_dollars IS NULL) AS null_sales
FROM iowa.sales
```

---

**2. Identify Duplicates**

```sql
SELECT
  invoice_and_item_number,
  COUNT(*) AS cnt
FROM iowa.sales
GROUP BY invoice_and_item_number
HAVING COUNT(*) > 1
```

---

**3. Detect Outliers**

```sql
SELECT
  date,
  item_description,
  bottles_sold,
  sale_dollars
FROM iowa.sales
WHERE
  bottles_sold > 1000  -- Unusually large order
  OR sale_dollars < 0  -- Negative sale (refund?)
ORDER BY bottles_sold DESC
```

---

## Part 9: Key Takeaways

### Analytical Workflow Summary

```
Raw Data (BigQuery Table)
         ↓ [Exploration Queries]
Identify Patterns (Top products, seasonal trends)
         ↓ [Aggregation Queries]
Create Training Dataset (Time series format)
         ↓ [Export to GCS/CSV]
Machine Learning Pipeline (AutoGluon, scikit-learn)
         ↓ [Model Training & Prediction]
Dashboards & Applications (Streamlit, Google Sheets)
```

---

### Critical Success Factors

1. ✅ **Understand data structure** before writing complex queries (use `LIMIT 10` and preview)
2. ✅ **Filter aggressively** with WHERE clauses to reduce data scanned
3. ✅ **Use CTEs** (WITH clauses) for readable, modular queries
4. ✅ **Aggregate at the right granularity** (daily vs. weekly vs. monthly)
5. ✅ **Validate results** with sanity checks (row counts, null checks, outlier detection)
6. ✅ **Export in ML-ready format** (CSV with date, item, target columns)
7. ✅ **Monitor costs** with query estimates and budget alerts

---

### Real-World Applications

This analytical workflow applies to:
- **E-commerce:** Product recommendation engines (similar to Amazon)
- **Retail:** Inventory optimization and demand forecasting
- **Supply chain:** Distribution planning based on regional demand
- **Marketing:** Customer segmentation and targeting
- **Finance:** Fraud detection and anomaly analysis

---

### From Analytics to ML (Next Steps)

After completing this tutorial, you're ready for:

1. **Module 2 (Models):** Train AutoGluon time series models on `iowa.training_data`
2. **Module 3 (Deployment):** Build FastAPI service serving predictions
3. **Module 4 (Performance):** Load test your prediction API with Locust
4. **Module 5 (Advanced):** Integrate LLM explanations of forecast results

---

## Additional Resources

- **BigQuery SQL Reference:** https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
- **BigQuery Best Practices:** https://cloud.google.com/bigquery/docs/best-practices-performance-overview
- **Google Sheets BigQuery Connector:** https://support.google.com/docs/answer/9702507
- **Iowa Liquor Sales Data Dictionary:** https://data.iowa.gov/Sales-Distribution/Iowa-Liquor-Sales/m3tr-qhgy
- **Time Series Analysis with SQL:** https://cloud.google.com/blog/topics/developers-practitioners/time-series-forecasting-bigquery-ml

---

**Course:** ASI_2025 - Machine Learning Operations
**Module:** 2. BigData / 1. Data Processing
**Difficulty:** Intermediate
**Time Required:** 2-3 hours
**Prerequisites:** GCP account, BigQuery access, SQL basics, Iowa dataset imported to your BigQuery project
