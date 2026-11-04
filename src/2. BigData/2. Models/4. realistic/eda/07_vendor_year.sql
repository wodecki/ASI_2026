SELECT vendor_number, ANY_VALUE(vendor_name) AS vendor_name, EXTRACT(YEAR FROM date) AS year, SUM(sale_dollars) AS sales_usd
FROM `bigquery-public-data.iowa_liquor_sales.sales` WHERE date >= '2016-01-01' GROUP BY 1, 3
