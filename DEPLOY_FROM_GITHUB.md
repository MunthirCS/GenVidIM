# 🚀 Deploy GenVidIM from GitHub to RunPod Serverless

**No Docker installation needed!** RunPod builds directly from your GitHub repo.

## ✅ Prerequisites

- GitHub account with repo: https://github.com/MunthirCS/GenVidIM
- RunPod account: https://runpod.io
- RunPod API key (from Settings)

## 📋 Step-by-Step Deployment

### Step 1: Access RunPod Serverless

1. Go to https://runpod.io/console/serverless
2. Click **"+ New Endpoint"**

### Step 2: Configure Endpoint

**Basic Settings:**
- **Name**: `GenVidIM-Wan22`
- **Description**: `AI Video Generation from Text Prompts`

**Build Configuration:**
- **Build Method**: Select **"Build from GitHub"**
- **GitHub Repository**: `MunthirCS/GenVidIM`
- **Branch**: `main`
- **Dockerfile Path**: `serverless/Dockerfile`
- **Build Context**: `/` (root)

**GPU Configuration:**
- **GPU Type**: `RTX 4090` or `RTX 3090` (24GB VRAM minimum)
- **Container Disk**: `50 GB`
- **Volume Disk**: `0 GB` (not needed for serverless)

**Scaling Configuration:**
- **Min Workers**: `0` (scale to zero when idle = save money!)
- **Max Workers**: `3` (or more based on your needs)
- **Idle Timeout**: `30` seconds
- **Execution Timeout**: `900` seconds (15 minutes for video generation)

**Network Configuration:**
- **Flashboot**: ✅ Enable (faster cold starts)
- **HTTP Port**: `8000` (default)

### Step 3: Advanced Settings (Optional)

**Environment Variables:**
```
MODEL_PATH=/workspace/Wan2.2-TI2V-5B
PYTHONUNBUFFERED=1
```

**Volume Mount** (if you want persistent model storage):
- Create a network volume with model weights
- Mount at `/workspace/models`

### Step 4: Deploy!

1. Click **"Deploy"**
2. RunPod will:
   - Clone your GitHub repo ✅
   - Build Docker image ✅
   - Deploy serverless endpoint ✅
   - Give you an endpoint ID ✅

This takes **5-10 minutes** for first build.

### Step 5: Get Your Endpoint ID

After deployment:
1. Copy your **Endpoint ID** (looks like: `abc123def456`)
2. Copy your **API Key** from Settings

### Step 6: Configure Local Environment

Add to your `.runpod.env`:

```bash
RUNPOD_ENDPOINT_ID=abc123def456
RUNPOD_API_KEY=your_api_key_here
```

### Step 7: Test It!

```bash
cd /home/user/flowchart
python3 serverless/runpod_client.py "ships sailing in a volcano"
```

## 🔄 Auto-Deploy on Git Push

**Enable Webhooks** (optional but recommended):

1. In your RunPod endpoint settings
2. Enable "Auto-build on GitHub push"
3. RunPod will rebuild automatically when you push to GitHub

Now every git push triggers a new deployment! 🎉

## 📊 Cost Estimate

With **RTX 4090**:
- **Idle time**: $0.00/hour (scales to zero!)
- **Active generation**: ~$0.40/hour
- **Per 5-min video**: ~$0.03-0.05

**Much cheaper than keeping a pod running 24/7!**

Example costs:
- 10 videos/day = ~$0.50/day = ~$15/month
- 100 videos/day = ~$5/day = ~$150/month

## 🎯 Using from Your Platform

### Python Example:

```python
import requests

ENDPOINT_ID = "your_endpoint_id"
API_KEY = "your_api_key"

# Submit job
response = requests.post(
    f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run",
    headers={"Authorization": API_KEY},
    json={
        "input": {
            "prompt": "a cat playing in a sunny garden",
            "steps": 35
        }
    }
)

job_id = response.json()["id"]
print(f"Job submitted: {job_id}")

# Check status (poll every 10 seconds)
import time
while True:
    response = requests.get(
        f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{job_id}",
        headers={"Authorization": API_KEY}
    )

    result = response.json()

    if result["status"] == "COMPLETED":
        video_data = result["output"]["video_data"]
        # Decode base64 and save
        import base64
        with open("output.mp4", "wb") as f:
            f.write(base64.b64decode(video_data))
        break

    time.sleep(10)
```

### JavaScript Example:

```javascript
const ENDPOINT_ID = "your_endpoint_id";
const API_KEY = "your_api_key";

// Submit job
const response = await fetch(
  `https://api.runpod.ai/v2/${ENDPOINT_ID}/run`,
  {
    method: "POST",
    headers: {
      "Authorization": API_KEY,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      input: {
        prompt: "a cat playing in a sunny garden",
        steps: 35
      }
    })
  }
);

const { id: jobId } = await response.json();
console.log(`Job submitted: ${jobId}`);

// Poll for results
while (true) {
  const statusResponse = await fetch(
    `https://api.runpod.ai/v2/${ENDPOINT_ID}/status/${jobId}`,
    { headers: { "Authorization": API_KEY } }
  );

  const result = await statusResponse.json();

  if (result.status === "COMPLETED") {
    const videoData = result.output.video_data;
    // Handle base64 video data
    break;
  }

  await new Promise(resolve => setTimeout(resolve, 10000));
}
```

## 🔧 Troubleshooting

### Build Failed

**Check:**
- Dockerfile path is correct: `serverless/Dockerfile`
- All dependencies in requirements.txt
- GitHub repo is public or RunPod has access

**View build logs** in RunPod dashboard.

### Generation Times Out

**Increase timeout:**
- Go to endpoint settings
- Set "Execution Timeout" to 1200s (20 minutes)

### Out of Memory

**Increase GPU:**
- Change to RTX 4090 or H100
- Or enable model offloading in handler

### Cold Start Slow

**Enable Flashboot:**
- Keeps containers warm
- Faster cold starts (~10s vs ~60s)

## 📈 Monitoring

**View in RunPod Dashboard:**
- Active workers
- Queue length
- Success/failure rates
- Execution times
- Costs

**Set up alerts** for:
- High error rates
- Long queue times
- Budget thresholds

## 🎉 You're Done!

You now have:
- ✅ Auto-deploying serverless API
- ✅ Scales automatically (0 to N workers)
- ✅ Pay only for what you use
- ✅ Production-ready infrastructure
- ✅ No servers to manage

**Next**: Build your platform on top of this API! 🚀

## 📚 Additional Resources

- [RunPod Serverless Docs](https://docs.runpod.io/serverless/overview)
- [API Reference](https://docs.runpod.io/serverless/endpoints/send-requests)
- [Webhooks Guide](https://docs.runpod.io/serverless/endpoints/get-started)
