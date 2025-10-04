# ⚡ GenVidIM Quick Start

Generate AI videos in 3 steps!

## 🚀 Quick Deploy (5 minutes)

### 1️⃣ Deploy to RunPod

Go to: https://runpod.io/console/serverless

Click **"+ New Endpoint"** and configure:

```
Build Method: Build from GitHub
Repository: MunthirCS/GenVidIM
Branch: main
Dockerfile Path: serverless/Dockerfile

GPU: RTX 4090
Min Workers: 0
Max Workers: 3
```

Click **"Deploy"** → Get your **Endpoint ID**

### 2️⃣ Configure API Key

Create `.runpod.env`:

```bash
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
RUNPOD_API_KEY=your_api_key_here
```

### 3️⃣ Generate Videos

```bash
python3 serverless/runpod_client.py "ships sailing in a volcano"
```

Done! 🎉

---

## 💻 For Developers

### Test Locally (No GPU)

```bash
# Install dependencies
nix-shell

# View what would run
python3 generate.py --help
```

### Deploy from GitHub

See: [`DEPLOY_FROM_GITHUB.md`](DEPLOY_FROM_GITHUB.md)

### Use in Your App

```python
import requests

response = requests.post(
    f"https://api.runpod.ai/v2/{endpoint_id}/run",
    headers={"Authorization": api_key},
    json={"input": {"prompt": "your prompt"}}
)

job_id = response.json()["id"]
```

---

## 📊 What You Get

- ✅ **Scalable**: Auto-scales 0→N workers
- ✅ **Cost-effective**: $0.03-0.05 per video
- ✅ **Fast**: 5-10 minutes per video
- ✅ **API-first**: REST API for platforms
- ✅ **Production-ready**: Built on RunPod

---

## 📚 Documentation

- **Deployment**: [`DEPLOY_FROM_GITHUB.md`](DEPLOY_FROM_GITHUB.md)
- **Architecture**: [`FINAL_SOLUTION.md`](FINAL_SOLUTION.md)
- **Lessons Learned**: [`LESSONS_LEARNED.md`](LESSONS_LEARNED.md)

---

## 🆘 Need Help?

**Common Issues:**

1. **Build fails**: Check Dockerfile path is `serverless/Dockerfile`
2. **Timeout**: Increase execution timeout to 900s
3. **OOM**: Use RTX 4090 or larger GPU

**Still stuck?** Check the full deployment guide!

---

## 🎯 Next Steps

1. **Deploy** following this guide
2. **Test** with sample prompts
3. **Integrate** into your platform
4. **Scale** based on demand

Happy video generating! 🎬
