# Canary Deployment Demo

Educational demo showing **canary deployment** strategy using two chatbot versions.

## What is Canary Deployment?

**Canary deployment** = Gradually rolling out a new version to a small subset of users before full deployment.

**Why?**
- Test new features with real users (low risk)
- Detect issues before affecting everyone
- Easy rollback if problems occur

**Strategy:**
1. Deploy new version alongside old
2. Route 10% traffic → new, 90% → old
3. Monitor metrics (errors, latency)
4. Gradually increase: 30%, 50%, 70%, 100%
5. Rollback instantly if issues detected

## The Demo

**Two chatbot versions:**

| Version | Style | System Prompt |
|---------|-------|---------------|
| **Serious** | Professional academic | Polite, scholarly, formal citations |
| **Funny** | Hip-hop academic | Rap rhythm, slang, educational |

Users get routed to either version (50/50 split) to compare responses.

## Prerequisites

1. **OpenAI API Key**: Get from https://platform.openai.com/api-keys
2. **GCP Account**: With billing enabled
3. **gcloud CLI**: Installed and authenticated
4. **Docker**: Running
5. **Artifact Registry**: Repository created

### Setup `.env` (API key, model, GCP settings)

All settings - for local testing **and** for the build/deploy scripts - live in one `.env` file in this directory:
```bash
# Copy template
cp .env.example .env

# Edit .env and fill in the values
nano .env
```

```bash
# .env
OPENAI_API_KEY=sk-...                 # your OpenAI API key
OPENAI_MODEL=gpt-4o-mini              # chat model used by both chatbot versions
PROJECT_ID=your-gcp-project-id        # your GCP project ID (see: gcloud projects list)
REGION=europe-west4
REPOSITORY=chatbot                    # Artifact Registry repository
IMAGE_TAG=v1
```

The apps (`app-serious.py`, `app-funny.py`) load `.env` with `load_dotenv(override=True)` and show an error if `OPENAI_API_KEY` or `OPENAI_MODEL` is missing. The `build-*.sh`, `deploy-*.sh` and `canary.sh` scripts read the same `.env` and stop with an error if a value they need is empty - no `export` needed.

**Security Note:** API key is NEVER in source code. It's loaded from:
- Local: `.env` file (git-ignored)
- Cloud Run: Environment variable (passed during deployment by `deploy-*.sh`)

### Setup GCP

```bash
# Login
gcloud auth login

# Set project (replace with your project ID)
gcloud config set project your-gcp-project-id

# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# Create Artifact Registry repository (name/location must match REPOSITORY/REGION in .env)
gcloud artifacts repositories create chatbot \
  --repository-format=docker \
  --location=europe-west4 \
  --description="Chatbot canary demo"
```

## Local Testing

```bash
# Install dependencies
uv sync

# Test serious version
uv run streamlit run app-serious.py

# Test funny version (in another terminal)
uv run streamlit run app-funny.py
```

Open: http://localhost:8501

## Deployment Workflow

You can deploy using either **CLI** (automated scripts) or **Web GUI** (recommended for learning).

---

### Option A: Deploy via Web GUI (Recommended for Learning)

This approach demonstrates true canary deployment with Cloud Run revisions and traffic splitting.

#### Step 1: Build Both Images

```bash
# Build serious version
./build-serious.sh

# Build funny version
./build-funny.sh
```

Both images pushed to Artifact Registry.

#### Step 2: Deploy Initial Version (Serious)

1. Go to **Cloud Run** in GCP Console
2. Click **Create Service**
3. Configure:
   - **Container image URL**: `europe-west4-docker.pkg.dev/your-gcp-project-id/chatbot/chatbot-serious:v1`
   - **Service name**: `chatbot-serious`
   - **Region**: `europe-west4`
   - **Authentication**: Allow unauthenticated invocations
   - **Container port**: `8080` (important!)

