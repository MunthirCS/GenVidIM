#!/usr/bin/env python3
"""
Check the latest job status
"""

import json
import urllib.request
import os
import time

def check_job_status(job_id):
    """Check status of a specific job"""
    
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
    
    print(f"🔍 Checking job: {job_id}")
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"\n📋 JOB STATUS:")
            print("-" * 40)
            print(f"  ID: {result.get('id')}")
            print(f"  Status: {result.get('status')}")
            
            if result.get('status') == 'COMPLETED':
                print(f"  ✅ Job completed successfully!")
                output = result.get('output', {})
                if output:
                    print(f"  📁 Output: {output}")
            elif result.get('status') == 'FAILED':
                print(f"  ❌ Job failed!")
                error = result.get('error', 'Unknown error')
                print(f"  Error: {error}")
            elif result.get('status') == 'IN_PROGRESS':
                print(f"  ⏳ Job in progress...")
            elif result.get('status') == 'IN_QUEUE':
                print(f"  📋 Job queued...")
            
            return result.get('status')
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    # Check the latest job
    job_id = "8c544691-7690-4b28-8aff-ec9803ebc254-e2"
    check_job_status(job_id)
