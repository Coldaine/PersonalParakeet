#!/usr/bin/env python3
"""
Test audio device selection functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from personalparakeet.audio_devices import AudioDeviceManager
import sounddevice as sd

def test_device_listing():
    """Test listing audio devices"""
    print("TEST 1: List Audio Devices")
    print("=" * 60)
    
    devices = AudioDeviceManager.list_input_devices()
    print(f"Found {len(devices)} input devices:")
    
    for device in devices:
        print(f"\n  Device {device['index']}: {device['name']}")
        print(f"    - Channels: {device['channels']}")
        print(f"    - Sample Rate: {device['sample_rate']} Hz")
        print(f"    - Default: {device['is_default']}")
    
    return len(devices) > 0

def test_device_search():
    """Test device search by name"""
    print("\n\nTEST 2: Device Search by Name")
    print("=" * 60)
    
    test_patterns = [
        "microphone",
        "mic",
        "headset",
        "webcam",
        "usb",
        "realtek",
        "default"
    ]
    
    found_any = False
    for pattern in test_patterns:
        idx = AudioDeviceManager.find_device_by_name(pattern)
        if idx is not None:
            info = AudioDeviceManager.get_device_info(idx)
            print(f"[PASS] Found '{pattern}' → {info['name']} (index {idx})")
            found_any = True
        else:
            print(f"[FAIL] No match for '{pattern}'")
    
    return found_any

def test_device_validation():
    """Test device validation"""
    print("\n\nTEST 3: Device Validation")
    print("=" * 60)
    
    # Test default device
    valid, msg = AudioDeviceManager.validate_device(None)
    print(f"Default device: {msg}")
    
    # Test all found devices
    devices = AudioDeviceManager.list_input_devices()
    valid_count = 0
    
    for device in devices[:5]:  # Test first 5 devices
        valid, msg = AudioDeviceManager.validate_device(device['index'])
        if valid:
            print(f"[PASS] Device {device['index']}: {msg}")
            valid_count += 1
        else:
            print(f"[FAIL] Device {device['index']}: {msg}")
    
    return valid_count > 0

def test_interactive_selection():
    """Test interactive device selection (requires user input)"""
    print("\n\nTEST 4: Interactive Selection (Optional)")
    print("=" * 60)
    
    response = input("Test interactive device selection? (y/n): ").strip().lower()
    if response == 'y':
        selected = AudioDeviceManager.select_device_interactive()
        if selected is not None:
            print(f"\n[PASS] You selected device index: {selected}")
            return True
        else:
            print("\n[FAIL] No device selected")
            return False
    else:
        print("Skipped interactive test")
        return True

def run_all_tests():
    """Run all device selection tests"""
    print("STARTING: Audio Device Selection Test Suite")
    print("=" * 80)
    
    results = {
        "Device Listing": test_device_listing(),
        "Device Search": test_device_search(),
        "Device Validation": test_device_validation(),
        "Interactive Selection": test_interactive_selection()
    }
    
    print("\n\nRESULTS:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("SUCCESS: All tests passed!")
    else:
        print("WARNING: Some tests failed")
    
    return all_passed

if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        print(f"\n[FAIL] Test suite error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()