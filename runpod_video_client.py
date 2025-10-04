#!/usr/bin/env python3
"""
RunPod Video Generation Client
A simple client to manage video generation on RunPod cloud instances
"""

import requests
import json
import time
import os
from typing import Dict, List, Optional

class RunPodVideoClient:
    def __init__(self, api_key: str = None):
        """
        Initialize RunPod client
        
        Args:
            api_key: Your RunPod API key (get from runpod.io/console)
        """
        self.api_key = api_key or os.getenv('RUNPOD_API_KEY')
        self.base_url = "https://api.runpod.io/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def list_gpu_types(self) -> Dict:
        """List available GPU types and their pricing"""
        query = """
        query {
            gpuTypes {
                id
                displayName
                memoryInGb
                secureCloud
                communityCloud
                lowestPrice {
                    minimumBidPrice
                    uninterruptablePrice
                }
            }
        }
        """
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": query}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {}
    
    def list_templates(self) -> Dict:
        """List available RunPod templates"""
        query = """
        query {
            templates {
                id
                name
                description
                dockerImage
                category
            }
        }
        """
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": query}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {}
    
    def create_pod(self, 
                   name: str,
                   gpu_type_id: str,
                   template_id: str = None,
                   docker_image: str = None,
                   volume_size: int = 50) -> Dict:
        """
        Create a new pod instance
        
        Args:
            name: Name for your pod
            gpu_type_id: GPU type ID (get from list_gpu_types)
            template_id: Template ID (optional)
            docker_image: Custom docker image (optional)
            volume_size: Storage size in GB
        """
        
        mutation = f"""
        mutation {{
            podFindAndDeployOnDemand(
                input: {{
                    name: "{name}"
                    imageName: "{docker_image or 'runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04'}"
                    gpuTypeId: "{gpu_type_id}"
                    cloudType: COMMUNITY
                    volumeInGb: {volume_size}
                    containerDiskInGb: 20
                    minVcpuCount: 2
                    minMemoryInGb: 15
                    {"templateId: " + json.dumps(template_id) if template_id else ""}
                    ports: "8888/http,22/tcp"
                    volumeMountPath: "/workspace"
                    env: [
                        {{key: "JUPYTER_PASSWORD", value: "runpod"}}
                        {{key: "ENABLE_TENSORBOARD", value: "1"}}
                    ]
                }}
            ) {{
                id
                desiredStatus
                imageName
                env
                machineId
                machine {{
                    podHostId
                }}
            }}
        }}
        """
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": mutation}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {}
    
    def list_pods(self) -> Dict:
        """List your running pods"""
        query = """
        query {
            myself {
                pods {
                    id
                    name
                    desiredStatus
                    imageName
                    machineId
                    costPerHr
                    uptimeSeconds
                    machine {
                        podHostId
                    }
                    runtime {
                        uptimeInSeconds
                        ports {
                            ip
                            isIpPublic
                            privatePort
                            publicPort
                            type
                        }
                    }
                }
            }
        }
        """
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": query}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {}
    
    def stop_pod(self, pod_id: str) -> Dict:
        """Stop a running pod"""
        mutation = f"""
        mutation {{
            podStop(input: {{podId: "{pod_id}"}}) {{
                id
                desiredStatus
            }}
        }}
        """
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": mutation}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {}
    
    def get_pod_logs(self, pod_id: str) -> str:
        """Get logs from a pod"""
        # Note: This is a simplified version - actual implementation may vary
        query = f"""
        query {{
            pod(input: {{podId: "{pod_id}"}}) {{
                id
                logs
            }}
        }}
        """
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": query}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('pod', {}).get('logs', '')
        else:
            return f"Error getting logs: {response.text}"

def main():
    """Example usage"""
    print("🚀 RunPod Video Generation Client")
    print("=" * 50)
    
    # Initialize client (you'll need to set your API key)
    client = RunPodVideoClient()
    
    if not client.api_key:
        print("❌ Please set your RunPod API key:")
        print("   export RUNPOD_API_KEY='your_api_key_here'")
        print("   Or pass it when creating the client")
        return
    
    print("📋 Available GPU Types:")
    gpu_types = client.list_gpu_types()
    
    if 'data' in gpu_types and 'gpuTypes' in gpu_types['data']:
        for gpu in gpu_types['data']['gpuTypes'][:5]:  # Show first 5
            name = gpu.get('displayName', 'Unknown')
            memory = gpu.get('memoryInGb', 'Unknown')
            price = gpu.get('lowestPrice', {}).get('uninterruptablePrice', 'Unknown')
            print(f"   • {name} ({memory}GB) - ${price}/hour")
    
    print("\n🔧 Available Templates:")
    templates = client.list_templates()
    
    if 'data' in templates and 'templates' in templates['data']:
        ml_templates = [t for t in templates['data']['templates'] 
                       if 'pytorch' in t.get('name', '').lower() or 
                          'ml' in t.get('name', '').lower()][:3]
        
        for template in ml_templates:
            name = template.get('name', 'Unknown')
            desc = template.get('description', 'No description')[:50]
            print(f"   • {name}: {desc}...")
    
    print("\n💡 Next steps:")
    print("   1. Get your API key from runpod.io/console")
    print("   2. Choose a GPU type and template")
    print("   3. Use client.create_pod() to launch your instance")
    print("   4. Access via Jupyter Lab or SSH")

if __name__ == "__main__":
    main()
