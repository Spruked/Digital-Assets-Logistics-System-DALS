#!/usr/bin/env python3
"""
DALS Multi-Monitor Workers Control Center Launcher
Starts both backend API and frontend for full multi-monitor experience.
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def check_node_installed():
    """Check if Node.js is installed"""
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_npm_installed():
    """Check if npm is installed"""
    try:
        subprocess.run(['npm', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def start_backend():
    """Start the DALS backend API server"""
    print("🚀 Starting DALS Backend API (port 8003)...")
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    # Start backend in background
    backend_process = subprocess.Popen([
        sys.executable, '-m', 'iss_module.api.api'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for backend to start
    time.sleep(3)

    # Check if backend is running
    try:
        import requests
        response = requests.get('http://localhost:8003/health', timeout=5)
        if response.status_code == 200:
            print("✅ DALS Backend API started successfully")
            return backend_process
        else:
            print("❌ DALS Backend API failed to start properly")
            backend_process.terminate()
            return None
    except:
        print("❌ Could not connect to DALS Backend API")
        backend_process.terminate()
        return None

def start_frontend():
    """Start the Next.js frontend"""
    print("🖥️ Starting DALS Frontend (port 3000)...")
    frontend_dir = Path(__file__).parent / 'dals_frontend'

    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None

    os.chdir(frontend_dir)

    # Install dependencies if needed
    if not (frontend_dir / 'node_modules').exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(['npm', 'install'], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            return None

    # Start frontend in background
    frontend_process = subprocess.Popen([
        'npm', 'run', 'dev'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for frontend to start
    time.sleep(5)

    print("✅ DALS Frontend started successfully")
    return frontend_process

def open_browser_windows():
    """Open browser windows for multi-monitor setup"""
    print("🌐 Opening multi-monitor browser windows...")

    try:
        # Main dashboard
        subprocess.run([
            'start', 'chrome',
            '--new-window',
            '--window-size=1400,900',
            '--window-position=0,0',
            'http://localhost:3000/workers'
        ], shell=True, check=False)

        time.sleep(2)

        # Registry monitor
        subprocess.run([
            'start', 'chrome',
            '--new-window',
            '--window-size=1200,800',
            '--window-position=1450,0',
            'http://localhost:3000/workers/registry'
        ], shell=True, check=False)

        time.sleep(2)

        # Forge monitor
        subprocess.run([
            'start', 'chrome',
            '--new-window',
            '--window-size=1000,700',
            '--window-position=1450,850',
            'http://localhost:3000/workers/forge'
        ], shell=True, check=False)

        print("✅ Browser windows opened for multi-monitor setup")
        print("💡 Arrange windows across your monitors for optimal control center experience")

    except Exception as e:
        print(f"⚠️ Could not auto-open browser windows: {e}")
        print("🌐 Manually open: http://localhost:3000/workers")

def main():
    print("🎯 DALS Multi-Monitor Workers Control Center")
    print("=" * 50)

    # Check prerequisites
    if not check_node_installed():
        print("❌ Node.js is not installed. Please install Node.js to run the frontend.")
        sys.exit(1)

    if not check_npm_installed():
        print("❌ npm is not installed. Please install npm to run the frontend.")
        sys.exit(1)

    processes = []

    try:
        # Start backend
        backend = start_backend()
        if backend:
            processes.append(('Backend', backend))

        # Start frontend
        frontend = start_frontend()
        if frontend:
            processes.append(('Frontend', frontend))

        if not processes:
            print("❌ Failed to start any services")
            sys.exit(1)

        # Open browser windows
        time.sleep(2)
        open_browser_windows()

        print("\n" + "=" * 50)
        print("🎉 DALS Multi-Monitor Control Center is running!")
        print("📊 Backend API: http://localhost:8003")
        print("🖥️ Frontend: http://localhost:3000/workers")
        print("🖥️ Registry: http://localhost:3000/workers/registry")
        print("⚒️ Forge: http://localhost:3000/workers/forge")
        print("📄 Templates: http://localhost:3000/workers/templates")
        print("=" * 50)
        print("💡 Use 'Pop Out' buttons for additional monitor windows")
        print("🛑 Press Ctrl+C to stop all services")
        print("=" * 50)

        # Keep running until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down DALS Control Center...")

    finally:
        # Clean shutdown
        for name, process in processes:
            print(f"Stopping {name}...")
            try:
                if os.name == 'nt':  # Windows
                    process.terminate()
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
            print(f"✅ {name} stopped")

        print("👋 DALS Control Center shutdown complete")

if __name__ == '__main__':
    main()