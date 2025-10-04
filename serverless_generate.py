#!/usr/bin/env python3
"""
Production-Ready Serverless Video Generation
Handles cold starts, queuing, and retries
"""

import json
import urllib.request
import time
import base64
from pathlib import Path

# Load config
env = {}
env_file = Path('.runpod.env')
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                env[key] = val

ENDPOINT_ID = env.get('RUNPOD_ENDPOINT_ID')
API_KEY = env.get('RUNPOD_API_KEY')


def submit_job(prompt, size="512*288", steps=10):
    """Submit video generation job"""
    
    url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"
    
    payload = {
        "input": {
            "prompt": prompt,
            "task": "ti2v-5B",
            "size": size,
            "steps": steps
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': API_KEY
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
    
    return result.get('id')


def check_status(job_id):
    """Check job status"""
    
    url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{job_id}"
    
    headers = {'Authorization': API_KEY}
    
    req = urllib.request.Request(url, headers=headers, method='GET')
    
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
    
    return result


def generate_video(prompt, size="512*288", steps=10, max_wait=1200):
    """
    Generate video with automatic handling of cold starts and queuing
    
    Args:
        prompt: Video prompt
        size: Video size (e.g., "512*288", "960*544")
        steps: Number of generation steps
        max_wait: Maximum wait time in seconds (default: 20 minutes)
    """
    
    print(f"\n{'='*60}")
    print(f"SERVERLESS VIDEO GENERATION")
    print(f"{'='*60}")
    print(f"Prompt: {prompt}")
    print(f"Size: {size}")
    print(f"Steps: {steps}")
    print(f"Endpoint: {ENDPOINT_ID}")
    print(f"{'='*60}\n")
    
    # Submit job
    print("[1/3] Submitting job to serverless endpoint...")
    job_id = submit_job(prompt, size, steps)
    
    if not job_id:
        print("ERROR: Failed to submit job")
        return False
    
    print(f"SUCCESS: Job submitted (ID: {job_id})")
    
    # Wait for completion
    print(f"\n[2/3] Waiting for completion...")
    print(f"  - Cold start may take 2-5 minutes")
    print(f"  - Generation takes 1-10 minutes depending on settings")
    print(f"  - Max wait time: {max_wait//60} minutes\n")
    
    start_time = time.time()
    check_count = 0
    last_status = None
    
    while True:
        time.sleep(10)
        check_count += 1
        elapsed = int(time.time() - start_time)
        
        try:
            status_data = check_status(job_id)
            status = status_data.get('status')
            
            # Print status updates
            if status != last_status:
                print(f"  [{elapsed}s] Status changed: {last_status} -> {status}")
                last_status = status
            elif check_count % 6 == 0:  # Every minute
                print(f"  [{elapsed}s] Still {status}...")
            
            # Handle different statuses
            if status == 'COMPLETED':
                print(f"\nSUCCESS: Generation completed after {elapsed}s!")
                
                output = status_data.get('output', {})
                
                if output.get('status') == 'success':
                    # Save video
                    video_data = output.get('video_data')
                    filename = output.get('video_filename', f'wan_output_{int(time.time())}.mp4')
                    
                    if video_data:
                        video_bytes = base64.b64decode(video_data)
                        output_path = Path('./videos') / filename
                        output_path.parent.mkdir(exist_ok=True)
                        output_path.write_bytes(video_bytes)
                        
                        print(f"\n[3/3] Video saved successfully!")
                        print(f"  Location: {output_path.absolute()}")
                        print(f"  Size: {len(video_bytes) / 1024 / 1024:.2f} MB")
                        print(f"  Time: {elapsed}s ({elapsed//60}m {elapsed%60}s)")
                        
                        return True
                else:
                    print(f"\nERROR: Generation failed")
                    print(f"  Error: {output.get('error')}")
                    return False
            
            elif status == 'FAILED':
                print(f"\nERROR: Job failed")
                print(f"  {status_data.get('error', 'Unknown error')}")
                return False
            
            elif status == 'IN_QUEUE':
                if elapsed > 300 and check_count % 6 == 0:  # After 5 min, remind every minute
                    print(f"  Note: Still waiting for GPU worker (cold start can take 5-10 minutes)")
            
            elif status == 'IN_PROGRESS':
                if check_count % 3 == 0:  # Every 30 seconds during generation
                    print(f"  Generating video... ({elapsed}s elapsed)")
            
            # Timeout
            if elapsed > max_wait:
                print(f"\nTIMEOUT: Exceeded {max_wait//60} minute limit")
                print(f"  Job may still be processing. Check RunPod dashboard:")
                print(f"  https://runpod.io/console/serverless")
                return False
                
        except Exception as e:
            print(f"  WARNING: Status check error: {e}")
            # Continue trying


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
SERVERLESS VIDEO GENERATION - Production Ready

Usage:
  python serverless_generate.py "your prompt"
  python serverless_generate.py "your prompt" --size 960*544 --steps 20

Speed presets (valid sizes):
  Quick test:  --size 480*832 --steps 10   (1-2 min generation)
  Fast:        --size 832*480 --steps 15   (2-3 min generation)
  HD:          --size 1280*720 --steps 20  (3-4 min generation)
  Portrait:    --size 720*1280 --steps 20  (3-4 min generation)

Note: First request includes 2-5 minute cold start time

Examples:
  python serverless_generate.py "a blue butterfly"
  python serverless_generate.py "red sports car" --size 832*480 --steps 15
        """)
        sys.exit(1)
    
    prompt = sys.argv[1]
    size = "480*832"  # Default to valid size
    steps = 10
    
    # Parse optional args
    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == '--size' and i+1 < len(sys.argv):
            size = sys.argv[i+1]
        elif arg == '--steps' and i+1 < len(sys.argv):
            steps = int(sys.argv[i+1])
    
    success = generate_video(prompt, size, steps, max_wait=1800)  # 30 min max
    sys.exit(0 if success else 1)

