#!/usr/bin/env python3
"""
Test UNSAFE Wayland injection - for personal use only!
This will try every dirty trick to make text injection work.
"""

import sys
import time
import subprocess
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from personalparakeet.core.wayland_injector_unsafe import UnsafeWaylandInjector


def main():
    print("🚨 UNSAFE Wayland Injection Test 🚨")
    print("===================================")
    print("This will try EVERYTHING to inject text:")
    print("- sudo ydotool")
    print("- chmod /dev/uinput") 
    print("- aggressive clipboard manipulation")
    print("- xdotool on Wayland")
    print()
    
    # Check for sudo
    try:
        # Test if we can use sudo without password
        result = subprocess.run(['sudo', '-n', 'true'], capture_output=True)
        if result.returncode == 0:
            print("✅ Passwordless sudo available")
        else:
            print("⚠️  May need to enter sudo password")
            print("   Run: sudo visudo")
            print("   Add: %sudo ALL=(ALL) NOPASSWD: /usr/bin/ydotool")
    except:
        pass
    
    print("\n⚠️  POSITION YOUR CURSOR IN A TEXT FIELD!")
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    # Create unsafe injector
    injector = UnsafeWaylandInjector()
    
    # Test texts
    tests = [
        "UNSAFE injection works! ",
        "No logout required! ",
        "Personal use FTW! ",
    ]
    
    for text in tests:
        print(f"\nInjecting: {text}")
        success, error = injector.inject_text(text)
        
        if success:
            print("✅ Success!")
        else:
            print(f"❌ Failed: {error}")
        
        time.sleep(1)
    
    print("\n" + "="*40)
    print("For even more unsafe mode, run:")
    print("  sudo chmod 666 /dev/uinput")
    print("  (Don't forget to chmod 600 after!)")
    print()
    print("Or add to sudoers for ydotool:")
    print("  echo '$USER ALL=(ALL) NOPASSWD: /usr/bin/ydotool' | sudo tee -a /etc/sudoers")


if __name__ == "__main__":
    main()