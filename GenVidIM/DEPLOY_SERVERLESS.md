# 🚀 Deploy Wan2.2 as RunPod Serverless

This is the **proper, scalable solution** for your platform.

## Why Serverless?

✅ **Fully scalable** - Auto-scales with demand
✅ **Cost effective** - Pay per second of compute
✅ **API-first** - Perfect for platform integration
✅ **No SSH issues** - Pure HTTP API
✅ **Production ready** - Used by AI platforms like Replicate

## 📋 Prerequisites

- RunPod account with API key
- Docker installed locally (for building the image)
- Your Wan2.2 model weights

## 🎯 Deployment Steps

### Step 1: Build Docker Image

```bash
cd /home/user/flowchart/serverless
docker build -t your-dockerhub-username/wan22-serverless:latest .
docker push your-dockerhub-username/wan22-serverless:latest
```

### Step 2: Create Serverless Endpoint on RunPod

1. Go to https://runpod.io/console/serverless
2. Click "New Endpoint"
3. Configure:
   - **Name**: Wan2.2 Video Generator
   - **Docker Image**: `your-dockerhub-username/wan22-serverless:latest`
   - **GPU Type**: RTX 4090 or better
   - **Container Disk**: 50 GB
   - **Min Workers**: 0 (scales to zero)
   - **Max Workers**: 3 (or more)
   - **Idle Timeout**: 30 seconds

4. Click "Deploy"

### Step 3: Get Endpoint ID

After deployment, copy your endpoint ID (looks like: `abc123def456`)

### Step 4: Configure Local Environment

Add to your `.runpod.env`:

```bash
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
RUNPOD_API_KEY=your_api_key_here
```

### Step 5: Test It!

```bash
cd /home/user/flowchart
python3 serverless/runpod_client.py "ships sailing in a volcano"
```

## 📊 Cost Estimate

- **Idle time**: $0/hour (scales to zero)
- **Active generation**: ~$0.40/hour on RTX 4090
- **Per video**: ~$0.05 - $0.10 (5-10 minutes)

Much cheaper than keeping a pod running 24/7!

## 🎬 Usage from Your Platform

```python
import requests

# Submit job
response = requests.post(
    f"https://api.runpod.ai/v2/{endpoint_id}/run",
    headers={"Authorization": api_key},
    json={
        "input": {
            "prompt": "your prompt",
            "steps": 35
        }
    }
)

job_id = response.json()['id']

# Check status
response = requests.get(
    f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}",
    headers={"Authorization": api_key}
)

result = response.json()
```

## 🔥 Benefits for Your Platform

1. **Scalability**: Handles 1 or 1000 requests
2. **Reliability**: RunPod manages infrastructure
3. **Cost**: Pay only for compute used
4. **Speed**: No cold start after first request
5. **Simple**: Just HTTP API calls

This is how production AI platforms work!

## ⚡ Quick Alternative: Use Existing Pod for Now

If you want to test immediately while deploying serverless:

```bash
# SSH to RunPod
ssh jf6md7u8x71d53-64410b7b@ssh.runpod.io

# Run generation
cd /workspace/Wan2.2
python generate.py --task ti2v-5B --prompt "ships sailing in a volcano" --offload_model True --convert_model_dtype --t5_cpu
```

But **deploy serverless for your platform** - it's the right architecture.
