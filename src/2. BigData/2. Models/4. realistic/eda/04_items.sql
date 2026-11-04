SELECT item_number, ANY_VALUE(item_description) AS item_description, COUNT(DISTINCT item_description) AS n_desc,
  ANY_VALUE(UPPER(TRIM(category_name))) AS category_name, ANY_VALUE(vendor_name) AS vendor_name,
  ANY_VALUE(bottle_volume_ml) AS bottle_volume_ml, MIN(date) AS first_date, MAX(date) AS last_date,
  SUM(sale_dollars) AS sales_total, SUM(IF(EXTRACT(YEAR FROM date)=2025, sale_dollars, 0)) AS sales_2025,
  SUM(IF(EXTRACT(YEAR FROM date)=2025, bottles_sold, 0)) AS bottles_2025,
  COUNT(DISTINCT IF(EXTRACT(YEAR FROM date)=2025, store_number, NULL)) AS stores_2025,
  COUNT(DISTINCT IF(EXTRACT(YEAR FROM date)=2025, date, NULL)) AS order_days_2025,
  COUNT(DISTINCT IF(EXTRACT(YEAR FROM date) BETWEEN 2023 AND 2025, state_bottle_retail, NULL)) AS n_prices_23_25,
  MIN(IF(EXTRACT(YEAR FROM date) BETWEEN 2023 AND 2025, state_bottle_retail, NULL)) AS min_price_23_25,
  MAX(IF(EXTRACT(YEAR FROM date) BETWEEN 2023 AND 2025, state_bottle_retail, NULL)) AS max_price_23_25,
  APPROX_QUANTILES(SAFE_DIVIDE(state_bottle_retail, state_bottle_cost), 2)[OFFSET(1)] AS median_markup
FROM `bigquery-public-data.iowa_liquor_sales.sales` GROUP BY item_number
