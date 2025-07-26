#!/usr/bin/env python3
"""
Start PersonalParakeet Workshop Box
Handles common issues gracefully
"""

import subprocess
import sys
import os
import time

def check_cuda():
    """Check if CUDA is available"""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print("[OK] CUDA is available")
            return True
        else:
            print("[X] CUDA not available - GPU acceleration disabled")
            print("\nTo enable GPU acceleration:")
            print("1. Ensure NVIDIA drivers are installed")
            print("2. Run: python personalparakeet/cuda_fix.py")
            return False
    except ImportError:
        print("[X] PyTorch not installed")
        print("\nTo install PyTorch with CUDA:")
        print("Run: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        return False

def check_rust():
    """Check if Rust is installed"""
    # Try standard path first
    try:
        result = subprocess.run(["rustc", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Rust installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    # Try user cargo directory
    rust_path = os.path.expanduser("~/.cargo/bin/rustc.exe")
    if os.path.exists(rust_path):
        try:
            result = subprocess.run([rust_path, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[OK] Rust installed: {result.stdout.strip()}")
                print("     (Found in ~/.cargo/bin - consider adding to PATH)")
                return True
        except:
            pass
    
    print("[X] Rust not found in PATH")
    print("\nRust may be installed but not in PATH.")
    print("Try: setx PATH \"%PATH%;%USERPROFILE%\\.cargo\\bin\"")
    print("Then restart your terminal.")
    return False

def check_node():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Node.js installed: {result.stdout.strip()}")
            return True
        else:
            print("[X] Node.js not found")
            print("\nTo install Node.js:")
            print("Visit: https://nodejs.org/")
            return False
    except FileNotFoundError:
        print("[X] Node.js not installed")
        print("\nTo install Node.js:")
        print("Visit: https://nodejs.org/")
        return False

def start_dictation_view():
    """Start the Dictation View"""
    print("=== PersonalParakeet Dictation View ===")
    print("Checking prerequisites...\n")
    
    # Check prerequisites
    cuda_ok = check_cuda()
    rust_ok = check_rust()
    node_ok = check_node()
    
    print()
    
    if not rust_ok or not node_ok:
        print("WARNING: Missing prerequisites. Please install the required software.")
        print("\nSee DICTATION_VIEW_SETUP_GUIDE.md for detailed instructions.")
        return False
    
    if not cuda_ok:
        print("WARNING: Running without GPU acceleration (slower performance)")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
    print("\nStarting Dictation View...\n")
    
    # Start Python backend
    print("1. Starting Python WebSocket backend...")
    backend_cmd = [sys.executable, "dictation_websocket_bridge.py"]
    
    try:
        backend_process = subprocess.Popen(
            backend_cmd, 
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        print("   [OK] Backend started (PID: {})".format(backend_process.pid))
    except Exception as e:
        print(f"   [X] Failed to start backend: {e}")
        return False
    
    # Wait for backend to initialize
    print("\n2. Waiting for backend to initialize...")
    time.sleep(3)
    
    # Start Tauri UI
    print("\n3. Starting Dictation View UI...")
    os.chdir("dictation-view-ui")
    
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    ui_cmd = [npm_cmd, "run", "tauri", "dev"]
    
    try:
        ui_process = subprocess.Popen(
            ui_cmd,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        print("   [OK] UI build started (PID: {})".format(ui_process.pid))
    except Exception as e:
        print(f"   [X] Failed to start UI: {e}")
        backend_process.terminate()
        return False
    
    print("\n" + "="*50)
    print("Dictation View is starting up!")
    print("="*50)
    print("\nWhat to expect:")
    print("- First run: Tauri will compile (1-2 minutes)")
    print("- Dictation View window will appear after compilation")
    print("- Look for status indicator:")
    print("  - Green = Connected and listening")
    print("  - Red = Disconnected from backend")
    print("\nControls:")
    print("- Drag window to move")
    print("- Escape to hide")
    print("- Close console windows to stop")
    
    print("\nPress Ctrl+C to stop all processes...")
    
    try:
        # Wait for user to stop
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        backend_process.terminate()
        ui_process.terminate()
        print("Stopped.")
    
    return True

if __name__ == "__main__":
    try:
        success = start_dictation_view()
        if not success:
            print("\nDictation View startup failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)