4. **Add Environment Variable** (critical step):
   - Expand "Containers, Volumes, Networking, Security"
   - Click "Variables & Secrets" tab
   - Under "Environment variables":
     - **Name 1**: `OPENAI_API_KEY`
     - **Value 1**: Paste your API key **without quotes** (e.g., `sk-proj-...`)
     - **Name 2**: `OPENAI_MODEL`
     - **Value 2**: `gpt-4o-mini` (the app stops with an error without it)

5. Click **Create**
6. Wait for deployment to complete

#### Step 3: Add New Revision (Funny)

1. In the `chatbot-serious` service page, click **Edit & deploy new revision**
2. Change container image:
   - **Container image URL**: `europe-west4-docker.pkg.dev/your-gcp-project-id/chatbot/chatbot-funny:v1`
3. Keep environment variables (OPENAI_API_KEY and OPENAI_MODEL are already set)
4. Click **Deploy**
5. Now you have TWO revisions:
   - `chatbot-serious-00001-xxx` (old)
   - `chatbot-serious-00002-yyy` (new)

#### Step 4: Manage Traffic (Canary Deployment)

1. Go to **Revisions** tab
2. Click **Manage Traffic**
3. Split traffic between revisions:
   - Revision 1 (serious): `50%`
   - Revision 2 (funny): `50%`
4. Click **Save**

**Result**: 50% of users get serious chatbot, 50% get funny chatbot!

#### Step 5: Monitor & Adjust

- Test the service URL - refresh to see different versions
- Monitor metrics in "Observability" tab
- Gradually shift traffic: 70/30, 90/10, or 100% to new version
- Instant rollback: Set old revision to 100%

---

### Option B: Deploy via CLI (Automated)

#### Step 1: Build Both Versions

```bash
# Build serious version
./build-serious.sh

# Build funny version
./build-funny.sh
```

Both images pushed to Artifact Registry.

#### Step 2: Deploy Both Versions

Make sure `OPENAI_API_KEY` and `OPENAI_MODEL` are set in `.env` - the deploy scripts pass both to Cloud Run with `--set-env-vars`.

```bash
# Deploy serious version
./deploy-serious.sh

# Deploy funny version
./deploy-funny.sh
```

Each deploys as separate Cloud Run service.

#### Step 3: Run Canary Demo

```bash
./canary.sh
```

This displays both URLs and explains the canary strategy.

**Note**: CLI approach creates TWO separate services (not revisions), so traffic splitting requires a load balancer.

## Testing the Deployment

Get URLs:
```bash
gcloud run services describe chatbot-serious --project your-gcp-project-id --region europe-west4 --format 'value(status.url)'
gcloud run services describe chatbot-funny --project your-gcp-project-id --region europe-west4 --format 'value(status.url)'
```

Open both in browser and ask the same question:
- **Example**: "Why is the sky blue?"
- **Serious**: Formal, academic response
- **Funny**: Hip-hop style response

## File Structure

```
5. Experiments/
├── .env.example          # Template for .env (API key, model, GCP settings)
├── .gitignore            # Ignore secrets
├── pyproject.toml        # Dependencies
├── app-serious.py        # Serious chatbot
├── app-funny.py          # Funny chatbot
├── Dockerfile-serious    # Serious container
├── Dockerfile-funny      # Funny container
├── build-serious.sh      # Build serious
├── build-funny.sh        # Build funny
├── deploy-serious.sh     # Deploy serious
├── deploy-funny.sh       # Deploy funny
├── canary.sh             # Canary demo
└── README.md             # This file
```

## Key Concepts Demonstrated

### 1. Secret Management
- ✓ API key in `.env` (local)
- ✓ API key as env var (Cloud Run)
- ✗ Never hardcode secrets

### 2. Canary Deployment
- Deploy two versions simultaneously
- Split traffic between versions
- Compare user experience
- Enable instant rollback

### 3. Cloud Run Features
- Multiple services (serious, funny)
- Environment variables for secrets
- Auto-scaling for both
- Independent deployments

## Troubleshooting

