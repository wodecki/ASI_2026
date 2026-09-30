# BigQuery Iowa Analysis - Local Setup Guide

## Overview

This guide walks you through setting up your local environment to run BigQuery Python scripts that query the Iowa liquor sales dataset. You'll learn how to authenticate with Google Cloud, install dependencies using `uv`, and execute data analysis scripts locally.

**What You'll Learn:**
- Install and configure Google Cloud CLI (`gcloud`)
- Authenticate with Application Default Credentials (ADC)
- Set up Python environment with `uv`
- Run BigQuery queries from Python scripts
- Export query results to CSV files

**Prerequisites:**
- Active Google Cloud Platform account
- Iowa dataset imported to BigQuery (see `README - import.md`)
- macOS, Linux, or Windows with WSL2
- Python 3.10 or higher

---

## Part 1: Install Google Cloud CLI

The `gcloud` CLI is required for authenticating with Google Cloud services from your local machine.

### macOS Installation

**Option 1: Using Homebrew (Recommended)**

```bash
# Install gcloud CLI
brew install --cask google-cloud-sdk

# Verify installation
gcloud --version
```

**Expected Output:**
```
Google Cloud SDK 501.0.0
bq 2.1.8
core 2024.10.18
gsutil 5.30
```

---

**Option 2: Using Official Installer**

```bash
# Download installer
curl https://sdk.cloud.google.com | bash

# Restart shell
exec -l $SHELL

# Verify installation
gcloud --version
```

---

### Linux Installation

```bash
# Add Cloud SDK distribution URI as a package source
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Update and install
sudo apt-get update && sudo apt-get install google-cloud-cli

# Verify installation
gcloud --version
```

---

### Windows Installation

**Using PowerShell:**

1. Download the installer: https://cloud.google.com/sdk/docs/install#windows
2. Run `GoogleCloudSDKInstaller.exe`
3. Follow installation wizard
4. Restart terminal and verify:

```powershell
gcloud --version
```

---

## Part 2: Authenticate with Google Cloud

### Step 1: Initialize gcloud CLI

```bash
gcloud init
```

**Interactive Prompts:**

1. **"Pick configuration to use"**
   - Select: `[1] Re-initialize this configuration [default]`

2. **"Choose the account you would like to use"**
   - Select your Google account (e.g., `your-email@gmail.com`)
   - Or select `[2] Log in with a new account`

3. **"Pick cloud project to use"**
   - Enter the number corresponding to your project (e.g., `asi2024-415408`)
   - Or enter project ID manually

4. **"Do you want to configure a default Compute Region?"**
   - Select `Y`
   - Choose: `[14] europe-west4-a` (or your preferred region)

**Verification:**

```bash
# Check active configuration
gcloud config list

# Expected output:
# [core]
# account = your-email@gmail.com
# project = asi2024-415408
#
# [compute]
# region = europe-west4
```

---

### Step 2: Set Up Application Default Credentials (ADC)

This creates credentials that Python libraries (like `google-cloud-bigquery`) can automatically discover.

```bash
gcloud auth application-default login
```

**What Happens:**
1. Browser opens to Google login page
2. Select your account
3. Grant permissions to "Google Auth Library"
4. Confirmation message: "You are now authenticated with the gcloud CLI"

**Credential Storage Location:**
- **macOS/Linux:** `~/.config/gcloud/application_default_credentials.json`
- **Windows:** `%APPDATA%\gcloud\application_default_credentials.json`

**Verify ADC Setup:**

```bash
# Check if credentials file exists
ls ~/.config/gcloud/application_default_credentials.json

# Expected output: (file path with timestamp)
```

---

### Step 3: Set Default Project (Optional but Recommended)

```bash
# Set your project as default
gcloud config set project asi2024-415408

# Verify
gcloud config get-value project
# Output: asi2024-415408
```

---

## Part 3: Install uv Package Manager

`uv` is a fast, modern Python package manager (replacement for pip/poetry).

### macOS/Linux Installation

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
# Expected output: uv 0.4.x or higher
```

---

### Windows Installation

```powershell
# Using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

