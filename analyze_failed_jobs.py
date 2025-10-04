#!/usr/bin/env python3
"""
Get detailed error information for failed jobs
"""

import runpod
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".runpod.env")
api_key = os.getenv("RUNPOD_API_KEY")
print(f"API Key from env: {api_key}")
runpod.api_key = api_key
print(f"runpod.api_key: {runpod.api_key}")

endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
endpoint = runpod.Endpoint(endpoint_id)

health = endpoint.health()
jobs = health['jobs']

print(f"Analyzing jobs for endpoint: https://www.runpod.io/console/serverless/endpoints/{endpoint_id}")
print("\n" + "="*60)
print("JOB STATUS")
print("="*60)
print(f"Completed: {jobs['completed']}")
print(f"Failed: {jobs['failed']}")
print(f"In Progress: {jobs['inProgress']}")
print(f"In Queue: {jobs['inQueue']}")
print(f"Retried: {jobs['retried']}")

if jobs['failed'] > 0:
    print("\n" + "="*60)
    print("ANALYZING FAILED JOBS")
    print("="*60)
    print("To get more information about the failed jobs, please go to the RunPod dashboard.")
    print(f"https://www.runpod.io/console/serverless/endpoints/{endpoint_id}/jobs")
