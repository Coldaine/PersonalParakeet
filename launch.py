#!/usr/bin/env python3
"""
Simple launcher - starts PersonalParakeet and exits immediately
"""

import subprocess
import sys
from pathlib import Path

log_dir = Path.home() / '.personalparakeet'
log_file = log_dir / 'personalparakeet.log'

print(f"Launching PersonalParakeet...")
print(f"Log file: {log_file}")

# Start as detached process
process = subprocess.Popen(
    [sys.executable, '-m', 'personalparakeet'],
    stdout=open(log_file, 'a'),
    stderr=subprocess.STDOUT,
    start_new_session=True
)

print(f"Started with PID: {process.pid}")
print(f"Check logs: tail -f {log_file}")

# Exit immediately
sys.exit(0)