# 🚀 RunPod Video Generation Setup Guide

This guide will help you set up a flexible cloud infrastructure for open-source video generation using RunPod.

## 📋 Prerequisites

1. **RunPod Account**: Sign up at [runpod.io](https://runpod.io)
2. **Payment Method**: Add a credit card (they usually give $10 free credit)
3. **API Key**: Get your API key from the RunPod console

## 🏗️ Quick Start

### Step 1: Set Up Your Local Environment

```bash
# Install the RunPod client
pip install requests

# Set your API key
export RUNPOD_API_KEY="your_api_key_here"

# Test the client
python runpod_video_client.py
```

### Step 2: Launch RunPod Instance

1. **Go to RunPod Console**: [runpod.io/console](https://runpod.io/console)
2. **Click "Deploy"** → **"GPU Pod"**
3. **Choose Template**: 
   - Search for "PyTorch" or "Machine Learning"
   - Recommended: "RunPod PyTorch 2.0.1"
4. **Select GPU**:
   - **RTX 4090** (~$0.50/hour) - Best value
   - **RTX 3090** (~$0.40/hour) - Good performance
   - **A100** (~$1.50/hour) - Maximum performance
5. **Configure**:
   - Container Disk: 20GB
   - Volume Disk: 50GB (for models and outputs)
   - Expose HTTP Ports: 8888, 7860
   - Expose TCP Ports: 22
6. **Deploy**

### Step 3: Set Up Video Generation Environment

Once your pod is running:

1. **Connect via Jupyter Lab**:
   - Click "Connect" → "Jupyter Lab"
   - Password: `runpod`

2. **Upload setup script**:
   - Upload `setup_video_generation.py` to your pod
   - Run it in a terminal: `python setup_video_generation.py`

3. **Wait for setup** (10-15 minutes):
   - Downloads models and dependencies
   - Sets up web interface
   - Configures environment

### Step 4: Start Generating Videos

**Option A: Web Interface**
```bash
python /workspace/video_interface.py
```
Then access via port 7860

**Option B: Jupyter Notebook**
```bash
jupyter lab --allow-root --ip=0.0.0.0 --port=8888
```

**Option C: Direct Python**
```python
# Example code for Stable Video Diffusion
import torch
from diffusers import StableVideoDiffusionPipeline

pipe = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid-xt"
)
pipe.to("cuda")

# Generate video from text
video = pipe("A cat playing with yarn").frames
```

## 🎬 Available Models

### 1. Stable Video Diffusion
- **Best for**: High-quality, realistic videos
- **Input**: Text prompts or images
- **Output**: 4-second videos at 1024x576

### 2. AnimateDiff
- **Best for**: Animated content, character animation
- **Input**: Text prompts
- **Output**: Customizable length and resolution

### 3. Wan2.2 (Optional)
- **Best for**: Advanced video generation
- **Input**: Text, images, audio
- **Output**: High-resolution videos

## 💰 Cost Estimation

| GPU Type | Cost/Hour | 5-min Video | 1-hour Session |
|----------|-----------|-------------|----------------|
| RTX 3090 | $0.40     | ~$0.10      | $0.40          |
| RTX 4090 | $0.50     | ~$0.12      | $0.50          |
| A100     | $1.50     | ~$0.35      | $1.50          |

**Typical usage**: 2-3 videos per hour = **$0.20-0.50 per session**

## 🔧 Management Commands

### Using the Python Client

```python
from runpod_video_client import RunPodVideoClient

client = RunPodVideoClient("your_api_key")

# List available GPUs
gpus = client.list_gpu_types()

# Create a pod
pod = client.create_pod(
    name="video-generation",
    gpu_type_id="NVIDIA RTX 4090",
    volume_size=50
)

# List your pods
pods = client.list_pods()

# Stop a pod
client.stop_pod("pod_id_here")
```

### Via RunPod Console

1. **Monitor Usage**: Check costs and runtime
2. **Stop Pods**: Always stop when done to save money
3. **Save Work**: Download important outputs before stopping

## 📁 File Organization

```
/workspace/
├── video_generation/          # Main workspace
│   ├── generative-models/     # Stable Video Diffusion
│   ├── AnimateDiff/           # AnimateDiff
│   ├── Wan2.2/               # Wan2.2 (optional)
│   └── outputs/              # Generated videos
├── video_interface.py         # Web interface
└── models/                    # Downloaded model weights
```

## 🚨 Important Tips

### Cost Management
- **Always stop pods** when not in use
- **Monitor spending** in RunPod console
- **Use spot instances** for cheaper rates (may be interrupted)

### Performance Optimization
- **Choose right GPU**: RTX 4090 is usually best value
- **Batch generation**: Generate multiple videos in one session
- **Cache models**: Keep frequently used models on volume storage

### Troubleshooting
- **Out of memory**: Reduce batch size or use smaller models
- **Slow generation**: Check GPU utilization in `nvidia-smi`
- **Connection issues**: Use RunPod's built-in terminals/Jupyter

## 🔗 Useful Links

- **RunPod Console**: [runpod.io/console](https://runpod.io/console)
- **RunPod Documentation**: [docs.runpod.io](https://docs.runpod.io)
- **Stable Video Diffusion**: [huggingface.co/stabilityai](https://huggingface.co/stabilityai)
- **AnimateDiff**: [github.com/guoyww/AnimateDiff](https://github.com/guoyww/AnimateDiff)

## 🆘 Support

If you run into issues:
1. Check RunPod's community Discord
2. Review model-specific documentation
3. Monitor GPU memory usage with `nvidia-smi`
4. Check pod logs in RunPod console

---

**Ready to generate amazing videos in the cloud!** 🎬✨
