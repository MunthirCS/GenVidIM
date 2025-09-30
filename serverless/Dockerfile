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

# Clone Wan2.2 repository
WORKDIR /workspace
RUN git clone https://github.com/Wan-Video/Wan2.2.git

# Download model (optional - can be done on first run)
# RUN cd Wan2.2 && huggingface-cli download Wan-AI/Wan2.2-TI2V-5B --local-dir ./Wan2.2-TI2V-5B

# Copy handler
COPY handler.py /workspace/handler.py

# Set working directory
WORKDIR /workspace

# Start the handler
CMD ["python", "-u", "handler.py"]
