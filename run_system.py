import subprocess
import time
import os
import signal
import sys

def run_system():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, 'backend')
    frontend_dir = os.path.join(base_dir, 'frontend')

    print("🚀 Starting Vehicle Violation Detection System...")

    # 1. Start Backend
    print("🔹 Launching Backend (FastAPI)...")
    # We assume 'venv' exists in backend/venv
    venv_python = os.path.join(backend_dir, 'venv', 'bin', 'python')
    if not os.path.exists(venv_python):
        print(f"⚠️  Virtual environment not found at {venv_python}. Trying global python...")
        venv_python = "python3" # Fallback

    backend_cmd = [venv_python, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    
    # Start backend process
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=backend_dir,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    # 2. Start Frontend
    print("🔹 Launching Frontend (React/Vite)...")
    # We use 'npm run dev'
    frontend_cmd = ["npm", "run", "dev"]
    
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_dir,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    print("\n✨ System is running!")
    print("👉 Backend: http://localhost:8000")
    print("👉 Frontend: http://localhost:5173 (usually)")
    print("Press CTRL+C to stop everything.\n")

    try:
        # Keep the script running to monitor processes
        while True:
            time.sleep(1)
            # Check if processes are still alive
            if backend_process.poll() is not None:
                print("❌ Backend process died unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend process died unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping system...")
    finally:
        # Graceful shutdown
        print("Terminating Backend...")
        backend_process.terminate()
        print("Terminating Frontend...")
        frontend_process.terminate()
        
        backend_process.wait()
        frontend_process.wait()
        print("✅ System stopped.")

if __name__ == "__main__":
    run_system()
