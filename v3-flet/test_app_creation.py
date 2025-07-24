#!/usr/bin/env python3
"""
Test Application Creation - Verify PersonalParakeet v3 main class can be created
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_app_creation():
    """Test that the main application class can be created"""
    logger.info("Testing PersonalParakeet v3 application creation...")
    
    try:
        # Import the main application class
        from main import PersonalParakeetV3
        
        # Create the application instance
        app = PersonalParakeetV3()
        logger.info("- Application instance created: OK")
        
        # Verify basic attributes exist
        assert hasattr(app, 'config'), "Missing config attribute"
        assert hasattr(app, 'audio_engine'), "Missing audio_engine attribute" 
        assert hasattr(app, 'dictation_view'), "Missing dictation_view attribute"
        assert hasattr(app, 'is_running'), "Missing is_running attribute"
        logger.info("- Required attributes present: OK")
        
        # Check initial state
        assert app.is_running == False, "Should start in not running state"
        assert app.audio_engine is None, "Audio engine should be None initially"
        logger.info("- Initial state correct: OK")
        
        logger.info("SUCCESS: Application can be created without errors")
        return True
        
    except Exception as e:
        logger.error(f"Application creation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("PersonalParakeet v3 Application Creation Test")
    print("=" * 50)
    
    success = test_app_creation()
    
    if success:
        print("RESULT: Application class creation works correctly")
    else:
        print("RESULT: Application class has creation issues")
    
    sys.exit(0 if success else 1)