**API key / model error** ("OPENAI_API_KEY not found" or "OPENAI_MODEL not found"):
- Check that `.env` exists in this directory (`cp .env.example .env`)
- Check that `OPENAI_API_KEY` and `OPENAI_MODEL` (e.g. `gpt-4o-mini`) are filled in there
- On Cloud Run: check both variables under the service's "Variables & Secrets" tab

**Build fails:**
```bash
# Check Docker is running
docker ps

# Check Artifact Registry exists
gcloud artifacts repositories list
```

**Deploy fails:**
```bash
# "Set ... in .env" error: fill in the named value in .env
# (PROJECT_ID, REGION, REPOSITORY, IMAGE_TAG, OPENAI_API_KEY, OPENAI_MODEL)

# Check gcloud is authenticated
gcloud auth list
```

## Cost Warning

OpenAI API charges per token:
- gpt-4o-mini: ~$0.15 per million input tokens
- Each chat message = ~100-500 tokens

Cloud Run charges:
- ~$0.01 per 1000 requests
- Memory/CPU: ~$0.10/hour when running

**Keep tests short to minimize costs!**

## Clean Up

```bash
# Delete services
gcloud run services delete chatbot-serious --project your-gcp-project-id --region europe-west4
gcloud run services delete chatbot-funny --project your-gcp-project-id --region europe-west4

# Delete images
gcloud artifacts docker images delete \
  europe-west4-docker.pkg.dev/your-gcp-project-id/chatbot/chatbot-serious:v1
gcloud artifacts docker images delete \
  europe-west4-docker.pkg.dev/your-gcp-project-id/chatbot/chatbot-funny:v1
```

## Educational Takeaways

1. **Never hardcode secrets** - Use environment variables
2. **Canary deployment** reduces risk of bad deployments
3. **Traffic splitting** enables A/B testing
4. **Multiple services** allow independent scaling and rollback
5. **Cloud Run** makes canary deployments simple

## Advanced: Traffic Splitting via CLI

If you prefer CLI for traffic management (instead of Web GUI):

```bash
# Load PROJECT_ID, OPENAI_API_KEY and OPENAI_MODEL from .env
set -a; source .env; set +a

# Deploy revision 1 (serious) - no traffic initially
gcloud run deploy chatbot-serious \
  --project ${PROJECT_ID} \
  --image europe-west4-docker.pkg.dev/${PROJECT_ID}/chatbot/chatbot-serious:v1 \
  --region europe-west4 \
  --port 8080 \
  --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY},OPENAI_MODEL=${OPENAI_MODEL}" \
  --no-traffic \
  --tag serious

# Deploy revision 2 (funny) - no traffic initially
gcloud run deploy chatbot-serious \
  --project ${PROJECT_ID} \
  --image europe-west4-docker.pkg.dev/${PROJECT_ID}/chatbot/chatbot-funny:v1 \
  --region europe-west4 \
  --port 8080 \
  --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY},OPENAI_MODEL=${OPENAI_MODEL}" \
  --no-traffic \
  --tag funny

# Split traffic: 90% serious, 10% funny (initial canary)
gcloud run services update-traffic chatbot-serious \
  --to-revisions serious=90,funny=10 \
  --project ${PROJECT_ID} \
  --region europe-west4

# Gradually shift: 50/50
gcloud run services update-traffic chatbot-serious \
  --to-revisions serious=50,funny=50 \
  --project ${PROJECT_ID} \
  --region europe-west4

# Full rollout: 100% funny
gcloud run services update-traffic chatbot-serious \
  --to-revisions funny=100 \
  --project ${PROJECT_ID} \
  --region europe-west4

# Rollback: 100% serious
gcloud run services update-traffic chatbot-serious \
  --to-revisions serious=100 \
  --project ${PROJECT_ID} \
  --region europe-west4
```

**This achieves the same result as the Web GUI approach** (Option A) - a SINGLE service with multiple revisions and traffic splitting.
