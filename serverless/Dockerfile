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

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install RunPod SDK
RUN pip install --no-cache-dir runpod

# Create output directory
RUN mkdir -p /workspace/GenVidIM/outputs

# Start the handler
CMD ["python", "-u", "serverless/handler.py"]
