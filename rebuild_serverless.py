#!/usr/bin/env python3
"""
Force rebuild of serverless endpoint via RunPod API
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

API_KEY = env.get('RUNPOD_API_KEY')
ENDPOINT_ID = env.get('RUNPOD_ENDPOINT_ID')

print(f"""
╔══════════════════════════════════════════════════════════╗
║   🔧 Force Rebuild Serverless Endpoint                  ║
╚══════════════════════════════════════════════════════════╝

Endpoint ID: {ENDPOINT_ID}
""")

# GraphQL mutation to trigger rebuild
url = "https://api.runpod.io/graphql"

# Try to cancel current build and start new one
cancel_mutation = """
mutation {
  cancelEndpointBuild(input: {endpointId: "%s"}) {
    id
  }
}
""" % ENDPOINT_ID

rebuild_mutation = """
mutation {
  rebuildEndpoint(input: {endpointId: "%s"}) {
    id
    name
  }
}
""" % ENDPOINT_ID

headers = {
    'Content-Type': 'application/json',
    'Authorization': API_KEY
}

try:
    # Cancel current build
    print("1️⃣ Cancelling stuck build...")
    payload = json.dumps({"query": cancel_mutation})
    req = urllib.request.Request(url, data=payload.encode('utf-8'), headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"   Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   Note: {e}")
    
    # Trigger rebuild
    print("\n2️⃣ Triggering new build from GitHub...")
    payload = json.dumps({"query": rebuild_mutation})
    req = urllib.request.Request(url, data=payload.encode('utf-8'), headers=headers, method='POST')
    
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"   ✅ Build triggered!")
        print(f"   Response: {json.dumps(result, indent=2)}")
    
    print("\n" + "="*60)
    print("✅ New build started!")
    print("\n⏳ Build will take 5-10 minutes")
    print("📊 Monitor at: https://runpod.io/console/serverless")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Alternative: Manually rebuild in dashboard")
    print("   https://runpod.io/console/serverless")


