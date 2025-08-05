#!/usr/bin/env python3
"""
Automated test for Wayland injection (non-interactive)
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from personalparakeet.core.wayland_injector import WaylandInjector


def main():
    print("PersonalParakeet Wayland Detection Test")
    print("======================================")
    
    # Create injector and check capabilities
    injector = WaylandInjector()
    caps = injector.capabilities
    
    print(f"\nEnvironment:")
    print(f"  Session Type: {caps.session_type}")
    print(f"  Compositor: {caps.compositor.value}")
    print(f"  Has XWayland: {caps.has_xwayland}")
    
    print(f"\nAvailable Methods:")
    for method in caps.available_methods:
        print(f"  - {method.value}")
    
    print(f"\nMethod Priority:")
    for i, method in enumerate(injector.method_priority, 1):
        print(f"  {i}. {method.value}")
    
    # Check what's missing
    print(f"\nMissing Tools:")
    if 'ydotool' not in [m.value for m in caps.available_methods]:
        print("  - ydotool (run: sudo apt install ydotool)")
    if 'wtype' not in [m.value for m in caps.available_methods]:
        print("  - wtype (run: sudo apt install wtype)")
    if 'clipboard' not in [m.value for m in caps.available_methods]:
        print("  - wl-clipboard (run: sudo apt install wl-clipboard)")
    
    # Test injection (dry run)
    print(f"\nInjection Test (dry run):")
    test_text = "Test injection"
    success, error = injector.inject_text(test_text)
    
    if success:
        print("  ✅ Injection would succeed")
    else:
        print(f"  ❌ Injection would fail: {error}")
    
    # Show setup instructions if needed
    if not caps.available_methods or not success:
        print("\n" + "="*50)
        print(injector.get_setup_instructions())


if __name__ == "__main__":
    main()