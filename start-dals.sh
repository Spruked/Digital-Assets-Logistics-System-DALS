#!/bin/bash
# DALS Multi-Service Startup Script
# Runs both API server (port 8003) and Dashboard server (port 8008)

set -e

echo "🚀 Starting DALS Multi-Service..."

# Function to handle shutdown
shutdown() {
    echo "🛑 Shutting down DALS services..."
    kill $API_PID $DASHBOARD_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap shutdown SIGTERM SIGINT

# Start API server in background
echo "📡 Starting API server on port 8003..."
python -m iss_module.service &
API_PID=$!

# Wait a moment for API to initialize
sleep 2

# Start dashboard server in background
echo "📊 Starting Dashboard server on port 8008..."
python dashboard_server.py &
DASHBOARD_PID=$!

echo "✅ DALS services started:"
echo "   API: http://localhost:8003"
echo "   Dashboard: http://localhost:8008"
echo "   PIDs: API=$API_PID, Dashboard=$DASHBOARD_PID"

# Wait for services
wait