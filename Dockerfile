# ──────────────────────────────────────────────────────────────────────────
# Startup Idea Validator — Docker image
# ──────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Prevent .pyc files and enable unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .

# Default command — run the hard task in offline mode
# Override with:  docker run -e OPENAI_API_KEY=sk-... startup-validator --difficulty hard
ENTRYPOINT ["python", "backend/run.py"]
CMD ["--difficulty", "hard", "--no-llm"]
