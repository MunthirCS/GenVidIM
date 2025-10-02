FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# GenVidIM Serverless - Build date: 2025-10-02
# Fixed dependencies: peft, decord, sentencepiece, numpy<2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace/GenVidIM

# Copy repository
COPY . /workspace/GenVidIM/

# Install Python dependencies in stages for better error handling

# Stage 1: Core dependencies with NumPy version control (CRITICAL)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    "numpy<2,>=1.23.5" \
    Pillow \
    packaging \
    requests

# Stage 2: PyTorch ecosystem (ensure no numpy upgrade)
RUN pip install --no-cache-dir \
    einops \
    safetensors

# Stage 3: HuggingFace and Diffusers
RUN pip install --no-cache-dir \
    transformers==4.51.3 \
    tokenizers \
    diffusers==0.31.0 \
    accelerate \
    sentencepiece

# Stage 4: Image/Video processing
RUN pip install --no-cache-dir \
    opencv-python-headless \
    imageio \
    imageio-ffmpeg \
    decord \
    av

# Stage 5: Audio processing
RUN pip install --no-cache-dir \
    librosa

# Stage 6: Other dependencies
RUN pip install --no-cache-dir \
    ftfy \
    regex \
    omegaconf \
    easydict \
    tqdm \
    dashscope

# Stage 7: PEFT and optional acceleration (CRITICAL - was missing!)
RUN pip install --no-cache-dir \
    peft \
    onnxruntime \
    pandas

# Stage 8: RunPod SDK
RUN pip install --no-cache-dir runpod

# Create output directory
RUN mkdir -p /workspace/GenVidIM/outputs

# Verify critical imports work
RUN python -c "\
import sys; \
import torch; \
import numpy; \
print(f'NumPy version: {numpy.__version__}'); \
assert numpy.__version__ < '2', f'ERROR: NumPy {numpy.__version__} >= 2.0'; \
import einops; \
import transformers; \
import diffusers; \
import peft; \
import decord; \
import librosa; \
import sentencepiece; \
print('✅ All critical imports successful'); \
print(f'Python: {sys.version}'); \
print(f'PyTorch: {torch.__version__}'); \
print(f'CUDA Available: {torch.cuda.is_available()}'); \
"

# Start the handler
CMD ["python", "-u", "serverless/handler.py"]

