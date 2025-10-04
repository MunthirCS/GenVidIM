"""
RunPod Serverless Handler for Wan2.2 Video Generation
This runs ON RunPod serverless workers
"""

import runpod
import subprocess
import os
from pathlib import Path
import logging
import uuid
import time
import torch

# --- Configuration ---
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define model paths and other constants
MODEL_BASE_PATH = Path('/workspace/models')
OUTPUT_BASE_PATH = Path('/workspace/GenVidIM/outputs')
MODEL_DIRS = {
    't2v-A14B': MODEL_BASE_PATH / 'Wan2.2-T2V-A14B',
    'i2v-A14B': MODEL_BASE_PATH / 'Wan2.2-I2V-A14B',
    'ti2v-5B': MODEL_BASE_PATH / 'Wan2.2-TI2V-5B',
    's2v-14B': MODEL_BASE_PATH / 'Wan2.2-S2V-14B',
    'animate-14B': MODEL_BASE_PATH / 'Wan2.2-Animate-14B'
}
DEFAULT_TASK = 'ti2v-5B'
JOB_TIMEOUT = 1200  # 20 minutes

# --- Health Check ---
def health_check(job):
    """
    Health check endpoint to verify the environment and model availability.
    RunPod will call this endpoint to ensure the worker is ready.
    """
    # Check if essential directories exist
    if not MODEL_BASE_PATH.exists() or not OUTPUT_BASE_PATH.exists():
        return {"error": "Essential directories are missing."}

    # Check if at least one model is available
    if not any(MODEL_DIRS.values()):
        return {"error": "No models found."}

    return {"status": "ok"}

# --- Video Generation ---
def generate_video(job):
    """
    Main handler for video generation.
    """
    start_time = time.time()
    job_input = job['input']
    job_id = job.get('id', str(uuid.uuid4()))

    # Extract and validate parameters
    prompt = job_input.get('prompt')
    if not prompt:
        logging.error(f"Job {job_id}: No prompt provided.")
        return {"error": "A prompt is required."}

    task = job_input.get('task', DEFAULT_TASK)
    size = job_input.get('size', '1280*704')
    steps = job_input.get('steps', 35)

    logging.info(f"Job {job_id}: Starting generation for task '{task}' with prompt: '{prompt}'")

    # Select model directory
    ckpt_dir = get_model_dir(task)
    if not ckpt_dir or not ckpt_dir.exists():
        logging.error(f"Job {job_id}: Model directory for task '{task}' not found.")
        return {"error": f"Model for task '{task}' is not available."}

    # Determine the number of GPUs
    num_gpus = torch.cuda.device_count()

    # Build the generation command
    if num_gpus > 1:
        cmd = [
            'torchrun',
            f'--nproc_per_node={num_gpus}',
            'generate.py',
            '--task', task,
            '--size', size,
            '--sample_steps', str(steps),
            '--prompt', prompt,
            '--ckpt_dir', str(ckpt_dir),
            '--dit_fsdp',
            '--t5_fsdp',
            f'--ulysses_size={num_gpus}'
        ]
    else:
        cmd = [
            'python', 'generate.py',
            '--task', task,
            '--size', size,
            '--sample_steps', str(steps),
            '--prompt', prompt,
            '--ckpt_dir', str(ckpt_dir),
            '--offload_model', 'True',
            '--convert_model_dtype',
            '--t5_cpu'
        ]

    # Add prompt extension arguments if provided
    if job_input.get('use_prompt_extend'):
        cmd.append('--use_prompt_extend')
        if job_input.get('prompt_extend_method'):
            cmd.extend(['--prompt_extend_method', job_input['prompt_extend_method']])
        if job_input.get('prompt_extend_model'):
            cmd.extend(['--prompt_extend_model', job_input['prompt_extend_model']])
        if job_input.get('prompt_extend_target_lang'):
            cmd.extend(['--prompt_extend_target_lang', job_input['prompt_extend_target_lang']])

    # Execute the generation process
    try:
        logging.info(f"Job {job_id}: Executing command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd='/workspace/GenVidIM',
            capture_output=True,
            text=True,
            timeout=JOB_TIMEOUT
        )

        if result.returncode != 0:
            logging.error(f"Job {job_id}: Generation failed. Stderr: {result.stderr}")
            return {
                "error": "Video generation process failed.",
                "stderr": result.stderr,
                "stdout": result.stdout
            }

        # Find the most recently generated video
        video_files = sorted(OUTPUT_BASE_PATH.glob('*.mp4'), key=lambda p: p.stat().st_mtime, reverse=True)
        if not video_files:
            logging.error(f"Job {job_id}: No video file was generated.")
            return {
                "error": "Generation completed, but no video file was found.",
                "stdout": result.stdout
            }

        latest_video_path = video_files[0]
        processing_time = time.time() - start_time
        logging.info(f"Job {job_id}: Generation successful in {processing_time:.2f} seconds. Video: {latest_video_path}")

        # Return the path to the video file for RunPod to handle
        return {
            "status": "success",
            "video_path": str(latest_video_path),
            "processing_time_seconds": round(processing_time, 2),
            "stdout": result.stdout[-1000:]
        }

    except subprocess.TimeoutExpired:
        logging.error(f"Job {job_id}: Generation timed out after {JOB_TIMEOUT} seconds.")
        return {"error": f"Process timed out after {JOB_TIMEOUT // 60} minutes."}
    except Exception as e:
        logging.error(f"Job {job_id}: An unexpected error occurred: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}

def get_model_dir(task):
    """Returns the model directory for the given task."""
    return MODEL_DIRS.get(task)

# --- Start Serverless Worker ---
# Register the handlers with RunPod
runpod.serverless.start({
    "handler": generate_video,
    "health_check": health_check
})
