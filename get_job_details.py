#!/usr/bin/env python3
"""
Get detailed job information including error logs
"""

import json
import urllib.request
import os

def get_job_details(job_id):
    """Get detailed information about a job"""
    
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
    
    print(f"🔍 Getting details for job: {job_id}")
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"\n📋 JOB DETAILS:")
            print("=" * 60)
            print(f"  ID: {result.get('id')}")
            print(f"  Status: {result.get('status')}")
            
            if result.get('status') == 'FAILED':
                print(f"\n❌ FAILURE DETAILS:")
                print("-" * 40)
                error = result.get('error', 'No error details available')
                print(f"  Error: {error}")
                
                # Check for execution logs
                execution_logs = result.get('executionLogs', [])
                if execution_logs:
                    print(f"\n📝 EXECUTION LOGS:")
                    print("-" * 40)
                    for log in execution_logs:
                        print(f"  {log}")
                
            elif result.get('status') == 'COMPLETED':
                print(f"\n✅ SUCCESS!")
                output = result.get('output', {})
                if output:
                    print(f"  Output: {json.dumps(output, indent=2)}")
            
            # Show all available fields for debugging
            print(f"\n🔍 ALL FIELDS:")
            print("-" * 40)
            for key, value in result.items():
                if key not in ['id', 'status']:
                    print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    job_id = "8c544691-7690-4b28-8aff-ec9803ebc254-e2"
    get_job_details(job_id)
