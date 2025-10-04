#!/usr/bin/env python3
"""
Setup automated SSH connection to RunPod for production automation
"""

import json
import urllib.request
import subprocess
import os
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
POD_ID = 'jf6md7u8x71d53'

print("""
╔══════════════════════════════════════════════════════════╗
║   🔧 Setup Production SSH Automation                    ║
║   For automated video generation                        ║
╚══════════════════════════════════════════════════════════╝
""")

# Step 1: Get pod connection details via API
print("\n1️⃣ Getting pod SSH details...")

url = "https://api.runpod.io/graphql"

query = """
query Pods {
  myself {
    pods {
      id
      name
      runtime {
        ports {
          ip
          privatePort
          publicPort
        }
      }
    }
  }
}
"""

headers = {
    'Content-Type': 'application/json',
    'Authorization': API_KEY
}

payload = json.dumps({"query": query})

try:
    req = urllib.request.Request(url, data=payload.encode('utf-8'), headers=headers, method='POST')
    
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        pods = result.get('data', {}).get('myself', {}).get('pods', [])
        
        ssh_host = None
        ssh_port = None
        
        for pod in pods:
            if pod.get('id') == POD_ID:
                ports = pod.get('runtime', {}).get('ports', [])
                for port in ports:
                    if port.get('privatePort') == 22:
                        ssh_host = port.get('ip')
                        ssh_port = port.get('publicPort')
                        break
                break
        
        if not ssh_host or not ssh_port:
            print("❌ Could not find SSH port for pod")
            exit(1)
        
        print(f"✅ Found pod SSH details:")
        print(f"   Host: {ssh_host}")
        print(f"   Port: {ssh_port}")
        
        # Step 2: Check if SSH key exists
        print("\n2️⃣ Checking SSH key...")
        
        ssh_dir = Path.home() / '.ssh'
        ssh_key = ssh_dir / 'id_ed25519'
        ssh_pub = ssh_dir / 'id_ed25519.pub'
        
        if not ssh_key.exists():
            print("⚠️  SSH key not found. Generating new key...")
            ssh_dir.mkdir(exist_ok=True)
            
            # Generate SSH key
            result = subprocess.run([
                'ssh-keygen', '-t', 'ed25519',
                '-f', str(ssh_key),
                '-N', '',  # No passphrase for automation
                '-C', 'runpod-automation'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ SSH key generated!")
            else:
                print(f"❌ Failed to generate SSH key: {result.stderr}")
                exit(1)
        else:
            print("✅ SSH key already exists")
        
        # Show public key
        if ssh_pub.exists():
            with open(ssh_pub, 'r') as f:
                pub_key = f.read().strip()
            
            print(f"\n📋 Your public key (add to RunPod if not already):")
            print(f"   {pub_key}")
            print(f"\n   Add it at: https://www.runpod.io/console/user/settings")
        
        # Step 3: Setup SSH config
        print("\n3️⃣ Configuring SSH...")
        
        ssh_config = ssh_dir / 'config'
        config_entry = f"""
# RunPod Pod - GenVidIM
Host runpod-genvidim
    HostName {ssh_host}
    User root
    Port {ssh_port}
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
"""
        
        # Check if entry already exists
        config_exists = False
        if ssh_config.exists():
            with open(ssh_config, 'r') as f:
                content = f.read()
                if 'runpod-genvidim' in content:
                    config_exists = True
        
        if not config_exists:
            with open(ssh_config, 'a') as f:
                f.write(config_entry)
            print("✅ SSH config updated!")
        else:
            print("✅ SSH config already exists")
        
        # Step 4: Test connection
        print("\n4️⃣ Testing SSH connection...")
        
        test_result = subprocess.run([
            'ssh', '-o', 'ConnectTimeout=10',
            'runpod-genvidim',
            'echo "SSH connection successful!"'
        ], capture_output=True, text=True, timeout=15)
        
        if test_result.returncode == 0:
            print("✅ SSH connection works!")
            print(f"   Output: {test_result.stdout.strip()}")
        else:
            print(f"⚠️  SSH connection failed (this is expected if key not uploaded yet)")
            print(f"   Error: {test_result.stderr}")
            print("\n📝 To fix:")
            print("   1. Copy your public key from above")
            print("   2. Add it to: https://www.runpod.io/console/user/settings")
            print("   3. Restart your pod or run this in pod terminal:")
            print(f'      echo "{pub_key}" >> ~/.ssh/authorized_keys')
        
        # Step 5: Create automation script
        print("\n5️⃣ Creating automation script...")
        
        automation_script = Path('automated_generate.py')
        
        with open(automation_script, 'w') as f:
            f.write(f'''#!/usr/bin/env python3
"""
Automated Video Generation via SSH
Production-ready automation script
"""

import subprocess
import sys
import time

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
    
    print(f"\\n🎬 Generating Video on RunPod")
    print("="*60)
    print(f"📝 Prompt: {{prompt}}")
    print(f"📐 Size: {{size}}")
    print(f"⚙️  Steps: {{steps}}")
    print("="*60)
    
    # Step 1: Setup GenVidIM
    print("\\n1️⃣ Setting up GenVidIM...")
    
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
        print(f"❌ Setup failed: {{stderr}}")
        return False
    
    print("✅ Setup complete!")
    
    # Step 2: Generate video
    print("\\n2️⃣ Generating video (this will take 1-2 minutes)...")
    
    generate_cmd = f"""
cd /workspace/GenVidIM
python generate.py \\
  --task ti2v-5B \\
  --size '{{size}}' \\
  --sample_steps {{steps}} \\
  --prompt "{{prompt}}" \\
  --offload_model True \\
  --convert_model_dtype \\
  --t5_cpu
"""
    
    success, stdout, stderr = run_ssh_command(generate_cmd, timeout=600)
    
    if success:
        print("\\n✅ Video generated successfully!")
        print(stdout)
    else:
        print(f"\\n❌ Generation failed:")
        print(stderr)
        return False
    
    # Step 3: List videos
    print("\\n3️⃣ Finding generated video...")
    
    list_cmd = "ls -lh /workspace/GenVidIM/outputs/*.mp4 | tail -1"
    success, stdout, stderr = run_ssh_command(list_cmd)
    
    if success and stdout:
        print("✅ Video saved:")
        print(stdout)
        
        # Extract filename
        filename = stdout.split()[-1] if stdout else None
        
        if filename:
            print(f"\\n📥 To download:")
            print(f"   scp -P {{ssh_port}} root@{{ssh_host}}:{{filename}} ./")
        
        return True
    else:
        print("⚠️  Could not list videos")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
🎬 Automated Video Generation

Usage:
  python automated_generate.py "your prompt"
  python automated_generate.py "your prompt" --size 960*544 --steps 20

Examples:
  python automated_generate.py "a blue butterfly"
  python automated_generate.py "red sports car" --size 832*480 --steps 15
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
''')
        
        automation_script.chmod(0o755)
        print(f"✅ Created: {automation_script}")
        
        print("\n" + "="*60)
        print("✅ Setup Complete!")
        print("\n📚 Usage:")
        print(f'   python automated_generate.py "your prompt"')
        print("\n📝 Next Steps:")
        print("   1. Make sure your SSH key is uploaded to RunPod")
        print("   2. Test: python automated_generate.py \"test video\"")
        print("   3. Use in production!")
        print("="*60)
        
except Exception as e:
    print(f"\\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

