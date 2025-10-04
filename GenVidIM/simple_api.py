#!/usr/bin/env python3
"""
Simple HTTP API for video generation on RTX 5090 pod
Production-ready alternative to serverless
"""

from flask import Flask, request, jsonify, send_file
import subprocess
import os
import uuid
from pathlib import Path
import threading
import time

app = Flask(__name__)

# Configuration
OUTPUT_DIR = Path("/workspace/GenVidIM/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Job tracking
jobs = {}

def generate_video_task(job_id, prompt, size="512*288", steps=10):
    """Background task for video generation"""
    
    try:
        jobs[job_id]["status"] = "IN_PROGRESS"
        jobs[job_id]["started_at"] = time.time()
        
        # Run generation
        cmd = [
            "python", "generate.py",
            "--task", "ti2v-5B",
            "--size", size,
            "--sample_steps", str(steps),
            "--prompt", prompt,
            "--offload_model", "True",
            "--convert_model_dtype",
            "--t5_cpu"
        ]
        
        result = subprocess.run(
            cmd,
            cwd="/workspace/GenVidIM",
            capture_output=True,
            text=True,
            timeout=1200
        )
        
        if result.returncode == 0:
            # Find generated video
            videos = sorted(OUTPUT_DIR.glob("*.mp4"), key=lambda x: x.stat().st_mtime)
            
            if videos:
                latest_video = videos[-1]
                jobs[job_id]["status"] = "COMPLETED"
                jobs[job_id]["video_path"] = str(latest_video)
                jobs[job_id]["completed_at"] = time.time()
            else:
                jobs[job_id]["status"] = "FAILED"
                jobs[job_id]["error"] = "No video file generated"
        else:
            jobs[job_id]["status"] = "FAILED"
            jobs[job_id]["error"] = result.stderr
            
    except subprocess.TimeoutExpired:
        jobs[job_id]["status"] = "FAILED"
        jobs[job_id]["error"] = "Generation timed out"
    except Exception as e:
        jobs[job_id]["status"] = "FAILED"
        jobs[job_id]["error"] = str(e)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "gpu": "RTX 5090"})


@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate video from prompt
    
    POST /generate
    {
        "prompt": "your prompt here",
        "size": "512*288",  // optional
        "steps": 10         // optional
    }
    """
    
    data = request.json
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in request"}), 400
    
    prompt = data['prompt']
    size = data.get('size', '512*288')
    steps = data.get('steps', 10)
    
    # Create job
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "id": job_id,
        "status": "IN_QUEUE",
        "prompt": prompt,
        "size": size,
        "steps": steps,
        "created_at": time.time()
    }
    
    # Start generation in background
    thread = threading.Thread(
        target=generate_video_task,
        args=(job_id, prompt, size, steps)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "job_id": job_id,
        "status": "IN_QUEUE",
        "message": "Video generation started"
    }), 202


@app.route('/status/<job_id>', methods=['GET'])
def status(job_id):
    """Check job status"""
    
    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404
    
    job = jobs[job_id].copy()
    
    # Calculate elapsed time
    if "started_at" in job:
        elapsed = time.time() - job["started_at"]
        job["elapsed_seconds"] = int(elapsed)
    
    return jsonify(job)


@app.route('/download/<job_id>', methods=['GET'])
def download(job_id):
    """Download generated video"""
    
    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404
    
    job = jobs[job_id]
    
    if job["status"] != "COMPLETED":
        return jsonify({"error": f"Job status: {job['status']}"}), 400
    
    video_path = job.get("video_path")
    
    if not video_path or not os.path.exists(video_path):
        return jsonify({"error": "Video file not found"}), 404
    
    return send_file(
        video_path,
        mimetype='video/mp4',
        as_attachment=True,
        download_name=f"{job_id}.mp4"
    )


@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    return jsonify({"jobs": list(jobs.values())})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎬 GenVidIM HTTP API - Production Ready")
    print("="*60)
    print("\nEndpoints:")
    print("  POST   /generate      - Generate video")
    print("  GET    /status/<id>   - Check job status")
    print("  GET    /download/<id> - Download video")
    print("  GET    /health        - Health check")
    print("  GET    /jobs          - List all jobs")
    print("\nStarting server on 0.0.0.0:8000...")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=8000, threaded=True)

