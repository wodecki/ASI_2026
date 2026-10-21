# GCP VM Setup Guide - ASI 2025 Course

## Overview
This guide walks you through creating and connecting to a Google Cloud Platform (GCP) Virtual Machine for the ASI 2026 course. You will learn four different methods to access your VM: browser-based SSH, the gcloud command-line interface (CLI), plain SSH from your terminal (without gcloud), and Visual Studio Code.

**Prerequisites:**
- A Google Cloud Platform account with billing enabled
- Administrative access to your local machine (Mac/Linux/Windows)
- VS Code installed (for the VS Code connection method)

---

## Part 1: Create Your GCP Project and VM

### Step 1: Set Up the GCP Project

1. Navigate to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project named `ASI_2026` (or use existing if already created)
3. Ensure billing is enabled for this project
4. Note your **project ID** (shown next to the project name in the project picker; GCP usually appends a suffix, e.g. `asi-2026-123456`). Commands in this course use the placeholder `your-gcp-project-id` — replace it with your own project ID.

### Step 2: Create a Virtual Machine Instance

1. In the GCP Console, navigate to **Compute Engine > VM Instances**
2. Click **Create Instance**
3. Configure your VM with the following settings:
   - **Name:** `asi-micro`
   - **Region:** `europe-west4`
   - **Zone:** `europe-west4-a`
   - **Machine type:** Select based on your needs (e.g., `e2-micro` for testing, higher specs for ML workloads)
   - **Boot disk:** Ubuntu 22.04 LTS (or latest stable version)
   - Leave other settings at defaults unless specific requirements exist
4. Click **Create**
5. Wait for the VM to finish provisioning (green checkmark will appear)

**Verification:** You should see your `asi-micro` instance listed with a green status indicator and an external IP address.

---

## Part 2: Connection Method 1 - SSH in Browser (Quickest Method)

This is the simplest method, requiring no local configuration.

### Steps:

1. In the GCP Console, navigate to **Compute Engine > VM Instances**
2. Locate your `asi-micro` instance
3. Click the **SSH** button in the "Connect" column
4. A new browser window will open with a terminal connected to your VM

**Verification:** You should see a terminal prompt like `username@asi-micro:~$`

**Use Case:** Quick access, troubleshooting, or when you don't have CLI tools configured.

---

## Part 3: Connection Method 2 - gcloud CLI (Command Line)

This method uses Google's `gcloud` command-line tool for more powerful management capabilities.

### Step 1: Install gcloud CLI

