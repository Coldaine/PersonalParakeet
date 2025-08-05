#!/usr/bin/env python3
"""
Debug which injection method is being used
"""

import sys
import time
import logging
from pathlib import Path

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from personalparakeet.core.text_injector import TextInjector
from personalparakeet.core.wayland_injector import WaylandInjector


def main():
    print("PersonalParakeet Injection Debug")
    print("================================")
    
    # Check Wayland capabilities
    wayland = WaylandInjector()
    print(f"\nDetected compositor: {wayland.capabilities.compositor.value}")
    print(f"Available methods: {[m.value for m in wayland.capabilities.available_methods]}")
    print(f"Method priority: {[m.value for m in wayland.method_priority]}")
    
    print("\n⚠️  Position cursor in text field!")
    print("Testing in 3 seconds...")
    time.sleep(3)
    
    # Test injection with debug
    injector = TextInjector()
    
    test_text = "Debug test "
    print(f"\nInjecting: '{test_text}'")
    
    success = injector.inject_text(test_text)
    
    if success:
        print("✅ Success!")
    else:
        print("❌ Failed!")


if __name__ == "__main__":
    main()