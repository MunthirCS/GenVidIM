#!/usr/bin/env python3
"""
Check error details for the latest failed jobs
"""

import urllib.request
import json
from dotenv import dotenv_values

env = dotenv_values(".runpod.env")
API_KEY = env['RUNPOD_API_KEY']
ENDPOINT_ID = env['RUNPOD_ENDPOINT_ID']

# Get the latest job
url = f"https://api.runpod.io/v2/{ENDPOINT_ID}/jobs"
print(f"URL: {url}")
headers = {
    'Authorization': f"Bearer {API_KEY}"
}
req = urllib.request.Request(url, headers=headers, method='GET')
with urllib.request.urlopen(req, timeout=10) as response:
    jobs = json.loads(response.read().decode('utf-8')).get('jobs', [])
    if not jobs:
        print("No jobs found.")
        exit()

latest_job = jobs[0]
print(f"Latest job: {latest_job['id']} ({latest_job['status']})")

if latest_job['status'] == 'FAILED':
    # Get the logs for the failed job
    url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{latest_job['id']}"
    print(f"URL: {url}")
    req = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(req, timeout=10) as response:
        job_details = json.loads(response.read().decode('utf-8'))
        print("\n" + "="*60)
        print("JOB DETAILS")
        print("="*60)
        print(json.dumps(job_details, indent=2))
        
        print("\n" + "="*60)
        print("JOB OUTPUT")
        print("="*60)
        print(job_details.get('output', 'No output found.'))
