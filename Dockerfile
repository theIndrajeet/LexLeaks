# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including PostgreSQL libraries
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend-api/app /app/app
COPY backend-api/alembic /app/alembic
COPY backend-api/alembic.ini /app/alembic.ini

# Cloud Run will set the PORT environment variable
EXPOSE 8080

# Run the application on the port provided by Cloud Run
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
