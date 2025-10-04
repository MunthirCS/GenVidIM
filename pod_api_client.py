#!/usr/bin/env python3
"""
Client for GenVidIM HTTP API running on RTX 5090 pod
WORKING PRODUCTION SOLUTION
"""

import requests
import time
import sys
from pathlib import Path

# Your pod's public IP and port (get from RunPod dashboard)
POD_IP = "149.36.1.141"  # Update if changed
POD_PORT = "8000"  # Default API port

API_URL = f"http://{POD_IP}:{POD_PORT}"


def generate_video(prompt, size="512*288", steps=10):
    """Generate video via HTTP API"""
    
    print(f"\n{'='*60}")
    print("PRODUCTION VIDEO GENERATION - RTX 5090 Pod")
    print(f"{'='*60}")
    print(f"Prompt: {prompt}")
    print(f"Size: {size}")
    print(f"Steps: {steps}")
    print(f"API: {API_URL}")
    print(f"{'='*60}\n")
    
    # Submit job
    print("[1/3] Submitting job...")
    
    try:
        response = requests.post(
            f"{API_URL}/generate",
            json={
                "prompt": prompt,
                "size": size,
                "steps": steps
            },
            timeout=30
        )
        
        if response.status_code != 202:
            print(f"ERROR: Failed to submit job: {response.text}")
            return False
        
        result = response.json()
        job_id = result['job_id']
        
        print(f"SUCCESS: Job submitted (ID: {job_id})")
        
    except Exception as e:
        print(f"ERROR: Cannot connect to API: {e}")
        print("\nMake sure:")
        print("1. API is running on pod: python simple_api.py")
        print("2. Port 8000 is exposed in RunPod")
        print("3. Pod IP is correct")
        return False
    
    # Wait for completion
    print(f"\n[2/3] Waiting for completion...")
    
    start_time = time.time()
    
    while True:
        time.sleep(5)
        elapsed = int(time.time() - start_time)
        
        try:
            response = requests.get(f"{API_URL}/status/{job_id}", timeout=10)
            status_data = response.json()
            
            status = status_data['status']
            
            if status == 'COMPLETED':
                print(f"\nSUCCESS: Generation completed!")
                print(f"Time: {elapsed}s ({elapsed//60}m {elapsed%60}s)")
                
                # Download video
                print(f"\n[3/3] Downloading video...")
                
                response = requests.get(
                    f"{API_URL}/download/{job_id}",
                    timeout=60
                )
                
                if response.status_code == 200:
                    output_dir = Path('./videos')
                    output_dir.mkdir(exist_ok=True)
                    
                    output_path = output_dir / f"{job_id}.mp4"
                    output_path.write_bytes(response.content)
                    
                    size_mb = len(response.content) / 1024 / 1024
                    
                    print(f"SUCCESS: Video saved!")
                    print(f"Location: {output_path.absolute()}")
                    print(f"Size: {size_mb:.2f} MB")
                    
                    return True
                else:
                    print(f"ERROR: Download failed: {response.text}")
                    return False
                    
            elif status == 'FAILED':
                print(f"\nERROR: Generation failed")
                print(f"Error: {status_data.get('error', 'Unknown error')}")
                return False
                
            elif status == 'IN_PROGRESS':
                if elapsed % 30 == 0:  # Every 30 seconds
                    print(f"  [{elapsed}s] Generating...")
            else:
                print(f"  [{elapsed}s] Status: {status}")
            
            # Timeout after 20 minutes
            if elapsed > 1200:
                print(f"\nTIMEOUT: Exceeded 20 minute limit")
                return False
                
        except Exception as e:
            print(f"  WARNING: Status check error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
PRODUCTION VIDEO GENERATION - RTX 5090 Pod

Usage:
  python pod_api_client.py "your prompt"
  python pod_api_client.py "your prompt" --size 960*544 --steps 20

Examples:
  python pod_api_client.py "a blue butterfly"
  python pod_api_client.py "red sports car" --size 960*544 --steps 20

Speed presets:
  Quick:    --size 512*288 --steps 10   (1-2 min)
  Fast:     --size 832*480 --steps 15   (2-3 min)
  Balanced: --size 960*544 --steps 20   (3-4 min)
  Quality:  --size 1280*704 --steps 35  (8-10 min)
        """)
        sys.exit(1)
    
    prompt = sys.argv[1]
    size = "512*288"
    steps = 10
    
    # Parse optional args
    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == '--size' and i+1 < len(sys.argv):
            size = sys.argv[i+1]
        elif arg == '--steps' and i+1 < len(sys.argv):
            steps = int(sys.argv[i+1])
    
    success = generate_video(prompt, size, steps)
    sys.exit(0 if success else 1)

