#!/bin/bash
# RunPod Quick Setup for Video Generation
# Upload this file to your RunPod instance and run: bash runpod_quick_setup.sh

echo "🚀 Setting up RunPod for Video Generation..."
echo "================================================"

# Update system
echo "📦 Updating system packages..."
apt-get update -y
apt-get install -y git wget curl ffmpeg htop tree

# Install Python packages
echo "🐍 Installing Python packages..."
pip install --upgrade pip

# Core ML packages
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers diffusers accelerate huggingface_hub

# Video/Image processing
pip install opencv-python pillow imageio imageio-ffmpeg decord
pip install einops timm

# Web interfaces
pip install gradio streamlit jupyter jupyterlab

# Utilities
pip install tqdm requests python-dotenv

echo "🎬 Setting up video generation models..."

# Create workspace structure
mkdir -p /workspace/video_generation
mkdir -p /workspace/outputs
mkdir -p /workspace/models
mkdir -p /workspace/collaboration_logs

cd /workspace/video_generation

# Clone popular video generation repositories
echo "📥 Cloning Stable Video Diffusion..."
if [ ! -d "generative-models" ]; then
    git clone https://github.com/Stability-AI/generative-models.git
    cd generative-models
    pip install -e .
    cd ..
fi

echo "📥 Cloning AnimateDiff..."
if [ ! -d "AnimateDiff" ]; then
    git clone https://github.com/guoyww/AnimateDiff.git
    cd AnimateDiff
    pip install -r requirements.txt
    cd ..
fi

echo "📥 Cloning CogVideo..."
if [ ! -d "CogVideo" ]; then
    git clone https://github.com/THUDM/CogVideo.git
    cd CogVideo
    pip install -r requirements.txt
    cd ..
fi

# Create a simple test script
cat > /workspace/test_setup.py << 'EOF'
#!/usr/bin/env python3
"""Test script to verify setup"""

import torch
import sys
from pathlib import Path

def test_gpu():
    """Test GPU availability"""
    print("🔥 GPU Test:")
    print(f"   CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   Device: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
        
        # Test tensor operations
        x = torch.randn(1000, 1000).cuda()
        y = torch.matmul(x, x)
        print(f"   ✅ GPU computation test passed")
    else:
        print("   ❌ No GPU available")

def test_models():
    """Test model availability"""
    print("\n📚 Model Test:")
    
    try:
        from diffusers import StableDiffusionPipeline
        print("   ✅ Diffusers available")
    except ImportError:
        print("   ❌ Diffusers not available")
    
    try:
        from transformers import AutoModel
        print("   ✅ Transformers available")
    except ImportError:
        print("   ❌ Transformers not available")
    
    # Check repositories
    repos = [
        "/workspace/video_generation/generative-models",
        "/workspace/video_generation/AnimateDiff", 
        "/workspace/video_generation/CogVideo"
    ]
    
    for repo in repos:
        if Path(repo).exists():
            print(f"   ✅ {Path(repo).name} cloned")
        else:
            print(f"   ❌ {Path(repo).name} missing")

def test_workspace():
    """Test workspace setup"""
    print("\n📁 Workspace Test:")
    
    dirs = [
        "/workspace/video_generation",
        "/workspace/outputs",
        "/workspace/models",
        "/workspace/collaboration_logs"
    ]
    
    for dir_path in dirs:
        if Path(dir_path).exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} missing")

if __name__ == "__main__":
    print("🧪 RunPod Setup Test")
    print("=" * 30)
    
    test_gpu()
    test_models()
    test_workspace()
    
    print("\n🎉 Setup test complete!")
    print("\n📋 Copy this output and share with Claude for next steps.")
EOF

# Make test script executable
chmod +x /workspace/test_setup.py

echo "✅ Setup complete!"
echo "================================================"
echo "🎉 Your RunPod instance is ready for video generation!"
echo ""
echo "📋 Next steps:"
echo "   1. Run test: python /workspace/test_setup.py"
echo "   2. Copy the output and share with Claude"
echo "   3. Start generating videos!"
echo ""
echo "🔗 Useful paths:"
echo "   • Workspace: /workspace/video_generation"
echo "   • Outputs: /workspace/outputs"
echo "   • Logs: /workspace/collaboration_logs"
echo ""
echo "🌐 Access points:"
echo "   • Jupyter Lab: http://localhost:8888 (password: runpod)"
echo "   • Terminal: Available in Jupyter or SSH"

