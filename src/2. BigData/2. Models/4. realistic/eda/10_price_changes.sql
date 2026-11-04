-- month-level retail price per item for top-selling items, to see how often and how much prices move
WITH m AS (
  SELECT item_number, DATE_TRUNC(date, MONTH) AS month, APPROX_QUANTILES(state_bottle_retail, 2)[OFFSET(1)] AS retail,
    SUM(bottles_sold) AS bottles, COUNT(DISTINCT store_number) AS stores
  FROM `bigquery-public-data.iowa_liquor_sales.sales` WHERE date BETWEEN '2022-01-01' AND '2025-12-31' AND bottles_sold > 0 GROUP BY 1, 2)
SELECT * FROM m WHERE item_number IN (
  SELECT item_number FROM `bigquery-public-data.iowa_liquor_sales.sales` WHERE date BETWEEN '2025-01-01' AND '2025-12-31' GROUP BY 1 ORDER BY SUM(sale_dollars) DESC LIMIT 200)
