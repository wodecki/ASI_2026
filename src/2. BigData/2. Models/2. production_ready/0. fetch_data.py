import logging
from google.cloud import bigquery
import pandas as pd
from datetime import datetime
import sys

# Import tomllib (Python 3.11+) or tomli (Python < 3.11)
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration from TOML file
logger.info("Loading configuration from config/config.toml")
with open("config/config.toml", "rb") as f:
    config = tomllib.load(f)

# BigQuery setup
PROJECT_ID = config['bigquery']['project_id']
DATASET = config['bigquery']['dataset']
TABLE = config['bigquery']['table']

# Extract configuration
products = config['data']['products']
date_start = config['data']['date_range']['start']
date_end = config['data']['date_range']['end']
output_file = config['data']['input_file']

# Build query from configuration
# Use double quotes for strings to avoid escaping issues with apostrophes
escaped_products = []
for p in products:
    # Escape double quotes if any (unlikely in product names)
    escaped_p = p.replace('"', '\\"')
    escaped_products.append(f'"{escaped_p}"')
products_list = ', '.join(escaped_products)

query = f"""
SELECT
  date,
  item_description AS item_name,
  SUM(bottles_sold) AS total_amount_sold
FROM {DATASET}.{TABLE}
WHERE date BETWEEN '{date_start}' AND '{date_end}'
  AND item_description IN ({products_list})
GROUP BY date, item_name
ORDER BY date
"""

logger.info(f"Fetching data from BigQuery project: {PROJECT_ID}")
logger.info(f"Dataset: {DATASET}.{TABLE}")
logger.info(f"Date range: {date_start} to {date_end}")
logger.info(f"Products: {len(products)}")
logger.debug(f"Generated query:\n{query}")

try:
    # Connect to BigQuery
    client = bigquery.Client(project=PROJECT_ID)

    # Execute query
    logger.info("Executing query...")
    df = client.query(query).to_dataframe()

    # Data validation
    logger.info("Validating downloaded data...")
    assert len(df) > 0, "ERROR: Query returned no data"
    assert not df['date'].isna().any(), "ERROR: Found missing dates"
    assert not df['item_name'].isna().any(), "ERROR: Found missing item names"
    assert not df['total_amount_sold'].isna().any(), "ERROR: Found missing sales values"
    assert (df['total_amount_sold'] >= 0).all(), "ERROR: Found negative sales values"

    # Log data summary
    logger.info("✓ Data validation passed")
    logger.info(f"✓ Downloaded {len(df)} rows")
    logger.info(f"✓ Products: {df['item_name'].nunique()} ({', '.join(df['item_name'].unique())})")
    logger.info(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")

    # Save to CSV
    df.to_csv(output_file, index=False)
    logger.info(f"✓ Data saved to {output_file}")

    # Summary statistics
    logger.info("\nData Summary:")
    logger.info(f"  Total sales: {df['total_amount_sold'].sum():,.0f}")
    logger.info(f"  Average daily sales per product: {df['total_amount_sold'].mean():,.0f}")
    logger.info(f"  Min/Max sales: {df['total_amount_sold'].min():,.0f} / {df['total_amount_sold'].max():,.0f}")

except FileNotFoundError:
    logger.error("ERROR: config/config.toml not found")
    logger.error("Make sure you're running this script from the 2. production_ready/ directory")
    raise

except Exception as e:
    logger.error(f"Failed to fetch data: {e}")
    logger.error("\nTroubleshooting steps:")
    logger.error("1. Check GCP authentication:")
    logger.error("   gcloud auth application-default login")
    logger.error("2. Verify project ID in config/config.toml matches your GCP project")
    logger.error("3. Ensure BigQuery dataset exists (see Module 1.2: BigQuery Iowa Transfer)")
    logger.error("4. Check that you have BigQuery permissions (BigQuery User role)")
    raise
