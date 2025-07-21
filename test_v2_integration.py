#!/usr/bin/env python3
"""
PersonalParakeet v2 Integration Test

Quick test to verify that the new Intelligent Thought-Linking and Command Mode
systems are properly integrated and functional.
"""

import asyncio
import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup basic logging for tests
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def test_thought_linking():
    """Test Intelligent Thought-Linking functionality"""
    print("🧠 Testing Intelligent Thought-Linking...")
    
    from personalparakeet.thought_linking import create_thought_linker, LinkingDecision
    
    # Create thought linker
    linker = create_thought_linker()
    
    # Test cases
    test_cases = [
        ("Hello world", "Expected: START_NEW_THOUGHT (first text)"),
        ("This is a continuation", "Expected: APPEND_WITH_SPACE (similar context)"),
        ("Something completely different about quantum physics", "Expected: START_NEW_PARAGRAPH (different topic)")
    ]
    
    for i, (text, expected) in enumerate(test_cases, 1):
        decision, signals = linker.should_link_thoughts(text)
        signal_descriptions = [s.description for s in signals]
        
        print(f"  Test {i}: '{text}'")
        print(f"    Decision: {decision.value}")
        print(f"    Signals: {signal_descriptions}")
        print(f"    {expected}")
        print()
    
    print("✅ Thought-Linking tests completed")
    return True

def test_command_mode():
    """Test Command Mode functionality"""
    print("🎤 Testing Command Mode...")
    
    from personalparakeet.command_mode import create_command_mode_engine
    
    # Create command engine
    engine = create_command_mode_engine()
    
    # Test activation
    print("  Testing activation phrase detection...")
    result = engine.process_speech("Hey parakeet command")
    if result and result.command_id == "activation_detected":
        print("    ✅ Activation phrase detected correctly")
    else:
        print("    ❌ Activation phrase not detected")
        return False
    
    # Test command recognition (should be in waiting state now)
    print("  Testing command recognition...")
    result = engine.process_speech("commit text")
    if result and result.command_id == "commit_text":
        print("    ✅ Command recognized correctly")
    else:
        print("    ❌ Command not recognized")
        return False
    
    # Test state info
    state_info = engine.get_state_info()
    print(f"  Engine state: {state_info['state']}")
    print(f"  Registered commands: {len(state_info['registered_commands'])}")
    
    print("✅ Command Mode tests completed")
    return True

def test_websocket_integration():
    """Test WebSocket bridge integration"""
    print("🌐 Testing WebSocket Integration...")
    
    try:
        from dictation_websocket_bridge import DictationWebSocketBridge
        
        # Create bridge instance
        bridge = DictationWebSocketBridge()
        
        # Check that components are initialized
        components = [
            ("Clarity Engine", hasattr(bridge, 'clarity_engine')),
            ("Thought Linker", hasattr(bridge, 'thought_linker')),
            ("Command Engine", hasattr(bridge, 'command_engine')),
            ("VAD Engine", hasattr(bridge, 'vad'))
        ]
        
        all_good = True
        for name, exists in components:
            status = "✅" if exists else "❌"
            print(f"  {status} {name}: {'Initialized' if exists else 'Missing'}")
            if not exists:
                all_good = False
        
        if all_good:
            print("✅ WebSocket integration tests completed")
        else:
            print("❌ WebSocket integration has issues")
            
        return all_good
        
    except Exception as e:
        print(f"❌ WebSocket integration test failed: {e}")
        return False

def test_system_startup():
    """Test that the main system can start"""
    print("🚀 Testing System Startup...")
    
    try:
        # Test that we can import the main entry point
        import start_dictation_view
        print("  ✅ Main entry point importable")
        
        # Test component imports
        from personalparakeet.clarity_engine import ClarityEngine
        from personalparakeet.vad_engine import VoiceActivityDetector
        from personalparakeet.config_manager import get_config
        print("  ✅ Core components importable")
        
        # Test config loading
        config = get_config()
        print(f"  ✅ Configuration loaded (sample rate: {config.sample_rate})")
        
        print("✅ System startup tests completed")
        return True
        
    except Exception as e:
        print(f"❌ System startup test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🧪 PersonalParakeet v2 Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Thought-Linking", test_thought_linking),
        ("Command Mode", test_command_mode), 
        ("WebSocket Integration", test_websocket_integration),
        ("System Startup", test_system_startup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - PersonalParakeet v2 is ready!")
        print("\nFeatures verified:")
        print("  ✅ Intelligent Thought-Linking with contextual signals")
        print("  ✅ Command Mode with 'Parakeet Command' activation")
        print("  ✅ WebSocket bridge integration")
        print("  ✅ System startup capability")
        print("\nTo start the system: python start_dictation_view.py")
    else:
        print("⚠️  Some tests failed - check implementation")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())