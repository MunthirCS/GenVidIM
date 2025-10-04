#!/usr/bin/env python3
"""
RunPod Quick Manager
Easy start/stop workflow for video generation
"""

import json
import time
from runpod_video_client import RunPodVideoClient
from pathlib import Path

class RunPodManager:
    def __init__(self, api_key=None):
        self.client = RunPodVideoClient(api_key)
        self.config_file = Path("runpod_config.json")
        
    def save_config(self, config):
        """Save pod configuration for easy restart"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self):
        """Load saved pod configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def quick_start(self, gpu_type="NVIDIA RTX 4090", volume_size=50):
        """Start a video generation pod quickly"""
        print("🚀 Starting RunPod instance...")
        
        config = {
            "name": f"video-gen-{int(time.time())}",
            "gpu_type": gpu_type,
            "volume_size": volume_size,
            "template": "pytorch"
        }
        
        # Create pod
        result = self.client.create_pod(
            name=config["name"],
            gpu_type_id=gpu_type,
            volume_size=volume_size
        )
        
        if 'data' in result:
            pod_data = result['data']['podFindAndDeployOnDemand']
            config["pod_id"] = pod_data['id']
            config["started_at"] = time.time()
            
            # Save config for later
            self.save_config(config)
            
            print(f"✅ Pod started: {pod_data['id']}")
            print(f"💰 Cost: ~${self.get_hourly_rate(gpu_type)}/hour")
            print("⏱️ Waiting for pod to be ready...")
            
            # Wait for pod to be ready
            self.wait_for_ready(config["pod_id"])
            
            return config
        else:
            print(f"❌ Failed to start pod: {result}")
            return None
    
    def quick_stop(self):
        """Stop the current pod and show session summary"""
        config = self.load_config()
        
        if not config or 'pod_id' not in config:
            print("❌ No active pod found")
            return
        
        pod_id = config['pod_id']
        
        print(f"🛑 Stopping pod: {pod_id}")
        
        # Stop the pod
        result = self.client.stop_pod(pod_id)
        
        if 'data' in result:
            # Calculate session cost
            if 'started_at' in config:
                duration_hours = (time.time() - config['started_at']) / 3600
                estimated_cost = duration_hours * self.get_hourly_rate(config.get('gpu_type', 'NVIDIA RTX 4090'))
                
                print(f"✅ Pod stopped successfully")
                print(f"⏱️ Session duration: {duration_hours:.2f} hours")
                print(f"💰 Estimated cost: ${estimated_cost:.2f}")
                print(f"💾 Your data is preserved on the volume")
            
            # Clear config
            config.clear()
            self.save_config(config)
            
        else:
            print(f"❌ Failed to stop pod: {result}")
    
    def status(self):
        """Show current pod status and costs"""
        config = self.load_config()
        
        if not config or 'pod_id' not in config:
            print("💤 No active pods")
            return
        
        # Get current pods
        pods_result = self.client.list_pods()
        
        if 'data' in pods_result and 'myself' in pods_result['data']:
            pods = pods_result['data']['myself']['pods']
            active_pod = next((p for p in pods if p['id'] == config['pod_id']), None)
            
            if active_pod:
                uptime_hours = active_pod.get('uptimeSeconds', 0) / 3600
                cost_per_hour = float(active_pod.get('costPerHr', 0.5))
                current_cost = uptime_hours * cost_per_hour
                
                print(f"🟢 Active Pod: {active_pod['id']}")
                print(f"⏱️ Uptime: {uptime_hours:.2f} hours")
                print(f"💰 Current cost: ${current_cost:.2f}")
                print(f"📊 Rate: ${cost_per_hour}/hour")
                
                # Show connection info
                if 'runtime' in active_pod and active_pod['runtime']:
                    ports = active_pod['runtime'].get('ports', [])
                    for port in ports:
                        if port['privatePort'] == 8888:
                            print(f"🔗 Jupyter: https://{port['ip']}:{port['publicPort']}")
                        elif port['privatePort'] == 7860:
                            print(f"🌐 Web UI: https://{port['ip']}:{port['publicPort']}")
            else:
                print("❌ Pod not found (may have been stopped)")
                config.clear()
                self.save_config(config)
    
    def wait_for_ready(self, pod_id, timeout=300):
        """Wait for pod to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            pods_result = self.client.list_pods()
            
            if 'data' in pods_result:
                pods = pods_result['data']['myself']['pods']
                pod = next((p for p in pods if p['id'] == pod_id), None)
                
                if pod and pod.get('desiredStatus') == 'RUNNING':
                    if 'runtime' in pod and pod['runtime']:
                        print("✅ Pod is ready!")
                        return True
            
            print("⏳ Still starting...")
            time.sleep(10)
        
        print("⚠️ Timeout waiting for pod to be ready")
        return False
    
    def get_hourly_rate(self, gpu_type):
        """Get approximate hourly rate for GPU type"""
        rates = {
            "NVIDIA RTX 3090": 0.40,
            "NVIDIA RTX 4090": 0.50,
            "NVIDIA A100": 1.50,
            "NVIDIA RTX A6000": 0.80,
        }
        return rates.get(gpu_type, 0.50)

def main():
    """Command line interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("🎬 RunPod Video Generation Manager")
        print("Usage:")
        print("  python runpod_manager.py start    # Start a new pod")
        print("  python runpod_manager.py stop     # Stop current pod")
        print("  python runpod_manager.py status   # Show current status")
        return
    
    manager = RunPodManager()
    command = sys.argv[1].lower()
    
    if command == "start":
        config = manager.quick_start()
        if config:
            print("\n🎉 Ready to generate videos!")
            print("Next steps:")
            print("  1. Connect to Jupyter Lab")
            print("  2. Run your video generation")
            print("  3. Use 'python runpod_manager.py stop' when done")
    
    elif command == "stop":
        manager.quick_stop()
        print("\n💡 Remember:")
        print("  • Your data is preserved")
        print("  • You can restart anytime")
        print("  • No charges while stopped")
    
    elif command == "status":
        manager.status()
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()

