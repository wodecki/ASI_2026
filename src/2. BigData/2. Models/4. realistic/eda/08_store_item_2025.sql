WITH p AS (
  SELECT store_number, item_number, COUNT(DISTINCT DATE_TRUNC(date, WEEK(MONDAY))) AS weeks_ordered,
    COUNT(DISTINCT date) AS days_ordered, SUM(bottles_sold) AS bottles
  FROM `bigquery-public-data.iowa_liquor_sales.sales` WHERE date BETWEEN '2025-01-01' AND '2025-12-31' GROUP BY 1, 2)
SELECT COUNT(*) AS n_pairs, COUNT(DISTINCT store_number) AS n_stores, COUNT(DISTINCT item_number) AS n_items,
  AVG(weeks_ordered) AS mean_weeks, APPROX_QUANTILES(weeks_ordered, 10) AS weeks_deciles,
  COUNTIF(weeks_ordered >= 26) AS pairs_ge26_weeks, COUNTIF(weeks_ordered = 1) AS pairs_1_week,
  APPROX_QUANTILES(bottles, 10) AS bottles_deciles
FROM p
