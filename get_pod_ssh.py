#!/usr/bin/env python3
"""
Get SSH connection details for your RTX 5090 pod
"""

import json
import urllib.request
from pathlib import Path

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
    exit(1)

print("\n🔍 Fetching your pod connection details...")
print("="*60)

# GraphQL query to get pods
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
        uptimeInSeconds
      }
      machine {
        gpuDisplayName
      }
      costPerHr
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
            exit(1)
        
        for pod in pods:
            if pod.get('desiredStatus') == 'RUNNING':
                print(f"\n📦 Pod: {pod.get('name')}")
                print(f"   ID: {pod.get('id')}")
                print(f"   GPU: {pod.get('machine', {}).get('gpuDisplayName')}")
                print(f"   Cost: ${pod.get('costPerHr')}/hr")
                
                uptime = pod.get('runtime', {}).get('uptimeInSeconds', 0)
                hours = uptime / 3600
                print(f"   Uptime: {hours:.1f} hours")
                
                # Get SSH port
                ports = pod.get('runtime', {}).get('ports', [])
                ssh_port = None
                
                for port in ports:
                    if port.get('privatePort') == 22:
                        ssh_port = port.get('publicPort')
                        ssh_ip = port.get('ip')
                        break
                
                if ssh_port:
                    pod_id = pod.get('id')
                    print(f"\n🔌 SSH Connection:")
                    print(f"   ssh root@{ssh_ip} -p {ssh_port}")
                    print(f"\n   OR (using RunPod format):")
                    print(f"   ssh {pod_id}@ssh.runpod.io -p {ssh_port}")
                    
                    print(f"\n📋 Setup Commands (run after connecting):")
                    print(f"   cd /workspace")
                    print(f"   git clone https://github.com/MunthirCS/GenVidIM.git")
                    print(f"   cd GenVidIM")
                    print(f"   pip install -r requirements.txt")
                    
                    print(f"\n🎬 Quick Test Video:")
                    print(f'   python generate.py --task ti2v-5B --size "512*288" --sample_steps 10 \\')
                    print(f'     --prompt "a blue butterfly" --offload_model True --convert_model_dtype --t5_cpu')
                    
                else:
                    print(f"\n⚠️  SSH port not found. Use RunPod web terminal:")
                    print(f"   https://runpod.io/console/pods")
                
                print("\n" + "="*60)
        
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print("\n💡 Full setup guide: setup_rtx5090_pod.md")
print()

