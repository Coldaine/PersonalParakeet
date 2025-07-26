#!/usr/bin/env python3
"""
Start only the backend WebSocket server for testing
"""

import subprocess
import sys
import os

print("=== Starting PersonalParakeet Backend Only ===\n")
print("This will start the WebSocket server on ws://127.0.0.1:8765")
print("You can test it with: python test_backend_only.py\n")

# Start the backend
backend_proc = subprocess.Popen(
    [sys.executable, "dictation_websocket_bridge.py"],
    cwd=os.path.dirname(os.path.abspath(__file__))
)

print(f"Backend started (PID: {backend_proc.pid})")
print("\nPress Ctrl+C to stop...")

try:
    backend_proc.wait()
except KeyboardInterrupt:
    print("\nStopping backend...")
    backend_proc.terminate()