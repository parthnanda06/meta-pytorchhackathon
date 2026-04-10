#!/bin/bash
# Startup script for CLI-only execution as required by the Hackathon validator.
# Runs the inference script and then sleeps to keep the container alive for logs.

python inference.py

echo "Inference complete. Keeping container alive for validator logs..."
# Sleep forever to prevent 'Runtime Error' status on Hugging Face
tail -f /dev/null
