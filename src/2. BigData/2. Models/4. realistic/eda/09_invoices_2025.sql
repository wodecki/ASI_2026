WITH inv AS (
  SELECT SUBSTR(invoice_and_item_number, 1, LENGTH(invoice_and_item_number)-5) AS inv_id,
    ANY_VALUE(store_number) AS store_number, COUNT(DISTINCT store_number) AS n_store, COUNT(DISTINCT date) AS n_date,
    COUNT(*) AS n_lines, SUM(sale_dollars) AS usd, LOGICAL_OR(STARTS_WITH(invoice_and_item_number,'RINV')) AS is_return
  FROM `bigquery-public-data.iowa_liquor_sales.sales` WHERE date BETWEEN '2025-01-01' AND '2025-12-31' GROUP BY 1)
SELECT COUNT(*) AS n_invoices, COUNTIF(n_store>1 OR n_date>1) AS inconsistent_invoices, COUNTIF(is_return) AS return_invoices,
  APPROX_QUANTILES(n_lines, 10) AS lines_deciles, APPROX_QUANTILES(usd, 10) AS usd_deciles,
  COUNT(DISTINCT store_number) AS n_stores, COUNT(*)/COUNT(DISTINCT store_number) AS invoices_per_store
FROM inv WHERE NOT is_return
