#!/usr/bin/env python3
"""
Simple script to check if we're in the correct virtual environment
"""

import sys
import os

def check_virtual_env():
    """Check if we're running in the correct virtual environment"""
    venv_path = os.environ.get('VIRTUAL_ENV')
    expected_venv = os.path.join(os.getcwd(), '.venv')
    
    print(f"Current Python: {sys.executable}")
    print(f"Virtual ENV: {venv_path}")
    print(f"Expected: {expected_venv}")
    
    if venv_path and os.path.normpath(venv_path) == os.path.normpath(expected_venv):
        print("✅ Correct virtual environment is active")
        return True
    else:
        print("❌ Virtual environment not active or incorrect")
        print("Run: .venv\\Scripts\\Activate.ps1")
        return False

if __name__ == "__main__":
    check_virtual_env()