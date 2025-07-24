#!/usr/bin/env python3
"""
Quick Test - Verify PersonalParakeet v3 can initialize without crashes
"""

import sys
import time
import logging
from pathlib import Path

# Setup simple logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all components can be imported"""
    logger.info("Testing imports...")
    
    try:
        # Test Flet import
        import flet as ft
        logger.info("- Flet: OK")
        
        # Test config import
        from config import V3Config
        logger.info("- Config: OK")
        
        # Test core imports
        from core.stt_processor import STTProcessor
        from core.clarity_engine import ClarityEngine
        logger.info("- Core components: OK")
        
        # Test UI imports
        from ui.dictation_view import DictationView
        from ui.components import StatusIndicator
        logger.info("- UI components: OK")
        
        return True
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        return False

def test_basic_initialization():
    """Test basic component initialization"""
    logger.info("Testing basic initialization...")
    
    try:
        from config import V3Config
        from core.stt_processor import STTProcessor
        from core.clarity_engine import ClarityEngine
        
        # Test config creation
        config = V3Config()
        logger.info("- Config created: OK")
        
        # Test STT processor creation (without model loading)
        stt = STTProcessor(config)
        logger.info("- STT processor created: OK")
        
        # Test Clarity Engine creation
        clarity = ClarityEngine(config)
        logger.info("- Clarity engine created: OK")
        
        return True
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return False

def test_ui_creation():
    """Test UI components can be created"""
    logger.info("Testing UI creation...")
    
    try:
        import flet as ft
        from ui.components import StatusIndicator, ControlPanel, ConfidenceBar
        
        # Create mock components
        status = StatusIndicator(True, False)
        logger.info("- Status indicator: OK")
        
        confidence = ConfidenceBar(0.85)
        logger.info("- Confidence bar: OK")
        
        return True
        
    except Exception as e:
        logger.error(f"UI creation failed: {e}")
        return False

def main():
    """Run quick tests"""
    print("=" * 50)
    print("PersonalParakeet v3 Quick Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Initialization Test", test_basic_initialization),
        ("UI Creation Test", test_ui_creation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                logger.info(f"PASS: {test_name}")
                passed += 1
            else:
                logger.error(f"FAIL: {test_name}")
                failed += 1
        except Exception as e:
            logger.error(f"FAIL: {test_name} - {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("Status: Code appears functional (basic tests passed)")
        return True
    else:
        print("Status: Code has issues that prevent basic functionality")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)