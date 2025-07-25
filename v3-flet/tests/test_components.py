#!/usr/bin/env python3
"""
Component Import Test for PersonalParakeet v3
Tests that all components can be imported without errors
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComponentImportTest:
    """Test component imports"""
    
    def __init__(self):
        self.test_results = {
            'core_imports': False,
            'ui_imports': False,
            'config_imports': False,
            'flet_imports': False,
            'total_errors': 0
        }
    
    def test_flet_imports(self):
        """Test Flet framework imports"""
        try:
            logger.info("Testing Flet imports...")
            import flet as ft
            
            # Test specific Flet components we use
            test_components = [
                ft.Colors.BLUE_500,
                ft.Icons.MIC,
                ft.Text("test"),
                ft.Container(),
                ft.Page,
                ft.FLET_APP
            ]
            
            logger.info("✓ Flet imports successful")
            self.test_results['flet_imports'] = True
            return True
            
        except Exception as e:
            logger.error(f"✗ Flet import error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    def test_core_imports(self):
        """Test core component imports"""
        try:
            logger.info("Testing core component imports...")
            
            from core.stt_processor import STTProcessor
            from core.clarity_engine import ClarityEngine
            from core.vad_engine import VoiceActivityDetector
            
            logger.info("✓ Core component imports successful")
            self.test_results['core_imports'] = True
            return True
            
        except Exception as e:
            logger.error(f"✗ Core import error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    def test_ui_imports(self):
        """Test UI component imports"""
        try:
            logger.info("Testing UI component imports...")
            
            from ui.dictation_view import DictationView
            from ui.components import StatusIndicator, ControlPanel, ConfidenceBar
            from ui.theme import get_dictation_theme
            
            logger.info("✓ UI component imports successful")
            self.test_results['ui_imports'] = True
            return True
            
        except Exception as e:
            logger.error(f"✗ UI import error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    def test_config_imports(self):
        """Test config imports"""
        try:
            logger.info("Testing config imports...")
            
            from config import V3Config
            
            logger.info("✓ Config imports successful")
            self.test_results['config_imports'] = True
            return True
            
        except Exception as e:
            logger.error(f"✗ Config import error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    def run_test(self):
        """Run all import tests"""
        logger.info("=== PersonalParakeet v3 Component Import Test ===")
        
        # Run tests in dependency order
        self.test_flet_imports()
        self.test_config_imports()
        self.test_core_imports()
        self.test_ui_imports()
        
        # Generate report
        return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        logger.info("=== IMPORT TEST RESULTS ===")
        
        passed_tests = []
        failed_tests = []
        
        for test_name, result in self.test_results.items():
            if test_name == 'total_errors':
                continue
                
            if result:
                passed_tests.append(test_name)
                logger.info(f"✓ {test_name}: PASS")
            else:
                failed_tests.append(test_name)
                logger.error(f"✗ {test_name}: FAIL")
        
        logger.info(f"Total import errors: {self.test_results['total_errors']}")
        logger.info(f"Tests passed: {len(passed_tests)}/{len(passed_tests) + len(failed_tests)}")
        
        if self.test_results['total_errors'] == 0 and len(failed_tests) == 0:
            logger.info("🎉 OVERALL: IMPORT TEST PASSED")
            overall_result = "PASS"
        else:
            logger.error("❌ OVERALL: IMPORT TEST FAILED")
            overall_result = "FAIL"
        
        return {
            'overall_result': overall_result,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'total_errors': self.test_results['total_errors']
        }


if __name__ == "__main__":
    test = ComponentImportTest()
    results = test.run_test()
    
    exit_code = 0 if results['overall_result'] == 'PASS' else 1
    sys.exit(exit_code)