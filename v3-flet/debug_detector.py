#!/usr/bin/env python3
"""
Debug application detector
"""

import subprocess
from core.application_detector import EnhancedApplicationDetector

def debug_xdotool():
    print("=== xdotool debugging ===")
    try:
        result = subprocess.run(['xdotool', 'getactivewindow'], 
                              capture_output=True, text=True, timeout=2)
        print(f"getactivewindow return code: {result.returncode}")
        print(f"stdout: '{result.stdout.strip()}'")
        print(f"stderr: '{result.stderr.strip()}'")
        
        if result.returncode == 0:
            window_id = result.stdout.strip()
            print(f"Active window ID: {window_id}")
            
            # Test xprop
            result2 = subprocess.run(['xprop', '-id', window_id], 
                                   capture_output=True, text=True, timeout=2)
            print(f"xprop return code: {result2.returncode}")
            if result2.returncode == 0:
                lines = result2.stdout.split('\n')
                for line in lines:
                    if 'WM_NAME' in line or 'WM_CLASS' in line:
                        print(f"  {line}")
        
    except Exception as e:
        print(f"xdotool error: {e}")

def debug_detector():
    print("\n=== Detector debugging ===")
    detector = EnhancedApplicationDetector()
    
    # Test Linux detection specifically
    app_info = detector._detect_linux_application()
    
    if app_info:
        print(f"App detected: {app_info}")
    else:
        print("No app detected")

if __name__ == "__main__":
    debug_xdotool()
    debug_detector()