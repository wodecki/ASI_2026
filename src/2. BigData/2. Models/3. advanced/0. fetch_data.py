import logging
import os
import json
import sys
from google.cloud import bigquery
import pandas as pd
from datetime import datetime

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
DRY_RUN = config['bigquery'].get('dry_run', False)

# Extract configuration
products = config['data']['products']
date_start = config['data']['date_range']['start']
date_end = config['data']['date_range']['end']
output_file = config['data']['input_file']
cache_max_age_days = config['data'].get('cache_max_age_days', 7)
quality_report_file = config['output']['data_quality_report']

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

# Check if cached data exists and is fresh
if os.path.exists(output_file):
    file_age_seconds = datetime.now().timestamp() - os.path.getmtime(output_file)
    file_age_days = file_age_seconds / (24 * 3600)

    logger.info(f"Found existing data file: {output_file}")
    logger.info(f"  File age: {file_age_days:.1f} days")
    logger.info(f"  Cache max age: {cache_max_age_days} days")

    if file_age_days < cache_max_age_days:
        logger.info("✓ Using cached data (within freshness threshold)")
        logger.info(f"To force refresh:")
        logger.info(f"  1. Delete {output_file}, or")
        logger.info(f"  2. Set cache_max_age_days = 0 in config/config.toml")
        exit(0)
    else:
        logger.info("⚠ Cached data is stale, will re-fetch from BigQuery")

# Dry-run mode (preview query without executing)
if DRY_RUN:
    logger.info("="*60)
    logger.info("DRY RUN MODE - Query Preview:")
    logger.info("="*60)
    logger.info(query)
    logger.info("="*60)
    logger.info("Set dry_run = false in config/config.toml to execute query")
    logger.info("="*60)
    exit(0)

logger.info(f"Fetching data from BigQuery project: {PROJECT_ID}")
logger.info(f"Dataset: {DATASET}.{TABLE}")
logger.info(f"Date range: {date_start} to {date_end}")
logger.info(f"Products: {len(products)}")

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

    # Generate data quality report
    logger.info("\nGenerating data quality report...")

    def generate_data_quality_report(df):
        """Generate comprehensive data quality report"""
        # Convert date to datetime for analysis
        df_analysis = df.copy()
        df_analysis['date'] = pd.to_datetime(df_analysis['date'])

        report = {
            "generated_at": datetime.now().isoformat(),
            "data_source": {
                "project": PROJECT_ID,
                "dataset": DATASET,
                "table": TABLE,
                "query_date_range": {
                    "start": date_start,
                    "end": date_end
                }
            },
            "basic_stats": {
                "num_rows": len(df),
                "num_products": int(df['item_name'].nunique()),
                "products": list(df['item_name'].unique()),
                "date_range": {
                    "start": str(df_analysis['date'].min()),
                    "end": str(df_analysis['date'].max()),
                    "days": int((df_analysis['date'].max() - df_analysis['date'].min()).days)
                }
            },
            "data_quality": {
                "missing_values": {
                    "date": int(df['date'].isna().sum()),
                    "item_name": int(df['item_name'].isna().sum()),
                    "total_amount_sold": int(df['total_amount_sold'].isna().sum())
                },
                "duplicates": int(df.duplicated().sum()),
                "negative_values": int((df['total_amount_sold'] < 0).sum())
            },
            "sales_statistics": {
                "total_sales": float(df['total_amount_sold'].sum()),
                "mean_daily_sales_per_product": float(df['total_amount_sold'].mean()),
                "median_daily_sales_per_product": float(df['total_amount_sold'].median()),
                "min_sales": float(df['total_amount_sold'].min()),
                "max_sales": float(df['total_amount_sold'].max()),
                "std_dev": float(df['total_amount_sold'].std())
            },
            "per_product_stats": {}
        }

        # Per-product statistics
        for product in df['item_name'].unique():
            product_df = df[df['item_name'] == product]
            report["per_product_stats"][product] = {
                "num_records": len(product_df),
                "total_sales": float(product_df['total_amount_sold'].sum()),
                "mean_sales": float(product_df['total_amount_sold'].mean()),
                "median_sales": float(product_df['total_amount_sold'].median()),
                "min_sales": float(product_df['total_amount_sold'].min()),
                "max_sales": float(product_df['total_amount_sold'].max())
            }

        return report

    quality_report = generate_data_quality_report(df)

    # Save quality report
    os.makedirs(os.path.dirname(quality_report_file), exist_ok=True)
    with open(quality_report_file, "w") as f:
        json.dump(quality_report, f, indent=2)

    logger.info(f"✓ Data quality report saved to {quality_report_file}")

    # Display key quality metrics
    logger.info("\n" + "="*60)
    logger.info("Data Quality Summary:")
    logger.info("="*60)
    logger.info(f"  Total sales: {quality_report['sales_statistics']['total_sales']:,.0f}")
    logger.info(f"  Average daily sales: {quality_report['sales_statistics']['mean_daily_sales_per_product']:,.0f}")
    logger.info(f"  Missing values: {sum(quality_report['data_quality']['missing_values'].values())}")
    logger.info(f"  Duplicates: {quality_report['data_quality']['duplicates']}")
    logger.info(f"  Data quality: {'✓ EXCELLENT' if sum(quality_report['data_quality']['missing_values'].values()) == 0 else '⚠ ISSUES FOUND'}")
    logger.info("="*60)

    # Save to CSV
    df.to_csv(output_file, index=False)
    logger.info(f"\n✓ Data saved to {output_file}")

except FileNotFoundError:
    logger.error("ERROR: config/config.toml not found")
    logger.error("Make sure you're running this script from the 3. advanced/ directory")
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
