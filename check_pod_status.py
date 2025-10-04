import runpod
import os
import sys
from dotenv import load_dotenv

load_dotenv(dotenv_path=".runpod.env")
runpod.api_key = os.getenv("RUNPOD_API_KEY")

if len(sys.argv) < 2:
    print("Please provide a pod ID as a command-line argument.")
    exit()

pod_id_to_find = sys.argv[1]

print(f"Searching for pod with ID: {pod_id_to_find}...")

try:
    pods = runpod.get_pods()
    pod_found = False
    for pod in pods:
        if pod['id'] == pod_id_to_find:
            pod_found = True
            print("\n" + "="*60)
            print("POD DETAILS FOUND")
            print("="*60)
            for key, value in pod.items():
                print(f"{key}: {value}")
            print("="*60)
            break
    
    if not pod_found:
        print(f"\nCould not find a pod with ID: {pod_id_to_find}")

except Exception as e:
    print(f"An error occurred: {e}")
