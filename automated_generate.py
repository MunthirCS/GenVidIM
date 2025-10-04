#!/usr/bin/env python3
"""
Automated Video Generation via SSH - Production Ready
"""

import subprocess
import sys

SSH_HOST = "runpod-genvidim"

def run_ssh_command(command, timeout=600):
    """Execute command on pod via SSH"""
    
    ssh_cmd = ['ssh', SSH_HOST, command]
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def generate_video(prompt, size="512*288", steps=10):
    """Generate video on RunPod"""
    
    print(f"\nGenerating Video on RunPod")
    print("="*60)
    print(f"Prompt: {prompt}")
    print(f"Size: {size}")
    print(f"Steps: {steps}")
    print("="*60)
    
    # Step 1: Setup GenVidIM
    print("\n[1/3] Setting up GenVidIM...")
    
    setup_cmd = """
cd /workspace
if [ ! -d "GenVidIM" ]; then
    git clone https://github.com/MunthirCS/GenVidIM.git
    cd GenVidIM
    pip install -q -r requirements.txt
else
    cd GenVidIM
    git pull
fi
echo "Setup complete"
"""
    
    success, stdout, stderr = run_ssh_command(setup_cmd, timeout=120)
    
    if not success:
        print(f"ERROR: Setup failed: {stderr}")
        return False
    
    print("SUCCESS: Setup complete!")
    
    # Step 2: Generate video
    print(f"\n[2/3] Generating video (estimated time: 1-2 minutes)...")
    
    generate_cmd = f"""
cd /workspace/GenVidIM
python generate.py \
  --task ti2v-5B \
  --size '{size}' \
  --sample_steps {steps} \
  --prompt "{prompt}" \
  --offload_model True \
  --convert_model_dtype \
  --t5_cpu
"""
    
    success, stdout, stderr = run_ssh_command(generate_cmd, timeout=600)
    
    if success:
        print("\nSUCCESS: Video generated successfully!")
        print(stdout[-500:] if len(stdout) > 500 else stdout)  # Last 500 chars
    else:
        print(f"\nERROR: Generation failed:")
        print(stderr)
        return False
    
    # Step 3: List videos
    print("\n[3/3] Finding generated video...")
    
    list_cmd = "ls -lh /workspace/GenVidIM/outputs/*.mp4 | tail -1"
    success, stdout, stderr = run_ssh_command(list_cmd)
    
    if success and stdout:
        print("SUCCESS: Video saved:")
        print(stdout)
        
        # Extract filename
        parts = stdout.split()
        filename = parts[-1] if parts else None
        
        if filename:
            print(f"\nTo download:")
            print(f"  scp runpod-genvidim:{filename} ./videos/")
        
        return True
    else:
        print("WARNING: Could not list videos")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
Automated Video Generation - Production Ready

Usage:
  python automated_generate.py "your prompt"
  python automated_generate.py "your prompt" --size 960*544 --steps 20

Examples:
  python automated_generate.py "a blue butterfly"
  python automated_generate.py "red sports car" --size 832*480 --steps 15

Speed presets:
  Quick test:  --size 512*288 --steps 10   (1-2 min)
  Fast:        --size 832*480 --steps 15   (2-3 min)
  Balanced:    --size 960*544 --steps 20   (3-4 min)
  Quality:     --size 1280*704 --steps 35  (8-10 min)
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

