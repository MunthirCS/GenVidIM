#!/usr/bin/env python3
"""
Comprehensive test suite for serverless endpoint
Tests different tasks and parameters to identify what works
"""

import json
import urllib.request
import os
import time
import sys

def submit_test_job(task, prompt, size, steps=5):
    """Submit a test job with specific parameters"""
    
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
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    
    payload = {
        "input": {
            "prompt": prompt,
            "task": task,
            "steps": steps,
            "size": size
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
            return result.get('id')
                
    except Exception as e:
        print(f"❌ Error submitting job: {e}")
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

def monitor_job(job_id, max_wait_minutes=5):
    """Monitor job with timeout"""
    
    max_checks = max_wait_minutes * 2  # Check every 30 seconds
    start_time = time.time()
    
    for i in range(max_checks):
        status = check_job_status(job_id)
        
        if status is None:
            print(f"❌ Failed to check status")
            return None
        
        elapsed = (time.time() - start_time) / 60
        print(f"  [{elapsed:.1f}m] Status: {status}")
        
        if status == 'COMPLETED':
            print("  ✅ SUCCESS!")
            return True
        elif status == 'FAILED':
            print("  ❌ FAILED!")
            return False
        elif status in ['IN_PROGRESS', 'IN_QUEUE']:
            time.sleep(30)
        else:
            print(f"  ❓ Unknown status: {status}")
            time.sleep(30)
    
    print(f"  ⏰ TIMEOUT after {max_wait_minutes} minutes")
    return None

def run_test_suite():
    """Run comprehensive test suite"""
    
    print("🧪 COMPREHENSIVE SERVERLESS TEST SUITE")
    print("=" * 60)
    
    # Test configurations
    tests = [
        # Task: animate
        {
            "name": "Animate Task - Small Size",
            "task": "animate",
            "prompt": "a simple red circle",
            "size": "512*512",
            "steps": 5
        },
        {
            "name": "Animate Task - Medium Size", 
            "task": "animate",
            "prompt": "a simple red circle",
            "size": "832*480",
            "steps": 5
        },
        
        # Task: ti2v-5B (text-image-to-video)
        {
            "name": "TI2V-5B Task - Landscape",
            "task": "ti2v-5B", 
            "prompt": "a simple red circle",
            "size": "1280*704",
            "steps": 5
        },
        {
            "name": "TI2V-5B Task - Portrait",
            "task": "ti2v-5B",
            "prompt": "a simple red circle", 
            "size": "704*1280",
            "steps": 5
        },
        
        # Task: s2v (speech-to-video)
        {
            "name": "S2V Task - Small",
            "task": "s2v",
            "prompt": "hello world",
            "size": "512*512", 
            "steps": 5
        },
        
        # Task: t2v (text-to-video)
        {
            "name": "T2V Task - Small",
            "task": "t2v",
            "prompt": "a simple red circle",
            "size": "512*512",
            "steps": 5
        }
    ]
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(f"\n🔬 TEST {i}/{len(tests)}: {test['name']}")
        print("-" * 50)
        print(f"  Task: {test['task']}")
        print(f"  Size: {test['size']}")
        print(f"  Steps: {test['steps']}")
        print(f"  Prompt: {test['prompt']}")
        
        # Submit job
        job_id = submit_test_job(
            test['task'], 
            test['prompt'], 
            test['size'], 
            test['steps']
        )
        
        if not job_id:
            print("  ❌ Failed to submit job")
            results.append({**test, 'result': 'SUBMIT_FAILED'})
            continue
        
        print(f"  📋 Job ID: {job_id}")
        
        # Monitor job
        result = monitor_job(job_id, max_wait_minutes=3)  # 3 min timeout per test
        
        if result is True:
            results.append({**test, 'result': 'SUCCESS', 'job_id': job_id})
        elif result is False:
            results.append({**test, 'result': 'FAILED', 'job_id': job_id})
        else:
            results.append({**test, 'result': 'TIMEOUT', 'job_id': job_id})
        
        # Wait between tests
        if i < len(tests):
            print(f"\n⏳ Waiting 30s before next test...")
            time.sleep(30)
    
    # Summary
    print(f"\n📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r['result'] == 'SUCCESS')
    failed_count = sum(1 for r in results if r['result'] == 'FAILED')
    timeout_count = sum(1 for r in results if r['result'] == 'TIMEOUT')
    submit_failed_count = sum(1 for r in results if r['result'] == 'SUBMIT_FAILED')
    
    print(f"✅ SUCCESS: {success_count}")
    print(f"❌ FAILED: {failed_count}")
    print(f"⏰ TIMEOUT: {timeout_count}")
    print(f"🚫 SUBMIT_FAILED: {submit_failed_count}")
    
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        status_emoji = {
            'SUCCESS': '✅',
            'FAILED': '❌', 
            'TIMEOUT': '⏰',
            'SUBMIT_FAILED': '🚫'
        }
        print(f"  {status_emoji[result['result']]} {result['name']}")
        print(f"     Task: {result['task']}, Size: {result['size']}")
        if 'job_id' in result:
            print(f"     Job: {result['job_id']}")
    
    return results

if __name__ == "__main__":
    run_test_suite()
