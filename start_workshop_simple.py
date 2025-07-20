import subprocess
import time
import os
import sys

print("Starting PersonalParakeet Workshop Box...")

# Start Python WebSocket bridge
print("\nStarting Python backend...")
backend_cmd = [sys.executable, "workshop_websocket_bridge_v2.py"]
backend_process = subprocess.Popen(backend_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)

# Wait for backend to initialize
print("Waiting for backend to initialize...")
time.sleep(3)

# Start Tauri UI
print("\nStarting Workshop Box UI...")
os.chdir("workshop-box-ui")

# Use npm to run tauri dev
ui_cmd = ["C:\\Program Files\\nodejs\\npm.cmd", "run", "tauri", "dev"]
print(f"Running: {' '.join(ui_cmd)}")

try:
    ui_process = subprocess.Popen(ui_cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    print("\nWorkshop Box is starting up!")
    print("Two new console windows should appear:")
    print("1. Python WebSocket backend")
    print("2. Tauri development server")
    print("\nThe Workshop Box UI should appear shortly...")
    print("\nTo stop, close both command windows.")
except Exception as e:
    print(f"Error starting UI: {e}")
    print("Make sure Rust and Node.js are installed")

print("\nPress Enter to exit this launcher...")
input()