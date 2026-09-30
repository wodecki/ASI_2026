# Deploy on GCP VM with External Disk

Educational demonstration of **cloud disk portability** - attach your codebase disk to different VMs for flexible compute scaling.

## Learning Objectives

This guide demonstrates a fundamental cloud computing pattern: **separation of compute and storage**.

**The Concept:**
1. **Boot disk** (small, 10GB) - Operating system only
2. **Data disk** (large, 100GB) - Your code, models, and data
3. **Portability** - Detach data disk from weak VM, attach to powerful VM

**Why This Matters:**
- Train models on expensive GPU VM, then move to cheap CPU VM for inference
- Develop on small VM, test on production-sized VM
- Your work persists even if VM is deleted
- Pay for compute only when needed

**Real-World Scenario:**
- **asi-micro** (e2-micro, 2 vCPU, 1GB RAM) - Initial development, low cost
- **asi-macro** (e2-standard-4, 4 vCPU, 16GB RAM) - Heavy training, higher performance

Same disk, different VMs, zero data migration!

---

## Prerequisites

- **GCP account** with billing enabled
- **External disk** `disk-20251107-123056` (100GB, created in `europe-west4-a`)
- **Two VMs** (or create them as needed):
  - `asi-micro` (e2-micro) - Initial setup
  - `asi-macro` (e2-standard-4) - Stronger compute
- SSH access

---

# Part 1: Initial Setup on Small VM (asi-micro)

This section covers first-time setup: format disk, install dependencies, train model.

---

## Step 1: Attach External Disk to VM

The external disk must be attached to the running VM.

### Option A: Via Web Console

1. Go to **Compute Engine** > **Disks**
2. Click on `disk-20251107-123056`
3. Click **ATTACH** (top menu)
4. Select VM: `asi-micro`
5. Mode: **Read/write**
6. Click **ATTACH**

### Option B: Via gcloud CLI

```bash
gcloud compute instances attach-disk asi-micro \
  --disk disk-20251107-123056 \
  --zone europe-west4-a
```

**Verify attachment:**
```bash
# SSH into VM
gcloud compute ssh asi-micro --zone europe-west4-a

# List attached disks
lsblk
```

Example output:
```
NAME    MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda       8:0    0  100G  0 disk              <- External disk (not mounted)
sdb       8:16   0   10G  0 disk              <- Boot disk
├─sdb1    8:17   0  9.9G  0 part /
├─sdb14   8:30   0    3M  0 part
└─sdb15   8:31   0  124M  0 part /boot/efi
```

**IMPORTANT**: Identify the 100GB disk (external) vs 10GB disk (boot):
- Look for the **100G** disk with **no MOUNTPOINTS** - this is your external disk
- In this example: `/dev/sda` is the external disk

---

## Step 2: Format and Mount External Disk

**CRITICAL**: Use the correct device name! Check `lsblk` output first.

In this guide, we assume `/dev/sda` is the 100GB external disk. **If your output shows a different name, adjust commands accordingly.**

### Identify the external disk device name

```bash
# Show all disks with sizes
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS

# Identify which device is 100GB and not mounted
# Common names: /dev/sda, /dev/sdc, /dev/nvme0n1
```

**For this example, we'll use `/dev/sda`** (100GB external disk).

### Check if disk is formatted

```bash
# Check disk filesystem (replace /dev/sda if needed)
sudo file -s /dev/sda
```

**Interpretation:**
- Output: `/dev/sda: data` → Disk is **not formatted** (proceed to format)
- Output: `/dev/sda: Linux rev 1.0 ext4 filesystem` → Disk is **already formatted** (skip to mounting)
- Output: `/dev/sda: DOS/MBR boot sector` → This is the **boot disk** (WRONG DISK! Check lsblk again)

### Format disk (first time only)

**WARNING**: This erases all data on the disk!

```bash
# Format as ext4 (replace /dev/sda with your external disk)
sudo mkfs.ext4 -m 0 -F -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/sda
```

### Create mount point and mount

```bash
# Create directory
sudo mkdir -p /mnt/data

# Mount disk (replace /dev/sda with your external disk)
sudo mount -o discard,defaults /dev/sda /mnt/data

# Change ownership to your user
sudo chown -R $USER:$USER /mnt/data

# Verify mount
df -h | grep /mnt/data
```

