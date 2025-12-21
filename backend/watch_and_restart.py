"""
File watcher that automatically restarts the backend server when files change.
This script watches for changes in Python files and restarts the server.
"""
import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Ensure we're in the backend directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)
print(f"[Watcher] Working directory: {os.getcwd()}")

class BackendRestartHandler(FileSystemEventHandler):
    """Handler that restarts the backend when Python files change."""
    
    def __init__(self, restart_callback):
        super().__init__()
        self.restart_callback = restart_callback
        self.last_restart = 0
        self.debounce_seconds = 2  # Wait 2 seconds after last change before restarting
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Only watch Python files
        if event.src_path.endswith('.py'):
            # Debounce: don't restart too frequently
            current_time = time.time()
            if current_time - self.last_restart < self.debounce_seconds:
                return
                
            print(f"\n[Watcher] Detected change in: {os.path.basename(event.src_path)}")
            print("[Watcher] Restarting backend server...")
            self.last_restart = current_time
            self.restart_callback()

def start_backend():
    """Start the backend server process."""
    return subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=sys.stdout,
        stderr=sys.stderr
    )

def main():
    """Main function to watch files and restart backend."""
    backend_dir = Path(__file__).parent
    backend_process = None
    
    def restart_backend():
        nonlocal backend_process
        if backend_process:
            try:
                # Try graceful shutdown
                backend_process.terminate()
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't stop
                backend_process.kill()
                backend_process.wait()
            except Exception as e:
                print(f"[Watcher] Error stopping backend: {e}")
        
        # Start new backend process
        backend_process = start_backend()
        print("[Watcher] Backend restarted successfully!")
    
    # Start backend initially
    print("=" * 50)
    print("  BACKEND SERVER (FastAPI)")
    print("  Auto-restart: ENABLED via file watcher")
    print("=" * 50)
    print("Starting backend server...")
    print("")
    
    backend_process = start_backend()
    
    # Set up file watcher
    event_handler = BackendRestartHandler(restart_backend)
    observer = Observer()
    observer.schedule(event_handler, str(backend_dir), recursive=True)
    observer.start()
    
    try:
        print("[Watcher] File watcher started. Monitoring for changes...")
        print("[Watcher] Press Ctrl+C to stop")
        print("")
        
        # Keep the script running
        while True:
            time.sleep(1)
            # Check if backend process is still alive
            if backend_process.poll() is not None:
                print("[Watcher] Backend process died, restarting...")
                restart_backend()
                
    except KeyboardInterrupt:
        print("\n[Watcher] Stopping file watcher...")
        observer.stop()
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
    
    observer.join()
    print("[Watcher] File watcher stopped.")

if __name__ == "__main__":
    main()

