FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    runpod \
    diffusers \
    transformers \
    accelerate \
    torch \
    torchvision \
    opencv-python \
    imageio \
    imageio-ffmpeg

# Set working directory
WORKDIR /workspace

# Copy the entire repository (when building from GitHub)
# RunPod will clone the repo automatically, so files are already present
COPY . /workspace/

# Install additional Wan2.2 requirements if needed
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy serverless handler to root
COPY serverless/handler.py /workspace/handler.py

# Download model on first run (optional - uncomment to pre-download)
# RUN huggingface-cli download Wan-AI/Wan2.2-TI2V-5B --local-dir ./Wan2.2-TI2V-5B

# Set working directory
WORKDIR /workspace

# Start the handler
CMD ["python", "-u", "handler.py"]
