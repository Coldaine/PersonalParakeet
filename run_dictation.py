#!/usr/bin/env python3
"""
PersonalParakeet Dictation System - Main Entry Point

This script starts the real-time dictation system with LocalAgreement buffering.
Press F4 to toggle dictation on/off.
Press Ctrl+C to exit.

Usage:
    python run_dictation.py                    # Use default audio device
    python run_dictation.py --list-devices     # List available devices  
    python run_dictation.py --device 2         # Use device index 2
    python run_dictation.py --device-name "Blue Yeti"  # Use device by name
"""

import sys
import os

# Ensure the package is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the CLI
from personalparakeet.dictation import cli

if __name__ == "__main__":
    cli()