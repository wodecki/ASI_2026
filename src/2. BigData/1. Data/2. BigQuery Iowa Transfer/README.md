# Transferring IOWA Dataset from Google Public Datasets to Your GCP Project

## Overview

This tutorial demonstrates how to copy large public datasets from Google Cloud Public Datasets to your own Google Cloud Platform (GCP) infrastructure. You'll learn the complete workflow from accessing public data through exporting to Google Cloud Storage (GCS) and importing to BigQuery.

**Learning Objectives:**
- Access Google Cloud Public Datasets
- Export BigQuery tables to Google Cloud Storage
- Create and configure GCS buckets
- Import data from GCS to your BigQuery project
- Understand data storage formats and optimization

**Prerequisites:**
- Active GCP account with billing enabled
- Project created in Google Cloud Console (e.g., `ASI_2025`)
- Appropriate IAM permissions for BigQuery and Cloud Storage

---

## Part 1: Understanding the Data Architecture

### Key Concepts

**Data Storage Locations:**
1. **Google Cloud Storage (GCS Bucket)** - Object storage for raw/serialized data
2. **BigQuery** - Relational data warehouse for analytical queries
3. **Public Datasets** - Shared datasets provided by Google

**Data Formats:**
- **CSV** - Human-readable, larger file size
- **Avro** - Binary format, better compression and schema preservation
- **Parquet** - Columnar storage, optimized for analytics

**Why This Workflow Matters:**
Copying public datasets to your own project is essential for:
- Running custom analyses without query limits
- Modifying and enriching data
- Integrating with your ML pipelines
- Controlling costs through storage optimization

---

## Part 2: Step-by-Step Workflow

### Phase 1: Access the Iowa Liquor Sales Dataset

**1. Navigate to BigQuery Public Datasets**

```
Google Cloud Console → BigQuery → + Add Data → Explore public datasets
```

**2. Find Iowa Liquor Sales Dataset**

- Search for: `iowa liquor sales`
- Public dataset path: `bigquery-public-data.iowa_liquor_sales.sales`
- **Dataset size:** ~26 million rows, ~17 GB
- **Columns:** date, store_number, store_name, address, city, zip_code, county, category, item_name, vendor, bottles_sold, sale_dollars, volume_sold_liters, etc.

**3. Preview the Data**

```sql
-- Run this query to explore the dataset
SELECT *
FROM `bigquery-public-data.iowa_liquor_sales.sales`
LIMIT 10
```


---

### Phase 2: Create Google Cloud Storage Bucket

**Why create a bucket first?**
BigQuery cannot export directly to another BigQuery project. You must use GCS as an intermediate storage layer.

**1. Navigate to Cloud Storage**

```
Google Cloud Console → Cloud Storage → Buckets → CREATE BUCKET
```

**2. Configure Bucket Settings**

**Bucket Name:**
```
iowa2025
```
- Must be globally unique
- Use lowercase letters, numbers, hyphens
- Example: `iowa2025`

**Location:**
- Type: **Region**
- Region: **europe-west4 (Netherlands)**
- *Choose the region closest to your compute resources*

**Storage Class:**
- **Standard** (for frequently accessed data)
- Alternative: **Nearline** or **Coldline** for archival

**Access Control:**
- **Uniform** access control (recommended)
- Public access prevention: **On** (enforced)

**3. Create the Bucket**

Click **CREATE** to finalize the bucket.

**4. Verify Bucket Creation**

- Navigate to Cloud Storage → Buckets
- Confirm `iowa2025` appears in the list
- Status: "No objects found" (expected at this stage)

---

### Phase 3: Export BigQuery Table to GCS

**1. Navigate to the Source Table**

```
BigQuery → bigquery-public-data → iowa_liquor_sales → sales
```

**2. Open Export Menu**

- Click the `sales` table
- Select **Export** → **Export to Cloud Storage**

**Alternative path:**
```
EXPORT → Explore with Sheets → [dropdown] → Explore with Cloud Storage
```

**3. Configure Export Settings**

**Export to Google Cloud Storage dialog:**

