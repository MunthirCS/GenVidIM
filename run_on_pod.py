#!/usr/bin/env python3
"""
Execute commands on RunPod via SSH and generate video
"""

import subprocess
import sys
import time

# Pod connection details
POD_HOST = "root@149.36.1.141"
POD_PORT = "23404"

def run_ssh_command(command, wait_for_output=True):
    """Run command via SSH"""
    ssh_cmd = [
        "ssh",
        "-p", POD_PORT,
        "-o", "StrictHostKeyChecking=no",
        POD_HOST,
        command
    ]
    
    print(f"\n🔄 Running: {command[:80]}...")
    
    try:
        if wait_for_output:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            return result.returncode == 0
        else:
            # Run in background
            subprocess.Popen(ssh_cmd)
            return True
            
    except subprocess.TimeoutExpired:
        print("⚠️  Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║         🎬 RunPod Video Generation                      ║
║         GPU: RTX 5090                                   ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check if SSH works
    print("\n1️⃣ Testing SSH connection...")
    if not run_ssh_command("echo 'SSH connection successful!'"):
        print("\n❌ SSH connection failed!")
        print("\nPlease ensure:")
        print("  • You have SSH key configured in RunPod")
        print("  • Or connect manually using:")
        print(f"    ssh {POD_HOST} -p {POD_PORT}")
        sys.exit(1)
    
    print("✅ SSH connection working!")
    
    # Check if GenVidIM exists
    print("\n2️⃣ Checking if GenVidIM is installed...")
    
    if not run_ssh_command("test -d /workspace/GenVidIM && echo 'GenVidIM found' || echo 'GenVidIM not found'"):
        print("\n📦 Installing GenVidIM...")
        
        commands = [
            "cd /workspace",
            "git clone https://github.com/MunthirCS/GenVidIM.git",
            "cd GenVidIM && pip install -r requirements.txt"
        ]
        
        for cmd in commands:
            if not run_ssh_command(cmd):
                print(f"❌ Failed: {cmd}")
                sys.exit(1)
        
        print("✅ GenVidIM installed!")
    else:
        print("✅ GenVidIM already installed!")
    
    # Generate video
    print("\n3️⃣ Generating test video (this will take 1-2 minutes)...")
    print("="*60)
    
    prompt = input("Enter prompt (or press Enter for default): ").strip()
    if not prompt:
        prompt = "a blue butterfly flying over colorful flowers in slow motion"
    
    print(f"\n📝 Generating: {prompt}")
    print("⚙️  Settings: 512x288, 10 steps (quick test)")
    print("⏱️  Expected time: 1-2 minutes\n")
    
    generate_cmd = f'''cd /workspace/GenVidIM && python generate.py \
--task ti2v-5B \
--size "512*288" \
--sample_steps 10 \
--prompt "{prompt}" \
--offload_model True \
--convert_model_dtype \
--t5_cpu'''
    
    if run_ssh_command(generate_cmd):
        print("\n✅ Video generation completed!")
        
        # List videos
        print("\n4️⃣ Finding generated video...")
        run_ssh_command("ls -lh /workspace/GenVidIM/outputs/*.mp4 | tail -1")
        
        print("\n" + "="*60)
        print("📹 Video saved on pod at: /workspace/GenVidIM/outputs/")
        print("\n💾 To download the video:")
        print(f"   scp -P {POD_PORT} {POD_HOST}:/workspace/GenVidIM/outputs/*.mp4 ./")
        print("\n   OR use RunPod File Browser:")
        print("   https://runpod.io/console/pods → Your Pod → Connect → Browse Files")
        print("="*60)
        
    else:
        print("\n❌ Video generation failed")
        print("Check the pod directly: https://runpod.io/console/pods")


if __name__ == "__main__":
    main()

