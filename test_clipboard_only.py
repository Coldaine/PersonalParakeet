#!/usr/bin/env python3
"""
Test clipboard-only injection - Works on ANY system!
"""

import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from personalparakeet.core.clipboard_injector import ClipboardInjector


def main():
    print("📋 Clipboard-Only Injection Test")
    print("================================")
    print("This works on ANY system with clipboard!")
    print()
    print("How it works:")
    print("1. Saves your current clipboard")
    print("2. Copies text to clipboard")
    print("3. Tries to paste automatically")
    print("4. If paste fails, just press Ctrl+V manually!")
    print("5. Restores your original clipboard after 1 second")
    print()
    
    injector = ClipboardInjector()
    
    print("⚠️  POSITION YOUR CURSOR IN A TEXT FIELD!")
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    tests = [
        "This text was injected via clipboard! ",
        "No special permissions needed! ",
        "Works on Wayland, X11, everywhere! ",
    ]
    
    for i, text in enumerate(tests, 1):
        print(f"\nTest {i}: Injecting '{text[:30]}...'")
        
        if injector.inject_text(text):
            print("✅ Text copied to clipboard!")
            print("   (Should auto-paste, or press Ctrl+V)")
        else:
            print("❌ Failed to copy to clipboard")
            
        time.sleep(2)
    
    print("\n" + "="*50)
    print("💡 TIP: This is the ultimate fallback!")
    print("   - No root/sudo needed")
    print("   - No special groups needed")
    print("   - No logout/login needed")
    print("   - Works on ANY desktop environment")
    print("\nWorst case: User just presses Ctrl+V manually!")


if __name__ == "__main__":
    main()