**GCS Location:**
```
gs://iowa2025/sales-*
```
- `gs://` = GCS protocol
- `iowa2025` = your bucket name
- `sales-*` = filename pattern (wildcard for sharding)

**Export Format:**
```
Avro
```

**Why Avro?**
- Preserves BigQuery schema (data types, nested fields)
- Better compression than CSV (~30-50% smaller)
- Faster to import back to BigQuery
- Native support in BigQuery

**Compression:**
```
None
```
- Optional: Choose `GZIP` or `SNAPPY` for additional compression
- Trade-off: Smaller files vs. slower processing

**4. Execute Export**

Click **EXPORT** to start the export job.

**Expected Behavior:**
- BigQuery creates an export job
- Large tables are automatically sharded into multiple files (sales-000000000000, sales-000000000001, etc.)
- Export time: ~5-15 minutes for 17 GB dataset

**5. Monitor Export Progress**

```
BigQuery → Job History → [Find your export job]
```

Look for job type: `extract` with status `Complete`

**6. Verify Files in GCS Bucket**

Navigate to:
```
Cloud Storage → Buckets → iowa2025
```

**Expected files:**
```
sales-000000000000.avro
sales-000000000001.avro
sales-000000000002.avro
...
sales-000000000029.avro
```

---

### Phase 4: Import Data from GCS to BigQuery

**1. Create a BigQuery Dataset**

A dataset is a container for tables within your project.

```
BigQuery → Your Project (e.g., ASI_2025-420908) → ⋮ → Create dataset
```

**Dataset Configuration:**
- **Dataset ID:** `iowa`
- **Location:** `europe-west4` (must match bucket location)
- **Default table expiration:** None
- **Encryption:** Google-managed key

**2. Create Table from GCS**

```
BigQuery → iowa dataset → ⋮ → Create table
```

**3. Configure Import Settings**

**Source:**
- **Create table from:** Google Cloud Storage
- **Select file from GCS bucket:** Browse → `iowa2025/sales-*`
- **File format:** Avro

**Why use wildcard pattern `sales-*`?**
BigQuery automatically loads all matching files (all shards) into a single table.

**Destination:**
- **Project:** `ASI_2025-420908` (your project ID)
- **Dataset:** `iowa`
- **Table:** `sales`
- **Table type:** Native table

**Schema:**
- **Auto detect:** ✓ (Avro files contain schema metadata)
- Alternatively: **Edit as text** for manual schema definition

**Partitioning Settings:**
- **No partitioning** (default)
- Advanced: Partition by date column for query optimization

**Cluster Settings:**
- Optional: Cluster by frequently filtered columns (e.g., `city`, `category`)

**4. Create the Table**

Click **CREATE TABLE** to start the import job.

**Import Duration:**
- ~5-10 minutes for 17 GB / 26M rows
- Check Job History for progress

**5. Verify Import Success**

```
BigQuery → iowa → sales → Details
```

**Expected Table Info:**
- **Table ID:** `ASI_2025-420908.iowa.sales`
- **Created:** [timestamp]
- **Last modified:** [timestamp]
- **Table expiration:** NEVER
- **Number of rows:** ~26,702,170
- **Total logical bytes:** ~17 GB
- **Long-term logical bytes:** 0 B (newly created)

---

## Part 3: Verification and Data Quality Checks

### Verify Row Counts

**Original table (public dataset):**
```sql
SELECT COUNT(*) AS total_rows
FROM `bigquery-public-data.iowa_liquor_sales.sales`
```

**Your imported table:**
```sql
SELECT COUNT(*) AS total_rows
FROM `ASI_2025-420908.iowa.sales`
```

**Expected result:** Both queries should return the same count (~26.7 million)

### Sample Data Comparison

```sql
-- Public dataset
SELECT *
FROM `bigquery-public-data.iowa_liquor_sales.sales`
ORDER BY date DESC
LIMIT 5

-- Your dataset
SELECT *
FROM `ASI_2025-420908.iowa.sales`
ORDER BY date DESC
LIMIT 5
```

Compare column names, data types, and sample values.

### Schema Validation

