FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace/GenVidIM

# Copy entire GenVidIM repository
COPY . /workspace/GenVidIM/

# Install Python dependencies (skip flash_attn if it fails)
RUN pip install --no-cache-dir torch>=2.4.0 torchvision>=0.19.0 torchaudio && \
    pip install --no-cache-dir \
    opencv-python>=4.9.0.80 \
    diffusers>=0.31.0 \
    transformers>=4.49.0 \
    tokenizers>=0.20.3 \
    accelerate>=1.1.1 \
    tqdm \
    imageio[ffmpeg] \
    easydict \
    ftfy \
    dashscope \
    imageio-ffmpeg \
    "numpy>=1.23.5,<2" && \
    pip install --no-cache-dir flash-attn --no-build-isolation || echo "flash-attn install failed, continuing without it"

# Install RunPod SDK
RUN pip install --no-cache-dir runpod

# Create output directory
RUN mkdir -p /workspace/GenVidIM/outputs

# Start the handler
CMD ["python", "-u", "serverless/handler.py"]
