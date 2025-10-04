#!/usr/bin/env python3
"""
Test RunPod endpoint directly
"""

import json
import urllib.request
from pathlib import Path

# Load config
env = {}
with open('GenVidIM/.runpod.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            env[key] = val

endpoint_id = env['RUNPOD_ENDPOINT_ID']
api_key = env['RUNPOD_API_KEY']

print(f"\n🔍 Testing Endpoint: {endpoint_id}")
print("="*60)

# Test 1: Health check
try:
    url = f"https://api.runpod.ai/v2/{endpoint_id}/health"
    req = urllib.request.Request(url, headers={'Authorization': api_key})
    
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"\n✅ Health Check: {json.dumps(result, indent=2)}")
except Exception as e:
    print(f"\n❌ Health Check Failed: {e}")

# Test 2: Submit simple job with valid size
try:
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    payload = {
        "input": {
            "prompt": "a blue butterfly flying in a garden",
            "task": "ti2v-5B",
            "steps": 10,
            "size": "1280*704"  # Valid size for ti2v-5B task
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': api_key
        },
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"\n✅ Job Submission: {json.dumps(result, indent=2)}")
        
        if 'id' in result:
            print(f"\n📋 Job ID: {result['id']}")
            print("   Endpoint is working! Job submitted successfully.")
        
except urllib.error.HTTPError as e:
    print(f"\n❌ Job Submission Failed: HTTP {e.code}")
    print(f"   Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"\n❌ Job Submission Failed: {e}")

print("\n" + "="*60)
print("\n💡 If you see errors, rebuild the endpoint in RunPod dashboard")
print("   https://runpod.io/console/serverless\n")

