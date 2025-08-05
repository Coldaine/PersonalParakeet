#!/usr/bin/env python3
"""
REAL text injection test - actually types text!
"""

import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from personalparakeet.core.text_injector import TextInjector


def main():
    print("PersonalParakeet REAL Injection Test")
    print("====================================")
    print("\n⚠️  WARNING: This will ACTUALLY type text!")
    print("⚠️  Position your cursor in a text field NOW!")
    print("\nStarting in 5 seconds...")
    
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # Create injector
    injector = TextInjector()
    
    # Test texts
    tests = [
        "Hello from Wayland! ",
        "Testing injection... ",
        "It works! 🎉 ",
    ]
    
    print("\nInjecting text NOW:")
    
    for i, text in enumerate(tests, 1):
        print(f"\nTest {i}: '{text}'")
        
        success = injector.inject_text(text)
        
        if success:
            print("✅ Injected successfully!")
        else:
            print("❌ Injection failed!")
            
        # Get stats
        stats = injector.get_injection_stats()
        print(f"Stats: {stats}")
        
        time.sleep(1)  # Pause between injections
    
    print("\n" + "="*50)
    print("Check the text field - did the text appear?")


if __name__ == "__main__":
    main()