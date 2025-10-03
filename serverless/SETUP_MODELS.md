# Setup Models for Serverless Endpoint

## Overview

The serverless workers need the Wan2.2 model weights stored on the network volume.

**Network Volume:** Serverless1 (300 GB) - Already configured ✅  
**Mount Point:** `/runpod-volume`

---

## Quick Setup (Recommended)

### Option 1: Download Using Your RTX 5090 Pod

Your pod `passing_yellow_caribou` (RTX 5090) is already running and can access the same network volume.

**Steps:**

1. **SSH into your pod** (or use RunPod web terminal)

2. **Mount the network volume** (if not already mounted)

3. **Run the download script:**
   ```bash
   cd /workspace/GenVidIM
   bash serverless/download_models.sh
   ```

4. **Wait for download** (~20-30 GB, takes 10-30 minutes depending on speed)

5. **Done!** Models are now available to all serverless workers

---

### Option 2: Add Model Download to Dockerfile (Auto Setup)

Add this to the Dockerfile (after installing dependencies):

```dockerfile
# Download models to a temporary location, then copy to volume on first run
RUN mkdir -p /tmp/models && \
    pip install "huggingface_hub[cli]" && \
    huggingface-cli download Wan-AI/Wan2.2-TI2V-5B --local-dir /tmp/models/Wan2.2-TI2V-5B

# Note: Models in /tmp will be lost when container stops
# They need to be on /runpod-volume for persistence
```

**Downside:** Models download on every build, slow and inefficient

---

### Option 3: Manual Upload via RunPod UI

1. Go to RunPod Console → **Storage**
2. Select **Serverless1** volume
3. Create folder: `Wan2.2-TI2V-5B`
4. Upload model files from your local machine

**Downside:** Need to download models locally first, then upload (slow)

---

## Recommended: Use Your RTX 5090 Pod

### Step-by-Step:

**1. Connect to your pod:**
```bash
# Get pod SSH details from RunPod dashboard
ssh root@[pod-ssh-host] -p [port]
```

**2. Check if network volume is mounted:**
```bash
ls -la /runpod-volume
# Should show your network volume
```

**3. Download model:**
```bash
# Install huggingface-cli
pip install "huggingface_hub[cli]"

# Download to network volume
huggingface-cli download Wan-AI/Wan2.2-TI2V-5B \
    --local-dir /runpod-volume/Wan2.2-TI2V-5B \
    --resume-download
```

**4. Verify:**
```bash
ls -lh /runpod-volume/Wan2.2-TI2V-5B
# Should show model files
```

**5. Test serverless:**
```bash
# From your local machine
python test_endpoint.py
```

---

## Model Info

### TI2V-5B (Recommended for serverless):
- **Size:** ~20-30 GB
- **HuggingFace:** https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B
- **Requirements:** 24GB+ VRAM (works on RTX 4090, 5090, etc.)
- **Speed:** Fastest 720P model

### Model Structure:
```
Wan2.2-TI2V-5B/
├── model_index.json
├── models_dit/
├── models_t5_umt5-xxl-enc-bf16.pth
├── models_vae/
└── ... (other weight files)
```

---

## Handler Configuration

The handler is already configured to use:

```python
ckpt_dir = '/runpod-volume/Wan2.2-TI2V-5B'
```

Once you download the model to this location, everything will work!

---

## Troubleshooting

### If network volume not mounted on pod:
```bash
# Check volume ID
runpodctl get volumes

# Mount volume to pod
# (Usually done automatically via RunPod UI)
```

### If download fails:
```bash
# Use ModelScope instead (faster in some regions)
pip install modelscope
modelscope download Wan-AI/Wan2.2-TI2V-5B --local_dir /runpod-volume/Wan2.2-TI2V-5B
```

---

## Next Steps

1. ✅ Network volume configured (300 GB)
2. ✅ Handler updated to use `/runpod-volume/Wan2.2-TI2V-5B`
3. ⏳ **Download model to network volume** ← You need to do this
4. ⏳ Test serverless endpoint

**Recommended:** Use your RTX 5090 pod to download (it's already running!)

