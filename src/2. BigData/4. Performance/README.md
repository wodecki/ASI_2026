# Performance Testing & Auto-Scaling Demo

Compare **local (single container)** vs **serverless (GCP Cloud Run)** performance under load.

## Learning Objective

Demonstrate that **auto-scaling** maintains stable performance while **single containers** become bottlenecks.

| Scenario | Infrastructure | Expected Behavior |
|----------|---------------|-------------------|
| **Test 1: Local** | Single Docker container | Latency **increases** as load grows |
| **Test 2: GCP Run** | Auto-scaling containers | Latency **stays stable**, containers scale 1 → 15-20 |

## Prerequisites

```bash
# Install dependencies
uv sync
```

**For Test 1 (Local)**: Docker image built in `3. Deployment/2-docker`
**For Test 2 (GCP)**: Service deployed in `3. Deployment/4-GCP-Run`, and a `.env` file here (see Test 2, Step 1)

## Test 1: Local (No Auto-Scaling)

### Step 1: Start Docker Container

```bash
# Navigate to Docker backend
cd ../3.\ Deployment/2-docker/backend

# Start container
docker run -d -p 8003:8003 --name iowa_backend iowa-backend:v1

# Wait for model to load (30 seconds)
sleep 30

# Verify it's working
curl http://localhost:8003/items
```

### Step 2: Run Load Test

```bash
# Go back to Performance directory
cd ../../../4.\ Performance

# Start Locust
./test-local.sh
```

### Step 3: Configure Locust

Browser opens at: **http://localhost:8089**

**Settings:**
- **Number of users**: `30-50`
  - Total simulated concurrent users making requests
  - Each user waits 1-3 seconds between requests
  - More users = more load
- **Spawn rate**: `5`
  - How many users to add per second
  - Example: 50 users at rate 5 = takes 10 seconds to ramp up
  - Lower rate = gradual stress increase
- **Host**: Pre-filled as `http://localhost:8003`

Click **Start swarming**

### Step 4: Watch the Breakdown

**What to observe in Locust UI:**

| Users | Median Response Time | What's Happening |
|-------|----------------------|------------------|
| 0-10 | 5-8s | Normal operation |
| 15-20 | 15-25s | Container struggling |
| 25-30 | 30-50s | Severely overwhelmed |
| 35+ | 60s+ timeouts | Complete breakdown |

**Key metrics:**
- **Response times**: Increases dramatically
- **RPS (Requests/second)**: Stays low (~2-4)
- **Failures**: May increase at high load

**Lesson**: Single container = performance **degrades** under load.

## Test 2: GCP Cloud Run (Auto-Scaling)

### Step 1: Configure `.env` and Verify Service Running

`test-gcp.sh` reads its settings from a `.env` file in this directory and stops with an error if any value is missing. Create it from the template:

```bash
cp .env.example .env
```

```bash
# .env
GCP_URL=https://iowa-backend-XXXXXXXXXX.europe-west4.run.app   # your service URL (printed by deploy.sh)
PROJECT_ID=your-gcp-project-id                                 # used for the metrics link
REGION=europe-west4
SERVICE_NAME=iowa-backend
```

If you don't have the URL at hand:
```bash
gcloud run services describe iowa-backend --project your-gcp-project-id --region europe-west4 --format 'value(status.url)'
```

Test if the service is accessible:
```bash
source .env && curl "${GCP_URL}/items"
```

If not deployed, deploy it first:
```bash
cd ../3.\ Deployment/4-GCP-Run/backend
./deploy.sh
cd ../../../4.\ Performance
```

