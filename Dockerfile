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

# Ensure run script is executable
RUN chmod +x run.sh

# Run the startup script
CMD ["./run.sh"]
