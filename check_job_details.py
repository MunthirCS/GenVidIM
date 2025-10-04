#!/usr/bin/env python3
"""
Check detailed job error from RunPod
"""

import runpod
import os
import sys
from dotenv import load_dotenv

load_dotenv(dotenv_path=".runpod.env")
runpod.api_key = os.getenv("RUNPOD_API_KEY")

endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
endpoint = runpod.Endpoint(endpoint_id)

if len(sys.argv) < 2:
    print("Please provide a job ID as a command-line argument.")
    exit()

job_id = sys.argv[1]
job = endpoint.job(job_id)

print("\n" + "="*60)
print("JOB DETAILS")
print("="*60)
print(job)

print("\n" + "="*60)
print("JOB OUTPUT")
print("="*60)
print(job.output())


