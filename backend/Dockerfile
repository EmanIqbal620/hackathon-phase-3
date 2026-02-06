FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port 7860 (standard for Hugging Face Spaces)
EXPOSE 7860

# Set the startup command
CMD ["sh", "-c", "python setup_database.py && uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]