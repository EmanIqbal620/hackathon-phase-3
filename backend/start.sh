#!/bin/bash
# Startup script for the Todo App Backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please copy .env.example to .env and configure your database settings:"
    echo "cp .env.example .env"
    echo "Then edit .env with your Neon database connection string"
    exit 1
fi

# Setup database tables
echo "Setting up database tables..."
python setup_database.py

# Start the application
echo "Starting the application..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload