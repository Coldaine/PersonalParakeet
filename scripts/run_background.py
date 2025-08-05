#!/usr/bin/env python3
"""
Background runner for PersonalParakeet with separate log monitoring
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path
import threading

# Log file location
LOG_DIR = Path.home() / '.personalparakeet'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'personalparakeet.log'
PID_FILE = LOG_DIR / 'personalparakeet.pid'

def start_personalparakeet():
    """Start PersonalParakeet in the background"""
    # Check if already running
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text())
            # Check if process is still running
            os.kill(pid, 0)
            print(f"PersonalParakeet is already running (PID: {pid})")
            print(f"To stop it, run: python run_background.py stop")
            return
        except (ProcessLookupError, ValueError):
            # Process not running, remove stale PID file
            PID_FILE.unlink()
    
    print("Starting PersonalParakeet in background...")
    
    # Start the process
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'  # Ensure immediate log output
    env['PERSONALPARAKEET_BACKGROUND'] = '1'  # Signal background mode
    
    # Ensure we're in the project directory
    project_dir = Path(__file__).parent
    
    process = subprocess.Popen(
        ['poetry', 'run', 'python', '-m', 'personalparakeet'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        text=True,
        bufsize=1,  # Line buffered
        cwd=project_dir
    )
    
    # Save PID
    PID_FILE.write_text(str(process.pid))
    print(f"PersonalParakeet started (PID: {process.pid})")
    print(f"Log file: {LOG_FILE}")
    print(f"To monitor logs: tail -f {LOG_FILE}")
    print(f"To stop: python run_background.py stop")
    
    # Start log writer thread
    def write_logs():
        with open(LOG_FILE, 'a') as f:
            for line in process.stdout:
                f.write(line)
                f.flush()
    
    log_thread = threading.Thread(target=write_logs, daemon=True)
    log_thread.start()
    
    # Keep process running
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping PersonalParakeet...")
        process.terminate()
        process.wait(timeout=5)
    finally:
        if PID_FILE.exists():
            PID_FILE.unlink()

def stop_personalparakeet():
    """Stop PersonalParakeet if running"""
    if not PID_FILE.exists():
        print("PersonalParakeet is not running")
        return
    
    try:
        pid = int(PID_FILE.read_text())
        print(f"Stopping PersonalParakeet (PID: {pid})...")
        
        # Send SIGTERM
        os.kill(pid, signal.SIGTERM)
        
        # Wait for process to stop
        for _ in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(0.5)
            except ProcessLookupError:
                break
        else:
            # Force kill if still running
            print("Force killing process...")
            os.kill(pid, signal.SIGKILL)
        
        PID_FILE.unlink()
        print("PersonalParakeet stopped")
        
    except (ProcessLookupError, ValueError) as e:
        print(f"Error stopping process: {e}")
        if PID_FILE.exists():
            PID_FILE.unlink()

def show_logs(follow=False):
    """Show PersonalParakeet logs"""
    if not LOG_FILE.exists():
        print(f"No log file found at {LOG_FILE}")
        return
    
    if follow:
        print(f"Following logs from {LOG_FILE} (Ctrl+C to stop)...")
        subprocess.run(['tail', '-f', str(LOG_FILE)])
    else:
        print(f"Last 50 lines from {LOG_FILE}:")
        subprocess.run(['tail', '-n', '50', str(LOG_FILE)])

def show_status():
    """Show PersonalParakeet status"""
    if not PID_FILE.exists():
        print("PersonalParakeet is not running")
        return
    
    try:
        pid = int(PID_FILE.read_text())
        os.kill(pid, 0)
        print(f"PersonalParakeet is running (PID: {pid})")
        print(f"Log file: {LOG_FILE}")
    except (ProcessLookupError, ValueError):
        print("PersonalParakeet is not running (stale PID file)")
        PID_FILE.unlink()

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='PersonalParakeet background runner')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'logs', 'follow'],
                        help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        start_personalparakeet()
    elif args.command == 'stop':
        stop_personalparakeet()
    elif args.command == 'status':
        show_status()
    elif args.command == 'logs':
        show_logs(follow=False)
    elif args.command == 'follow':
        show_logs(follow=True)

if __name__ == '__main__':
    main()