#!/usr/bin/env python3
"""
Status Verification - Check if PersonalParakeet v3 is running
"""

import os
import psutil
import time

def check_running_status():
    """Check if PersonalParakeet is currently running"""
    parakeet_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'main.py' in cmdline and 'PersonalParakeet' in cmdline:
                parakeet_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline,
                    'age_seconds': time.time() - proc.info['create_time']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return parakeet_processes

def check_log_status():
    """Check the latest log file for status"""
    log_file = "personalparakeet_v3.log"
    
    if not os.path.exists(log_file):
        return "No log file found"
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return "Log file is empty"
        
        # Check for key success indicators
        success_indicators = [
            "PersonalParakeet v3 initialized successfully",
            "PersonalParakeet v3 is ready!",
            "Audio processing started"
        ]
        
        found_indicators = []
        for line in lines:
            for indicator in success_indicators:
                if indicator in line:
                    found_indicators.append(indicator)
        
        return {
            'total_log_lines': len(lines),
            'last_log_entry': lines[-1].strip(),
            'success_indicators_found': found_indicators,
            'appears_successful': len(found_indicators) >= 2
        }
        
    except Exception as e:
        return f"Error reading log: {e}"

if __name__ == "__main__":
    print("PersonalParakeet v3 Status Check")
    print("=" * 40)
    
    # Check running processes
    processes = check_running_status()
    print(f"Running processes: {len(processes)}")
    
    for proc in processes:
        print(f"  PID {proc['pid']}: {proc['name']} (running {proc['age_seconds']:.1f}s)")
    
    # Check log status
    print("\nLog Analysis:")
    log_status = check_log_status()
    
    if isinstance(log_status, dict):
        print(f"  Log lines: {log_status['total_log_lines']}")
        print(f"  Success indicators: {len(log_status['success_indicators_found'])}")
        print(f"  Appears successful: {log_status['appears_successful']}")
        print(f"  Last entry: {log_status['last_log_entry']}")
        
        if log_status['success_indicators_found']:
            print("  Found indicators:")
            for indicator in log_status['success_indicators_found']:
                print(f"    ✓ {indicator}")
    else:
        print(f"  {log_status}")
    
    # Overall assessment
    print(f"\nStatus: Application appears to be {'working' if processes or (isinstance(log_status, dict) and log_status['appears_successful']) else 'not running'}")