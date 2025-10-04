#!/usr/bin/env python3
"""
Quick serverless endpoint status check
"""

import json
import urllib.request
import os

def check_serverless_status():
    """Check serverless endpoint status"""
    
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
    
    print(f"🔍 Checking serverless endpoint: {endpoint_id}")
    
    url = "https://api.runpod.io/graphql"
    
    query = """
    query ServerlessEndpoints {
      myself {
        serverlessEndpoints {
          id
          name
          templateId
          gpuIds
          idleTimeout
          maxWorkers
          workers {
            id
            status
            gpuUtilization
            memoryUtilization
            lastSeen
          }
        }
      }
    }
    """
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': api_key
    }
    
    payload = json.dumps({"query": query})
    
    try:
        req = urllib.request.Request(
            url,
            data=payload.encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if 'errors' in result:
                print(f"❌ GraphQL errors: {result['errors']}")
                return
            
            endpoints = result.get('data', {}).get('myself', {}).get('serverlessEndpoints', [])
            
            print(f"\n📡 SERVERLESS ENDPOINTS:")
            print("-" * 60)
            
            if not endpoints:
                print("  No serverless endpoints found")
                return
            
            for endpoint in endpoints:
                if endpoint and endpoint.get('id') == endpoint_id:
                    print(f"\n  🎯 {endpoint.get('name', 'Unnamed')}")
                    print(f"      ID: {endpoint.get('id')}")
                    print(f"      Template: {endpoint.get('templateId')}")
                    print(f"      Max Workers: {endpoint.get('maxWorkers')}")
                    print(f"      Idle Timeout: {endpoint.get('idleTimeout')}s")
                    
                    workers = endpoint.get('workers', [])
                    print(f"\n  👥 WORKERS ({len(workers)}):")
                    
                    if workers:
                        for worker in workers:
                            if worker:
                                print(f"      Worker {worker.get('id', 'Unknown')[:8]}...")
                                print(f"        Status: {worker.get('status', 'Unknown')}")
                                print(f"        GPU: {worker.get('gpuUtilization', 0)}%")
                                print(f"        Memory: {worker.get('memoryUtilization', 0)}%")
                                print(f"        Last Seen: {worker.get('lastSeen', 'Unknown')}")
                    else:
                        print("      No active workers")
                    
                    break
            else:
                print(f"  ❌ Endpoint {endpoint_id} not found")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_serverless_status()
