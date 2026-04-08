# ──────────────────────────────────────────────────────────────────────────
# Startup Idea Validator — Docker image
# ──────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm

# Prevent .pyc files and enable unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .

# Ensure root is in PYTHONPATH
ENV PYTHONPATH="/app"

# Default command to run the web UI for Hugging Face Spaces
EXPOSE 7860
CMD ["python", "app.py"]