---

### Alternative: Install via pip

```bash
pip install uv

# Verify
uv --version
```

---

## Part 4: Set Up Python Environment

### Step 1: Navigate to Project Directory

```bash
cd "src/2. BigData/1. Data/3. BigQuery Iowa Analysis"
```

---

### Step 2: Install Dependencies with uv

The `pyproject.toml` file already defines all required dependencies.

```bash
# Sync dependencies from pyproject.toml
uv sync
```

**What Gets Installed:**
- `google-cloud-bigquery>=3.25.0` - BigQuery Python client
- `pandas>=2.2.0` - Data manipulation library
- `db-dtypes>=1.2.0` - Database data type conversions for pandas
- `pyarrow>=17.0.0` - Fast columnar data processing (required for BigQuery)

**Expected Output:**
```
Resolved 12 packages in 1.2s
Installed 12 packages in 450ms
 + google-cloud-bigquery==3.25.0
 + pandas==2.2.2
 + db-dtypes==1.2.1
 + pyarrow==17.0.0
 + ... (dependencies)
```

---

### Step 3: Verify Installation

```bash
# Check installed packages
uv pip list

# Expected output includes:
# google-cloud-bigquery  3.25.0
# pandas                 2.2.2
# db-dtypes              1.2.1
# pyarrow                17.0.0
```

---

## Part 5: Configure Your Script

### Step 1: Update Project ID in Script

Open `1. read_from_GBQ.py` and update the project ID to match your GCP project:

**Current code:**
```python
client = bigquery.Client(project="asi2025-850710718243")
```

**Updated code (replace with YOUR project ID):**
```python
import os
from google.cloud import bigquery
import pandas as pd

# Use environment variable or hardcode your project ID
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "asi2024-415408")  # Replace with your project ID

# Initialize client
client = bigquery.Client(project=PROJECT_ID)

# Query data
query = """
SELECT date, item_name, total_amount_sold
FROM `asi2024-415408.iowa.training_data`  -- Update this too!
ORDER BY item_name, date
"""

# Execute query and load to pandas
df = client.query(query).to_dataframe()

print(df.head())

# Save locally (uncomment to enable)
# df.to_csv("data/iowa_sales.csv", index=False)
```

---

### Step 2: Create Data Directory (Optional)

If you want to save CSV outputs:

```bash
# Create data directory
mkdir -p data

# Verify
ls -la
# Expected: data/ directory exists
```

---

## Part 6: Run the Script

### Option 1: Run with uv (Recommended)

```bash
uv run python "1. read_from_GBQ.py"
```

**Expected Output:**
```
         date           item_name  total_amount_sold
0  2023-01-01        Black Velvet               1234
1  2023-01-02        Black Velvet               1456
2  2023-01-03        Black Velvet               1123
3  2023-01-04        Black Velvet               1345
4  2023-01-05        Black Velvet               1289
```

---

### Option 2: Run with Python Directly

```bash
# Activate uv environment first
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate  # Windows

# Run script
python "1. read_from_GBQ.py"
```

---

### Option 3: Run with Environment Variable

Set project ID via environment variable:

```bash
# macOS/Linux
export GCP_PROJECT_ID="asi2024-415408"
uv run python "1. read_from_GBQ.py"

# Windows PowerShell
$env:GCP_PROJECT_ID="asi2024-415408"
uv run python "1. read_from_GBQ.py"
```

---

## Part 7: Troubleshooting Common Issues

### Issue 1: "DefaultCredentialsError: Could not automatically determine credentials"

**Error Message:**
```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials.
```

**Solution:**

```bash
# Re-run Application Default Credentials login
gcloud auth application-default login

# Verify credentials file exists
ls ~/.config/gcloud/application_default_credentials.json
```

---

### Issue 2: "403 Forbidden: Access Denied"

**Error Message:**
```
google.api_core.exceptions.Forbidden: 403 GET https://bigquery.googleapis.com/...
Access Denied: Project asi2024-415408: User does not have permission
```

**Solution:**

