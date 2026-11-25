# GCP Cloud Run Deployment - Backend

Deploy the Iowa Sales forecasting API to **Google Cloud Run** - a serverless platform for containerized applications.

## What is Cloud Run?

Cloud Run runs Docker containers without managing servers:
- **Serverless**: No infrastructure to manage
- **Auto-scaling**: Scales from 0 → N instances automatically
- **Pay-per-use**: Only charged during request handling
- **HTTPS**: Automatic SSL certificates
- **Cost**: ~$1-2/month for typical demo usage

## Prerequisites

1. **GCP Account** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** running
4. **Model trained** (run `0. train.py`)

### Install gcloud CLI

**macOS:**
```bash
brew install --cask google-cloud-sdk
```

**Linux/Windows:** https://cloud.google.com/sdk/docs/install

### Setup GCP

```bash
# Login (run it again whenever gcloud reports "invalid_grant" - the token has expired)
gcloud auth login

# Set project (replace with your project ID)
gcloud config set project your-gcp-project-id

# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# Create Artifact Registry repository (REQUIRED - build.sh will fail without this)
# Name and location must match REPOSITORY and REGION in .env
gcloud artifacts repositories create iowa \
  --repository-format=docker \
  --location=europe-west4 \
  --description="Iowa sales containers"

# Verify repository was created
gcloud artifacts repositories list
```

### Train Model

```bash
cd backend
uv sync
uv run python "0. train.py"
```

This creates `autogluon-iowa-daily/` directory needed for deployment.

## Images, indexes, containers and revisions

Four words appear on the way from your laptop to a running service. They are easy to mix up, because the GCP console shows some of them side by side.

| Term | What it is | Analogy (MS Word) |
|------|------------|-------------------|
| **Image** | Static, read-only package: filesystem layers (Python, `.venv`, `main.py`, the model) plus a config (`CMD`, `ENV PORT=8080`). Built for exactly one platform, e.g. `linux/amd64`. | The `WINWORD.EXE` binary on disk |
| **Index** | A ~1 KB JSON list that points to images: "for linux/amd64 use image X". It holds no layers. | The download page: "Word for Windows → this file, Word for Mac → that file" |
| **Container** | An instance created from an image: the image's layers + a thin writable layer + an isolated process. One image can run as many containers. | A running Word process |
| **Revision** (Cloud Run) | An immutable deployment record: "run image X with 2 GiB, 2 CPU, port 8080". Every deploy creates a new revision. | An IT policy: "run this Word version with these settings" |
| **Instance** (Cloud Run) | A container that Cloud Run starts from a revision when requests arrive (0 → max instances). | The Word processes started under that policy |

Note on wording: **"container image"** (as in the console field *Container image URL*) means *an image to make containers from* - it is an image, not a container. A container also exists when stopped (`docker ps -a` lists it until `docker rm`), so "a container is an instance of an image" is more precise than "a running image".

### What you see in Artifact Registry

After `./build.sh`, the repository shows **two versions per build** (three with *Hide OCI alternative artifacts* switched off):

| Version | Media type | Size | Tag | What it is |
|---------|------------|------|-----|------------|
| `fc86b03…` | `application/vnd.oci.image.index.v1+json` | – | `v1` | **Index** - points to the image below and to an attestation |
| `ad76e0b…` | `application/vnd.oci.image.manifest.v1+json` | ~755 MB | – | **Image** for `linux/amd64` - what Cloud Run downloads and runs |
| (hidden) | attestation manifest | ~2 KB | – | Provenance record: how and when the image was built |

Why an index for a single platform? Recent Docker versions (BuildKit) attach a **provenance attestation** to every build by default, and Docker Desktop's **containerd image store** pushes it together with the image. An index is the OCI way to bundle them. Older Docker setups (or `docker build --provenance=false`) push just the image manifest - one row per build.

