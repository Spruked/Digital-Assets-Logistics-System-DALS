@echo off
REM CANS Startup Script for Windows
REM Starts the Cognitive Autonomous Neural Synchronizer

echo 🚀 Starting CANS - Cognitive Autonomous Neural Synchronizer

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Start CANS service
echo 🧠 Starting CANS service on port 8020...
python main.py

pause