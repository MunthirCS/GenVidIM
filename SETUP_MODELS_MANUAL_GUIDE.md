# Manual Model Setup Guide for Serverless

## ✅ Summary

Your serverless endpoint is **fully configured** and all dependencies are working!

The only remaining step is to **download the model weights** to your network volume.

---

## 🎯 Quick Setup Using RunPod Web Terminal

Since SSH from Windows may have issues, use RunPod's built-in web terminal:

### Step 1: Open Pod Terminal

1. Go to: **https://runpod.io/console/pods**
2. Find your pod: **passing_yellow_caribou** (RTX 5090)
3. Click **"Connect"** button
4. Select **"Start Web Terminal"** or **"Web Terminal"**

---

### Step 2: Run These Commands in the Terminal

Copy and paste these commands one by one:

```bash
# Navigate to workspace
cd /workspace

# Clone or update GenVidIM
if [ -d "GenVidIM" ]; then
  cd GenVidIM && git pull origin main
else
  git clone https://github.com/MunthirCS/GenVidIM.git
  cd GenVidIM
fi

# Install huggingface-cli
pip install -q "huggingface_hub[cli]"

# Download model to network volume (THIS IS THE KEY STEP)
huggingface-cli download Wan-AI/Wan2.2-TI2V-5B \
    --local-dir /runpod-volume/Wan2.2-TI2V-5B \
    --resume-download
```

---

### Step 3: Wait for Download

**Expected:**
- Size: ~20-30 GB
- Time: 10-30 minutes (depending on connection speed)
- Progress bar will show download status

**You'll see:**
```
Fetching files...
Downloading model files...
100%|████████████████| XX.XGB/XX.XGB [XX:XX<00:00, XX.XMB/s]
✅ Download complete
```

---

### Step 4: Verify Models Are There

```bash
# Check if models downloaded successfully
ls -lh /runpod-volume/Wan2.2-TI2V-5B/

# Should show files like:
# - models_dit/
# - models_t5_umt5-xxl-enc-bf16.pth
# - models_vae/
# - model_index.json
# etc.
```

---

### Step 5: Test Serverless Endpoint

From your **local Windows machine**:

```powershell
cd C:\Users\Admin\.cursor\Projects\FlowCharts
python test_endpoint.py
```

**Expected result:**
- ✅ Job completes successfully
- ✅ Video generated
- ✅ No "FileNotFoundError" for models

---

## 📋 Alternative: One-Line Command

If you prefer, paste this single command in the pod terminal:

```bash
cd /workspace && ([ -d GenVidIM ] || git clone https://github.com/MunthirCS/GenVidIM.git) && cd GenVidIM && git pull && pip install -q "huggingface_hub[cli]" && huggingface-cli download Wan-AI/Wan2.2-TI2V-5B --local-dir /runpod-volume/Wan2.2-TI2V-5B --resume-download && echo "✅ Setup complete!"
```

---

## 🔍 Troubleshooting

### "Permission denied" on /runpod-volume
- The network volume might not be mounted
- Check in RunPod console that Serverless1 is attached to the pod
- Or download to /workspace and copy later

### "Network error" during download
- HuggingFace download can be slow
- Use `--resume-download` flag to continue interrupted downloads
- Or use ModelScope (faster in some regions):
  ```bash
  pip install modelscope
  modelscope download Wan-AI/Wan2.2-TI2V-5B --local_dir /runpod-volume/Wan2.2-TI2V-5B
  ```

### "Not enough space"
- Check volume size: `df -h /runpod-volume`
- Your Serverless1 has 300 GB (plenty of space)
- Model is ~25 GB

---

## 📊 What Happens After Model Download

**Once models are on the network volume:**

1. ✅ Serverless workers can access them at `/runpod-volume/Wan2.2-TI2V-5B`
2. ✅ Handler is configured to use this path
3. ✅ All dependencies are installed
4. ✅ NumPy < 2 enforced
5. ✅ Everything ready to generate videos!

**Test with:**
```powershell
python test_endpoint.py
```

**Full video generation:**
```powershell
python serverless_generate.py "a blue butterfly flying in a garden" --size 1280*704 --steps 20
```

---

## 🎉 Final Checklist

- [x] Serverless endpoint created
- [x] Network volume configured (300 GB)
- [x] All dependencies installed (peft, decord, etc.)
- [x] NumPy < 2 constraint working
- [x] Handler configured for network volume
- [ ] **Download models to /runpod-volume** ← YOU ARE HERE
- [ ] Test serverless endpoint
- [ ] Generate first video!

---

## 💡 Summary

**What to do:**
1. Open RunPod web terminal for your RTX 5090 pod
2. Run the download command
3. Wait 10-30 minutes
4. Test serverless endpoint

**That's it!** Everything else is already set up and working.

---

## 📞 Your Pod Connection Info

**Pod:** passing_yellow_caribou  
**GPU:** RTX 5090  
**SSH:** `root@149.36.1.141 -p 23404`  
**Web Terminal:** https://runpod.io/console/pods → Your pod → Connect  

**Network Volume:** Serverless1 (300 GB)  
**Mount Point:** `/runpod-volume`  
**Model Path:** `/runpod-volume/Wan2.2-TI2V-5B`

---

**Good luck! You're almost done!** 🚀

