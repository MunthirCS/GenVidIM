#!/bin/bash
# Start GenVidIM HTTP API on RTX 5090 pod

cd /workspace/GenVidIM

# Install Flask if not present
pip install -q flask

# Start API server
python simple_api.py

