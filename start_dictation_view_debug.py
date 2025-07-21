#!/usr/bin/env python3
"""
PersonalParakeet Dictation View Debug Launcher

This launcher shows real-time logs and errors without blocking.
"""

import subprocess
import threading
import time
import sys
import os
import queue
import signal
import shutil

# Colors for output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class DebugLauncher:
    def __init__(self):
        self.processes = []
        self.log_queue = queue.Queue()
        self.running = True
        
    def log(self, message, level="INFO"):
        """Thread-safe logging"""
        timestamp = time.strftime("%H:%M:%S")
        if level == "ERROR":
            color = RED
        elif level == "SUCCESS":
            color = GREEN
        elif level == "WARNING":
            color = YELLOW
        else:
            color = BLUE
        
        self.log_queue.put(f"{color}[{timestamp}] {level}: {message}{RESET}")
    
    def stream_output(self, process, name):
        """Stream output from a process in real-time"""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    line = line.strip()
                    if "error" in line.lower() or "exception" in line.lower():
                        self.log(f"[{name}] {line}", "ERROR")
                    elif "warning" in line.lower():
                        self.log(f"[{name}] {line}", "WARNING")
                    else:
                        self.log(f"[{name}] {line}")
        except Exception as e:
            self.log(f"[{name}] Stream error: {e}", "ERROR")
    
    def start_backend(self):
        """Start the Python WebSocket backend with detailed logging"""
        self.log("Starting Python WebSocket backend...")
        
        try:
            # Run backend with unbuffered output
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            
            backend_proc = subprocess.Popen(
                [sys.executable, "-u", "dictation_websocket_bridge.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env
            )
            self.processes.append(backend_proc)
            
            # Start thread to stream output
            thread = threading.Thread(
                target=self.stream_output,
                args=(backend_proc, "BACKEND"),
                daemon=True
            )
            thread.start()
            
            self.log(f"Backend started (PID: {backend_proc.pid})", "SUCCESS")
            return backend_proc
            
        except Exception as e:
            self.log(f"Failed to start backend: {e}", "ERROR")
            return None
    
    def check_backend_ready(self):
        """Check if backend is ready by testing WebSocket connection"""
        import socket
        
        for i in range(30):  # Wait up to 30 seconds
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', 8765))
                sock.close()
                
                if result == 0:
                    self.log("Backend WebSocket server is ready!", "SUCCESS")
                    return True
            except:
                pass
            
            if i % 5 == 0:
                self.log(f"Waiting for backend to initialize... ({i}s)")
            time.sleep(1)
        
        self.log("Backend failed to start within 30 seconds", "ERROR")
        return False
    
    def start_frontend(self):
        """Start the Tauri frontend with detailed logging"""
        self.log("Starting Dictation View UI...")
        
        try:
            # Change to UI directory
            ui_dir = os.path.join(os.path.dirname(__file__), "dictation-view-ui")
            
            # Check if node_modules exists
            if not os.path.exists(os.path.join(ui_dir, "node_modules")):
                self.log("node_modules not found, running npm install...", "WARNING")
                # Find npm first
                npm_install = shutil.which("npm") or r"C:\Program Files\nodejs\npm.cmd"
                install_proc = subprocess.run(
                    [npm_install, "install"],
                    cwd=ui_dir,
                    capture_output=True,
                    text=True,
                    shell=npm_install.endswith('.cmd')
                )
                if install_proc.returncode != 0:
                    self.log(f"npm install failed: {install_proc.stderr}", "ERROR")
                    return None
                else:
                    self.log("npm install completed successfully", "SUCCESS")
            
            # Run Tauri dev - try multiple npm locations
            npm_cmd = None
            npm_locations = [
                r"C:\Program Files\nodejs\npm.cmd",  # Common Windows location
                r"C:\Program Files (x86)\nodejs\npm.cmd",  # Alternative location
                shutil.which("npm"),  # Search in PATH
                "npm.cmd",  # Try with extension
                "npm"  # System PATH
            ]
            
            for npm_path in npm_locations:
                if npm_path:
                    if npm_path in ["npm", "npm.cmd"]:
                        # Try to run it
                        try:
                            subprocess.run([npm_path, "--version"], capture_output=True, check=True)
                            npm_cmd = npm_path
                            self.log(f"Found npm using command: {npm_path}", "SUCCESS")
                            break
                        except:
                            continue
                    elif os.path.exists(npm_path):
                        npm_cmd = npm_path
                        self.log(f"Found npm at: {npm_path}", "SUCCESS")
                        break
            
            if not npm_cmd:
                self.log("npm not found! Please ensure Node.js is installed", "ERROR")
                self.log("Searched locations: " + str(npm_locations), "ERROR")
                return None
            
            # On Windows, we need to use shell=True for npm.cmd
            use_shell = npm_cmd.endswith('.cmd') or npm_cmd.endswith('.bat')
            
            frontend_proc = subprocess.Popen(
                [npm_cmd, "run", "tauri", "dev"],
                cwd=ui_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                shell=use_shell
            )
            self.processes.append(frontend_proc)
            
            # Start thread to stream output
            thread = threading.Thread(
                target=self.stream_output,
                args=(frontend_proc, "FRONTEND"),
                daemon=True
            )
            thread.start()
            
            self.log(f"Frontend started (PID: {frontend_proc.pid})", "SUCCESS")
            return frontend_proc
            
        except Exception as e:
            self.log(f"Failed to start frontend: {e}", "ERROR")
            return None
    
    def print_logs(self):
        """Print logs from the queue"""
        while self.running or not self.log_queue.empty():
            try:
                log_msg = self.log_queue.get(timeout=0.1)
                print(log_msg)
            except queue.Empty:
                continue
    
    def cleanup(self):
        """Clean up all processes"""
        self.log("Shutting down...", "WARNING")
        self.running = False
        
        for proc in self.processes:
            try:
                self.log(f"Terminating process {proc.pid}")
                proc.terminate()
                proc.wait(timeout=5)
            except:
                proc.kill()
    
    def run(self):
        """Main run method"""
        print(f"{BLUE}=== PersonalParakeet Dictation View Debug Launcher ==={RESET}")
        print(f"{YELLOW}This will show all logs and errors in real-time{RESET}\n")
        
        # Set up signal handler
        signal.signal(signal.SIGINT, lambda s, f: self.cleanup())
        
        # Start log printer thread
        log_thread = threading.Thread(target=self.print_logs, daemon=True)
        log_thread.start()
        
        # Check prerequisites
        self.log("Checking prerequisites...")
        
        # Check CUDA
        try:
            import torch
            if torch.cuda.is_available():
                self.log(f"CUDA is available (Device: {torch.cuda.get_device_name(0)})", "SUCCESS")
            else:
                self.log("CUDA not available - will use CPU", "WARNING")
        except Exception as e:
            self.log(f"Failed to check CUDA: {e}", "ERROR")
        
        # Check dependencies
        try:
            import websockets
            import sounddevice
            import nemo
            self.log("Core Python dependencies OK", "SUCCESS")
        except ImportError as e:
            self.log(f"Missing Python dependency: {e}", "ERROR")
            return
        
        # Start backend
        backend = self.start_backend()
        if not backend:
            return
        
        # Wait for backend
        if not self.check_backend_ready():
            self.cleanup()
            return
        
        # Start frontend
        frontend = self.start_frontend()
        if not frontend:
            self.cleanup()
            return
        
        self.log("=" * 50)
        self.log("SYSTEM STARTED - Monitoring for errors...", "SUCCESS")
        self.log("Press Ctrl+C to stop", "WARNING")
        self.log("=" * 50)
        
        # Monitor processes
        try:
            while self.running:
                # Check if processes are still alive
                for proc in self.processes:
                    if proc.poll() is not None:
                        self.log(f"Process {proc.pid} exited with code {proc.returncode}", "ERROR")
                        self.running = False
                        break
                
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
            log_thread.join()

if __name__ == "__main__":
    launcher = DebugLauncher()
    launcher.run()