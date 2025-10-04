#!/usr/bin/env python3
"""
Check RunPod available GPU pods and serverless endpoints
"""

import json
import urllib.request
import sys
from datetime import datetime


def get_runpod_gpus(api_key):
    """Get available GPU types and pricing"""
    
    url = "https://api.runpod.io/graphql"
    
    query = """
    query GpuTypes {
      gpuTypes {
        id
        displayName
        memoryInGb
        secureCloud
        communityCloud
        securePrice
        communityPrice
        oneMonthPrice
        threeMonthPrice
        sixMonthPrice
        lowestPrice(input: {gpuCount: 1}) {
          minimumBidPrice
          uninterruptablePrice
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
            return result.get('data', {}).get('gpuTypes', [])
    except Exception as e:
        print(f"❌ Error fetching GPU types: {e}")
        return []


def get_serverless_endpoints(api_key):
    """Get your serverless endpoints"""
    
    url = "https://api.runpod.io/graphql"
    
    query = """
    query Endpoints {
      myself {
        serverlessDiscount {
          discountFactor
          type
          expirationDate
        }
        endpoints {
          aiKey
          id
          name
          userId
          scalerType
          scalerValue
          workersMin
          workersMax
          gpuIds
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
            return result.get('data', {}).get('myself', {})
    except Exception as e:
        print(f"❌ Error fetching endpoints: {e}")
        return {}


def get_pods(api_key):
    """Get your current pods"""
    
    url = "https://api.runpod.io/graphql"
    
    query = """
    query Pods {
      myself {
        pods {
          id
          name
          runtime {
            uptimeInSeconds
          }
          machine {
            gpuDisplayName
          }
          desiredStatus
          imageName
          memoryInGb
          podType
          containerDiskInGb
          volumeInGb
          costPerHr
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
            return result.get('data', {}).get('myself', {}).get('pods', [])
    except Exception as e:
        print(f"❌ Error fetching pods: {e}")
        return []


def main():
    print("\n🔍 RunPod Resource Checker\n" + "="*60)
    
    # Check for API key
    api_key = None
    
    # Try to load from .runpod.env
    try:
        with open('.runpod.env', 'r') as f:
            for line in f:
                if line.strip().startswith('RUNPOD_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    except FileNotFoundError:
        pass
    
    # Check command line
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        print("\n❌ No API key found!")
        print("\nUsage:")
        print("  python check_runpod_pods.py YOUR_API_KEY")
        print("  OR create .runpod.env with: RUNPOD_API_KEY=your_key")
        print("\nGet your API key from: https://runpod.io/console/user/settings")
        sys.exit(1)
    
    print(f"\n✅ API Key: {api_key[:20]}...")
    
    # Get current pods
    print("\n📦 YOUR CURRENT PODS:")
    print("-" * 60)
    pods = get_pods(api_key)
    
    if pods:
        for pod in pods:
            if pod is None:
                continue
            uptime = pod.get('runtime', {}).get('uptimeInSeconds', 0)
            hours = uptime / 3600
            print(f"\n  🖥️  {pod.get('name', 'Unnamed')}")
            print(f"      ID: {pod.get('id')}")
            print(f"      GPU: {pod.get('machine', {}).get('gpuDisplayName', 'Unknown')}")
            print(f"      Status: {pod.get('desiredStatus', 'Unknown')}")
            print(f"      Cost: ${pod.get('costPerHr', 0):.4f}/hr")
            print(f"      Uptime: {hours:.1f} hours")
            print(f"      Type: {pod.get('podType', 'Unknown')}")
    else:
        print("  No pods running")
    
    # Get serverless endpoints
    print("\n\n🚀 YOUR SERVERLESS ENDPOINTS:")
    print("-" * 60)
    endpoint_data = get_serverless_endpoints(api_key)
    endpoints = endpoint_data.get('endpoints', [])
    
    if endpoints:
        for endpoint in endpoints:
            print(f"\n  ⚡ {endpoint.get('name', 'Unnamed')}")
            print(f"      ID: {endpoint.get('id')}")
            print(f"      Min Workers: {endpoint.get('workersMin', 0)}")
            print(f"      Max Workers: {endpoint.get('workersMax', 0)}")
            print(f"      GPU IDs: {endpoint.get('gpuIds', 'Any')}")
    else:
        print("  No serverless endpoints")
    
    # Show discount if available
    discount = endpoint_data.get('serverlessDiscount')
    if discount:
        print(f"\n  💰 Serverless Discount: {discount.get('discountFactor', 1)}x")
    
    # Get available GPU types
    print("\n\n🎮 AVAILABLE GPU TYPES (Recommended for Video Gen):")
    print("-" * 60)
    gpus = get_runpod_gpus(api_key)
    
    # Filter for 24GB+ memory GPUs suitable for AI video generation
    suitable_gpus = [
        gpu for gpu in gpus 
        if gpu.get('memoryInGb', 0) >= 24
    ]
    
    suitable_gpus.sort(key=lambda x: x.get('lowestPrice', {}).get('uninterruptablePrice', 999) or 999)
    
    for gpu in suitable_gpus[:10]:  # Top 10 best options
        name = gpu.get('displayName', 'Unknown')
        memory = gpu.get('memoryInGb', 0)
        secure_price = gpu.get('securePrice')
        community_price = gpu.get('communityPrice')
        lowest = gpu.get('lowestPrice', {})
        
        print(f"\n  🔥 {name} ({memory}GB VRAM)")
        
        if lowest.get('uninterruptablePrice'):
            print(f"      On-Demand: ${lowest['uninterruptablePrice']:.4f}/hr")
        
        if lowest.get('minimumBidPrice'):
            print(f"      Spot (Bid): ${lowest['minimumBidPrice']:.4f}/hr")
        
        if secure_price:
            print(f"      Secure Cloud: ${secure_price:.4f}/hr")
        
        if community_price:
            print(f"      Community: ${community_price:.4f}/hr")
    
    print("\n" + "="*60)
    print("✅ Done!")
    print("\nFor serverless deployment, recommended GPUs:")
    print("  • RTX 4090 (24GB) - Best price/performance")
    print("  • RTX 3090 (24GB) - Good budget option")
    print("  • A100 (40GB/80GB) - For larger models")
    print("\n")


if __name__ == "__main__":
    main()

