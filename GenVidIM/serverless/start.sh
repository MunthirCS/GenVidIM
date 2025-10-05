#!/bin/bash
# start.sh

# Activate the virtual environment from the network volume
source /workspace/venv/bin/activate

# Execute the RunPod handler
python -u /workspace/GenVidIM/serverless/handler.py
