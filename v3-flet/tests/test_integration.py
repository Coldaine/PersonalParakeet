#!/usr/bin/env python3
"""
Integration Tests for PersonalParakeet v3
Tests end-to-end functionality without requiring user interaction
"""

import sys
import asyncio
import logging
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import flet as ft
from main import PersonalParakeetV3
from config import V3Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationTest:
    """Integration test suite for PersonalParakeet v3"""
    
    def __init__(self):
        self.test_results = {
            'app_initialization': False,
            'component_integration': False,
            'ui_creation': False,
            'audio_pipeline_integration': False,
            'cleanup_integration': False,
            'total_errors': 0
        }
        self.app = None
        self.mock_page = None
    
    def create_mock_page(self):
        """Create a mock Flet page for testing"""
        mock_page = Mock(spec=ft.Page)
        
        # Configure page properties
        mock_page.window_always_on_top = True
        mock_page.window_frameless = True
        mock_page.window_resizable = False
        mock_page.window_width = 450
        mock_page.window_height = 350
        mock_page.window_min_width = 450
        mock_page.window_max_width = 450
        mock_page.window_min_height = 350
        mock_page.window_max_height = 350
        mock_page.window_opacity = 0.95
        mock_page.bgcolor = ft.Colors.TRANSPARENT
        mock_page.theme_mode = ft.ThemeMode.DARK
        mock_page.title = "PersonalParakeet v3"
        
        # Mock methods
        mock_page.add = Mock()
        mock_page.update_async = AsyncMock()
        mock_page.window_destroy = Mock()
        mock_page.on_window_event = None
        
        return mock_page
    
    async def test_app_initialization(self):
        """Test PersonalParakeetV3 app initialization"""
        try:
            logger.info("Testing app initialization...")
            
            self.app = PersonalParakeetV3()
            self.mock_page = self.create_mock_page()
            
            # Mock all hardware dependencies
            with patch('sounddevice.query_devices'), \
                 patch('sounddevice.default'), \
                 patch('torch.cuda.is_available', return_value=True), \
                 patch('asyncio.get_event_loop') as mock_loop:
                
                mock_loop.return_value = asyncio.get_event_loop()
                
                # Initialize app
                await self.app.initialize(self.mock_page)
                
                # Verify components were created
                assert self.app.audio_engine is not None
                assert self.app.dictation_view is not None
                assert self.app.injection_manager is not None
                assert self.app.is_running == True
                
                logger.info("✓ App initialization successful")
                self.test_results['app_initialization'] = True
                return True
                
        except Exception as e:
            logger.error(f"✗ App initialization error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    async def test_component_integration(self):
        """Test integration between components"""
        try:
            logger.info("Testing component integration...")
            
            if not self.app:
                logger.warning("Skipping - app not initialized")
                return False
            
            # Test that components can communicate
            assert hasattr(self.app.dictation_view, 'audio_engine')
            assert hasattr(self.app.dictation_view, 'injection_manager')
            assert hasattr(self.app.dictation_view, 'config')
            
            # Test audio engine components
            assert self.app.audio_engine.stt_processor is not None
            assert self.app.audio_engine.clarity_engine is not None
            assert self.app.audio_engine.vad_engine is not None
            
            logger.info("✓ Component integration successful")
            self.test_results['component_integration'] = True
            return True
            
        except Exception as e:
            logger.error(f"✗ Component integration error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    async def test_ui_creation(self):
        """Test UI component creation"""
        try:
            logger.info("Testing UI creation...")
            
            if not self.app or not self.app.dictation_view:
                logger.warning("Skipping - dictation view not initialized")
                return False
            
            # Test UI building
            ui_container = self.app.dictation_view.build()
            assert ui_container is not None
            
            # Verify page.add was called
            self.mock_page.add.assert_called_once()
            
            logger.info("✓ UI creation successful")
            self.test_results['ui_creation'] = True
            return True
            
        except Exception as e:
            logger.error(f"✗ UI creation error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    async def test_audio_pipeline_integration(self):
        """Test audio pipeline integration with UI"""
        try:
            logger.info("Testing audio pipeline integration...")
            
            if not self.app or not self.app.audio_engine:
                logger.warning("Skipping - audio engine not initialized")
                return False
            
            # Mock transcription update
            mock_transcription = "Integration test transcription"
            
            # Test that dictation view can receive updates
            if hasattr(self.app.dictation_view, 'update_transcription'):
                await self.app.dictation_view.update_transcription(mock_transcription)
            
            # Test that audio engine can process data
            assert self.app.audio_engine.is_running == True
            
            logger.info("✓ Audio pipeline integration successful")
            self.test_results['audio_pipeline_integration'] = True
            return True
            
        except Exception as e:
            logger.error(f"✗ Audio pipeline integration error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    async def test_cleanup_integration(self):
        """Test integrated cleanup"""
        try:
            logger.info("Testing cleanup integration...")
            
            if not self.app:
                logger.warning("Skipping - app not initialized")
                return False
            
            # Test shutdown
            await self.app.shutdown()
            
            # Verify shutdown state
            assert self.app.is_running == False
            
            logger.info("✓ Cleanup integration successful")
            self.test_results['cleanup_integration'] = True
            return True
            
        except Exception as e:
            logger.error(f"✗ Cleanup integration error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    async def run_test(self):
        """Run all integration tests"""
        logger.info("=== PersonalParakeet v3 Integration Test ===")
        
        # Run tests in order
        await self.test_app_initialization()
        await self.test_component_integration()
        await self.test_ui_creation()
        await self.test_audio_pipeline_integration()
        await self.test_cleanup_integration()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        logger.info("=== INTEGRATION TEST RESULTS ===")
        
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
        
        logger.info(f"Total errors: {self.test_results['total_errors']}")
        logger.info(f"Tests passed: {len(passed_tests)}/{len(passed_tests) + len(failed_tests)}")
        
        if len(failed_tests) == 0:
            logger.info("🎉 OVERALL: INTEGRATION TEST PASSED")
            overall_result = "PASS"
        else:
            logger.error("❌ OVERALL: INTEGRATION TEST FAILED")
            overall_result = "FAIL"
        
        return {
            'overall_result': overall_result,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'total_errors': self.test_results['total_errors']
        }


if __name__ == "__main__":
    async def main():
        test = IntegrationTest()
        results = await test.run_test()
        
        exit_code = 0 if results['overall_result'] == 'PASS' else 1
        sys.exit(exit_code)
    
    asyncio.run(main())