**Check the scaling settings.** The test only shows auto-scaling if the service runs with **1 concurrent request per instance** and **max 20 instances**. `deploy.sh` sets both; if you deployed from the web console, set *Maximum concurrent requests per instance* = `1` and *Maximum instances* = `20` (see [Why concurrency 1?](../3.%20Deployment/4-GCP-Run/backend/README.md#why-concurrency-1)). Verify:
```bash
source .env && gcloud run services describe "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" \
  --format 'yaml(metadata.annotations,spec.template.metadata.annotations,spec.template.spec.containerConcurrency)' \
  | grep -iE 'concurrency|maxScale'
# expected: containerConcurrency: 1, and maxScale: '20'
# (the console stores max instances as run.googleapis.com/maxScale on the service,
#  gcloud as autoscaling.knative.dev/maxScale on the revision template - either counts)
```

**Warm up** one instance (its first prediction downloads the model weights, ~30-40 s):
```bash
source .env && time curl "${GCP_URL}/predict/BLACK%20VELVET"
```

### Step 2: Run Load Test

```bash
./test-gcp.sh
```

### Step 3: Configure Locust

Browser opens at: **http://localhost:8089**

**Settings:**
- **Number of users**: `40-50`
  - More than the local test - a single container cannot handle this
  - Do not go much higher: the service is limited to 20 instances (see [How much load can it take?](#how-much-load-can-it-take))
- **Spawn rate**: `2`
  - Gradual ramp-up (25 s to 50 users), so Cloud Run adds instances as the load grows
- **Host**: Pre-filled with `GCP_URL` from `.env`

Click **Start swarming**

### Step 4: Watch Auto-Scaling

**In Locust UI** (approximate - your numbers will differ):

| Phase | Median Response Time | Container Count | What's Happening |
|-------|----------------------|-----------------|------------------|
| First ~1 min | spikes up to 30-40 s | 1 → 15-20 | New instances start; each one downloads the model weights on its first prediction |
| After warm-up | ~1-3 s | 15-20 | Every request gets its own instance |
| Above ~60 users | grows, HTTP 429 failures | 20 (max) | All instances busy - the limit is reached |

**Key metrics:**
- **Response times**: **stable** after the warm-up phase
- **RPS**: grows with users, ~12-17 at 50 users
- **Failures**: none, as long as you stay below the instance limit

**In GCP Console (open in another tab)** - `test-gcp.sh` prints this link filled in from `.env`:
```
https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}
```

The console metrics lag **about 3 minutes** behind Locust - if the charts look flat, wait and click **Refresh**. Watch:
- **Container instance count**: Goes from 1 → 15-20
- **Request latency (p95)**: High during warm-up, then stable
- **Request count**: Spikes up
- **CPU utilization**: Distributed across containers

For an exact, immediate count of instances that served requests, use the request logs:
```bash
source .env && gcloud logging read \
  "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$SERVICE_NAME\" AND httpRequest.status>0 AND timestamp>=\"$(date -u -v-10M +%Y-%m-%dT%H:%M:%SZ)\"" \
  --project "$PROJECT_ID" --limit 5000 --format 'value(labels.instanceId)' | sort | uniq -c
# one line per instance: number of requests it served in the last 10 minutes
```
(`date -v-10M` is macOS syntax; on Linux use `date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%SZ`.)

**Lesson**: Auto-scaling = performance **stays stable** even under heavy load - up to the instance limit you set.

### How much load can it take?

A back-of-the-envelope estimate that explains the numbers above:
- One warm prediction takes **~1 s** on an instance with 2 CPUs, and one instance serves one request at a time → **~1 request/s per instance**.
- One Locust user sends a request, waits for the response (~1 s), then waits 1-3 s (average 2 s) → **~1 request every 3 s per user**.
- 50 users → ~17 requests/s → **~17 instances** needed. The limit of 20 instances is reached at **~60 users**.

The same arithmetic explains the local test: one container ≈ 1 request/s, so already 10 users (~3 requests/s) build up a queue.

## Understanding Locust Parameters

### Number of Users
- **Definition**: Total simulated concurrent users
- **Real-world**: Each user = one person using your API simultaneously
- **Behavior**: Each user makes requests, waits 1-3 seconds, repeats
- **Recommendation**:
  - Local: 30-50 (demonstrates bottleneck)
  - GCP: 40-50 (demonstrates auto-scaling, stays below the 20-instance limit)

### Spawn Rate
- **Definition**: Users added per second during ramp-up
- **Example**: 50 users, rate 2 = takes 25 seconds to reach full load
- **Purpose**: Simulates gradual traffic increase vs instant spike
- **Recommendation**:
  - Local: 5 users/s (gentle ramp-up)
  - GCP: 2 users/s (gives Cloud Run time to start instances)

### Why Higher Load for GCP?
- A single container is overwhelmed already at 10-20 users
- GCP handles 40-50 users by spawning more containers
- Higher load makes auto-scaling effect **visible**
- Demonstrates true advantage of serverless - and its limit: `max-instances` caps both the scale-out and the cost

## Side-by-Side Comparison

Approximate - your numbers will differ:

| Metric | Local (50 users) | GCP Run (50 users, after warm-up) |
|--------|------------------|-----------------------------------|
| Median Response Time | grows with every user (tens of seconds) | ~1-3 s |
| Max RPS | ~1-2 | ~12-17 |
| Container Count | 1 (fixed) | 1 → 15-20 (dynamic) |
| **Result** | **Breaks down** | **Stays stable** |

## Files

- **`locustfile.py`**: Load test definition (what requests to make)
- **`test-local.sh`**: Test local Docker container
- **`test-gcp.sh`**: Test GCP Cloud Run (reads `.env`)
- **`.env.example`**: Template for `.env` (GCP_URL, PROJECT_ID, REGION, SERVICE_NAME)
- **`pyproject.toml`**: Dependencies (Locust)

## Troubleshooting

**Local test: Connection refused**
```bash
# Check container is running
docker ps --filter name=iowa_backend

# Check logs
docker logs iowa_backend

# Restart if needed
docker restart iowa_backend
sleep 30
```

**Many failures with HTTP 404**
- The product names in `locustfile.py` must match the model's products; compare with `curl "${GCP_URL}/items"`

**GCP test: response times keep growing, instance count stays low**
- The service still runs with the default 80 concurrent requests per instance: one instance takes 80 requests but computes them one by one. Redeploy with `--concurrency 1` (`deploy.sh`) or set it in the console
- The console metrics lag ~3 minutes: check the instance count with the `gcloud logging` command from Test 2, Step 4

**GCP test: HTTP 429 / "Rate exceeded." / "aborted after waiting too long for an available instance"**
- All `max-instances` (20) are busy - reduce the number of users

**GCP test: 503 errors or very slow first requests**
- Cold start: each new instance downloads the model weights on its first prediction (~30-40 s)
- Check service has 2Gi memory in GCP Console

**Locust won't start**
```bash
uv sync  # Reinstall dependencies
```

**`.venv/bin/locust: ... .venv/bin/python: No such file or directory`**
- The folder was moved or renamed after `uv sync`: the scripts in `.venv/bin` contain the old absolute path. Rewrite them:
```bash
uv sync --reinstall
```

## Cost Warning

GCP charges for the time instances are busy: 20 instances × 2 vCPU for 5 minutes ≈ 12,000 vCPU-seconds, which fits in the monthly free tier (360,000 vCPU-seconds) - but every test uses some of it.

Keep tests short (3-5 minutes) for demos, and **stop Locust** when you are done.

## Clean Up

**Stop local container:**
```bash
docker stop iowa_backend
docker rm iowa_backend
```

**GCP**: Auto-scales to zero after traffic stops (no action needed).

## Educational Takeaways

1. **Single container** = bottleneck → Performance degrades linearly with load
2. **Auto-scaling** = resilience → Performance stays stable, cost scales with usage
3. **Serverless** advantages:
   - No capacity planning needed
   - Handles traffic spikes automatically
   - Pay only for actual usage
4. **Trade-offs**:
   - Local: Free, but doesn't scale
   - GCP: Costs money, handles load up to the `max-instances` limit you set
