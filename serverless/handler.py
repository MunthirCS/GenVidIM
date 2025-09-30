"""
RunPod Serverless Handler for Wan2.2 Video Generation
This runs ON RunPod serverless workers
"""

import runpod
import subprocess
import os
from pathlib import Path


def generate_video(job):
    """
    Main handler for video generation

    Input format:
    {
        "input": {
            "prompt": "your prompt here",
            "task": "ti2v-5B",
            "size": "1280*704",
            "steps": 35
        }
    }
    """

    job_input = job['input']

    # Extract parameters
    prompt = job_input.get('prompt', '')
    task = job_input.get('task', 'ti2v-5B')
    size = job_input.get('size', '1280*704')
    steps = job_input.get('steps', 35)

    if not prompt:
        return {"error": "No prompt provided"}

    print(f"🎬 Starting generation: {prompt}")

    # Build command
    cmd = [
        'python', 'generate.py',
        '--task', task,
        '--size', size,
        '--ckpt_dir', './Wan2.2-TI2V-5B',
        '--sample_steps', str(steps),
        '--prompt', prompt,
        '--offload_model', 'True',
        '--convert_model_dtype',
        '--t5_cpu'
    ]

    # Execute
    try:
        result = subprocess.run(
            cmd,
            cwd='/workspace/Wan2.2',
            capture_output=True,
            text=True,
            timeout=1200  # 20 minutes
        )

        if result.returncode != 0:
            return {
                "error": "Generation failed",
                "stderr": result.stderr,
                "stdout": result.stdout
            }

        # Find generated video
        video_files = list(Path('/workspace/Wan2.2').glob('*.mp4'))
        if not video_files:
            return {
                "error": "No video file generated",
                "stdout": result.stdout
            }

        # Get the most recent video
        latest_video = max(video_files, key=lambda p: p.stat().st_mtime)

        # Read video file as base64 (or upload to S3/cloud storage)
        import base64
        video_data = base64.b64encode(latest_video.read_bytes()).decode('utf-8')

        return {
            "status": "success",
            "video_filename": latest_video.name,
            "video_data": video_data,
            "stdout": result.stdout[-1000:]  # Last 1000 chars
        }

    except subprocess.TimeoutExpired:
        return {"error": "Generation timed out after 20 minutes"}
    except Exception as e:
        return {"error": str(e)}


# Start the serverless worker
runpod.serverless.start({"handler": generate_video})
