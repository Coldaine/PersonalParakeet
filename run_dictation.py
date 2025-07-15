#!/usr/bin/env python3
"""
PersonalParakeet Dictation System - Main Entry Point

This script starts the real-time dictation system with LocalAgreement buffering.
Press F4 to toggle dictation on/off.
Press Ctrl+C to exit.
"""

import sys
import os

# Ensure the package is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the dictation system
# The CUDA fix is automatically applied during package import
from personalparakeet import SimpleDictation
import keyboard

def main():
    print("🚀 PersonalParakeet Dictation System")
    print("=" * 50)
    
    try:
        # Create dictation system
        dictation = SimpleDictation()
        
        # Set up hotkey (F4 to toggle)
        print("⌨️  Setting up hotkey...")
        keyboard.add_hotkey('f4', dictation.toggle_dictation)
        print("✅ Hotkey registered: F4 to start/stop dictation")
        
        print("\n🎯 READY TO USE:")
        print("   1. Click in any text field (Notepad, browser, etc.)")
        print("   2. Press F4 to start dictation")
        print("   3. Speak clearly")
        print("   4. Watch text appear with LocalAgreement buffering")
        print("   5. Press F4 again to stop")
        print("   6. Press Ctrl+C to quit")
        print("\n⏳ Waiting for F4...")
        
        # Keep running until Ctrl+C
        keyboard.wait('ctrl+c')
        
    except KeyboardInterrupt:
        print("\n\n🔄 Shutting down...")
        if 'dictation' in locals():
            dictation.stop_dictation()
        print("👋 Goodbye!")
        
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        print("   - Check that CUDA is available")
        print("   - Ensure microphone permissions are granted")
        sys.exit(1)

if __name__ == "__main__":
    main()