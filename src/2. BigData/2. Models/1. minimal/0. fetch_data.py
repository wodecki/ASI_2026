from google.cloud import bigquery
import pandas as pd

# Hardcoded values (this is intentionally simple - NOT production-ready!)
PROJECT_ID = "asi2025"
QUERY = """
SELECT
  date,
  item_description AS item_name,
  SUM(bottles_sold) AS total_amount_sold
FROM iowa.sales
WHERE date BETWEEN '2023-01-01' AND '2024-05-30'
  AND item_description IN (
    'BLACK VELVET',
    'FIREBALL CINNAMON WHISKEY',
    'HAWKEYE VODKA',
    'TITOS HANDMADE VODKA',
    "FIVE O'CLOCK VODKA"
  )
GROUP BY date, item_name
ORDER BY date
"""

print("Connecting to BigQuery...")
client = bigquery.Client(project=PROJECT_ID)

print("Executing query...")
df = client.query(QUERY).to_dataframe()

print(f"Downloaded {len(df)} rows")
print(f"Products: {df['item_name'].nunique()}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")

# Save to CSV
df.to_csv("data/iowa_sales.csv", index=False)
print(f"✓ Data saved to data/iowa_sales.csv")
