SELECT date, COUNT(*) AS n_lines, COUNT(DISTINCT store_number) AS n_stores,
  SUM(sale_dollars) AS sales_usd, SUM(bottles_sold) AS bottles, SUM(volume_sold_liters) AS liters,
  COUNTIF(STARTS_WITH(invoice_and_item_number,'RINV')) AS n_return_lines,
  SUM(IF(STARTS_WITH(invoice_and_item_number,'RINV'), sale_dollars, 0)) AS return_usd
FROM `bigquery-public-data.iowa_liquor_sales.sales` GROUP BY date ORDER BY date
