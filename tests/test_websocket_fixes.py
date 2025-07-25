#!/usr/bin/env python3
"""Test script to verify WebSocket bridge fixes"""

import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all imports work correctly"""
    logger.info("Testing imports...")
    try:
        from personalparakeet.dictation import SimpleDictation
        logger.info("✓ SimpleDictation import successful")
        
        from personalparakeet.cuda_fix import ensure_cuda_available
        logger.info("✓ cuda_fix import successful")
        
        import asyncio
        import websockets
        import json
        import threading
        logger.info("✓ All standard imports successful")
        
        return True
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False

def test_dictation_init():
    """Test if SimpleDictation can be initialized"""
    logger.info("\nTesting SimpleDictation initialization...")
    try:
        from personalparakeet.dictation import SimpleDictation
        from personalparakeet.cuda_fix import ensure_cuda_available
        
        # Ensure CUDA is available
        ensure_cuda_available()
        
        # Try to create SimpleDictation instance
        dictation = SimpleDictation(
            audio_input_callback=None,
            stt_callback=None,
            device_index=None,
            agreement_threshold=1,
            chunk_duration=0.5
        )
        logger.info("✓ SimpleDictation initialized successfully")
        
        # Test if methods exist
        if hasattr(dictation, 'start_dictation'):
            logger.info("✓ start_dictation method exists")
        else:
            logger.error("✗ start_dictation method missing")
            
        if hasattr(dictation, 'stop_dictation'):
            logger.info("✓ stop_dictation method exists")
        else:
            logger.error("✗ stop_dictation method missing")
            
        # Clean up
        if hasattr(dictation, 'cleanup'):
            dictation.cleanup()
            
        return True
    except Exception as e:
        logger.error(f"Dictation initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_websocket_bridge():
    """Test if WebSocket bridge can be imported and initialized"""
    logger.info("\nTesting WebSocket bridge...")
    try:
        from workshop_websocket_bridge_v2 import WorkshopWebSocketBridge
        logger.info("✓ WebSocket bridge import successful")
        
        # Try to create bridge instance
        bridge = WorkshopWebSocketBridge()
        logger.info("✓ WebSocket bridge initialized successfully")
        
        # Check if dictation was initialized
        if bridge.dictation is not None:
            logger.info("✓ Dictation system initialized in bridge")
        else:
            logger.warning("⚠ Dictation system not initialized (may be due to model loading)")
            
        return True
    except Exception as e:
        logger.error(f"WebSocket bridge error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    logger.info("Starting WebSocket Bridge Fix Verification")
    logger.info("=" * 50)
    
    tests_passed = 0
    tests_total = 3
    
    # Run tests
    if test_imports():
        tests_passed += 1
        
    if test_dictation_init():
        tests_passed += 1
        
    if test_websocket_bridge():
        tests_passed += 1
        
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        logger.info("✓ All tests passed! WebSocket bridge should work now.")
        return 0
    else:
        logger.error("✗ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())