```sql
-- Check schema in your table
SELECT column_name, data_type, is_nullable
FROM `ASI_2025-420908.iowa.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'sales'
ORDER BY ordinal_position
```

---

## Part 4: Cost Optimization Strategies

### Understanding GCS Costs

**Storage costs (europe-west4):**
- Standard storage: $0.020 per GB/month
- For 17 GB: ~$0.34/month

**Data transfer costs:**
- Export from BigQuery to GCS (same region): **FREE**
- Import from GCS to BigQuery (same region): **FREE**

### Understanding BigQuery Costs

**Storage costs:**
- Active storage: $0.020 per GB/month
- Long-term storage (90+ days): $0.010 per GB/month

**Query costs:**
- On-demand: $5 per TB scanned
- Flat-rate: $2,000/month for 100 slots (better for heavy usage)

### Best Practices

1. **Delete GCS files after import** (if no longer needed)
   ```bash
   gsutil rm -r gs://iowa2025/sales-*
   ```

2. **Partition large tables** by date for query optimization
   ```sql
   CREATE OR REPLACE TABLE iowa.sales_partitioned
   PARTITION BY DATE(date)
   AS SELECT * FROM iowa.sales
   ```

3. **Use table expiration** for temporary datasets
   - Set expiration: 7 days, 30 days, etc.

4. **Monitor with billing alerts**
   - Set budget alerts in Google Cloud Console

---

## Part 5: Common Issues and Troubleshooting

### Issue 1: "Permission Denied" During Export

**Error:**
```
Access Denied: BigQuery BigQuery: Permission denied while getting Drive credentials.
```

**Solution:**
- Ensure service account has **Storage Admin** role
- Grant permissions: IAM → Service Accounts → [your service account] → Add role

### Issue 2: Export Job Fails with "Invalid GCS Path"

**Error:**
```
Invalid GCS path: gs://bucket-name/file
```

**Solution:**
- Verify bucket name is correct (case-sensitive)
- Use wildcard pattern for large exports: `gs://bucket/prefix-*`
- Ensure bucket and BigQuery dataset are in the same region

### Issue 3: Schema Mismatch During Import

**Error:**
```
Error while reading table: CSV table has 10 columns, expected 15
```

**Solution:**
- Use **Avro** format instead of CSV (preserves schema)
- Enable **Schema auto-detect**
- Manually define schema in "Edit as text" mode

### Issue 4: Import Is Slow or Hangs

**Symptoms:**
- Import job runs for hours without progress

**Solution:**
- Check file size (Avro files should be 100-500 MB each)
- Use sharded export: `gs://bucket/prefix-*` creates multiple files
- Ensure same region for bucket and BigQuery dataset

---

## Part 6: Advanced Topics

### File Format Comparison

| Format | Size | Compression | Schema Preservation | BigQuery Speed |
|--------|------|-------------|---------------------|----------------|
| **CSV** | Largest (17 GB) | None | ❌ No | Slow |
| **CSV.gz** | Medium (5 GB) | Good | ❌ No | Slow |
| **Avro** | Small (7 GB) | Good | ✅ Yes | Fast |
| **Parquet** | Smallest (4 GB) | Best | ✅ Yes | Fastest |

**Recommendation:** Use **Avro** for BigQuery exports (native support, good balance)

### Automating the Workflow

**Use `bq` command-line tool:**

```bash
# Export from BigQuery to GCS
bq extract \
  --destination_format=AVRO \
  bigquery-public-data:iowa_liquor_sales.sales \
  gs://iowa2025/sales-*.avro

# Import from GCS to BigQuery
bq load \
  --source_format=AVRO \
  --replace \
  ASI_2025-420908:iowa.sales \
  gs://iowa2025/sales-*.avro
```

**Use Python with BigQuery client library:**

