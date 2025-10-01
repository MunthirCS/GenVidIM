FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace/GenVidIM

# Copy entire GenVidIM repository
COPY . /workspace/GenVidIM/

# Create requirements without flash_attn (it's optional and causes build failures)
RUN grep -v "flash_attn" requirements.txt > requirements_minimal.txt || true

# Install Python dependencies (without flash_attn)
RUN pip install --no-cache-dir -r requirements_minimal.txt || \
    pip install --no-cache-dir \
    torch>=2.4.0 \
    torchvision>=0.19.0 \
    torchaudio \
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
    "numpy>=1.23.5,<2"

# Install RunPod SDK
RUN pip install --no-cache-dir runpod

# Create output directory
RUN mkdir -p /workspace/GenVidIM/outputs

# Start the handler
CMD ["python", "-u", "serverless/handler.py"]
