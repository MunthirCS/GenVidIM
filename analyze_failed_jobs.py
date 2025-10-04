#!/usr/bin/env python3
"""
Get detailed error information for failed jobs
"""

import json
import urllib.request
import os

def get_job_error_details(job_id):
    """Get detailed error information for a job"""
    
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
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"\n🔍 JOB ERROR DETAILS: {job_id}")
            print("=" * 60)
            print(f"Status: {result.get('status')}")
            print(f"Error: {result.get('error')}")
            
            # Check for execution logs
            execution_logs = result.get('executionLogs', [])
            if execution_logs:
                print(f"\n📝 EXECUTION LOGS:")
                print("-" * 40)
                for log in execution_logs:
                    print(f"  {log}")
            
            # Check for stderr/stdout in output
            output = result.get('output', {})
            if output:
                print(f"\n📤 OUTPUT:")
                print("-" * 40)
                if 'stderr' in output and output['stderr']:
                    print(f"STDERR:\n{output['stderr']}")
                if 'stdout' in output and output['stdout']:
                    print(f"STDOUT:\n{output['stdout']}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check the failed jobs from our test
    failed_jobs = [
        "d489db93-8c36-42e0-9d0c-724a20b12ffc-e1",  # animate small
        "6e804f60-a14a-42ba-9102-aa4e503ed73c-e2",  # animate medium  
        "138592b8-f5e4-4686-a792-de698066850c-e1",  # s2v
        "6557a75f-e145-4f0d-9dc4-695e172aaa73-e2"   # t2v
    ]
    
    for job_id in failed_jobs:
        get_job_error_details(job_id)
        print("\n" + "="*80 + "\n")