```python
from google.cloud import bigquery
from google.cloud import storage

# Initialize clients
bq_client = bigquery.Client(project="ASI_2025-420908")
storage_client = storage.Client()

# Export BigQuery table to GCS
bucket_name = "iowa2025"
destination_uri = f"gs://{bucket_name}/sales-*.avro"
dataset_ref = bigquery.DatasetReference("bigquery-public-data", "iowa_liquor_sales")
table_ref = dataset_ref.table("sales")

extract_job = bq_client.extract_table(
    table_ref,
    destination_uri,
    location="US"
)
extract_job.result()  # Wait for job to complete

# Import GCS files to BigQuery
dataset_ref = bq_client.dataset("iowa")
table_ref = dataset_ref.table("sales")
job_config = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.AVRO)

load_job = bq_client.load_table_from_uri(
    destination_uri,
    table_ref,
    job_config=job_config
)
load_job.result()  # Wait for import to complete
```

### Setting Up Scheduled Exports

Use **Cloud Scheduler** + **Cloud Functions** to automate regular exports:

1. Create Cloud Function that exports data
2. Set up Cloud Scheduler trigger (daily, weekly, etc.)
3. Monitor with Cloud Logging

---

## Part 7: Exercises for Students

### Exercise 1: Basic Transfer (Easy)

1. Create a GCS bucket named `[your-name]-iowa-test`
2. Export the Iowa sales table (first 1 million rows only)
3. Import to your BigQuery project
4. **Question:** What is the total storage size in GCS vs. BigQuery?

**Hint for limiting rows:**
```sql
CREATE OR REPLACE TABLE temp_dataset.sales_sample AS
SELECT * FROM `bigquery-public-data.iowa_liquor_sales.sales`
LIMIT 1000000
```

### Exercise 2: Format Comparison (Medium)

1. Export the same table in three formats: CSV, Avro, Parquet
2. Record file sizes for each format
3. Time the import process for each format
4. **Question:** Which format is fastest? Which uses least storage?

### Exercise 3: Partitioned Table (Advanced)

1. Export the full Iowa dataset
2. Create a partitioned table in BigQuery (partition by `date`)
3. Compare query performance: partitioned vs. non-partitioned
4. **Question:** How much does partitioning reduce query costs?

**Hint:**
```sql
CREATE OR REPLACE TABLE iowa.sales_partitioned
PARTITION BY DATE(date)
CLUSTER BY city, category
AS SELECT * FROM iowa.sales
```

### Exercise 4: Cost Calculation (Advanced)

Given:
- Dataset size: 17 GB
- Query frequency: 10 queries/day scanning full table
- Storage duration: 6 months

Calculate:
1. Monthly storage costs (GCS + BigQuery)
2. Monthly query costs (on-demand pricing)
3. Cost comparison: keeping data in GCS vs. BigQuery
4. **Question:** At what query frequency does flat-rate pricing become cheaper?

---

## Part 8: Key Takeaways

### Workflow Summary

```
Google Public Dataset (BigQuery)
         ↓ [Export]
Google Cloud Storage (GCS Bucket)
         ↓ [Import]
Your BigQuery Project
         ↓ [Query & Analyze]
ML Models / Dashboards / Applications
```

### Critical Success Factors

1. ✅ **Same region** for GCS bucket and BigQuery dataset (avoid transfer costs)
2. ✅ **Use Avro format** for schema preservation and performance
3. ✅ **Wildcard patterns** for large table exports (`gs://bucket/prefix-*`)
4. ✅ **Verify row counts** after import (data integrity check)
5. ✅ **Clean up intermediate files** in GCS to save costs

### Real-World Applications

This workflow is essential for:
- **Data science projects:** Copy public datasets for experimentation
- **ML pipelines:** Create training datasets from public sources
- **Data warehousing:** Centralize data from multiple sources
- **Compliance:** Keep data copies within specific regions

---

## Additional Resources

- **BigQuery Public Datasets Catalog:** https://cloud.google.com/bigquery/public-data
- **GCS Best Practices:** https://cloud.google.com/storage/docs/best-practices
- **BigQuery Pricing Calculator:** https://cloud.google.com/products/calculator
- **bq Command-Line Tool Reference:** https://cloud.google.com/bigquery/docs/bq-command-line-tool

---

**Course:** ASI_2025 - Machine Learning Operations
**Module:** 2. BigData / 1. Data Processing
**Difficulty:** Intermediate
**Time Required:** 1-2 hours
**Prerequisites:** GCP account, basic SQL knowledge