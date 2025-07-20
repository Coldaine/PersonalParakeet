#!/usr/bin/env python3
"""
Simple test to verify keyboard output functionality
"""

import keyboard
import time
import threading
from queue import Queue

def test_direct_keyboard():
    """Test direct keyboard output"""
    print("Testing direct keyboard output in 3 seconds...")
    print("Click in a text field (like Notepad) and wait...")
    time.sleep(3)
    
    try:
        keyboard.write("Hello from direct keyboard test!")
        print("[PASS] Direct keyboard test successful")
        return True
    except Exception as e:
        print(f"[FAIL] Direct keyboard test failed: {e}")
        return False

def test_threaded_keyboard():
    """Test keyboard output from a background thread"""
    print("\nTesting threaded keyboard output in 3 seconds...")
    print("Click in a text field (like Notepad) and wait...")
    time.sleep(3)
    
    text_queue = Queue()
    
    def background_thread():
        try:
            # Simulate the audio processing thread
            time.sleep(0.5)
            text_queue.put("Hello from background thread!")
        except Exception as e:
            print(f"[FAIL] Background thread error: {e}")
    
    def output_thread():
        try:
            text = text_queue.get(timeout=2)
            keyboard.write(text)
            print("[PASS] Threaded keyboard test successful")
            return True
        except Exception as e:
            print(f"[FAIL] Threaded keyboard test failed: {e}")
            return False
    
    # Start background thread
    bg_thread = threading.Thread(target=background_thread)
    bg_thread.start()
    
    # Try to output from main thread
    return output_thread()

def test_callback_mechanism():
    """Test the callback mechanism similar to LocalAgreement"""
    print("\nTesting callback mechanism in 3 seconds...")
    print("Click in a text field (like Notepad) and wait...")
    time.sleep(3)
    
    callback_called = False
    
    def text_output_callback(text):
        nonlocal callback_called
        try:
            print(f"INFO: Callback triggered with: '{text}'")
            keyboard.write(text)
            callback_called = True
            print("[PASS] Callback mechanism test successful")
        except Exception as e:
            print(f"[FAIL] Callback mechanism test failed: {e}")
    
    # Simulate the LocalAgreement callback
    try:
        text_output_callback("Hello from callback test!")
        return callback_called
    except Exception as e:
        print(f"[FAIL] Callback test error: {e}")
        return False

if __name__ == "__main__":
    print("TEST: Testing Keyboard Output Mechanisms")
    print("=" * 50)
    
    # Test 1: Direct keyboard output
    direct_success = test_direct_keyboard()
    
    # Test 2: Threaded keyboard output
    threaded_success = test_threaded_keyboard()
    
    # Test 3: Callback mechanism
    callback_success = test_callback_mechanism()
    
    print("\nRESULTS:")
    print(f"Direct keyboard: {'[PASS]' if direct_success else '[FAIL]'}")
    print(f"Threaded keyboard: {'[PASS]' if threaded_success else '[FAIL]'}")
    print(f"Callback mechanism: {'[PASS]' if callback_success else '[FAIL]'}")
    
    if all([direct_success, threaded_success, callback_success]):
        print("\nSUCCESS: All tests passed! Keyboard output should work.")
    else:
        print("\nWARNING: Some tests failed. Check Windows permissions and focus.")
        print("   - Make sure you clicked in a text field")
        print("   - Check if antivirus is blocking keyboard simulation")
        print("   - Try running as administrator if needed")