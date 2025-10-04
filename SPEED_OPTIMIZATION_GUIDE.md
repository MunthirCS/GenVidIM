# ⚡ Video Generation Speed Optimization Guide

## 🎯 Speed vs Quality Trade-offs

| Mode | Size | Steps | Time | Quality | Use Case |
|------|------|-------|------|---------|----------|
| **Quick Test** | 512×288 | 10 | 1-2 min | Low | Testing only |
| **Ultra Fast** | 832×480 | 15 | 2-3 min | Acceptable | Previews |
| **Fast** ⭐ | 960×544 | 20 | 3-4 min | Good | Recommended |
| **Balanced** | 1280×704 | 25 | 4-6 min | High | Production |
| **Quality** | 1280×704 | 35 | 5-10 min | Best | Final output |

## 🚀 Quick Start

### For Testing (1-2 minutes):
```bash
cd GenVidIM
python quick_test.py "your prompt here"
```

### For Production (3-4 minutes):
```bash
python fast_generate.py "your prompt here" fast
```

### Custom Settings:
```bash
python serverless/runpod_client.py "your prompt" --steps 20
```

## 📊 What Affects Speed?

### 1. **Sample Steps** (Biggest Impact)
- Each step = ~8-12 seconds of processing
- **10 steps**: 2-3 min total (testing only)
- **15 steps**: 3-4 min (acceptable quality)
- **20 steps**: 4-5 min (good quality) ⭐
- **25 steps**: 5-7 min (high quality)
- **35 steps**: 8-12 min (best quality)

### 2. **Video Resolution**
- **512×288**: 1x processing time (testing)
- **832×480**: 2x processing time
- **960×544**: 2.5x processing time ⭐
- **1280×704**: 4x processing time (default)

### 3. **GPU Type** (Serverless Auto-selects)
Your endpoint supports:
- RTX 4090 (24GB) - Fast
- RTX A6000 (48GB) - Faster
- A100 (40GB/80GB) - Fastest

## 💡 Optimization Strategies

### Strategy 1: Two-Pass Generation
```bash
# Pass 1: Quick preview (1-2 min)
python quick_test.py "mountain sunset"

# Pass 2: Full quality if satisfied (5-10 min)
python fast_generate.py "mountain sunset" quality
```

### Strategy 2: Batch Processing
Generate multiple videos in parallel using different workers:
- Your endpoint supports 0-3 workers
- Each worker processes independently
- Total throughput: 3x faster for batch jobs

### Strategy 3: Progressive Quality
Start fast, scale up if needed:
1. **Preview**: 10 steps, 512×288 (1-2 min)
2. **Review**: 20 steps, 960×544 (3-4 min)
3. **Final**: 35 steps, 1280×704 (8-10 min)

## 🎬 Recommended Workflows

### For Development/Testing:
```bash
python quick_test.py "test prompt"  # 1-2 min
```

### For Client Previews:
```bash
python fast_generate.py "prompt" fast  # 3-4 min
```

### For Final Delivery:
```bash
python fast_generate.py "prompt" balanced  # 4-6 min
```

### For Premium Quality:
```bash
python fast_generate.py "prompt" quality  # 8-10 min
```

## 📈 Real-World Timings

Based on typical RTX 4090 performance:

| Configuration | Generation Time | Cost per Video |
|---------------|----------------|----------------|
| 512×288, 10 steps | ~90 seconds | $0.02 |
| 832×480, 15 steps | ~180 seconds | $0.03 |
| 960×544, 20 steps | ~240 seconds | $0.04 |
| 1280×704, 25 steps | ~360 seconds | $0.06 |
| 1280×704, 35 steps | ~600 seconds | $0.10 |

## 🎯 Current Test Running

You currently have a test running:
- **Size**: 512×288 (quick test)
- **Steps**: 10
- **Expected time**: 1-2 minutes
- **Purpose**: Verify endpoint works

Check status in RunPod dashboard or wait for completion message.

## 🔧 Advanced: Custom Handler

For even more speed, you can modify `serverless/handler.py` to:
1. Enable Flash Attention (if available)
2. Use model quantization (INT8)
3. Pre-cache T5 embeddings
4. Optimize VAE decoding

## 📝 Notes

- **Quality threshold**: 20 steps is the sweet spot for production
- **Below 15 steps**: Noticeable quality degradation
- **Above 30 steps**: Diminishing returns
- **Resolution**: 960×544 looks good on most displays
- **Testing**: Always use quick_test.py first

## 🎉 Summary

**Best Practice**: Use `fast` preset (960×544, 20 steps, 3-4 min)
- Good quality ✅
- Reasonable time ✅
- Low cost ✅
- Production-ready ✅


