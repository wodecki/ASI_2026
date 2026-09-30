import os
from google.cloud import bigquery
import pandas as pd

# Configuration - UPDATE WITH YOUR PROJECT ID
PROJECT_ID = "asi2025"
DATASET = "iowa"
TABLE = "training_data"

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# Query data from BigQuery
query = f"""
SELECT date, item_name, total_amount_sold
FROM `{PROJECT_ID}.{DATASET}.{TABLE}`
ORDER BY item_name, date
"""

print(f"Querying BigQuery: {PROJECT_ID}.{DATASET}.{TABLE}")

# Execute query and load to pandas DataFrame
df = client.query(query).to_dataframe()

# Display results
print(f"\nQuery returned {len(df)} rows")
print("\nFirst 10 rows:")
print(df.head(10))

# Display summary statistics
print("\nSummary statistics:")
print(df.describe())

# Save to CSV (optional - uncomment to enable)
# output_path = "data/iowa_sales.csv"
# df.to_csv(output_path, index=False)
# print(f"\nData saved to: {output_path}")