1. Verify you're authenticated with correct account:
   ```bash
   gcloud auth list
   # * account 1 (ACTIVE)  <- Should be your account
   ```

2. Check project permissions in GCP Console:
   ```
   IAM & Admin → IAM → Check your account has "BigQuery User" role
   ```

3. Grant yourself BigQuery permissions:
   ```bash
   gcloud projects add-iam-policy-binding asi2024-415408 \
     --member="user:your-email@gmail.com" \
     --role="roles/bigquery.user"
   ```

---

### Issue 3: "Table Not Found: iowa.training_data"

**Error Message:**
```
google.api_core.exceptions.NotFound: 404 Not found: Table asi2024-415408:iowa.training_data
```

**Solution:**

1. Verify table exists in BigQuery Console:
   ```
   BigQuery → asi2024-415408 → iowa → training_data
   ```

2. If table doesn't exist, create it using SQL from `README.md` Part 3:
   ```sql
   CREATE OR REPLACE TABLE iowa.training_data AS (...)
   ```

3. Update script with correct table path:
   ```python
   query = """
   SELECT date, item_name, total_amount_sold
   FROM `asi2024-415408.iowa.training_data`  -- Check project ID and dataset name
   ORDER BY item_name, date
   """
   ```

---

### Issue 4: "ModuleNotFoundError: No module named 'google.cloud'"

**Error Message:**
```
ModuleNotFoundError: No module named 'google.cloud'
```

**Solution:**

```bash
# Reinstall dependencies
uv sync --reinstall

# Or manually install BigQuery client
uv add google-cloud-bigquery

# Verify installation
uv run python -c "from google.cloud import bigquery; print('OK')"
# Expected output: OK
```

---

### Issue 5: "ImportError: Missing optional dependency 'pyarrow'"

**Error Message:**
```
ImportError: Missing optional dependency 'pyarrow'. Use pip or conda to install pyarrow.
```

**Solution:**

```bash
# Add pyarrow explicitly
uv add pyarrow

# Or sync from pyproject.toml (it's already included)
uv sync
```

---

## Part 8: Advanced Configuration

### Option 1: Use Service Account (For Production)

Instead of ADC, use a service account key file:

**1. Create Service Account in GCP Console:**
```
IAM & Admin → Service Accounts → CREATE SERVICE ACCOUNT
Name: bigquery-python-client
Role: BigQuery User
```

**2. Create JSON Key:**
```
Service Accounts → [your service account] → Keys → ADD KEY → JSON
```

**3. Download `service-account-key.json` to project directory**

**4. Update script:**
```python
import os
from google.cloud import bigquery

# Set credentials file path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account-key.json"

# Initialize client
client = bigquery.Client(project="asi2024-415408")
```

**5. Add to .gitignore:**
```bash
echo "service-account-key.json" >> .gitignore
```

---

### Option 2: Use .env File for Configuration

Create `.env` file in project directory:

```bash
# .env
GCP_PROJECT_ID=asi2024-415408
BIGQUERY_DATASET=iowa
BIGQUERY_TABLE=training_data
```

**Install python-dotenv:**
```bash
uv add python-dotenv
```

**Update script:**
```python
import os
from dotenv import load_dotenv
from google.cloud import bigquery
import pandas as pd

# Load environment variables
load_dotenv(override=True)

# Get configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET = os.getenv("BIGQUERY_DATASET")
TABLE = os.getenv("BIGQUERY_TABLE")

# Initialize client
client = bigquery.Client(project=PROJECT_ID)

# Query data
query = f"""
SELECT date, item_name, total_amount_sold
FROM `{PROJECT_ID}.{DATASET}.{TABLE}`
ORDER BY item_name, date
"""

# Execute query
df = client.query(query).to_dataframe()
print(df.head())
```

---

### Option 3: Enable Query Caching

Reduce costs by enabling BigQuery query caching:

