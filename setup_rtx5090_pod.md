# 🚀 Setup GenVidIM on RTX 5090 Pod

## 📋 Pod Information
- **Pod Name**: passing_yellow_caribou
- **Pod ID**: jf6md7u8x71d53
- **GPU**: RTX 5090
- **Cost**: $0.89/hr
- **Status**: RUNNING ✅

## 🔌 Step 1: Connect to Your Pod

### Option A: SSH (Recommended)
Get your SSH connection details from RunPod dashboard:
```bash
ssh <pod_id>@ssh.runpod.io -p <port>
```

### Option B: Web Terminal
Go to: https://runpod.io/console/pods
Click on your pod → Click "Connect" → Use web terminal

## 📦 Step 2: Setup GenVidIM on Pod

Once connected, run these commands:

```bash
# Navigate to workspace
cd /workspace

# Clone GenVidIM
git clone https://github.com/MunthirCS/GenVidIM.git
cd GenVidIM

# Install dependencies
pip install -r requirements.txt

# Test installation
python generate.py --help
```

## 🎬 Step 3: Generate Your First Video

### Quick Test (1-2 minutes):
```bash
python generate.py \
  --task ti2v-5B \
  --size '512*288' \
  --sample_steps 10 \
  --prompt "a blue butterfly flying over flowers" \
  --offload_model True \
  --convert_model_dtype \
  --t5_cpu
```

### Production Quality (3-4 minutes):
```bash
python generate.py \
  --task ti2v-5B \
  --size '960*544' \
  --sample_steps 20 \
  --prompt "a red sports car driving on a highway at sunset" \
  --offload_model True \
  --convert_model_dtype \
  --t5_cpu
```

### High Quality (5-10 minutes):
```bash
python generate.py \
  --task ti2v-5B \
  --size '1280*704' \
  --sample_steps 35 \
  --prompt "ships sailing through a volcano with lava" \
  --offload_model True \
  --convert_model_dtype \
  --t5_cpu
```

## 📥 Step 4: Download Generated Videos

Videos are saved in `/workspace/GenVidIM/outputs/`

### Method A: Using RunPod File Browser
1. Go to your pod in RunPod dashboard
2. Click "Connect" → "HTTP Service" or "File Browser"
3. Navigate to `/workspace/GenVidIM/outputs/`
4. Download the `.mp4` files

### Method B: Using SCP
```bash
# From your local machine:
scp -P <port> <pod_id>@ssh.runpod.io:/workspace/GenVidIM/outputs/*.mp4 ./downloads/
```

### Method C: Using RunPod CLI
```bash
runpodctl receive <pod_id> /workspace/GenVidIM/outputs/ ./local_downloads/
```

## ⚡ Speed Optimization Commands

### Ultra Fast (testing only - 90 seconds):
```bash
python generate.py --task ti2v-5B --size '512*288' --sample_steps 10 \
  --prompt "test video" --offload_model True --convert_model_dtype --t5_cpu
```

### Fast (good quality - 3 minutes):
```bash
python generate.py --task ti2v-5B --size '832*480' --sample_steps 15 \
  --prompt "your prompt" --offload_model True --convert_model_dtype --t5_cpu
```

### Balanced (production - 4 minutes):
```bash
python generate.py --task ti2v-5B --size '960*544' --sample_steps 20 \
  --prompt "your prompt" --offload_model True --convert_model_dtype --t5_cpu
```

## 🔧 Troubleshooting

### If models are not downloaded:
Models will auto-download on first run. This might take 10-20 minutes for the first generation.

### If out of memory:
Add these flags (already included above):
- `--offload_model True`
- `--convert_model_dtype`
- `--t5_cpu`

### If generation is slow:
- Reduce `--sample_steps` (20 is good)
- Reduce `--size` (960*544 is optimal)

## 💰 Cost Tracking

Your pod costs: **$0.89/hr**

Estimated costs per video:
- Quick test (90s): ~$0.02
- Fast (3 min): ~$0.04
- Balanced (4 min): ~$0.06
- Quality (10 min): ~$0.15

**Remember to stop the pod when not in use to save costs!**

## 🎯 Next Steps

1. **SSH into your pod** using RunPod dashboard
2. **Run the setup commands** above
3. **Generate a test video** with quick settings
4. **Download and review**
5. **Generate production videos** as needed

## 📝 Useful Commands

```bash
# Check GPU status
nvidia-smi

# List generated videos
ls -lh /workspace/GenVidIM/outputs/

# Monitor generation in real-time
watch -n 1 nvidia-smi

# Check disk space
df -h

# Clean up old videos
rm /workspace/GenVidIM/outputs/*.mp4
```

---

**Ready to start?** Get your SSH connection from RunPod and follow Step 1! 🚀

