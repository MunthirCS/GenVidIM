#!/usr/bin/env python3
"""
RunPod Serverless Integration
Create a serverless endpoint for video generation that can be called via API
"""

import requests
import json
import time
import base64
from typing import Dict, Optional
import os

class RunPodServerlessClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('RUNPOD_API_KEY')
        self.base_url = "https://api.runpod.ai/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_serverless_endpoint(self, name: str, docker_image: str = None):
        """Create a serverless endpoint for video generation"""
        
        # Default to a video generation optimized image
        if not docker_image:
            docker_image = "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
        
        endpoint_config = {
            "name": name,
            "template": {
                "imageName": docker_image,
                "containerDiskInGb": 20,
                "volumeInGb": 50,
                "env": [
                    {"key": "MODEL_CACHE_DIR", "value": "/runpod-volume/models"},
                    {"key": "OUTPUT_DIR", "value": "/runpod-volume/outputs"}
                ]
            },
            "workers": {
                "min": 0,  # Scale to zero when not in use
                "max": 1,  # Scale up as needed
                "gpuType": "NVIDIA RTX 4090"
            },
            "networkVolumeId": None  # Will use container storage
        }
        
        response = requests.post(
            f"{self.base_url}/endpoints",
            headers=self.headers,
            json=endpoint_config
        )
        
        return response.json()
    
    def run_video_generation(self, endpoint_id: str, prompt: str, 
                           model: str = "stable-video-diffusion",
                           **kwargs) -> Dict:
        """Run video generation on serverless endpoint"""
        
        payload = {
            "input": {
                "prompt": prompt,
                "model": model,
                "parameters": kwargs
            }
        }
        
        response = requests.post(
            f"{self.base_url}/endpoints/{endpoint_id}/run",
            headers=self.headers,
            json=payload
        )
        
        return response.json()
    
    def check_job_status(self, job_id: str) -> Dict:
        """Check the status of a video generation job"""
        
        response = requests.get(
            f"{self.base_url}/status/{job_id}",
            headers=self.headers
        )
        
        return response.json()
    
    def get_job_output(self, job_id: str) -> Dict:
        """Get the output of a completed job"""
        
        response = requests.get(
            f"{self.base_url}/status/{job_id}",
            headers=self.headers
        )
        
        result = response.json()
        
        if result.get("status") == "COMPLETED":
            return result.get("output", {})
        else:
            return {"status": result.get("status"), "error": result.get("error")}

# Handler function that would run on RunPod serverless
RUNPOD_HANDLER = '''
import runpod
import torch
from diffusers import StableVideoDiffusionPipeline
import tempfile
import base64
from pathlib import Path

# Global model loading (happens once per worker)
pipe = None

def load_model():
    """Load the video generation model"""
    global pipe
    if pipe is None:
        print("Loading Stable Video Diffusion model...")
        pipe = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt",
            torch_dtype=torch.float16
        )
        pipe.to("cuda")
        print("Model loaded successfully!")

def handler(job):
    """Main handler function for video generation"""
    try:
        load_model()
        
        # Get job inputs
        job_input = job["input"]
        prompt = job_input.get("prompt", "A beautiful landscape")
        model = job_input.get("model", "stable-video-diffusion")
        parameters = job_input.get("parameters", {})
        
        print(f"Generating video for prompt: {prompt}")
        
        # Generate video
        with torch.autocast("cuda"):
            frames = pipe(
                prompt, 
                num_frames=parameters.get("num_frames", 14),
                guidance_scale=parameters.get("guidance_scale", 7.5),
                num_inference_steps=parameters.get("steps", 25)
            ).frames[0]
        
        # Save video
        output_path = f"/tmp/generated_video_{job['id']}.mp4"
        
        # Convert frames to video (simplified)
        import imageio
        imageio.mimsave(output_path, frames, fps=8)
        
        # Encode video as base64 for return
        with open(output_path, "rb") as f:
            video_data = base64.b64encode(f.read()).decode()
        
        return {
            "status": "success",
            "video_base64": video_data,
            "metadata": {
                "prompt": prompt,
                "num_frames": len(frames),
                "model": model,
                "parameters": parameters
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# Start the serverless worker
runpod.serverless.start({"handler": handler})
'''

def create_serverless_setup():
    """Create setup files for serverless deployment"""
    
    # Create requirements for serverless
    requirements = """
runpod
torch
torchvision 
torchaudio
diffusers
transformers
accelerate
imageio
imageio-ffmpeg
pillow
numpy
"""
    
    with open("serverless_requirements.txt", "w") as f:
        f.write(requirements)
    
    # Create handler file
    with open("runpod_handler.py", "w") as f:
        f.write(RUNPOD_HANDLER)
    
    # Create Dockerfile
    dockerfile = """
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /app

COPY serverless_requirements.txt .
RUN pip install -r serverless_requirements.txt

COPY runpod_handler.py .

CMD ["python", "runpod_handler.py"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    
    print("✅ Serverless setup files created:")
    print("   • serverless_requirements.txt")
    print("   • runpod_handler.py") 
    print("   • Dockerfile")

if __name__ == "__main__":
    create_serverless_setup()
    
    print("\n🚀 RunPod Serverless Integration")
    print("=" * 40)
    print("This creates a serverless video generation API that:")
    print("  • Scales to zero when not in use (no cost)")
    print("  • Automatically scales up when needed")
    print("  • Can be called via simple HTTP requests")
    print("  • Returns generated videos as base64")
    print("\nNext steps:")
    print("  1. Deploy this as a RunPod serverless endpoint")
    print("  2. Get the endpoint URL")
    print("  3. We can integrate via API calls!")