```python
from google.cloud import bigquery

client = bigquery.Client(project="asi2024-415408")

# Configure query job
job_config = bigquery.QueryJobConfig()
job_config.use_query_cache = True  # Enable cache (default)
job_config.use_legacy_sql = False  # Use standard SQL

query = """
SELECT date, item_name, total_amount_sold
FROM `asi2024-415408.iowa.training_data`
LIMIT 100
"""

# Run query with config
query_job = client.query(query, job_config=job_config)
df = query_job.to_dataframe()

# Check if cache was used
print(f"Cache hit: {query_job.cache_hit}")
print(f"Bytes processed: {query_job.total_bytes_processed:,}")
```

---

## Part 9: Cost Monitoring

### Check Query Costs Before Running

```python
from google.cloud import bigquery

client = bigquery.Client(project="asi2024-415408")

query = """
SELECT date, item_name, total_amount_sold
FROM `asi2024-415408.iowa.training_data`
ORDER BY item_name, date
"""

# Dry run to estimate costs
job_config = bigquery.QueryJobConfig(dry_run=True)
query_job = client.query(query, job_config=job_config)

# Calculate cost estimate
bytes_processed = query_job.total_bytes_processed
cost_per_tb = 5.0  # $5 per TB (on-demand pricing)
estimated_cost = (bytes_processed / (1024**4)) * cost_per_tb

print(f"Bytes to be processed: {bytes_processed:,} ({bytes_processed / (1024**2):.2f} MB)")
print(f"Estimated cost: ${estimated_cost:.6f}")

# Example output:
# Bytes to be processed: 45,678 (0.04 MB)
# Estimated cost: $0.000000
```

---

### Set Query Timeout and Max Bytes Billed

```python
from google.cloud import bigquery

client = bigquery.Client(project="asi2024-415408")

# Set limits
job_config = bigquery.QueryJobConfig(
    maximum_bytes_billed=10 * 1024**3,  # 10 GB limit
)

query = """
SELECT * FROM `asi2024-415408.iowa.sales`  -- Full table scan
"""

try:
    query_job = client.query(query, job_config=job_config)
    df = query_job.to_dataframe()
except Exception as e:
    print(f"Query exceeded billing limit: {e}")
```

---

## Part 10: Next Steps

After successfully running the script, you can:

1. **Modify the query** in `1. read_from_GBQ.py` to explore different analyses
2. **Export results to CSV** by uncommenting the `df.to_csv()` line
3. **Create visualizations** using matplotlib or seaborn
4. **Build ML models** using the exported data (see Module 2: Models)
5. **Automate queries** with scheduled Cloud Functions or Airflow DAGs

---

## Part 11: Quick Reference Commands

### Setup (One-Time)

```bash
# Install gcloud CLI
brew install --cask google-cloud-sdk  # macOS

# Authenticate
gcloud auth application-default login

# Set project
gcloud config set project asi2024-415408

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
cd "src/2. BigData/1. Data/3. BigQuery Iowa Analysis"
uv sync
```

---

### Daily Usage

```bash
# Navigate to directory
cd "src/2. BigData/1. Data/3. BigQuery Iowa Analysis"

# Run script
uv run python "1. read_from_GBQ.py"

# Check query costs
gcloud logging read "resource.type=bigquery_resource" --limit 5 --format=json
```

---

### Verify Setup

```bash
# Check gcloud installation
gcloud --version

# Check authentication
gcloud auth list

# Check project
gcloud config get-value project

# Check uv installation
uv --version

# Check Python packages
uv pip list | grep bigquery
```

---

## Additional Resources

- **Google Cloud CLI Documentation:** https://cloud.google.com/sdk/docs
- **BigQuery Python Client Library:** https://cloud.google.com/python/docs/reference/bigquery/latest
- **uv Package Manager:** https://github.com/astral-sh/uv
- **Application Default Credentials:** https://cloud.google.com/docs/authentication/application-default-credentials
- **BigQuery Pricing Calculator:** https://cloud.google.com/products/calculator

---

**Course:** ASI_2025 - Machine Learning Operations
**Module:** 2. BigData / 1. Data Processing / 3. BigQuery Iowa Analysis
**Difficulty:** Intermediate
**Time Required:** 30-45 minutes
**Prerequisites:** GCP account, Iowa dataset in BigQuery, basic Python knowledge
