#!/bin/bash

echo "Starting CloudAnoAgent API Server..."
echo "===================================="

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload