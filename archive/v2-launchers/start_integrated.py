#!/usr/bin/env python3
"""
Properly integrated PersonalParakeet v2 launcher
Handles path issues and starts both components cleanly
"""

import subprocess
import threading
import time
import sys
import os
import signal
import atexit

class IntegratedLauncher:
    def __init__(self):
        self.processes = []
        self.running = True
        
        # Register cleanup
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, lambda s, f: self.shutdown())
        
    def cleanup(self):
        """Clean up all processes"""
        for proc in self.processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                try:
                    proc.kill()
                except:
                    pass
    
    def shutdown(self):
        """Graceful shutdown"""
        print("\n\nShutting down PersonalParakeet...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def start_backend(self):
        """Start the Python backend"""
        print("Starting backend...")
        
        backend = subprocess.Popen(
            [sys.executable, "dictation_websocket_bridge.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        self.processes.append(backend)
        
        # Wait for WebSocket to be ready
        for line in backend.stdout:
            print(f"[Backend] {line.strip()}")
            if "server listening on 127.0.0.1:8765" in line:
                print("✅ Backend ready!")
                return True
            if "ERROR" in line:
                print("❌ Backend failed to start")
                return False
        
        return False
    
    def start_frontend(self):
        """Start the Tauri frontend with proper path handling"""
        print("\nStarting frontend...")
        
        ui_dir = os.path.join(os.path.dirname(__file__), "dictation-view-ui")
        
        # Fix for Windows npm path issues - use explicit cmd.exe
        if sys.platform == "win32":
            # Create a temporary batch file to avoid path issues
            batch_content = f"""@echo off
cd /d "{ui_dir}"
npm run tauri dev
"""
            batch_path = os.path.join(ui_dir, "_start_tauri.bat")
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            # Run the batch file
            frontend = subprocess.Popen(
                ["cmd.exe", "/c", batch_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
        else:
            # Unix/Linux/Mac
            frontend = subprocess.Popen(
                ["npm", "run", "tauri", "dev"],
                cwd=ui_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
        
        self.processes.append(frontend)
        
        # Stream output
        def stream_output():
            for line in frontend.stdout:
                print(f"[Frontend] {line.strip()}")
                if "Tauri app started" in line or "vite" in line:
                    print("✅ Frontend building...")
        
        thread = threading.Thread(target=stream_output, daemon=True)
        thread.start()
        
        return True
    
    def run(self):
        """Main run method"""
        print("=== PersonalParakeet v2 Integrated Launcher ===\n")
        
        # Check if npm exists
        npm_check = subprocess.run(
            ["cmd.exe", "/c", "where", "npm"],
            capture_output=True,
            text=True
        )
        
        if npm_check.returncode != 0:
            print("❌ npm not found! Please install Node.js first.")
            print("   Download from: https://nodejs.org/")
            return
        
        # Start backend
        if not self.start_backend():
            print("Failed to start backend")
            return
        
        time.sleep(1)  # Give backend a moment
        
        # Start frontend
        if not self.start_frontend():
            print("Failed to start frontend")
            return
        
        print("\n" + "="*50)
        print("🚀 PersonalParakeet v2 is starting!")
        print("="*50)
        print("\nWhat happens next:")
        print("1. Tauri will compile the frontend (first run: 1-2 minutes)")
        print("2. The Dictation View window will appear")
        print("3. Look for the status indicator (green = connected)")
        print("\nPress Ctrl+C to stop everything")
        print("="*50 + "\n")
        
        # Keep running
        try:
            while self.running:
                # Check if processes are still alive
                for proc in self.processes:
                    if proc.poll() is not None:
                        print(f"\n⚠️  A process exited unexpectedly")
                        self.shutdown()
                
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

if __name__ == "__main__":
    launcher = IntegratedLauncher()
    launcher.run()