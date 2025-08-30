#!/bin/bash
echo "Starting Smart Order Routing Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Set environment variables
export PYTHONPATH="$PWD/src"

# Start the API server
echo "Starting FastAPI server..."
python src/api/main.py
