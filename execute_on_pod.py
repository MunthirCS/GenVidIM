#!/usr/bin/env python3
"""
Execute commands on RunPod pod via API
No SSH needed!
"""

import json
import urllib.request
import time
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

API_KEY = env.get('RUNPOD_API_KEY')
POD_ID = 'jf6md7u8x71d53'  # Your RTX 5090 pod


def exec_command(command, description=""):
    """Execute command on pod via API"""
    
    if description:
        print(f"\n🔄 {description}")
    
    url = f"https://api.runpod.io/v2/pods/{POD_ID}/exec"
    
    payload = {
        "command": command if isinstance(command, list) else ["/bin/bash", "-c", command]
    }
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            # Print output if available
            if 'output' in result:
                print(result['output'])
            elif 'stdout' in result:
                print(result['stdout'])
            else:
                print(json.dumps(result, indent=2))
            
            return result
            
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        print(f"❌ HTTP Error {e.code}: {error_msg}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   🎬 RunPod Video Generation via API                    ║
║   GPU: RTX 5090                                         ║
║   Pod ID: jf6md7u8x71d53                                ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    if not API_KEY:
        print("❌ RUNPOD_API_KEY not found in .runpod.env")
        return
    
    # Step 1: Check if pod is accessible
    print("\n1️⃣ Testing pod connection...")
    result = exec_command("echo 'Pod is accessible!'", "Testing connection")
    
    if not result:
        print("\n❌ Cannot connect to pod via API")
        print("This might be because:")
        print("  • Pod needs to be restarted")
        print("  • API exec endpoint not available for this pod type")
        print("\nTrying alternative method...")
        return
    
    print("✅ Pod is accessible!")
    
    # Step 2: Setup GenVidIM if not exists
    print("\n2️⃣ Setting up GenVidIM...")
    
    setup_commands = """
if [ ! -d "/workspace/GenVidIM" ]; then
    echo "Installing GenVidIM..."
    cd /workspace
    git clone https://github.com/MunthirCS/GenVidIM.git
    cd GenVidIM
    pip install -q -r requirements.txt
    echo "✅ GenVidIM installed!"
else
    echo "✅ GenVidIM already exists"
fi
"""
    
    exec_command(setup_commands, "Checking/Installing GenVidIM")
    
    # Step 3: Generate video
    print("\n3️⃣ Generating test video...")
    print("="*60)
    print("📝 Prompt: a blue butterfly flying over flowers")
    print("⚙️  Settings: 512x288, 10 steps (quick test)")
    print("⏱️  Expected time: 1-2 minutes")
    print("="*60)
    
    generate_cmd = """
cd /workspace/GenVidIM
python generate.py \
  --task ti2v-5B \
  --size '512*288' \
  --sample_steps 10 \
  --prompt "a blue butterfly flying over colorful flowers in slow motion" \
  --offload_model True \
  --convert_model_dtype \
  --t5_cpu
"""
    
    print("\n🎬 Starting generation (this may take 1-2 minutes)...")
    result = exec_command(generate_cmd, "")
    
    # Step 4: List generated videos
    print("\n4️⃣ Checking generated videos...")
    exec_command("ls -lh /workspace/GenVidIM/outputs/*.mp4 2>/dev/null || echo 'No videos found yet'")
    
    print("\n" + "="*60)
    print("✅ Commands executed!")
    print("\n📹 Videos saved at: /workspace/GenVidIM/outputs/")
    print("\n💾 To download:")
    print("   • Use RunPod File Browser")
    print("   • Or SCP: scp -P 23404 root@149.36.1.141:/workspace/GenVidIM/outputs/*.mp4 ./")
    print("="*60)


if __name__ == "__main__":
    main()

