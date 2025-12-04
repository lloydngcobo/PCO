#!/bin/bash
# Startup script for PCO API Wrapper

echo "Starting PCO API Wrapper..."
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create a .env file with your PCO credentials."
    echo "You can copy .env.example as a template."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start the application
echo "Starting Flask application..."
python src/app.py