Expected output:
```
/dev/sda         98G   24K   93G   1% /mnt/data
```

### Auto-mount on reboot

```bash
# Get disk UUID (replace /dev/sda with your external disk)
sudo blkid /dev/sda

# Output example: /dev/sda: UUID="abc123..." TYPE="ext4"
# Copy the UUID value (the long string in quotes)

# Edit fstab
sudo nano /etc/fstab

# Add this line at the end (replace UUID with your actual UUID):
UUID=abc123-your-uuid-here /mnt/data ext4 discard,defaults,nofail 0 2

# Save and exit (Ctrl+O, Enter, Ctrl+X)

# Test fstab (mounts all entries)
sudo mount -a

# Verify it worked
df -h | grep /mnt/data
```

---

## Step 3: Install System Dependencies

### Update system and install Python 3.11

```bash
# Update package list
sudo apt update

# Install Python 3.11 and essentials
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
  build-essential git curl

# Verify Python version
python3.11 --version  # Should show 3.11.x
```

### Install uv (package manager)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# The installer installs to $HOME/.local/bin
# Add to PATH (choose one method):

# Method 1: Source the env file created by installer
source $HOME/.local/bin/env

# Method 2: Manually add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Make PATH permanent
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Verify installation
uv --version
```

**Troubleshooting**: If `uv --version` fails:

```bash
# Check where uv was installed
which uv
ls -la $HOME/.local/bin/uv

# Check installer output - it tells you the correct path
# Common locations:
#   - $HOME/.local/bin/uv (most common)
#   - $HOME/.cargo/bin/uv (older versions)

# Add correct path
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

---

## Step 4: Clone Repository to External Disk

```bash
# Navigate to external disk
cd /mnt/data

# Clone repository
git clone https://github.com/YOUR_USERNAME/ASI_2025.git

# Navigate to backend directory
cd ASI_2025/src/2.\ BigData/3.\ Deployment/1-local/backend
```

---

## Step 5: Setup and Train Model

### Install dependencies

```bash
# Initialize uv environment (uses Python 3.11)
uv sync
```

### Train the model

**IMPORTANT**: Training takes significant disk space (~2-5GB) and time (~5-15 minutes).

```bash
# Train model (creates autogluon-iowa-daily/ directory)
uv run python "0. train.py"
```

**Verify model was created:**
```bash
ls -lh autogluon-iowa-daily/
# Should show predictor.pkl, learner.pkl, models/, etc.
```

---

## Step 6: Open Firewall for API Access

The API runs on port **8003**. You need to open this port in GCP firewall.

### Create firewall rule

```bash
gcloud compute firewall-rules create allow-iowa-api \
  --allow tcp:8003 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow Iowa Sales Predictor API"
```

**Verify rule:**
```bash
gcloud compute firewall-rules list --filter="name=allow-iowa-api"
```

---

## Step 7: Run the API Service

### Get VM external IP

```bash
gcloud compute instances describe asi-micro \
  --zone europe-west4-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

**Example output**: `34.91.123.456`

### Start the API server

```bash
# Navigate to backend directory
cd /mnt/data/ASI_2025/src/2.\ BigData/3.\ Deployment/1-local/backend

# Start server
uv run uvicorn main:app --host 0.0.0.0 --port 8003
```

**Server is now running!**

---

## Step 8: Test the API

From your **local machine**:

```bash
# Replace with your VM's external IP
export VM_IP=34.91.123.456

# Health check
curl http://$VM_IP:8003/

# Get available items
curl http://$VM_IP:8003/items

# Get predictions
curl http://$VM_IP:8003/predict/BLACK%20VELVET
```

**Expected response:**
```json
{
  "item": "BLACK VELVET",
  "predictions": [
    {"timestamp": "2024-11-07", "date": "2024-11-07", "mean": 123.45},
    ...
  ]
}
```

---

## Step 9: Run as Background Service (Optional)

To keep the API running after you disconnect from SSH:

### Option A: Using screen

```bash
# Install screen
sudo apt install -y screen

# Create screen session
screen -S iowa-api

