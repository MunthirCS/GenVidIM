# --- Builder Stage ---
# This stage installs all dependencies, including build-time tools.
FROM python:3.10-slim AS builder

# Set environment variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install all Python dependencies in a single layer
COPY GenVidIM/requirements.txt GenVidIM/requirements_animate.txt GenVidIM/requirements_s2v.txt GenVidIM/requirements_gradio.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements_animate.txt && \
    pip install --no-cache-dir -r requirements_s2v.txt && \
    pip install --no-cache-dir -r requirements_gradio.txt && \
    pip install --no-cache-dir torch>=2.4.0 torchvision>=0.19.0 torchaudio --index-url https://download.pytorch.org/whl/cu121 && \
    pip install --no-cache-dir flash-attn --no-build-isolation || echo "Flash Attention 2 failed, continuing..."

# --- Runtime Stage ---
# This stage creates the final, lean image.
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install runtime system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the working directory
WORKDIR /workspace/GenVidIM

# Copy the application code
COPY . /workspace/GenVidIM/

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Create directories for models and outputs
RUN mkdir -p /workspace/models /workspace/GenVidIM/outputs

# Models should be mounted via a network volume, not downloaded in the Dockerfile.
# RUN pip install "huggingface_hub[cli]" && \
#     huggingface-cli download Wan-AI/Wan2.2-TI2V-5B --local-dir /workspace/models/Wan2.2-TI2V-5B --quiet && \
#     huggingface-cli download Wan-AI/Wan2.2-Animate-14B --local-dir /workspace/models/Wan2.2-Animate-14B --quiet && \
#     huggingface-cli download Wan-AI/Wan2.2-S2V-14B --local-dir /workspace/models/Wan2.2-S2V-14B --quiet && \
#     huggingface-cli download Wan-AI/Wan2.2-T2V-A14B --local-dir /workspace/models/Wan2.2-T2V-A14B --quiet && \
#     rm -rf /root/.cache/huggingface

# Set the entrypoint
CMD ["python", "-u", "serverless/handler.py"]

