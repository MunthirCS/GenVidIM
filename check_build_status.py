#!/usr/bin/env python3
"""
Check serverless endpoint build status
"""

import json
import urllib.request
from pathlib import Path

env = {}
with open('.runpod.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            env[key] = val

API_KEY = env['RUNPOD_API_KEY']
ENDPOINT_ID = env['RUNPOD_ENDPOINT_ID']

url = "https://api.runpod.io/graphql"

query = """
query {
  myself {
    endpoints {
      id
      name
      version
      workersRunning
      workersIdle
      workersMax
      workersMin
    }
  }
}
"""

headers = {
    'Content-Type': 'application/json',
    'Authorization': API_KEY
}

payload = json.dumps({"query": query})

req = urllib.request.Request(url, data=payload.encode('utf-8'), headers=headers, method='POST')

with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    
    endpoints = result.get('data', {}).get('myself', {}).get('endpoints', [])
    
    print("\n" + "="*60)
    print("SERVERLESS ENDPOINTS STATUS")
    print("="*60)
    
    for ep in endpoints:
        if ep['id'] == ENDPOINT_ID:
            print(f"\nEndpoint: {ep['name']}")
            print(f"ID: {ep['id']}")
            print(f"Version: {ep.get('version', 'N/A')}")
            print(f"Workers Running: {ep.get('workersRunning', 0)}")
            print(f"Workers Idle: {ep.get('workersIdle', 0)}")
            print(f"Min/Max Workers: {ep.get('workersMin', 0)}/{ep.get('workersMax', 0)}")
            
            if ep.get('workersRunning', 0) == 0 and ep.get('workersIdle', 0) == 0:
                print("\nSTATUS: No workers available (build may be incomplete)")
            else:
                print("\nSTATUS: Workers available")
    
    print("\n" + "="*60)
    print("\nRECOMMENDATION:")
    print("1. Go to: https://runpod.io/console/serverless")
    print("2. Check build status on GenVidIM endpoint")
    print("3. If stuck, cancel and rebuild")
    print("4. Meanwhile, use RTX 5090 pod via web terminal")
    print("="*60 + "\n")

