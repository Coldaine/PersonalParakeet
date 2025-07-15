#!/usr/bin/env python3
"""
Test the enhanced dictation system with improved error handling
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from personalparakeet.dictation import SimpleDictation
import time
import threading

def test_error_handling():
    """Test error handling improvements"""
    print("🧪 Testing Enhanced Dictation System")
    print("=" * 50)
    
    try:
        # Create dictation instance
        print("\n1️⃣ Testing initialization...")
        dictation = SimpleDictation()
        print("✅ Initialization successful")
        
        # Test text output callback directly
        print("\n2️⃣ Testing text output callback...")
        dictation.output_text("Test message from enhanced system")
        
        # Test with various text types
        test_texts = [
            "Simple text",
            "Text with numbers 123",
            "Text with symbols !@#",
            "Multi word sentence here",
            "Unicode text: café résumé",
        ]
        
        print("\n3️⃣ Testing various text types...")
        for text in test_texts:
            print(f"\nTesting: '{text}'")
            dictation.output_text(text)
            time.sleep(0.5)
        
        # Test fallback display
        print("\n4️⃣ Testing fallback display (simulating failures)...")
        dictation.injection_failures = 3  # Force fallback mode
        dictation.use_fallback_display = True
        dictation._display_fallback_text("This is fallback text that should appear in console")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

def test_thread_safety():
    """Test thread safety of text output"""
    print("\n\n🧪 Testing Thread Safety")
    print("=" * 50)
    
    try:
        dictation = SimpleDictation()
        
        def output_from_thread(thread_id):
            """Simulate output from background thread"""
            for i in range(3):
                dictation.output_text(f"Thread {thread_id} message {i}")
                time.sleep(0.2)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=output_from_thread, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        print("\n✅ Thread safety test completed!")
        
    except Exception as e:
        print(f"\n❌ Thread safety test failed: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced Dictation System Test Suite")
    print("=====================================")
    print("Note: Some tests require you to have a text editor open")
    print("Click in a text field before continuing...\n")
    
    input("Press Enter when ready to start tests...")
    
    # Run tests
    test_error_handling()
    test_thread_safety()
    
    print("\n\n📊 Test Summary:")
    print("- Error handling: Enhanced with fallback display")
    print("- Thread safety: Improved with better exception handling") 
    print("- Text injection: Multiple methods with graceful degradation")
    print("\n🎉 Testing complete!")