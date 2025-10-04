#!/usr/bin/env python3
"""
Check serverless endpoint build status
"""

import runpod
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".runpod.env")
api_key = os.getenv("RUNPOD_API_KEY")
print(f"API Key: {api_key}")
runpod.api_key = api_key

endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
endpoints = runpod.get_endpoints()

endpoint = None
for ep in endpoints:
    if ep['id'] == endpoint_id:
        endpoint = ep
        break

if not endpoint:
    print(f"Endpoint with ID {endpoint_id} not found.")
    exit()

print("\n" + "="*60)
print("SERVERLESS ENDPOINT STATUS")
print("="*60)

print(f"\nEndpoint: {endpoint['name']}")
print(f"ID: {endpoint['id']}")
print(f"Version: {endpoint['version']}")
print(f"Workers Standby: {endpoint['workersStandby']}")

if endpoint['workersStandby'] > 0:
    print("\nSTATUS: Endpoint is ready.")
else:
    print("\nSTATUS: Endpoint is not ready.")

