#!/usr/bin/env python3
"""
Client for RunPod Serverless Wan2.2 Endpoint
SCALABLE, PRODUCTION-READY SOLUTION
"""

import json
import urllib.request
import time
import sys
import base64
from pathlib import Path


def load_env():
    """Load environment from .runpod.env"""
    env_vars = {}
    env_file = Path('.runpod.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip()
    return env_vars


def submit_job(endpoint_id, api_key, prompt, task="ti2v-5B", size="1280*704", steps=35):
    """Submit job to RunPod serverless endpoint"""

    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"

    payload = {
        "input": {
            "prompt": prompt,
            "task": task,
            "size": size,
            "steps": steps
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': api_key
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


def check_status(endpoint_id, api_key, job_id):
    """Check job status"""

    url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"

    headers = {
        'Authorization': api_key
    }

    req = urllib.request.Request(url, headers=headers, method='GET')

    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))

    return result


def generate_video(prompt, task="ti2v-5B", size="1280*704", steps=35):
    """Generate video using RunPod Serverless"""

    print(f"\n🎬 Wan2.2 Video Generation (RunPod Serverless)")
    print(f"=" * 60)
    print(f"📝 Prompt: {prompt}")
    print(f"🎯 Task: {task}")
    print(f"📐 Size: {size}")
    print(f"⚙️  Steps: {steps}")
    print(f"=" * 60)
    print()

    env = load_env()
    endpoint_id = env.get('RUNPOD_ENDPOINT_ID')
    api_key = env.get('RUNPOD_API_KEY')

    if not endpoint_id:
        print("❌ RUNPOD_ENDPOINT_ID not set in .runpod.env")
        print("\nTo set up:")
        print("1. Deploy serverless endpoint (see DEPLOY_SERVERLESS.md)")
        print("2. Add RUNPOD_ENDPOINT_ID=your_endpoint_id to .runpod.env")
        return False

    if not api_key:
        print("❌ RUNPOD_API_KEY not set in .runpod.env")
        return False

    # Submit job
    print("📤 Submitting job to RunPod Serverless...")
    job_id = submit_job(endpoint_id, api_key, prompt, task, size, steps)

    if not job_id:
        print("❌ Failed to submit job")
        return False

    print(f"✅ Job submitted: {job_id}")
    print(f"\n⏳ Waiting for completion (5-10 minutes)...")
    print(f"   Checking status every 10 seconds...")
    print()

    start_time = time.time()
    check_count = 0

    while True:
        time.sleep(10)
        check_count += 1
        elapsed = int(time.time() - start_time)

        # Check status
        status_data = check_status(endpoint_id, api_key, job_id)
        status = status_data.get('status')

        if check_count % 6 == 0:  # Every minute
            print(f"   [{elapsed}s] Status: {status}")

        if status == 'COMPLETED':
            print(f"\n✅ Generation completed after {elapsed}s!")

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

                    print(f"\n📹 Video saved: {output_path}")
                    print(f"   Size: {len(video_bytes) / 1024 / 1024:.2f} MB")

                print(f"\n✅ Success!")
                return True
            else:
                print(f"\n❌ Generation failed:")
                print(f"   Error: {output.get('error')}")
                return False

        elif status == 'FAILED':
            print(f"\n❌ Job failed:")
            print(f"   {status_data.get('error', 'Unknown error')}")
            return False

        # Timeout after 15 minutes
        if elapsed > 900:
            print(f"\n⚠️  Timeout after 15 minutes")
            return False


def main():
    if len(sys.argv) < 2:
        print("""
🎬 RunPod Serverless Video Generator

Usage:
  python serverless/runpod_client.py "your prompt"
  python serverless/runpod_client.py "your prompt" --steps 40

Examples:
  python serverless/runpod_client.py "ships sailing in a volcano"
  python serverless/runpod_client.py "dragon flying" --steps 50

This uses RunPod Serverless - fully scalable and production-ready!
        """)
        sys.exit(1)

    prompt = sys.argv[1]
    steps = 35

    # Parse optional args
    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == '--steps' and i+1 < len(sys.argv):
            steps = int(sys.argv[i+1])

    success = generate_video(prompt, steps=steps)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
