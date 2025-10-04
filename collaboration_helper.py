#!/usr/bin/env python3
"""
Collaboration Helper for RunPod + Claude
This script helps bridge the gap between RunPod and our chat collaboration
"""

import json
import datetime
import traceback
import sys
import os
from pathlib import Path

class CollaborationLogger:
    def __init__(self, session_name="video_generation"):
        self.session_name = session_name
        self.log_dir = Path(f"/workspace/collaboration_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{session_name}_{timestamp}.json"
        
        self.session_data = {
            "session_name": session_name,
            "started_at": datetime.datetime.now().isoformat(),
            "steps": [],
            "errors": [],
            "outputs": [],
            "system_info": self.get_system_info()
        }
    
    def get_system_info(self):
        """Collect system information"""
        try:
            import torch
            import subprocess
            
            # Get GPU info
            gpu_info = "No GPU"
            if torch.cuda.is_available():
                gpu_info = {
                    "name": torch.cuda.get_device_name(0),
                    "memory_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
                    "cuda_version": torch.version.cuda
                }
            
            # Get disk space
            disk_info = subprocess.run(
                ["df", "-h", "/workspace"], 
                capture_output=True, text=True
            ).stdout
            
            return {
                "gpu": gpu_info,
                "pytorch_version": torch.__version__,
                "python_version": sys.version,
                "disk_space": disk_info,
                "working_directory": os.getcwd()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def log_step(self, step_name, description, code=None, result=None, error=None):
        """Log a step in the process"""
        step = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step_name": step_name,
            "description": description,
            "code": code,
            "result": str(result) if result else None,
            "error": str(error) if error else None,
            "success": error is None
        }
        
        self.session_data["steps"].append(step)
        self.save_log()
        
        # Also print for immediate feedback
        print(f"📝 STEP: {step_name}")
        print(f"   Description: {description}")
        if error:
            print(f"   ❌ Error: {error}")
        elif result:
            print(f"   ✅ Result: {result}")
        print()
    
    def log_output(self, output_type, content, metadata=None):
        """Log generated outputs (videos, images, etc.)"""
        output = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": output_type,
            "content": content,
            "metadata": metadata or {}
        }
        
        self.session_data["outputs"].append(output)
        self.save_log()
        
        print(f"📁 OUTPUT: {output_type}")
        print(f"   Content: {content}")
        if metadata:
            print(f"   Metadata: {metadata}")
        print()
    
    def save_log(self):
        """Save the current session log"""
        with open(self.log_file, 'w') as f:
            json.dump(self.session_data, f, indent=2)
    
    def get_summary(self):
        """Get a summary for sharing with Claude"""
        summary = {
            "session": self.session_name,
            "duration": f"Started at {self.session_data['started_at']}",
            "system": self.session_data["system_info"],
            "total_steps": len(self.session_data["steps"]),
            "successful_steps": len([s for s in self.session_data["steps"] if s["success"]]),
            "errors": len([s for s in self.session_data["steps"] if not s["success"]]),
            "outputs_generated": len(self.session_data["outputs"]),
            "recent_steps": self.session_data["steps"][-5:],  # Last 5 steps
            "all_errors": [s for s in self.session_data["steps"] if not s["success"]]
        }
        
        return json.dumps(summary, indent=2)

# Global logger instance
logger = CollaborationLogger()

def run_with_logging(step_name, description, func, *args, **kwargs):
    """Run a function with automatic logging"""
    try:
        print(f"🚀 Starting: {step_name}")
        result = func(*args, **kwargs)
        logger.log_step(step_name, description, result=result)
        return result
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        logger.log_step(step_name, description, error=error_msg)
        print(f"❌ Failed: {step_name}")
        print(f"Error: {str(e)}")
        raise

def test_video_generation():
    """Test function to demonstrate logging"""
    
    def setup_environment():
        """Set up the video generation environment"""
        import torch
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA not available")
        return f"CUDA available: {torch.cuda.get_device_name(0)}"
    
    def load_model():
        """Load a video generation model"""
        # Simulate model loading
        import time
        time.sleep(2)
        return "Model loaded successfully"
    
    def generate_video():
        """Generate a test video"""
        # Simulate video generation
        output_path = "/workspace/test_video.mp4"
        logger.log_output("video", output_path, {"prompt": "test", "duration": "5s"})
        return output_path
    
    # Run steps with logging
    run_with_logging("setup", "Setting up CUDA environment", setup_environment)
    run_with_logging("load_model", "Loading video generation model", load_model)
    run_with_logging("generate", "Generating test video", generate_video)
    
    print("\n🎉 Test completed!")
    print("📋 Summary for Claude:")
    print("=" * 50)
    print(logger.get_summary())

def print_collaboration_guide():
    """Print guide for collaborating with Claude"""
    
    guide = """
🤝 COLLABORATION GUIDE: RunPod + Claude

1. 📝 LOGGING EVERYTHING
   Every step is automatically logged with timestamps, results, and errors.

2. 🔄 SHARING WITH CLAUDE
   Copy the summary output and paste it in chat:
   
   ```
   print(logger.get_summary())
   ```

3. 💡 GETTING HELP FROM CLAUDE
   Share:
   - Error messages (full traceback)
   - System info
   - What you're trying to achieve
   - Recent step results

4. 🛠️ ITERATIVE DEVELOPMENT
   - Claude provides code
   - You run it with logging
   - Share results
   - Claude improves the code

5. 📁 OUTPUT TRACKING
   All generated videos/images are logged with metadata.

6. 🚨 ERROR HANDLING
   Errors are captured with full context for debugging.

EXAMPLE WORKFLOW:
================

# 1. You run this on RunPod:
test_video_generation()

# 2. Copy the summary and share with Claude:
print(logger.get_summary())

# 3. Claude analyzes and provides next steps
# 4. You implement and run again
# 5. Repeat until success!

CURRENT SESSION LOG: {log_file}
""".format(log_file=logger.log_file)
    
    print(guide)

if __name__ == "__main__":
    print("🤝 RunPod + Claude Collaboration Helper")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            test_video_generation()
        elif command == "guide":
            print_collaboration_guide()
        elif command == "summary":
            print(logger.get_summary())
    else:
        print_collaboration_guide()
        print("\nCommands:")
        print("  python collaboration_helper.py test     # Run test workflow")
        print("  python collaboration_helper.py guide    # Show collaboration guide")
        print("  python collaboration_helper.py summary  # Show current session summary")
