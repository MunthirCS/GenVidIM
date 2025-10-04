#!/usr/bin/env python3
"""
Final test with correct parameters based on analysis
"""

import json
import urllib.request
import os
import time
import sys

def submit_final_test():
    """Submit final test with correct parameters"""
    
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
    
    print("🎯 FINAL TEST - CORRECT PARAMETERS")
    print("=" * 50)
    
    # Test animate-14B with correct size
    print("\n🔬 TEST 1: animate-14B with correct size")
    print("-" * 40)
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    
    payload = {
        "input": {
            "prompt": "a simple red circle",
            "task": "animate-14B",
            "steps": 5,
            "size": "1280*720"  # Correct size for animate-14B
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
            
            print(f"✅ Job submitted: {result.get('id')}")
            print(f"   Task: animate-14B")
            print(f"   Size: 1280*720 (correct)")
            print(f"   Steps: 5")
            
            return result.get('id')
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

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
        return None
    
    if not api_key or not endpoint_id:
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
        return None

def monitor_final_test(job_id):
    """Monitor the final test"""
    
    print(f"\n🔍 MONITORING JOB: {job_id}")
    print("-" * 40)
    
    max_checks = 20  # 10 minutes
    start_time = time.time()
    
    for i in range(max_checks):
        status = check_job_status(job_id)
        
        if status is None:
            print(f"❌ Failed to check status")
            return None
        
        elapsed = (time.time() - start_time) / 60
        print(f"[{elapsed:.1f}m] Status: {status}")
        
        if status == 'COMPLETED':
            print("🎉 SUCCESS! Job completed!")
            return True
        elif status == 'FAILED':
            print("❌ FAILED!")
            return False
        elif status in ['IN_PROGRESS', 'IN_QUEUE']:
            time.sleep(30)
        else:
            print(f"❓ Unknown status: {status}")
            time.sleep(30)
    
    print("⏰ TIMEOUT after 10 minutes")
    return None

if __name__ == "__main__":
    job_id = submit_final_test()
    if job_id:
        result = monitor_final_test(job_id)
        
        print(f"\n📊 FINAL TEST RESULT:")
        print("=" * 40)
        if result is True:
            print("✅ SUCCESS - Endpoint is working!")
        elif result is False:
            print("❌ FAILED - Need to check error details")
        else:
            print("⏰ TIMEOUT - Need to increase timeout or optimize")
