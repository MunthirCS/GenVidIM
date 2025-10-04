#!/usr/bin/env python3
"""
Monitor job progress with periodic checks
"""

import json
import urllib.request
import os
import time
import sys

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
        return None
    
    if not api_key or not endpoint_id:
        print("❌ Missing API key or endpoint ID")
        return None
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('status')
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def monitor_job(job_id, max_checks=20):
    """Monitor job with periodic checks"""
    
    print(f"🔍 Monitoring job: {job_id}")
    print("=" * 60)
    
    for i in range(max_checks):
        status = check_job_status(job_id)
        
        if status is None:
            print(f"❌ Failed to check status (attempt {i+1})")
            time.sleep(30)
            continue
        
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] Status: {status}")
        
        if status == 'COMPLETED':
            print("🎉 Job completed successfully!")
            return True
        elif status == 'FAILED':
            print("❌ Job failed!")
            return False
        elif status in ['IN_PROGRESS', 'IN_QUEUE']:
            print(f"⏳ Still processing... (check {i+1}/{max_checks})")
            time.sleep(30)
        else:
            print(f"❓ Unknown status: {status}")
            time.sleep(30)
    
    print("⏰ Monitoring timeout reached")
    return None

if __name__ == "__main__":
    job_id = "8c544691-7690-4b28-8aff-ec9803ebc254-e2"
    monitor_job(job_id)
