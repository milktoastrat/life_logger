# Use a minimal Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy app code
COPY requirements.txt ./
COPY scripts/ ./scripts/
COPY config/ ./config/
COPY data/ ./data/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command (can be overridden in `docker run`)
CMD ["python", "./scripts/trakt_logger.py"]