# Start server
cd /mnt/data/ASI_2025/src/2.\ BigData/3.\ Deployment/1-local/backend
uv run uvicorn main:app --host 0.0.0.0 --port 8003

# Detach from screen: Ctrl+A, then D
# Reattach later: screen -r iowa-api
# List sessions: screen -ls
```

### Option B: Using systemd service

Create service file:

```bash
sudo nano /etc/systemd/system/iowa-api.service
```

Add content:

```ini
[Unit]
Description=Iowa Sales Predictor API
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/mnt/data/ASI_2025/src/2. BigData/3. Deployment/1-local/backend
Environment="PATH=/home/YOUR_USERNAME/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/YOUR_USERNAME/.cargo/bin/uv run uvicorn main:app --host 0.0.0.0 --port 8003
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_USERNAME` with your actual username!**

Enable and start service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable iowa-api

# Start service
sudo systemctl start iowa-api

# Check status
sudo systemctl status iowa-api

# View logs
sudo journalctl -u iowa-api -f
```

---

## Troubleshooting

### Disk not showing up

```bash
# Check if disk is attached
lsblk

# Check kernel messages
sudo dmesg | grep sd

# Re-scan SCSI bus
echo "- - -" | sudo tee /sys/class/scsi_host/host*/scan
```

### Out of disk space

```bash
# Check disk usage
df -h

# If boot disk is full, ensure you're working on /mnt/data
pwd  # Should show /mnt/data/...

# Clean up if needed
sudo apt autoremove -y
sudo apt clean
```

### API not accessible from internet

```bash
# Check if service is running (on the VM via SSH)
sudo lsof -i :8003

# Check firewall rule exists (from local machine)
gcloud compute firewall-rules list --filter="name=allow-iowa-api"

# Check VM tags match firewall rule (replace VM_NAME)
gcloud compute instances describe VM_NAME --zone europe-west4-a --format='get(tags.items[])'

# If needed, add network tag (replace VM_NAME)
gcloud compute instances add-tags VM_NAME --tags=http-server,https-server --zone europe-west4-a
```

### Disk shows as "data" instead of "ext4" on new VM

```bash
# This means you accidentally formatted a boot disk or wrong disk!
# Double-check disk size
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS

# The 100GB disk should be /dev/sda (or /dev/sdc)
# The 10GB disk is the boot disk - DO NOT TOUCH!

# If you formatted the wrong disk, restore from snapshot or start over
```

### Python version mismatch

```bash
# Check Python version
python3.11 --version

# If not 3.11, install it
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Force uv to use Python 3.11
uv sync --python python3.11
```

---

## Cost Optimization

### Stop VMs when not in use

```bash
# Stop current VM (keeps disk attached)
gcloud compute instances stop asi-micro --zone europe-west4-a

# Or stop the stronger VM
gcloud compute instances stop asi-macro --zone europe-west4-a

# Start VM
gcloud compute instances start asi-micro --zone europe-west4-a

# After start, remount disk if needed
sudo mount -a
```

**Note**: Boot disk charges even when stopped. External disk charges for storage only.

### Delete expensive VMs, keep disk

**Strategy**: Delete expensive VMs when not needed, keep only the disk with your data.

```bash
# Scenario: Training completed on asi-macro, switch back to cheap VM

# 1. Stop and detach from asi-macro
gcloud compute instances stop asi-macro --zone europe-west4-a
gcloud compute instances detach-disk asi-macro --disk disk-20251107-123056 --zone europe-west4-a

# 2. DELETE the expensive VM (saves ~$120/month!)
gcloud compute instances delete asi-macro --zone europe-west4-a

# 3. Attach disk back to cheap VM
gcloud compute instances attach-disk asi-micro --disk disk-20251107-123056 --zone europe-west4-a

# 4. SSH and mount
gcloud compute ssh asi-micro --zone europe-west4-a
sudo mount /dev/sda /mnt/data

# Your models are still there! Only paying ~$7/month for VM + $10/month for disk.
```

**Monthly costs:**
- asi-micro + 100GB disk = ~$17/month
- asi-macro + 100GB disk = ~$130/month
- Disk only (no VM) = ~$10/month

---

# Part 2: Switching to Stronger VM (asi-macro)

This demonstrates **disk portability** - move your entire workspace to a more powerful VM without re-cloning or re-training!

