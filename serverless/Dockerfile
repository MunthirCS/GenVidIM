FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

# GenVidIM Serverless - Complete Model Suite Build
# CUDA 12.1 compatible with all Wan models + Flash Attention 2
# Build date: 2025-10-04

# Install system dependencies and Python 3.10
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-dev \
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
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.10 /usr/bin/python \
    && python3.10 -m pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /workspace/GenVidIM

# Copy repository
COPY . /workspace/GenVidIM/

# Stage 1: Core dependencies with NumPy version control
RUN pip3 install --no-cache-dir \
    "numpy<2,>=1.23.5" \
    Pillow \
    packaging \
    requests

# Stage 2: Install PyTorch with CUDA 12.1 support
RUN pip3 install --no-cache-dir \
    torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 \
    --index-url https://download.pytorch.org/whl/cu121

# Stage 3: PyTorch ecosystem
RUN pip3 install --no-cache-dir \
    einops \
    safetensors

# Stage 4: HuggingFace and Diffusers
RUN pip3 install --no-cache-dir \
    transformers==4.51.3 \
    tokenizers \
    diffusers==0.31.0 \
    accelerate \
    sentencepiece

# Stage 5: Image/Video processing
RUN pip3 install --no-cache-dir \
    opencv-python-headless \
    imageio \
    imageio-ffmpeg \
    decord \
    av

# Fix NumPy version after decord (decord upgrades it to 2.x)
RUN pip3 install --no-cache-dir --force-reinstall "numpy<2,>=1.23.5"

# Stage 6: Audio processing
RUN pip3 install --no-cache-dir librosa

# Stage 7: Other dependencies
RUN pip3 install --no-cache-dir \
    ftfy \
    regex \
    omegaconf \
    easydict \
    tqdm \
    dashscope

# Stage 8: PEFT and optional acceleration
RUN pip3 install --no-cache-dir \
    peft \
    onnxruntime \
    pandas

# Stage 9: Flash Attention 2 (OPTIONAL - skip if fails)
# Note: Models work without Flash Attention 2, just slower
RUN pip3 install --no-cache-dir flash-attn --no-build-isolation || \
    echo "Flash Attention 2 installation failed, continuing without it (models will work but slower)"

# Stage 10: RunPod SDK
RUN pip3 install --no-cache-dir runpod

# Stage 11: Download COMPLETE model suite from HuggingFace
RUN pip3 install --no-cache-dir "huggingface_hub[cli]" && \
    mkdir -p /workspace/models

# Download all Wan model variants
RUN echo "Downloading Wan2.2-TI2V-5B..." && \
    huggingface-cli download Wan-AI/Wan2.2-TI2V-5B \
        --local-dir /workspace/models/Wan2.2-TI2V-5B \
        --quiet

RUN echo "Downloading Wan2.2-Animate-14B..." && \
    huggingface-cli download Wan-AI/Wan2.2-Animate-14B \
        --local-dir /workspace/models/Wan2.2-Animate-14B \
        --quiet

RUN echo "Downloading Wan2.2-S2V-14B..." && \
    huggingface-cli download Wan-AI/Wan2.2-S2V-14B \
        --local-dir /workspace/models/Wan2.2-S2V-14B \
        --quiet

RUN echo "Downloading Wan2.2-T2V-A14B..." && \
    huggingface-cli download Wan-AI/Wan2.2-T2V-A14B \
        --local-dir /workspace/models/Wan2.2-T2V-A14B \
        --quiet

# Create output directory
RUN mkdir -p /workspace/GenVidIM/outputs

# Verify critical imports and Flash Attention 2
RUN python -c "\
import sys; \
import torch; \
import numpy; \
print(f'Python: {sys.version}'); \
print(f'PyTorch: {torch.__version__}'); \
print(f'NumPy: {numpy.__version__}'); \
print(f'CUDA Version (compiled): {torch.version.cuda}'); \
assert numpy.__version__ < '2', f'ERROR: NumPy {numpy.__version__} >= 2.0'; \
import einops, transformers, diffusers, peft, decord, librosa, sentencepiece; \
print('All critical imports successful'); \
try: \
    import flash_attn; \
    print(f'Flash Attention 2: {flash_attn.__version__}'); \
    print('Flash Attention 2 available!'); \
except ImportError: \
    print('WARNING: Flash Attention 2 not available'); \
print('Note: CUDA will be available at runtime, not during build'); \
"

# Start the handler
CMD ["python", "-u", "serverless/handler.py"]

