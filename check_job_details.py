#!/usr/bin/env python3
"""
Check detailed job error from RunPod
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

ENDPOINT_ID = env['RUNPOD_ENDPOINT_ID']
API_KEY = env['RUNPOD_API_KEY']
JOB_ID = "4f2c9f08-8aa8-4c1f-987d-94fd3599ce54-e1"

url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{JOB_ID}"

headers = {'Authorization': API_KEY}

req = urllib.request.Request(url, headers=headers, method='GET')

with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))

print("\n" + "="*60)
print("JOB DETAILS")
print("="*60)
print(json.dumps(result, indent=2))
print("="*60 + "\n")