**Scenario**: You've been developing on `asi-micro` (cheap, slow). Now you need more power for production or heavy workloads. **Solution**: Move disk to `asi-macro` (expensive, fast).

---

## Step 1: Safely Detach Disk from asi-micro

### Stop the API service (if running)

```bash
# SSH into asi-micro
gcloud compute ssh asi-micro --zone europe-west4-a

# If using screen
screen -ls
screen -r iowa-api  # Reattach to session
# Press Ctrl+C to stop server
# Press Ctrl+A, then D to detach

# If using systemd
sudo systemctl stop iowa-api
```

### Unmount the disk (CRITICAL!)

**IMPORTANT**: Never detach a mounted disk - you'll corrupt data!

```bash
# Verify disk is mounted
df -h | grep /mnt/data

# Unmount safely
sudo umount /mnt/data

# Verify it's unmounted
df -h | grep /mnt/data  # Should return nothing

# Exit SSH session
exit
```

### Stop the VM

```bash
# Stop asi-micro (from your local machine)
gcloud compute instances stop asi-micro --zone europe-west4-a

# Wait for VM to stop
gcloud compute instances describe asi-micro --zone europe-west4-a --format='get(status)'
# Should show: TERMINATED
```

### Detach the disk

**Via Web Console:**
1. Go to **Compute Engine** > **Disks**
2. Click `disk-20251107-123056`
3. If "In use by" shows `asi-micro`, click **DETACH** (wait for VM to stop first)
4. Disk status should change to "Ready"

**Via gcloud CLI:**

```bash
gcloud compute instances detach-disk asi-micro \
  --disk disk-20251107-123056 \
  --zone europe-west4-a
```

---

## Step 2: Create Stronger VM (if needed)

If `asi-macro` doesn't exist yet:

```bash
gcloud compute instances create asi-macro \
  --zone=europe-west4-a \
  --machine-type=e2-standard-4 \
  --boot-disk-size=10GB \
  --boot-disk-type=pd-balanced \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud
```

**Machine types comparison:**
- `e2-micro`: 2 vCPU, 1GB RAM (~$7/month)
- `e2-standard-4`: 4 vCPU, 16GB RAM (~$120/month)

**Cost tip**: Only run powerful VMs when needed!

---

## Step 3: Attach Disk to asi-macro

**Via Web Console:**
1. Go to **Compute Engine** > **Disks**
2. Click `disk-20251107-123056`
3. Click **ATTACH**
4. Select VM: `asi-macro`
5. Mode: **Read/write**
6. Click **ATTACH**

**Via gcloud CLI:**

```bash
gcloud compute instances attach-disk asi-macro \
  --disk disk-20251107-123056 \
  --zone europe-west4-a
```

---

## Step 4: Mount Disk on asi-macro

**CRITICAL**: Do NOT format! Your code and models are already there.

```bash
# SSH into new VM
gcloud compute ssh asi-macro --zone europe-west4-a

# Check disk is attached
lsblk
# You should see the 100GB disk (e.g., /dev/sda)

# VERIFY disk has data (DO NOT FORMAT!)
sudo file -s /dev/sda
# Should show: "Linux rev 1.0 ext4 filesystem"
# If it shows "data", something went wrong!

# Create mount point
sudo mkdir -p /mnt/data

# Mount the disk (replace /dev/sda with your 100GB disk)
sudo mount -o discard,defaults /dev/sda /mnt/data

# Verify mount
df -h | grep /mnt/data

# Check your files are there
ls -la /mnt/data
# You should see: ASI_2025/ directory with all your code!
```

### Auto-mount on reboot

```bash
# Get disk UUID
sudo blkid /dev/sda

# Edit fstab
sudo nano /etc/fstab

# Add line (replace UUID with your actual UUID):
UUID=your-uuid-here /mnt/data ext4 discard,defaults,nofail 0 2

# Save and test
sudo mount -a
```

---

## Step 5: Install Dependencies on asi-macro

Even though your code is on the disk, the NEW VM needs Python and uv installed.

```bash
# Update system
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
  build-essential git curl

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH (installs to $HOME/.local/bin)
source $HOME/.local/bin/env
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Verify
python3.11 --version
uv --version
```

---

## Step 6: Run API on asi-macro

