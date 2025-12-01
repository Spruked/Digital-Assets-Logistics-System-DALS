#!/bin/bash
# CANS Startup Script
# Starts the Cognitive Autonomous Neural Synchronizer

echo "🚀 Starting CANS - Cognitive Autonomous Neural Synchronizer"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Start CANS service
echo "🧠 Starting CANS service on port 8020..."
python main.py