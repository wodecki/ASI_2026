SELECT EXTRACT(YEAR FROM date) AS year, COUNT(DISTINCT store_number) AS active_stores,
  COUNT(DISTINCT item_number) AS active_items, COUNT(DISTINCT vendor_number) AS active_vendors,
  COUNT(DISTINCT CONCAT(store_number,'|',CAST(date AS STRING))) AS store_order_days,
  COUNT(DISTINCT SUBSTR(invoice_and_item_number, 1, LENGTH(invoice_and_item_number)-5)) AS invoices
FROM `bigquery-public-data.iowa_liquor_sales.sales` GROUP BY year ORDER BY year
