import time
import subprocess
import os
from pathlib import Path

# --- Configuration ---
MODEL_CHOICES = [
    't2v-A14B',
    'i2v-A14B',
    'ti2v-5B',
    's2v-14B',
    'animate-14B'
]
SIZES = ["1280*720", "640*360"]
STEPS = [20, 50]
PROMPTS = [
    "A cat wearing a wizard hat",
    "A photorealistic dog flying a kite",
    "A beautiful landscape with a waterfall"
]

def run_benchmark():
    """
    Runs a series of benchmarks to measure the performance of the deployment.
    """
    results = []

    for model in MODEL_CHOICES:
        for size in SIZES:
            for step in STEPS:
                for prompt in PROMPTS:
                    start_time = time.time()

                    cmd = [
                        'python', 'generate.py',
                        '--task', model,
                        '--size', size,
                        '--sample_steps', str(step),
                        '--prompt', prompt,
                        '--ckpt_dir', f"/workspace/models/Wan2.2-{model}",
                        '--offload_model', 'True',
                        '--convert_model_dtype',
                        '--t5_cpu'
                    ]

                    try:
                        result = subprocess.run(
                            cmd,
                            cwd='/workspace/GenVidIM',
                            capture_output=True,
                            text=True,
                            timeout=1200
                        )

                        end_time = time.time()
                        duration = end_time - start_time

                        if result.returncode == 0:
                            results.append({
                                "model": model,
                                "size": size,
                                "steps": step,
                                "prompt": prompt,
                                "duration": duration,
                                "status": "success"
                            })
                        else:
                            results.append({
                                "model": model,
                                "size": size,
                                "steps": step,
                                "prompt": prompt,
                                "duration": duration,
                                "status": "failed",
                                "error": result.stderr
                            })
                    except Exception as e:
                        end_time = time.time()
                        duration = end_time - start_time
                        results.append({
                            "model": model,
                            "size": size,
                            "steps": step,
                            "prompt": prompt,
                            "duration": duration,
                            "status": "failed",
                            "error": str(e)
                        })

    # Print results
    for result in results:
        print(result)

if __name__ == "__main__":
    run_benchmark()
