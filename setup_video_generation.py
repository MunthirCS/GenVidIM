#!/usr/bin/env python3
"""
Video Generation Setup Script for RunPod
Run this on your RunPod instance to set up video generation models
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command and print output"""
    print(f"🔄 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"⚠️ {result.stderr}")
    
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    
    return result

def setup_environment():
    """Set up the basic environment"""
    print("🏗️ Setting up environment...")
    
    # Update system
    run_command("apt-get update")
    
    # Install system dependencies
    run_command("apt-get install -y git wget curl ffmpeg")
    
    # Install Python packages
    packages = [
        "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
        "transformers diffusers accelerate",
        "opencv-python pillow imageio imageio-ffmpeg",
        "huggingface_hub",
        "gradio streamlit",  # For web interfaces
        "jupyter jupyterlab",  # Enhanced Jupyter
    ]
    
    for package in packages:
        run_command(f"pip install {package}")

def setup_stable_video_diffusion():
    """Set up Stable Video Diffusion"""
    print("🎬 Setting up Stable Video Diffusion...")
    
    # Create workspace
    workspace = Path("/workspace/video_generation")
    workspace.mkdir(exist_ok=True)
    os.chdir(workspace)
    
    # Clone Stable Video Diffusion
    if not Path("generative-models").exists():
        run_command("git clone https://github.com/Stability-AI/generative-models.git")
    
    # Install requirements
    os.chdir("generative-models")
    run_command("pip install -e .")

def setup_animatediff():
    """Set up AnimateDiff"""
    print("🎭 Setting up AnimateDiff...")
    
    workspace = Path("/workspace/video_generation")
    os.chdir(workspace)
    
    # Clone AnimateDiff
    if not Path("AnimateDiff").exists():
        run_command("git clone https://github.com/guoyww/AnimateDiff.git")
    
    os.chdir("AnimateDiff")
    run_command("pip install -r requirements.txt")

def setup_wan22():
    """Set up Wan2.2 (the model we tried locally)"""
    print("🌟 Setting up Wan2.2...")
    
    workspace = Path("/workspace/video_generation")
    os.chdir(workspace)
    
    # Clone Wan2.2
    if not Path("Wan2.2").exists():
        run_command("git clone https://github.com/Wan-Video/Wan2.2.git")
    
    os.chdir("Wan2.2")
    run_command("pip install -r requirements.txt")

def create_web_interface():
    """Create a simple web interface for video generation"""
    print("🌐 Creating web interface...")
    
    interface_code = '''
import gradio as gr
import torch
import os
from pathlib import Path

def generate_video(prompt, model_choice, steps, guidance_scale):
    """Generate video based on prompt and settings"""
    
    # This is a placeholder - you'll implement specific model logic
    result_path = "/workspace/outputs/generated_video.mp4"
    
    # Create outputs directory
    Path("/workspace/outputs").mkdir(exist_ok=True)
    
    # Placeholder logic - replace with actual model inference
    status = f"""
    🎬 Video Generation Started
    
    Prompt: {prompt}
    Model: {model_choice}
    Steps: {steps}
    Guidance Scale: {guidance_scale}
    
    Status: Processing... (This is a placeholder)
    Output will be saved to: {result_path}
    """
    
    return status

def create_interface():
    """Create Gradio interface"""
    
    with gr.Blocks(title="RunPod Video Generation") as interface:
        gr.Markdown("# 🎬 Cloud Video Generation Studio")
        gr.Markdown("Generate videos using open-source models on RunPod")
        
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(
                    label="Video Prompt",
                    placeholder="A cute cat playing with a ball of yarn...",
                    lines=3
                )
                
                model_choice = gr.Dropdown(
                    choices=[
                        "Stable Video Diffusion",
                        "AnimateDiff",
                        "Wan2.2",
                        "CogVideo"
                    ],
                    label="Model",
                    value="Stable Video Diffusion"
                )
                
                steps = gr.Slider(
                    minimum=10,
                    maximum=100,
                    value=25,
                    label="Inference Steps"
                )
                
                guidance_scale = gr.Slider(
                    minimum=1.0,
                    maximum=20.0,
                    value=7.5,
                    label="Guidance Scale"
                )
                
                generate_btn = gr.Button("🚀 Generate Video", variant="primary")
            
            with gr.Column():
                output_text = gr.Textbox(
                    label="Generation Status",
                    lines=10,
                    interactive=False
                )
                
                output_video = gr.Video(label="Generated Video")
        
        generate_btn.click(
            fn=generate_video,
            inputs=[prompt, model_choice, steps, guidance_scale],
            outputs=[output_text]
        )
        
        gr.Markdown("""
        ## 📋 Instructions
        1. Enter your video prompt
        2. Choose a model
        3. Adjust settings
        4. Click Generate Video
        5. Wait for processing (can take 5-15 minutes)
        
        ## 💡 Tips
        - Be descriptive in your prompts
        - Start with lower steps for testing
        - Higher guidance scale = more prompt adherence
        """)
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )
'''
    
    # Write the interface code
    interface_path = Path("/workspace/video_interface.py")
    with open(interface_path, "w") as f:
        f.write(interface_code)
    
    print(f"✅ Web interface created at {interface_path}")
    print("   Run with: python /workspace/video_interface.py")

def create_jupyter_startup():
    """Create Jupyter startup script with useful imports"""
    print("📓 Setting up Jupyter environment...")
    
    startup_code = '''
# Video Generation Jupyter Startup
import torch
import torchvision
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os

# Check GPU
print(f"🔥 GPU Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   Device: {torch.cuda.get_device_name(0)}")
    print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")

# Set up workspace
workspace = Path("/workspace/video_generation")
workspace.mkdir(exist_ok=True)
os.chdir(workspace)

print("🚀 Ready for video generation!")
print("   Workspace:", workspace)
print("   Available models will be set up in subdirectories")
'''
    
    # Create Jupyter startup directory
    jupyter_dir = Path("/root/.ipython/profile_default/startup")
    jupyter_dir.mkdir(parents=True, exist_ok=True)
    
    # Write startup script
    startup_path = jupyter_dir / "00-video-generation.py"
    with open(startup_path, "w") as f:
        f.write(startup_code)
    
    print(f"✅ Jupyter startup script created at {startup_path}")

def main():
    """Main setup function"""
    print("🎬 RunPod Video Generation Setup")
    print("=" * 50)
    
    try:
        # Basic environment setup
        setup_environment()
        
        # Set up specific models (comment out what you don't need)
        setup_stable_video_diffusion()
        setup_animatediff()
        # setup_wan22()  # Uncomment if you want Wan2.2
        
        # Create interfaces
        create_web_interface()
        create_jupyter_startup()
        
        print("\n🎉 Setup Complete!")
        print("=" * 50)
        print("📋 What's available:")
        print("   • Stable Video Diffusion")
        print("   • AnimateDiff")
        print("   • Web interface at port 7860")
        print("   • Enhanced Jupyter Lab")
        print("\n🚀 Next steps:")
        print("   1. Start Jupyter Lab: jupyter lab --allow-root --ip=0.0.0.0")
        print("   2. Or run web interface: python /workspace/video_interface.py")
        print("   3. Access via RunPod's port forwarding")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
