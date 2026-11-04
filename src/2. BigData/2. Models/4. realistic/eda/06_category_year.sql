SELECT UPPER(TRIM(category_name)) AS category_name, EXTRACT(YEAR FROM date) AS year,
  SUM(sale_dollars) AS sales_usd, SUM(volume_sold_liters) AS liters, SUM(bottles_sold) AS bottles
FROM `bigquery-public-data.iowa_liquor_sales.sales` GROUP BY 1, 2
