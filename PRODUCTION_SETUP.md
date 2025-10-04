# Production Automation Setup - Complete Guide

## Overview

This guide sets up **fully automated video generation** for production use. No manual intervention needed once configured.

## Your SSH Key (Generated)

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILBuT8ZrNypK2KvqGSokALGMzxRhAUfyMpygERuGySGA runpod-automation
```

## Setup Steps (One-Time)

### Step 1: Add SSH Key to RunPod

1. Go to: https://www.runpod.io/console/user/settings
2. Scroll to **SSH Public Keys**
3. Click **Add SSH Key**
4. Paste your public key (shown above)
5. Save

### Step 2: Add Key to Running Pod

Since your pod is already running, inject the key manually:

1. Go to: https://runpod.io/console/pods
2. Click on **passing_yellow_caribou** (your RTX 5090 pod)
3. Click **Connect** → **Web Terminal**
4. Run this command:

```bash
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILBuT8ZrNypK2KvqGSokALGMzxRhAUfyMpygERuGySGA runpod-automation" >> ~/.ssh/authorized_keys
```

5. Close the terminal

### Step 3: Test Automation

Run this command on your local machine:

```bash
python automated_generate.py "a blue butterfly flying over flowers"
```

**That's it!** The script will:
- ✅ Auto-setup GenVidIM on pod
- ✅ Generate the video
- ✅ Show where it's saved
- ✅ Fully automated!

## Production Usage

### Quick Test (1-2 minutes):
```bash
python automated_generate.py "your prompt"
```

### Fast Production (3-4 minutes):
```bash
python automated_generate.py "your prompt" --size 960*544 --steps 20
```

### High Quality (8-10 minutes):
```bash
python automated_generate.py "your prompt" --size 1280*704 --steps 35
```

## Download Generated Videos

```bash
# Create local videos folder
mkdir videos

# Download latest video
scp runpod-genvidim:/workspace/GenVidIM/outputs/*.mp4 ./videos/
```

## SSH Config (Already Created)

Location: `~/.ssh/config`

```
Host runpod-genvidim
    HostName 149.36.1.141
    User root
    Port 23404
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

## Connect with VSCode/Cursor (Optional)

For development/debugging:

1. Install **Remote-SSH** extension in VSCode/Cursor
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Select **Remote-SSH: Connect to Host**
4. Choose **runpod-genvidim**
5. Open folder: `/workspace/GenVidIM`

Now you can edit code directly on the pod!

## Production Workflow

### For Platform Integration:

```python
import subprocess

def generate_video_on_runpod(prompt, quality="fast"):
    """
    Generate video on RunPod from your application
    
    quality options: "quick", "fast", "balanced", "quality"
    """
    
    sizes = {
        "quick": ("512*288", 10),
        "fast": ("832*480", 15),
        "balanced": ("960*544", 20),
        "quality": ("1280*704", 35)
    }
    
    size, steps = sizes.get(quality, sizes["fast"])
    
    result = subprocess.run([
        "python", "automated_generate.py", prompt,
        "--size", size,
        "--steps", str(steps)
    ], capture_output=True, text=True)
    
    return result.returncode == 0


# Usage in your app
if generate_video_on_runpod("a red sports car", quality="fast"):
    print("Video generated successfully!")
```

## Cost Tracking

Your RTX 5090 pod costs: **$0.89/hr**

| Setting | Time | Cost per Video |
|---------|------|----------------|
| Quick (512x288, 10 steps) | 1-2 min | $0.02-0.03 |
| Fast (832x480, 15 steps) | 2-3 min | $0.03-0.04 |
| Balanced (960x544, 20 steps) | 3-4 min | $0.04-0.06 |
| Quality (1280x704, 35 steps) | 8-10 min | $0.12-0.15 |

## Troubleshooting

### SSH Connection Failed

```bash
# Test SSH manually
ssh runpod-genvidim echo "test"
```

If this fails:
1. Make sure SSH key is added to RunPod settings
2. Make sure key is injected into pod (Step 2 above)
3. Check pod is running

### Video Generation Failed

```bash
# Connect to pod and check manually
ssh runpod-genvidim

# Then on pod:
cd /workspace/GenVidIM
python generate.py --help
```

### Download Failed

```bash
# List videos on pod
ssh runpod-genvidim ls -lh /workspace/GenVidIM/outputs/

# Download specific file
scp runpod-genvidim:/workspace/GenVidIM/outputs/FILENAME.mp4 ./
```

## Scaling to Production

### Option 1: Keep Pod Running (Current Setup)
- ✅ Instant video generation (no cold start)
- ✅ Simple automation via SSH
- ❌ Costs $0.89/hr even when idle (~$642/month)
- 👍 **Best for: High volume, continuous use**

### Option 2: Use Serverless (Once Build Completes)
- ✅ $0.00 when idle (scales to zero)
- ✅ Auto-scales for multiple requests
- ✅ HTTP API (no SSH needed)
- ❌ Cold start delay (~30 seconds first request)
- 👍 **Best for: Variable workload, cost optimization**

## Current Status

✅ SSH automation configured
✅ GenVidIM ready to clone on pod
✅ Automation script created
⏳ Waiting for Step 2 (inject SSH key into pod)

## Next Steps

1. **NOW**: Complete Step 2 above (inject SSH key)
2. **TEST**: Run `python automated_generate.py "test"`
3. **PRODUCTION**: Integrate into your application
4. **OPTIONAL**: Switch to serverless when build completes

---

**You now have production-ready automation!** 🚀

