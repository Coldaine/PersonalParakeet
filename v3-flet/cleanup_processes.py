#!/usr/bin/env python3
"""
Process Cleanup Utility for PersonalParakeet v3
Kills any hanging Flet or PersonalParakeet processes
"""

import os
import sys
import psutil
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_parakeet_processes():
    """Find all PersonalParakeet related processes"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if process is related to PersonalParakeet
            cmdline = ' '.join(proc.info['cmdline'] or [])
            
            if any(keyword in cmdline.lower() for keyword in [
                'personalparakeet', 'main.py', 'flet.exe', 
                'v3-flet', 'dictation'
            ]):
                processes.append(proc)
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return processes

def find_hanging_python_processes():
    """Find Python processes that might be hanging from PersonalParakeet"""
    processes = []
    current_pid = os.getpid()
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            if proc.info['pid'] == current_pid:
                continue
                
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                # Check if it's running our code or Flet
                if any(keyword in cmdline.lower() for keyword in [
                    'main.py', 'run_tests.py', 'test_gui_launch.py',
                    'flet', 'personalparakeet'
                ]):
                    # Check if process has been running for more than 5 minutes
                    age_seconds = time.time() - proc.info['create_time']
                    if age_seconds > 300:  # 5 minutes
                        processes.append(proc)
                        
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return processes

def kill_process_safely(proc):
    """Kill a process safely with timeout"""
    try:
        logger.info(f"Terminating process {proc.pid} ({proc.name()})")
        proc.terminate()
        
        # Wait up to 5 seconds for graceful shutdown
        try:
            proc.wait(timeout=5)
            logger.info(f"Process {proc.pid} terminated gracefully")
            return True
        except psutil.TimeoutExpired:
            logger.warning(f"Force killing process {proc.pid}")
            proc.kill()
            proc.wait(timeout=3)
            logger.info(f"Process {proc.pid} force killed")
            return True
            
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        logger.error(f"Cannot kill process {proc.pid}: {e}")
        return False

def cleanup_all():
    """Clean up all PersonalParakeet related processes"""
    logger.info("Starting process cleanup...")
    
    # Find PersonalParakeet processes
    parakeet_procs = find_parakeet_processes()
    hanging_procs = find_hanging_python_processes()
    
    all_procs = parakeet_procs + hanging_procs
    
    if not all_procs:
        logger.info("No PersonalParakeet processes found to clean up")
        return True
    
    logger.info(f"Found {len(all_procs)} processes to clean up:")
    for proc in all_procs:
        try:
            cmdline = ' '.join(proc.cmdline())
            logger.info(f"  PID {proc.pid}: {proc.name()} - {cmdline[:100]}...")
        except:
            logger.info(f"  PID {proc.pid}: {proc.name()}")
    
    # Kill processes
    success_count = 0
    for proc in all_procs:
        if kill_process_safely(proc):
            success_count += 1
    
    logger.info(f"Successfully cleaned up {success_count}/{len(all_procs)} processes")
    
    # Clean up any orphaned ports
    cleanup_ports()
    
    return success_count == len(all_procs)

def cleanup_ports():
    """Clean up any ports that might still be bound"""
    import socket
    
    # Test common Flet ports
    test_ports = [8550, 8551, 8552, 8553, 8554]
    
    for port in test_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                logger.warning(f"Port {port} is still in use")
            sock.close()
        except:
            sock.close()

if __name__ == "__main__":
    print("PersonalParakeet v3 Process Cleanup")
    print("=" * 40)
    
    success = cleanup_all()
    
    if success:
        print("✓ Cleanup completed successfully")
        sys.exit(0)
    else:
        print("⚠ Some processes could not be cleaned up")
        sys.exit(1)