Consequences:
- **Rebuilding without changes** gives the *same image digest* (layers come from the build cache, the *Built* date stays the old one) but a *new index digest* (the attestation records the build time).
- **Pushing the same tag again** moves the tag `v1` to the new index; the old index and image stay in the registry untagged (see [Clean Up](#clean-up)). Use a new `IMAGE_TAG` per build (`v1`, `v2`, ...) to keep versions readable.
- **Both rows have a Deploy button and both deploy the same image**: deploying the index makes Cloud Run look up the `linux/amd64` entry and pull the image; deploying the image skips that lookup.

**Which to deploy?** The **tag** (`v1`, which points to the index). It is the human-readable name, it matches `IMAGE_TAG` in `.env` and `deploy.sh`, and Cloud Run records the exact digest in the revision - so pushing a new `v1` later does not change a running revision until you deploy again. Deploy by image digest (`iowa-backend@sha256:ad76e0b…`) when you want to pin exact bytes, e.g. for a rollback.

## Deployment Steps

### 1. Configure `.env`

`build.sh` and `deploy.sh` read their settings from a `.env` file in `backend/` (next to the scripts) - you do not edit the scripts. Create it from the template and fill it in:
```bash
cp .env.example .env
```

```bash
# .env
PROJECT_ID=your-gcp-project-id   # Your GCP project ID (see: gcloud projects list)
REGION=europe-west4              # Deployment region
REPOSITORY=iowa                  # Artifact Registry repository name
IMAGE_TAG=v1
SERVICE_NAME=iowa-backend        # Cloud Run service name
```

Both scripts stop with an error if `.env` is missing or any of these values is empty. The image name is fixed to `iowa-backend`, so the image URL is `${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/iowa-backend:${IMAGE_TAG}`, e.g. `europe-west4-docker.pkg.dev/your-gcp-project-id/iowa/iowa-backend:v1`.

### 2. Build and Push Image

```bash
./build.sh
```

This script:
1. Builds Docker image for `linux/amd64`
2. Tags for Artifact Registry
3. Configures authentication
4. Pushes image (~5-10 minutes)

Check the result in the console: **Artifact Registry → `iowa` → `iowa-backend`**. You should see the tagged index and the ~755 MB image (see [above](#what-you-see-in-artifact-registry)).

### 3. Deploy to Cloud Run

Choose one of the three options. All create the same service.

#### Option A: Web console, starting from Cloud Run

1. Open **Cloud Run** in the GCP console → **Deploy container** → **Service**.
2. **Container image URL** → **Select** → **Artifact Registry** → `iowa` → `iowa-backend` → tag **`v1`**.
3. **Service name**: `iowa-backend`. **Region**: `europe-west4`.
4. **Authentication**: **Allow public access** (unauthenticated invocations).
5. **Billing**: Request-based. **Scaling**: minimum instances **0**, maximum **20**.
6. **Ingress**: **All**.
7. Expand **Containers, Volumes, Networking, Security** → tab **Settings**:
   - **Container port**: `8080`
   - **Memory**: **`2 GiB`** and **CPU**: **`2`** - change both! The form defaults to 512 MiB / 1 CPU, which is too little for AutoGluon (see [Troubleshooting](#troubleshooting)).
   - **Request timeout**: `300` seconds
   - **Maximum concurrent requests per instance**: **`1`** (default 80 - see [Why concurrency 1?](#why-concurrency-1))
   - **Startup CPU boost**: on
8. Click **Create** and wait for the green check mark. The service URL is shown at the top of the service page.

#### Option B: Web console, starting from Artifact Registry

1. Open **Artifact Registry** → repository `iowa` → package `iowa-backend`.
2. Click the version you want to deploy - the one tagged **`v1`** (media type `application/vnd.oci.image.index.v1+json`, see [above](#what-you-see-in-artifact-registry)).
3. Click **Deploy** at the top of the version page → **Deploy to Cloud Run**.
4. The Cloud Run form opens with **Container image URL** already filled in. It usually points to the version by digest (`.../iowa-backend@sha256:fc86b03…`), not by tag. This pins exactly this build: pushing a new `v1` later will not change what this form deploys.
5. Fill in the rest of the form as in **Option A, steps 3-8**. In particular, set **Memory `2 GiB`**, **CPU `2`**, **maximum concurrent requests `1`** and **maximum instances `20`**. The form defaults to 512 MiB / 1 CPU / 80 here too.

You can also click **Deploy** on the image version (`application/vnd.oci.image.manifest.v1+json`, ~755 MB). The result is the same: both versions lead Cloud Run to the same `linux/amd64` image.

#### Option C: Script

```bash
./deploy.sh
```

This script deploys the image to Cloud Run (by tag `IMAGE_TAG` from `.env`) with the same settings as Options A and B:
- `--memory 2Gi` - AutoGluon needs RAM
- `--cpu 2` - Faster predictions
- `--allow-unauthenticated` - Public access (no auth)
- `--port 8080` - Cloud Run's default port
- `--concurrency 1` - One request per instance (see below)
- `--max-instances 20` - Cost control

Get the service URL (the command is also printed at the end of `deploy.sh`):
```bash
gcloud run services describe iowa-backend --project your-gcp-project-id --region europe-west4 --format 'value(status.url)'
```

It looks like:
```
https://iowa-backend-XXXXXXXXXX.europe-west4.run.app
```

Every deploy (Option A, B or C) creates a new **revision** (`iowa-backend-00001-xxx`, `-00002-xxx`, ...); the **Revisions** tab of the service shows them and how traffic is split between them.

#### Why concurrency 1?

`main.py` computes one prediction at a time: `predictor.predict()` blocks the server's event loop for about 1 s, so a second request waits until the first one is finished. Cloud Run does not know that. With the default of **80 concurrent requests per instance**, it sends up to 80 requests to one instance, where 79 of them wait in a queue, and adds instances only slowly. Under load, response times then grow with every new user (observed: median ~52 s at 820 users, 10 instances).

With **concurrency 1**, every request that cannot be served immediately makes Cloud Run start another instance - this is the scale-out the load test in `4. Performance` demonstrates. The limit is **max instances**: when all 20 instances are busy, extra requests wait and eventually fail with *"The request was aborted after waiting too long for an available instance"* (HTTP 429).

### 4. Test

```bash
URL=https://iowa-backend-XXXXXXXXXX.europe-west4.run.app

# Health check
curl -v "$URL/"

# Prediction - the FIRST call on a new instance takes ~40 s, later calls ~1 s
time curl "$URL/predict/BLACK%20VELVET"

# Interactive docs
open "$URL/docs"
```

Why is the first prediction slow? The saved model does not contain the weights of the pretrained foundation models (Chronos2, Toto2). Each new instance downloads them from Hugging Face on its first prediction (~30 s), then they stay in the container's memory. When Cloud Run scales to zero and starts a new instance, the download happens again.

Run the frontend locally against the deployed backend:
```bash
cd ../frontend
API_URL="$URL" uv run streamlit run app.py
```
The frontend waits at most 10 s for a forecast, so warm the backend up with the `curl` prediction above first - otherwise the first click shows *Cannot connect to backend*.

## Cost Estimate

**Free tier** (per month):
- 2M requests
- 360K vCPU-seconds
- 180K GiB-seconds memory

**Example** (10K requests/month, 2s avg response):
- Compute: ~$1.06
- Storage: ~$0.15
- **Total: ~$1.21/month**

Setting **minimum instances to 1** keeps one instance warm (no 40 s first prediction), but it is billed while idle - set it back to 0 when you are done.

## Troubleshooting

**build.sh fails with "Repository not found":**
```bash
# Create the repository first (must match REPOSITORY and REGION in .env)
gcloud artifacts repositories create iowa \
  --repository-format=docker \
  --location=europe-west4 \
  --description="Iowa sales containers"

# Verify it exists
gcloud artifacts repositories list
```

**Read the logs** (or open the service in the console → **Logs**):
```bash
gcloud run services logs read iowa-backend --project your-gcp-project-id --region europe-west4 --limit 50
```

How to read them:
- `Default STARTUP TCP probe succeeded` and `Application startup complete` → the container started and listens on port 8080.
- A line like `"GET /predict/... HTTP/1.1" 200 OK` → requests reach the service.
- **The service is up, but your requests never appear in the logs** → they do not reach Cloud Run at all. Cloud Run logs every request it receives, even failed ones. Check the URL, and check whether your network blocks `*.run.app` (try `curl -v "$URL/"` from another network, e.g. a phone hotspot).

**Common issues:**
- Missing `autogluon-iowa-daily/` → Train model first
- **Deployed from the console with default resources (512 MiB)** → the first prediction needs ~640 MB of RAM, and the downloaded model weights are stored in the container's in-memory filesystem, which also counts against the limit. The instance is killed for exceeding memory. Use **2 GiB**.
- First prediction slow (~40 s) or the frontend times out → expected on a new instance (weights download); warm it up with `curl` or set minimum instances to 1
- `gcloud` reports `invalid_grant` → token expired, run `gcloud auth login`
- Response times keep growing under load, instance count stays low → maximum concurrent requests per instance is still 80; set it to 1 (see [Why concurrency 1?](#why-concurrency-1))
- HTTP 429 *"aborted after waiting too long for an available instance"* / *"Rate exceeded."* → all `max-instances` are busy; reduce the load or raise the limit

**Update deployment:**
```bash
# Change IMAGE_TAG to v2 in .env, then:
./build.sh
./deploy.sh        # or deploy v2 from the console (Option A or B)
```

## Clean Up

```bash
# Delete service (its revisions go with it)
gcloud run services delete iowa-backend --project your-gcp-project-id --region europe-west4

# Delete a tagged image (deletes the index and the tag)
gcloud artifacts docker images delete \
  europe-west4-docker.pkg.dev/your-gcp-project-id/iowa/iowa-backend:v1 --delete-tags
```

Untagged versions left over from re-pushing the same tag can be deleted in the console (**Artifact Registry → `iowa` → `iowa-backend`**, select the untagged rows → **Delete**) or by digest:
```bash
gcloud artifacts docker images delete \
  europe-west4-docker.pkg.dev/your-gcp-project-id/iowa/iowa-backend@sha256:<digest>
```

## Key Differences from Docker

| Feature | Local Docker | Cloud Run |
|---------|--------------|-----------|
| Hosting | Your machine | Google cloud |
| Scaling | Manual | Automatic |
| Cost | Free | ~$1-2/month |
| URL | localhost:8003 | HTTPS with SSL |
| Availability | When PC is on | 99.95% SLA |

## Resources

- Cloud Run docs: https://cloud.google.com/run/docs
- Pricing calculator: https://cloud.google.com/products/calculator
- Quotas: https://cloud.google.com/run/quotas
- OCI image index specification: https://github.com/opencontainers/image-spec/blob/main/image-index.md
