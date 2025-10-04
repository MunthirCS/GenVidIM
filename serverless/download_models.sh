#!/bin/bash
# Download Wan2.2 models to network volume
# This should be run once to populate the network volume

set -e

echo "=========================================="
echo "Downloading Wan2.2-TI2V-5B Model"
echo "=========================================="

# Install huggingface-cli if not present
pip install -q "huggingface_hub[cli]"

# Download model to network volume
# For serverless, this should be downloaded to /runpod-volume
MODEL_DIR="${MODEL_DIR:-/runpod-volume}"

echo "Downloading to: $MODEL_DIR"

# Download TI2V-5B model (smallest, runs on 24GB GPU)
huggingface-cli download Wan-AI/Wan2.2-TI2V-5B \
    --local-dir "$MODEL_DIR/Wan2.2-TI2V-5B" \
    --resume-download

echo ""
echo "=========================================="
echo "✅ Model download complete!"
echo "=========================================="
echo "Model location: $MODEL_DIR/Wan2.2-TI2V-5B"
echo ""
echo "Handler will use: --ckpt_dir $MODEL_DIR/Wan2.2-TI2V-5B"
echo ""