1. Download the Google Cloud SDK:
   - **Mac:** Visit [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
   - Or use Homebrew: `brew install google-cloud-sdk`
2. Follow the installation instructions for your operating system

### Step 2: Initialize and Authenticate

Run the following commands in your terminal:

```bash
# Initialize gcloud configuration
gcloud init
```

You will be prompted to:
- Log in to your Google account
- Select the `ASI-2026` project
- Set a default compute zone (choose `europe-west4-a`)

```bash
# Authenticate your account
gcloud auth login
```

This will open a browser window for authentication. Complete the login process.

### Step 3: Verify Configuration

```bash
# List all VM instances in your project
gcloud compute instances list
```

**Expected Output:**
```
NAME       ZONE            MACHINE_TYPE  PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP     STATUS
asi-micro  europe-west4-a  e2-micro                   10.x.x.x     34.141.xxx.xxx  RUNNING
```

### Step 4: Connect via SSH

**Option A - Simple connection:**
```bash
gcloud compute ssh asi-micro --zone=europe-west4-a --project=your-gcp-project-id
```

**Option B - Get the exact command from GCP Console:**
1. In the GCP Console, click the **three dots** next to your VM's SSH button
2. Select **View gcloud command**
3. Copy and paste the command into your terminal

**Verification:** You should see a terminal prompt like `username@asi-micro:~$`

### Step 5: Manage VM Instance (Start/Stop)

```bash
# Stop the VM (to save costs when not in use)
gcloud compute instances stop asi-micro --zone=europe-west4-a

# Start the VM
gcloud compute instances start asi-micro --zone=europe-west4-a

# Check status
gcloud compute instances list
```

**Important:** Always stop your VM when not in use to avoid unnecessary charges.

---

## Part 4: Connection Method 3 - SSH from Your Terminal (without gcloud)

This method uses your own SSH key and the standard `ssh` client (Terminal on Mac/Linux, PowerShell on Windows). Once the key is on the VM, you don't need gcloud at all. The VS Code method (Part 5) uses the same key.

### Step 1: Generate SSH Key Pair

On Your local computer (e.g. MacBook) open your terminal and run:

```bash
# Generate a new SSH key pair
# Identify your_username by SSH to Your GCP VM first and asking "who am i"
ssh-keygen -t rsa -f ~/.ssh/asi-micro -C your_username
```

When prompted:
- **Enter passphrase:** Press Enter for no passphrase (or set one for added security)
- **Enter same passphrase again:** Press Enter again

**Verification:** Two files should be created:
- `~/.ssh/asi-micro` (private key)
- `~/.ssh/asi-micro.pub` (public key)

### Step 2: Copy Your Public Key

Display your public key:

```bash
cat ~/.ssh/asi-micro.pub
```

**Copy the entire output** - it should look like:
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... your_username
```

### Step 3: Add SSH Key to Your GCP VM

1. Close any open **SSH-in-browser** windows for this VM (they change the VM's SSH keys in the background, see Troubleshooting)
2. In GCP Console, navigate to **Compute Engine > VM Instances**
3. Click on your `asi-micro` instance name
4. Click **Edit** at the top
5. Scroll down to **SSH Keys**
6. Click **Add Item**
7. Paste your public key (from Step 2)
8. Click **Save** at the bottom

**Verification:** On the VM details page, your key is listed under **SSH Keys**.

**Important:** Your username on the VM is the last part of the key, the comment you set with `-C` (e.g., `andrzej_wodecki`). You'll need it in the next steps.

### Step 4: Find the VM's External IP

In GCP Console, go to **Compute Engine > VM Instances** and note the **External IP** of `asi-micro` (e.g., `34.141.222.22`).

### Step 5: Connect via SSH

```bash
ssh -i ~/.ssh/asi-micro your_username@34.141.222.22
```

**Replace:**
- `your_username` with your username (from the SSH key)
- `34.141.222.22` with your VM's actual external IP

On the first connection, `ssh` asks whether you trust the host. Type `yes`.

**Verification:** You should see a terminal prompt like `your_username@asi-micro:~$`

### Step 6 (Optional): Add a Shortcut in `~/.ssh/config`

Add this entry to `~/.ssh/config` (create the file if it doesn't exist):

```
Host GCP-asi-micro
    HostName 34.141.222.22
    User your_username
    IdentityFile ~/.ssh/asi-micro
```

Now `ssh GCP-asi-micro` is enough. VS Code (Part 5) uses the same entry.

---

## Part 5: Connection Method 4 - Visual Studio Code (Best for Development)

This method integrates your VM directly into VS Code, allowing you to edit files, run code, and debug as if working locally. It needs the SSH key from Part 4, Steps 1–3.

### Step 1: Install VS Code Extension

1. Open Visual Studio Code
2. Go to Extensions (Cmd+Shift+X on Mac, Ctrl+Shift+X on Windows)
3. Search for **Remote - SSH**
4. Install the extension by Microsoft

### Step 2: Configure VS Code SSH Connection

If you already added the `GCP-asi-micro` entry in Part 4, Step 6, skip to Step 3.


1. Get your VM's external IP address:
   ```bash
   gcloud compute instances list
   ```
   Note the `EXTERNAL_IP` value (e.g., `34.141.222.22`)

2. In VS Code, press **Cmd+Shift+P** (Mac) or **Ctrl+Shift+P** (Windows)
3. Type and select: **Remote-SSH: Open SSH Configuration File**
4. Select your user config file (usually `~/.ssh/config`)
5. Add the following configuration:

```
Host GCP-asi-micro
    HostName 34.141.222.22
    User wodecki
    IdentityFile ~/.ssh/asi-micro
```

**Replace:**
- `34.141.222.22` with your VM's actual external IP
- `wodecki` with your actual username (from the SSH key)

6. Save the file (Cmd+S / Ctrl+S)

### Step 3: Connect from VS Code

1. Press **Cmd+Shift+P** (Mac) or **Ctrl+Shift+P** (Windows)
2. Type and select: **Remote-SSH: Connect to Host**
3. Select **GCP-asi-micro** from the list
4. A new VS Code window will open
5. When prompted "Select the platform of the remote host", choose **Linux**
6. Wait for VS Code to complete the connection and install the VS Code Server

**Verification:**
- The bottom-left corner should show: `SSH: GCP-asi-micro`
- You can now open folders on your VM: **File > Open Folder** and browse `/home/your_username`

---

## Troubleshooting

### Issue: "Permission denied (publickey)" when connecting

**Solution:**
- Verify your SSH key is correctly added to the VM in GCP Console
- Check that the username in your SSH config matches the one in your public key
- Ensure the private key file has correct permissions: `chmod 600 ~/.ssh/asi-micro`

### Issue: "Supplied fingerprint does not match current metadata fingerprint" when saving the SSH key

**Cause:** The VM's SSH keys changed while your Edit page was open. The browser **SSH** button adds temporary keys to the VM each time you use it.

**Solution:**
- Close SSH-in-browser windows for this VM
- Reload the VM details page, click **Edit** again, paste your key and **Save**

### Issue: VS Code connection times out

**Solution:**
- Verify your VM is running: `gcloud compute instances list`
- Check the external IP hasn't changed (IPs can change when VM restarts)
- Update the `HostName` in your `~/.ssh/config` file if the IP changed

### Issue: Cannot find gcloud command

**Solution:**
- Restart your terminal after installing gcloud SDK
- Or add gcloud to your PATH manually (see installation documentation)

### Issue: VM external IP keeps changing

**Solution:**
- Reserve a static IP address in GCP Console:
  - Navigate to **VPC network > IP addresses**
  - Click **Reserve External Static Address**
  - Assign it to your `asi-micro` VM

---

## Quick Reference Commands

```bash
# List all VM instances
gcloud compute instances list

# Start VM
gcloud compute instances start asi-micro --zone=europe-west4-a

# Stop VM
gcloud compute instances stop asi-micro --zone=europe-west4-a

# SSH into VM
gcloud compute ssh asi-micro --zone=europe-west4-a --project=your-gcp-project-id

# SSH into VM without gcloud
ssh -i ~/.ssh/asi-micro your_username@EXTERNAL_IP

# Check gcloud configuration
gcloud config list

# View your public SSH key
cat ~/.ssh/asi-micro.pub
```

---

## Next Steps

Once connected to your VM, you can:
- Install Python packages and ML frameworks
- Upload datasets
- Run training scripts
- Monitor resource usage with `htop` or `nvidia-smi` (for GPU instances)

**Remember:** Always stop your VM when not in use to minimize costs!

---

## Additional Resources

- [GCP Compute Engine Documentation](https://cloud.google.com/compute/docs)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
- [VS Code Remote Development](https://code.visualstudio.com/docs/remote/ssh)
