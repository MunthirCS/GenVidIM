import json
import urllib.request
import os
import time

def submit_job(api_key, endpoint_id, payload):
    """Submits a job to the RunPod API."""
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
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
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ Error submitting job: {e}")
        return None

def main():
    """Main function to run the quick test."""
    api_key = os.environ.get('RUNPOD_API_KEY')
    endpoint_id = os.environ.get('RUNPOD_ENDPOINT_ID')
    
    if not api_key or not endpoint_id:
        print("❌ Missing RUNPOD_API_KEY or RUNPOD_ENDPOINT_ID environment variables.")
        return

    print(f"🚀 Submitting QUICK TEST to endpoint: {endpoint_id}")
    
    payload = {
        "input": {
            "prompt": "a simple red circle",
            "task": "ti2v-5B",
            "steps": 5,
            "size": "480*832"
        }
    }
    
    result = submit_job(api_key, endpoint_id, payload)
    
    if result:
        print("\n✅ QUICK TEST SUBMITTED:")
        print("-" * 40)
        print(f"  Job ID: {result.get('id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Parameters: {json.dumps(payload['input'], indent=2)}")

if __name__ == "__main__":
    main()
