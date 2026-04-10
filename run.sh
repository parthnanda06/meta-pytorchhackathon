#!/bin/bash
# Startup script for Dual-Mode execution (CLI + OpenEnv HTTP Proxy).
# This satisfies both core orchestrator logs and HTTP-based validation.

# 1. Run the CLI inference script to populate stdout logs immediately
python inference.py

# 2. Launch the Flask server to handle /reset, /step, and /state requests
# Use gunicorn or similar for production if needed, but python -m backend.app is fine for now
python -m backend.app
