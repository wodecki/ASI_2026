# Performance Testing & Auto-Scaling Demo

Compare **local (single container)** vs **serverless (GCP Cloud Run)** performance under load.

## Learning Objective

Demonstrate that **auto-scaling** maintains stable performance while **single containers** become bottlenecks.

| Scenario | Infrastructure | Expected Behavior |
|----------|---------------|-------------------|
| **Test 1: Local** | Single Docker container | Latency **increases** as load grows |
| **Test 2: GCP Run** | Auto-scaling containers | Latency **stays stable**, containers scale 1 → 15 |

## Prerequisites

```bash
# Install dependencies
uv sync
```

**For Test 1 (Local)**: Docker image built in `3. Deployment/2-docker`
**For Test 2 (GCP)**: Service deployed in `3. Deployment/3-GCP-Run`

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

### Step 1: Verify Service Running

```bash
# Test if service is accessible
curl https://iowa-backend-850710718243.europe-west4.run.app/items
```

If not deployed, deploy it first:
```bash
cd ../3.\ Deployment/3-GCP-Run/backend
./deploy.sh
cd ../../4.\ Performance
```

### Step 2: Run Load Test

```bash
./test-gcp.sh
```

### Step 3: Configure Locust

Browser opens at: **http://localhost:8089**

**Settings (STRONGER LOAD):**
- **Number of users**: `80-100`
  - Much higher than local test to demonstrate auto-scaling
  - Single container couldn't handle this
- **Spawn rate**: `10`
  - Faster ramp-up to trigger auto-scaling quickly
  - GCP detects load and spawns containers
- **Host**: Pre-filled as `https://iowa-backend-850710718243.europe-west4.run.app`

Click **Start swarming**

### Step 4: Watch Auto-Scaling

**In Locust UI:**

| Users | Median Response Time | Container Count | What's Happening |
|-------|----------------------|-----------------|------------------|
| 0-20 | 8-12s | 1-2 | Initial containers |
| 30-50 | 8-10s | 3-6 | Scaling up |
| 60-80 | 7-9s | 8-12 | Fully scaled |
| 100 | 7-9s | 12-15 | Stable performance |

**Key metrics:**
- **Response times**: Stays **stable** (~7-10s)
- **RPS**: Increases to ~12-15
- **Failures**: Minimal (<1%)

**In GCP Console (open in another tab):**
```
https://console.cloud.google.com/run/detail/europe-west4/iowa-backend-2/metrics
```

Watch:
- **Container instance count**: Goes from 1 → 12-15
- **Request latency (p95)**: Stays stable
- **Request count**: Spikes up
- **CPU utilization**: Distributed across containers

**Lesson**: Auto-scaling = performance **stays stable** even under heavy load.

## Understanding Locust Parameters

### Number of Users
- **Definition**: Total simulated concurrent users
- **Real-world**: Each user = one person using your API simultaneously
- **Behavior**: Each user makes requests, waits 1-3 seconds, repeats
- **Recommendation**:
  - Local: 30-50 (demonstrates bottleneck)
  - GCP: 80-100 (demonstrates auto-scaling power)

### Spawn Rate
- **Definition**: Users added per second during ramp-up
- **Example**: 100 users, rate 10 = takes 10 seconds to reach full load
- **Purpose**: Simulates gradual traffic increase vs instant spike
- **Recommendation**:
  - Local: 5 users/s (gentle ramp-up)
  - GCP: 10 users/s (faster, triggers auto-scaling)

### Why Higher Load for GCP?
- Single container fails at 30-40 users
- GCP can handle 100+ users by spawning more containers
- Higher load makes auto-scaling effect **visible**
- Demonstrates true advantage of serverless

## Side-by-Side Comparison

| Metric | Local (50 users) | GCP Run (100 users) |
|--------|------------------|---------------------|
| Median Response Time | 25-40s | 7-10s |
| 95th Percentile | 60s+ | 12-15s |
| Max RPS | 2-4 | 12-15 |
| Container Count | 1 (fixed) | 1 → 15 (dynamic) |
| Failures | 10-20% | <1% |
| **Result** | **Breaks down** | **Stays stable** |

## Files

- **`locustfile.py`**: Load test definition (what requests to make)
- **`test-local.sh`**: Test local Docker container
- **`test-gcp.sh`**: Test GCP Cloud Run
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

**GCP test: 503 errors**
- First requests may be slow (cold start)
- Wait 30-60 seconds for warm-up
- Check service has 2Gi memory in GCP Console

**Locust won't start**
```bash
uv sync  # Reinstall dependencies
```

## Cost Warning

GCP charges for requests:
- 1,000 requests ≈ $0.01
- 10,000 requests ≈ $0.10

Keep tests short (3-5 minutes) for demos.

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
   - GCP: Costs money, but handles any load