```bash
# Navigate to backend directory
cd /mnt/data/ASI_2025/src/2.\ BigData/3.\ Deployment/1-local/backend

# Verify model exists (NO RE-TRAINING NEEDED!)
ls -la autogluon-iowa-daily/
# Should show: predictor.pkl, models/, etc.

# Install dependencies (fast - using existing uv.lock)
uv sync

# Start API server
uv run uvicorn main:app --host 0.0.0.0 --port 8003
```

**That's it!** Your API is now running on the stronger VM with zero re-training.

---

## Step 7: Open Firewall (if needed)

If firewall rule doesn't exist yet:

```bash
gcloud compute firewall-rules create allow-iowa-api \
  --allow tcp:8003 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow Iowa Sales Predictor API"
```

---

## Step 8: Test on New VM

```bash
# Get new VM's external IP
gcloud compute instances describe asi-macro \
  --zone europe-west4-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

# Test from your local machine (replace IP)
export VM_IP=34.91.NEW.IP

curl http://$VM_IP:8003/
curl http://$VM_IP:8003/predict/BLACK%20VELVET
```

**Success!** Same API, different VM, zero downtime for data migration.

---

## What Just Happened?

**You demonstrated:**
- ✓ Disk portability across VMs
- ✓ Separation of compute and storage
- ✓ Zero data migration (disk moved, not copied)
- ✓ No re-training needed (model persists on disk)
- ✓ Flexible compute scaling (micro → standard-4)

**Time saved:**
- No re-cloning repository
- No re-installing dependencies on disk
- No re-training models
- Only reinstalled: OS-level packages (Python, uv)

---

# Educational Takeaways

## Key Concepts Demonstrated

### 1. Separation of Compute and Storage
- **Boot disk** (ephemeral, OS-specific) vs. **Data disk** (persistent, portable)
- OS and system packages live on boot disk
- Application, code, models live on data disk

### 2. Cloud Flexibility
- Same data disk works with different VM sizes
- Pay for powerful compute only when needed
- Scale up for training, scale down for inference

### 3. Disk Attachment Rules
- Disk can attach to **ONE VM at a time** (exclusive access)
- Disk and VM must be in **same zone** (or use regional disk)
- Always **unmount before detaching** (data safety)
- **Never format an attached disk** unless intentional

### 4. Cost Optimization Strategies
- Develop on cheap VM (`e2-micro` ~$7/month)
- Train on expensive VM (`e2-standard-4` ~$120/month)
- Delete expensive VM after training
- Keep only disk ($10/month for 100GB)
- Recreate expensive VM only when needed

### 5. Production Patterns
- Disk snapshots for backups
- Regional persistent disks for cross-zone availability
- Cloud Storage for model registry
- Container images (Docker) for even more portability

---

## Comparison: VM Types

| VM Type | vCPU | RAM | Cost/month | Use Case |
|---------|------|-----|------------|----------|
| e2-micro | 2 | 1 GB | ~$7 | Development, testing |
| e2-small | 2 | 2 GB | ~$15 | Light workloads |
| e2-standard-4 | 4 | 16 GB | ~$120 | Training, production |
| n1-standard-16 | 16 | 60 GB | ~$570 | Heavy training |

**External disk**: ~$10/month for 100GB (regardless of VM)

---

## Summary

**What you've learned:**
- How to attach/detach persistent disks in GCP
- Portable workspace pattern (disk + VM flexibility)
- Cost-effective compute scaling
- Production-ready deployment patterns

**What you've deployed:**
- FastAPI REST API serving AutoGluon time series predictions
- Portable across different VM sizes
- Accessible via `http://<EXTERNAL_IP>:8003`

**Endpoints:**
- `GET /` - Health check
- `GET /items` - List available products
- `GET /predict/{item_name}` - Get 7-day forecast

**Disk layout:**
- `/` (10GB boot disk) - OS, Python, uv
- `/mnt/data` (100GB external disk) - Code, models, data (portable!)

**Production considerations:**
- Add HTTPS with Let's Encrypt
- Set up monitoring (CPU, memory, disk)
- Configure automatic backups (disk snapshots)
- Add authentication to API
- Use systemd service for auto-restart
- Consider Docker for even more portability
