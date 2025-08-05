#!/usr/bin/env python3
"""
Test script for Wayland text injection
"""

import os
import sys
import time
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from personalparakeet.core.wayland_injector import WaylandInjector, WaylandCapabilities


def test_wayland_detection():
    """Test Wayland environment detection"""
    print("=== Wayland Environment Detection ===")
    
    # Check environment
    session_type = os.environ.get('XDG_SESSION_TYPE', 'unknown')
    wayland_display = os.environ.get('WAYLAND_DISPLAY', 'not set')
    x11_display = os.environ.get('DISPLAY', 'not set')
    desktop = os.environ.get('XDG_CURRENT_DESKTOP', 'unknown')
    
    print(f"Session Type: {session_type}")
    print(f"Wayland Display: {wayland_display}")
    print(f"X11 Display: {x11_display}")
    print(f"Desktop Environment: {desktop}")
    print()
    
    # Create injector and check capabilities
    injector = WaylandInjector()
    caps = injector.capabilities
    
    print(f"Detected Compositor: {caps.compositor.value}")
    print(f"Has XWayland: {caps.has_xwayland}")
    print(f"Available Methods: {[m.value for m in caps.available_methods]}")
    print(f"Method Priority: {[m.value for m in injector.method_priority]}")
    
    return injector


def test_injection_methods(injector: WaylandInjector):
    """Test individual injection methods"""
    print("\n=== Testing Injection Methods ===")
    
    test_texts = [
        "Hello from Wayland!",
        "Testing special chars: @#$%",
        "Multi word test string",
    ]
    
    print("\n⚠️  POSITION YOUR CURSOR IN A TEXT FIELD NOW!")
    print("Starting tests in 3 seconds...")
    time.sleep(3)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: '{text}'")
        success, error = injector.inject_text(text)
        
        if success:
            print("✅ Injection successful!")
        else:
            print(f"❌ Injection failed: {error}")
        
        # Pause between tests
        time.sleep(2)


def test_setup_instructions(injector: WaylandInjector):
    """Show setup instructions"""
    print("\n=== Setup Instructions ===")
    print(injector.get_setup_instructions())


def main():
    """Run all tests"""
    print("PersonalParakeet Wayland Injection Test")
    print("=====================================")
    
    # Check if we're on Wayland
    session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
    if session_type != 'wayland':
        print(f"\n⚠️  WARNING: Not running on Wayland (session type: {session_type})")
        print("This test is designed for Wayland systems.")
        response = input("Continue anyway? [y/N]: ")
        if response.lower() != 'y':
            return
    
    # Run tests
    injector = test_wayland_detection()
    
    if not injector.method_priority:
        print("\n❌ No injection methods available!")
        test_setup_instructions(injector)
        return
    
    # Test injection
    response = input("\nTest text injection? [Y/n]: ")
    if response.lower() != 'n':
        test_injection_methods(injector)
    
    # Show setup instructions
    response = input("\nShow setup instructions? [y/N]: ")
    if response.lower() == 'y':
        test_setup_instructions(injector)


if __name__ == "__main__":
    main()