# ──────────────────────────────────────────────────────────────────────────
# Startup Idea Validator — CLI Validator Mode
# ──────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm

# Prevent .pyc files and enable unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .

# Ensure root is in PYTHONPATH
ENV PYTHONPATH="/app"

# Clean up web-related artifacts to prevent accidental Flask launches
RUN rm -rf server backend/app.py frontend

# Run the inference script directly for the validator to read stdout
CMD ["python", "inference.py"]
