import subprocess
import time
import os

print("Starting PersonalParakeet Workshop Box...")

# Start Python WebSocket bridge
print("Starting Python backend...")
backend_process = subprocess.Popen(
    [".venv\\Scripts\\python.exe", "workshop_websocket_bridge.py"],
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

# Wait for backend to initialize
print("Waiting for backend to initialize...")
time.sleep(2)

# Start Tauri UI
print("Starting Workshop Box UI...")
os.chdir("workshop-box-ui")
ui_process = subprocess.Popen(
    ["C:\\Program Files\\nodejs\\npm.cmd", "run", "tauri", "dev"],
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

print("\nWorkshop Box is starting up...")
print("To stop, close both command windows.")
print("\nPress Enter to continue...")
input()