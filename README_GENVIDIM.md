# 🎬 GenVidIM - AI Video Generation Platform

Generate high-quality AI videos from text prompts using Wan2.2 on RunPod Serverless.

[![Deploy on RunPod](https://img.shields.io/badge/Deploy-RunPod-6B4FBB)](https://runpod.io/console/serverless)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## ✨ Features

- 🎥 **Text-to-Video**: Generate videos from text descriptions
- ⚡ **Serverless**: Auto-scales from 0 to N workers
- 💰 **Cost-effective**: Pay only for generation time (~$0.03-0.05/video)
- 🚀 **Production-ready**: REST API for platform integration
- 🔄 **Auto-deploy**: Builds automatically from GitHub

## 🚀 Quick Start

### 1. Deploy to RunPod Serverless

```bash
# Go to: https://runpod.io/console/serverless
# Click "New Endpoint"
# Select "Build from GitHub"
# Repository: MunthirCS/GenVidIM
# Dockerfile: serverless/Dockerfile
```

### 2. Get Your Endpoint ID

After deployment, copy your endpoint ID and API key.

### 3. Generate Videos

```bash
# Configure
echo "RUNPOD_ENDPOINT_ID=your_endpoint_id" > .runpod.env
echo "RUNPOD_API_KEY=your_api_key" >> .runpod.env

# Generate
python3 serverless/runpod_client.py "ships sailing in a volcano"
```

**See full guide**: [QUICKSTART.md](QUICKSTART.md)

## 📖 Documentation

- **[Quick Start](QUICKSTART.md)** - Get running in 5 minutes
- **[Deploy from GitHub](DEPLOY_FROM_GITHUB.md)** - Complete deployment guide
- **[Architecture](FINAL_SOLUTION.md)** - How it works
- **[Lessons Learned](LESSONS_LEARNED.md)** - Integration insights

## 🏗️ Architecture

```
Your App → RunPod Serverless API → GPU Workers → Generated Videos
           (HTTPS REST API)        (Wan2.2 Model)
```

**Key Components:**
- `serverless/handler.py` - RunPod worker that runs Wan2.2
- `serverless/Dockerfile` - Container definition
- `serverless/runpod_client.py` - Python client for API calls

## 💻 Local Development

```bash
# Enter development environment
nix-shell

# View generation options
python3 generate.py --help
```

**Note**: Local generation requires GPU. For testing, use RunPod Serverless.

## 🔌 API Usage

### Python

```python
import requests

response = requests.post(
    f"https://api.runpod.ai/v2/{endpoint_id}/run",
    headers={"Authorization": api_key},
    json={
        "input": {
            "prompt": "a majestic dragon flying over mountains",
            "steps": 35
        }
    }
)

job_id = response.json()["id"]
```

### JavaScript

```javascript
const response = await fetch(
  `https://api.runpod.ai/v2/${endpointId}/run`,
  {
    method: "POST",
    headers: {
      "Authorization": apiKey,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      input: {
        prompt: "a majestic dragon flying over mountains",
        steps: 35
      }
    })
  }
);

const { id: jobId } = await response.json();
```

### cURL

```bash
curl -X POST https://api.runpod.ai/v2/$ENDPOINT_ID/run \
  -H "Authorization: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "a cat playing in a garden", "steps": 35}}'
```

## 📊 Performance & Costs

**Generation Time**: 5-10 minutes per video (720p, 5 seconds)

**Costs** (RTX 4090):
- Idle: $0.00/hour (scales to zero)
- Active: ~$0.40/hour
- Per video: $0.03-0.05

**Comparison**:
- Pod 24/7: ~$300/month
- Serverless (100 videos/day): ~$150/month
- Serverless (10 videos/day): ~$15/month

## 🛠️ Tech Stack

- **Model**: Wan2.2-TI2V-5B (5B parameters)
- **Framework**: PyTorch, Diffusers
- **Compute**: RunPod Serverless
- **API**: REST (JSON)
- **Deployment**: Docker + GitHub

## 📈 Scaling

- **Min Workers**: 0 (scale to zero when idle)
- **Max Workers**: Set based on demand (3-10+ workers)
- **Cold Start**: ~10-30 seconds with Flashboot
- **Concurrent Requests**: Limited by max workers

## 🤝 Contributing

This project builds on [Wan2.2](https://github.com/Wan-Video/Wan2.2) by the Wan team.

Contributions welcome! Areas:
- Model optimization
- API improvements
- Documentation
- Example integrations

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Wan Team** - For the amazing Wan2.2 model
- **RunPod** - For serverless GPU infrastructure
- **Community** - For feedback and contributions

## 🔗 Links

- **Repository**: https://github.com/MunthirCS/GenVidIM
- **RunPod**: https://runpod.io
- **Wan2.2**: https://github.com/Wan-Video/Wan2.2

---

Made with ❤️ for the AI video generation community
