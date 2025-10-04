#!/usr/bin/env python3
"""
Test with correct supported size for ti2v-5B
"""

import json
import urllib.request
import os
import time

def submit_corrected_test():
    """Submit test with correct size for ti2v-5B"""
    
    # Load API key and endpoint ID
    api_key = None
    endpoint_id = None
    
    try:
        with open('.runpod.env', 'r') as f:
            for line in f:
                if line.startswith('RUNPOD_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                elif line.startswith('RUNPOD_ENDPOINT_ID='):
                    endpoint_id = line.split('=', 1)[1].strip()
    except FileNotFoundError:
        print("❌ .runpod.env file not found")
        return
    
    if not api_key or not endpoint_id:
        print("❌ Missing API key or endpoint ID")
        return
    
    print(f"🚀 Submitting CORRECTED TEST to endpoint: {endpoint_id}")
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    
    # Use supported size for ti2v-5B
    payload = {
        "input": {
            "prompt": "a simple red circle",
            "task": "ti2v-5B",
            "steps": 5,  # Minimal steps for speed
            "size": "1280*704"  # Supported landscape size
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"\n✅ CORRECTED TEST SUBMITTED:")
            print("-" * 40)
            print(f"  Job ID: {result.get('id')}")
            print(f"  Status: {result.get('status')}")
            print(f"  Parameters: {json.dumps(payload['input'], indent=2)}")
            print(f"\n💡 This should work now - using supported size!")
            
            return result.get('id')
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    job_id = submit_corrected_test()
    if job_id:
        print(f"\n🔍 Monitor with: python check_job_status.py")
        print(f"   (Update job_id to: {job_id})")
