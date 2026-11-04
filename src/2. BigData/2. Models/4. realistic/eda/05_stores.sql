SELECT store_number, ANY_VALUE(store_name) AS store_name, COUNT(DISTINCT store_name) AS n_names,
  ANY_VALUE(UPPER(city)) AS city, ANY_VALUE(UPPER(county)) AS county, ANY_VALUE(zip_code) AS zip_code,
  MIN(date) AS first_date, MAX(date) AS last_date, COUNT(DISTINCT date) AS order_days,
  SUM(sale_dollars) AS sales_total, SUM(IF(EXTRACT(YEAR FROM date)=2025, sale_dollars, 0)) AS sales_2025,
  COUNT(DISTINCT IF(EXTRACT(YEAR FROM date)=2025, date, NULL)) AS order_days_2025,
  COUNT(DISTINCT IF(EXTRACT(YEAR FROM date)=2025, item_number, NULL)) AS items_2025,
  COUNTIF(store_location IS NULL) AS null_loc_rows
FROM `bigquery-public-data.iowa_liquor_sales.sales` GROUP BY store_number
