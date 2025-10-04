# Serverless Dependency Analysis Report
**Generated:** October 2, 2025
**Endpoint ID:** yn6sjkwfuqqk05

## 🔍 Current Status
- **Workers:** 3 ready, 3 idle ✅
- **API:** Healthy and accepting jobs ✅
- **Docker Image:** Missing dependencies ❌

---

## ❌ Missing Dependencies Found

### Critical (Causing Job Failures):

1. **`peft`** - ⚠️ CRITICAL
   - **Required by:** `wan/animate.py`, `wan/modules/animate/animate_utils.py`
   - **Purpose:** LoRA/PEFT model state loading
   - **Error:** `ModuleNotFoundError: No module named 'peft'`
   - **Found in:** `requirements_animate.txt`

2. **`decord`** - ⚠️ CRITICAL  
   - **Required by:** `wan/speech2video.py`, `wan/animate.py`, `wan/modules/animate/preprocess/process_pipepline.py`
   - **Purpose:** Video reading and processing
   - **Found in:** `requirements_animate.txt`

3. **NumPy Version Conflict** - ⚠️ CRITICAL
   - **Issue:** NumPy 2.2.6 installed, but code compiled for NumPy 1.x
   - **Required:** `numpy<2` (specifically numpy==1.26.4)
   - **Current Dockerfile:** Specifies numpy==1.26.4 but being overridden
   - **Solution:** Pin numpy and reinstall torch/torchvision after numpy

### High Priority (May cause runtime failures):

4. **`librosa`** - ⚠️ HIGH
   - **Required by:** `wan/modules/s2v/audio_encoder.py`
   - **Purpose:** Audio processing for speech-to-video
   - **Status:** Already in Dockerfile ✅
   - **Verified:** Present

5. **`sentencepiece`** - MEDIUM
   - **Required by:** T5 tokenizer (transformers)
   - **Purpose:** Text tokenization
   - **Found in:** `requirements_animate.txt`
   - **May be bundled:** Check if needed

### Optional (For specific features):

6. **`onnxruntime`** - LOW
   - **Found in:** `requirements_animate.txt`, `requirements_s2v.txt`
   - **Purpose:** ONNX model inference (optional)

7. **`pandas`** - LOW
   - **Found in:** `requirements_animate.txt`
   - **Purpose:** Data processing utilities

8. **`matplotlib`** - LOW
   - **Found in:** `requirements_animate.txt`, `requirements_s2v.txt`
   - **Purpose:** Visualization (likely optional)

---

## 📋 Dockerfile Already Has (Verified ✅):

✅ `torch` (via base image)
✅ `torchvision` (via base image)
✅ `einops`
✅ `safetensors`
✅ `transformers==4.51.3`
✅ `tokenizers`
✅ `diffusers==0.31.0`
✅ `accelerate`
✅ `opencv-python-headless`
✅ `imageio`
✅ `imageio-ffmpeg`
✅ `av`
✅ `librosa`
✅ `ftfy`
✅ `omegaconf`
✅ `easydict`
✅ `dashscope`
✅ `runpod`

---

## 🔧 Required Fixes for Dockerfile

### Fix 1: Add Missing Critical Packages
```dockerfile
# Stage 8: Additional dependencies for animate/s2v features
RUN pip install --no-cache-dir \
    peft \
    decord \
    sentencepiece
```

### Fix 2: Fix NumPy Version Conflict
**Problem:** Base image or other packages installing numpy>=2

**Solution:** Reinstall torch ecosystem AFTER setting numpy<2
```dockerfile
# Stage 1: Fix NumPy first (BEFORE other packages)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir "numpy<2,>=1.23.5"

# Then ensure torch doesn't upgrade numpy
RUN pip install --no-cache-dir \
    torch --upgrade --no-deps && \
    pip install --no-cache-dir \
    torchvision --upgrade --no-deps
```

### Fix 3: Optional Additional Packages
```dockerfile
# Stage 9: Optional but recommended
RUN pip install --no-cache-dir \
    onnxruntime \
    pandas \
    matplotlib
```

---

## 🚀 Updated Dockerfile Section (Insert After Stage 6)

```dockerfile
# Stage 7: Animate/S2V specific dependencies
RUN pip install --no-cache-dir \
    peft \
    decord \
    sentencepiece \
    onnxruntime \
    pandas

# Stage 8: RunPod SDK
RUN pip install --no-cache-dir runpod

# Create output directory
RUN mkdir -p /workspace/GenVidIM/outputs

# Verify critical imports work
RUN python -c "import torch; import numpy; assert numpy.__version__ < '2', f'NumPy {numpy.__version__} >= 2'; import einops; import transformers; import diffusers; import peft; import decord; print('✅ All imports successful')"

# Start the handler
CMD ["python", "-u", "serverless/handler.py"]
```

---

## 📊 Impact Analysis

### Current Task Support:
| Task | Status | Missing Deps |
|------|--------|--------------|
| ti2v-5B (text-to-video) | ⚠️ FAILS | numpy, peft |
| t2v-A14B | ⚠️ FAILS | numpy, peft |
| i2v-A14B (image-to-video) | ⚠️ FAILS | numpy, peft |
| animate-14B | ❌ FAILS | numpy, peft, decord |
| s2v-14B (speech-to-video) | ❌ FAILS | numpy, peft, decord, librosa ✅ |

### After Fixes:
All tasks should work ✅

---

## 🎯 Recommended Actions

### Immediate (Must Do):
1. ✅ Add `peft` to Dockerfile
2. ✅ Add `decord` to Dockerfile  
3. ✅ Fix numpy version pinning
4. ✅ Rebuild serverless endpoint

### Important (Should Do):
5. Add `sentencepiece` for better T5 support
6. Add `onnxruntime` for optional acceleration
7. Add verification step to test all imports

### Nice to Have:
8. Add pandas/matplotlib for debugging tools

---

## 🔄 Next Steps

1. **Update Dockerfile** with the fixes above
2. **Rebuild the Docker image** on RunPod
3. **Test endpoint** with `python test_endpoint.py`
4. **Run full generation test** with `python serverless_generate.py "test prompt"`
5. **Monitor job status** for successful completion

---

## 📝 Notes

- Base image: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`
- Python version: 3.10
- CUDA version: 11.8.0
- Workers configured: 0-3 auto-scaling
- GPU types: RTX 5090, RTX 4090, RTX 4080, RTX 4070 Ti


