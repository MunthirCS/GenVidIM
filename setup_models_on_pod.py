#!/usr/bin/env python3
"""
Automated script to download models to network volume via RTX 5090 pod
"""

import json
import urllib.request
import subprocess
import sys
from pathlib import Path

print("\n" + "="*70)
print("🤖 AUTOMATED MODEL SETUP FOR SERVERLESS")
print("="*70)

# Load API key
env = {}
env_file = Path('.runpod.env')
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                env[key] = val

api_key = env.get('RUNPOD_API_KEY')

if not api_key:
    print("❌ RUNPOD_API_KEY not found in .runpod.env")
    sys.exit(1)

print("\n[Step 1/5] Getting pod SSH details...")
print("-"*70)

# Get pod details
url = "https://api.runpod.io/graphql"

query = """
query Pods {
  myself {
    pods {
      id
      name
      desiredStatus
      runtime {
        ports {
          ip
          isIpPublic
          privatePort
          publicPort
          type
        }
      }
      machine {
        gpuDisplayName
      }
    }
  }
}
"""

headers = {
    'Content-Type': 'application/json',
    'Authorization': api_key
}

payload = json.dumps({"query": query})

try:
    req = urllib.request.Request(
        url,
        data=payload.encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        pods = result.get('data', {}).get('myself', {}).get('pods', [])
        
        if not pods:
            print("❌ No running pods found")
            sys.exit(1)
        
        # Find the running pod
        running_pod = None
        for pod in pods:
            if pod.get('desiredStatus') == 'RUNNING':
                running_pod = pod
                break
        
        if not running_pod:
            print("❌ No running pods found")
            sys.exit(1)
        
        pod_name = running_pod.get('name')
        pod_id = running_pod.get('id')
        gpu = running_pod.get('machine', {}).get('gpuDisplayName')
        
        print(f"✅ Found pod: {pod_name}")
        print(f"   GPU: {gpu}")
        print(f"   ID: {pod_id}")
        
        # Get SSH details
        ports = running_pod.get('runtime', {}).get('ports', [])
        ssh_port = None
        ssh_ip = None
        
        for port in ports:
            if port.get('privatePort') == 22:
                ssh_port = port.get('publicPort')
                ssh_ip = port.get('ip')
                break
        
        if not ssh_port:
            print("\n❌ SSH port not found. Please use RunPod web terminal instead.")
            print("   Go to: https://runpod.io/console/pods")
            print("   Click your pod → Connect → Web Terminal")
            print("\n   Then run these commands:")
            print("   cd /workspace")
            print("   git clone https://github.com/MunthirCS/GenVidIM.git")
            print("   cd GenVidIM")
            print("   bash serverless/download_models.sh")
            sys.exit(1)
        
        print(f"   SSH: root@{ssh_ip}:{ssh_port}")
        
except Exception as e:
    print(f"❌ Error getting pod details: {e}")
    sys.exit(1)

# Now run commands via SSH
print("\n[Step 2/5] Testing SSH connection...")
print("-"*70)

def run_ssh(command, timeout=600):
    """Run command via SSH"""
    ssh_cmd = [
        "ssh",
        "-p", str(ssh_port),
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        f"root@{ssh_ip}",
        command
    ]
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr}")
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⚠️  Command timed out after {timeout}s")
        return False
    except FileNotFoundError:
        print("\n❌ SSH not found on your system!")
        print("\n📱 ALTERNATIVE: Use RunPod Web Terminal")
        print("   1. Go to: https://runpod.io/console/pods")
        print(f"   2. Click pod: {pod_name}")
        print("   3. Click 'Connect' → 'Web Terminal'")
        print("   4. Run these commands:")
        print("      cd /workspace")
        print("      git clone https://github.com/MunthirCS/GenVidIM.git")
        print("      cd GenVidIM")
        print("      bash serverless/download_models.sh")
        return False
    except Exception as e:
        print(f"❌ SSH error: {e}")
        return False

# Test SSH
if not run_ssh("echo 'SSH connection successful!'"):
    print("\n❌ Cannot connect via SSH")
    print("\n📱 Use RunPod Web Terminal instead:")
    print(f"   ssh root@{ssh_ip} -p {ssh_port}")
    sys.exit(1)

print("✅ SSH connection working!")

# Check if network volume is mounted
print("\n[Step 3/5] Checking network volume...")
print("-"*70)

if run_ssh("ls /runpod-volume && echo 'Volume mounted' || echo 'Volume not found'"):
    print("✅ Network volume accessible at /runpod-volume")
else:
    print("⚠️  Network volume not mounted or not accessible")
    print("   This may still work if models are stored elsewhere")

# Clone or update repo
print("\n[Step 4/5] Setting up GenVidIM repository...")
print("-"*70)

# Check if repo exists
repo_exists = run_ssh("test -d /workspace/GenVidIM && echo 'exists' || echo 'not found'")

if 'not found' in subprocess.run(
    ["ssh", "-p", str(ssh_port), "-o", "StrictHostKeyChecking=no", f"root@{ssh_ip}", 
     "test -d /workspace/GenVidIM && echo 'exists' || echo 'not found'"],
    capture_output=True, text=True
).stdout:
    print("📥 Cloning GenVidIM repository...")
    run_ssh("cd /workspace && git clone https://github.com/MunthirCS/GenVidIM.git")
else:
    print("📥 Updating GenVidIM repository...")
    run_ssh("cd /workspace/GenVidIM && git pull origin main")

print("✅ Repository ready!")

# Download models
print("\n[Step 5/5] Downloading models to network volume...")
print("-"*70)
print("⚠️  This will take 10-30 minutes (~20-30 GB download)")
print("    Model: Wan2.2-TI2V-5B from HuggingFace")
print("")

response = input("Continue with model download? (y/n): ").lower()

if response != 'y':
    print("\n❌ Model download cancelled")
    print("\nTo download manually, run on the pod:")
    print("   cd /workspace/GenVidIM")
    print("   bash serverless/download_models.sh")
    sys.exit(0)

print("\n🚀 Starting model download...")
print("   This runs in the background. You can monitor progress in the pod terminal.")

# Run download script
download_cmd = """
cd /workspace/GenVidIM && \
export MODEL_DIR=/runpod-volume && \
bash serverless/download_models.sh
"""

print("\n📥 Downloading models...")
if run_ssh(download_cmd, timeout=3600):  # 1 hour timeout
    print("\n✅ Model download completed!")
    print("\n📦 Models installed at: /runpod-volume/Wan2.2-TI2V-5B")
    print("\n🎉 Setup complete! Serverless endpoint is ready to use!")
    print("\n🧪 Test your serverless endpoint:")
    print("   python test_endpoint.py")
    print("\n   OR generate a video:")
    print('   python serverless_generate.py "a blue butterfly flying" --size 1280*704 --steps 10')
else:
    print("\n⚠️  Download may have failed or is still running")
    print("\n📱 Check pod terminal to see progress:")
    print(f"   ssh root@{ssh_ip} -p {ssh_port}")
    print("   Then run: tail -f /workspace/GenVidIM/download.log")

print("\n" + "="*70)
print()


