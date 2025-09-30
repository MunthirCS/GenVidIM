FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone Wan2.2 repository
RUN git clone https://github.com/Wan-xiaohui/Wan2.2.git /workspace/Wan2.2

# Install Wan2.2 requirements
WORKDIR /workspace/Wan2.2
RUN pip install --no-cache-dir -r requirements.txt

# Install RunPod SDK
RUN pip install --no-cache-dir runpod

# Copy handler from your repo
COPY serverless/handler.py /workspace/handler.py

# Set working directory back to workspace
WORKDIR /workspace

# Start the handler
CMD ["python", "-u", "handler.py"]
