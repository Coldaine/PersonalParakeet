"""Unit tests for Windows injection strategies"""

import unittest
import sys
from unittest.mock import Mock, patch, MagicMock, call
from personalparakeet.text_injection import ApplicationInfo, ApplicationType
from personalparakeet.config import InjectionConfig

# Only run these tests on Windows
if sys.platform != 'win32':
    import pytest
    pytestmark = pytest.mark.skip(reason="Windows-specific tests")


class TestWindowsInjectionStrategies(unittest.TestCase):
    """Test cases for Windows-specific injection strategies"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = InjectionConfig(
            default_key_delay=0.01,
            focus_acquisition_delay=0.1
        )
        self.app_info = ApplicationInfo(
            name="Test App",
            process_name="test.exe",
            window_title="Test Window",
            app_type=ApplicationType.EDITOR
        )
        
    @patch('personalparakeet.windows_injection.comtypes.client')
    def test_ui_automation_initialization_success(self, mock_comtypes):
        """Test successful UI Automation initialization"""
        from personalparakeet.windows_injection import WindowsUIAutomationStrategy
        
        # Mock successful COM object creation
        mock_uia = Mock()
        mock_comtypes.CreateObject.return_value = mock_uia
        
        strategy = WindowsUIAutomationStrategy(self.config)
        
        # Verify COM object was created
        mock_comtypes.CreateObject.assert_called_once()
        self.assertIsNotNone(strategy.uia)
        self.assertEqual(strategy.uia, mock_uia)
        
    @patch('personalparakeet.windows_injection.comtypes.client')
    def test_ui_automation_initialization_failure(self, mock_comtypes):
        """Test UI Automation initialization failure handling"""
        from personalparakeet.windows_injection import WindowsUIAutomationStrategy
        
        # Mock COM object creation failure
        mock_comtypes.CreateObject.side_effect = Exception("COM error")
        
        strategy = WindowsUIAutomationStrategy(self.config)
        
        # Should handle error gracefully
        self.assertIsNone(strategy.uia)
        
    @patch('personalparakeet.windows_injection.comtypes.client')
    def test_ui_automation_inject_text_pattern(self, mock_comtypes):
        """Test text injection using TextPattern"""
        from personalparakeet.windows_injection import WindowsUIAutomationStrategy
        
        # Set up mocks
        mock_uia = Mock()
        mock_focused = Mock()
        mock_text_pattern = Mock()
        mock_doc_range = Mock()
        
        mock_comtypes.CreateObject.return_value = mock_uia
        mock_uia.GetFocusedElement.return_value = mock_focused
        mock_focused.GetCurrentPattern.return_value = mock_text_pattern
        mock_text_pattern.DocumentRange = mock_doc_range
        
        strategy = WindowsUIAutomationStrategy(self.config)
        
        # Test injection
        result = strategy.inject("Hello World", self.app_info)
        
        # Verify text was injected
        self.assertTrue(result)
        mock_doc_range.InsertText.assert_called_once_with("Hello World ")
        
    @patch('personalparakeet.windows_injection.comtypes.client')
    def test_ui_automation_inject_value_pattern(self, mock_comtypes):
        """Test text injection using ValuePattern when TextPattern fails"""
        from personalparakeet.windows_injection import WindowsUIAutomationStrategy
        
        # Set up mocks
        mock_uia = Mock()
        mock_focused = Mock()
        mock_value_pattern = Mock()
        
        mock_comtypes.CreateObject.return_value = mock_uia
        mock_uia.GetFocusedElement.return_value = mock_focused
        
        # First call for TextPattern fails, second for ValuePattern succeeds
        mock_focused.GetCurrentPattern.side_effect = [
            Exception("TextPattern not supported"),
            mock_value_pattern
        ]
        
        mock_value_pattern.CurrentValue = "existing text"
        
        strategy = WindowsUIAutomationStrategy(self.config)
        
        # Test injection
        result = strategy.inject("Hello", self.app_info)
        
        # Verify value was set
        self.assertTrue(result)
        mock_value_pattern.SetValue.assert_called_once_with("existing textHello ")
        
    @patch('personalparakeet.windows_injection.keyboard')
    def test_keyboard_strategy_basic(self, mock_keyboard):
        """Test basic keyboard injection strategy"""
        from personalparakeet.windows_injection import WindowsKeyboardStrategy
        
        strategy = WindowsKeyboardStrategy(self.config)
        
        # Test injection
        result = strategy.inject("Hello World", self.app_info)
        
        # Verify keyboard was used
        self.assertTrue(result)
        mock_keyboard.write.assert_called_once_with("Hello World ")
        
    @patch('personalparakeet.windows_injection.keyboard')
    def test_keyboard_strategy_with_newlines(self, mock_keyboard):
        """Test keyboard injection with newline handling"""
        from personalparakeet.windows_injection import WindowsKeyboardStrategy
        
        strategy = WindowsKeyboardStrategy(self.config)
        
        # Test injection with newlines
        text_with_newlines = "Line 1\nLine 2\nLine 3"
        result = strategy.inject(text_with_newlines, self.app_info)
        
        # Should handle newlines properly
        self.assertTrue(result)
        # Verify keyboard.write was called
        mock_keyboard.write.assert_called()
        
    @patch('personalparakeet.windows_injection.win32clipboard')
    @patch('personalparakeet.windows_injection.keyboard')
    def test_clipboard_strategy(self, mock_keyboard, mock_clipboard):
        """Test clipboard injection strategy"""
        from personalparakeet.windows_injection import WindowsClipboardStrategy
        
        # Mock clipboard operations
        mock_clipboard.GetClipboardData.return_value = "old clipboard"
        
        strategy = WindowsClipboardStrategy(self.config)
        
        # Test injection
        result = strategy.inject("Hello World", self.app_info)
        
        # Verify clipboard operations
        self.assertTrue(result)
        mock_clipboard.OpenClipboard.assert_called()
        mock_clipboard.EmptyClipboard.assert_called()
        mock_clipboard.SetClipboardText.assert_called_with("Hello World ")
        mock_clipboard.CloseClipboard.assert_called()
        
        # Verify paste operation
        mock_keyboard.press_and_release.assert_called_with('ctrl+v')
        
    @patch('personalparakeet.windows_injection.ctypes')
    def test_sendinput_strategy(self, mock_ctypes):
        """Test SendInput injection strategy"""
        from personalparakeet.windows_injection import WindowsSendInputStrategy
        
        # Mock ctypes structures and functions
        mock_ctypes.windll.user32.SendInput.return_value = 1
        
        strategy = WindowsSendInputStrategy(self.config)
        
        # Test injection
        result = strategy.inject("A", self.app_info)
        
        # Verify SendInput was called
        self.assertTrue(result)
        mock_ctypes.windll.user32.SendInput.assert_called()
        
    def test_application_specific_strategy_selection(self):
        """Test that strategies are selected based on application type"""
        from personalparakeet.windows_injection import WindowsKeyboardStrategy
        
        strategy = WindowsKeyboardStrategy(self.config)
        
        # Test terminal app detection
        terminal_app = ApplicationInfo(
            name="Terminal",
            process_name="WindowsTerminal.exe",
            window_title="Terminal",
            app_type=ApplicationType.TERMINAL
        )
        
        # Terminal apps should be supported
        self.assertTrue(strategy.is_available())
        
    @patch('personalparakeet.windows_injection_improved.comtypes.client')
    def test_improved_ui_automation_retry(self, mock_comtypes):
        """Test improved UI Automation with retry mechanism"""
        from personalparakeet.windows_injection_improved import ImprovedWindowsUIAutomationStrategy
        
        # Set up mocks
        mock_uia = Mock()
        mock_focused = Mock()
        mock_text_pattern = Mock()
        mock_doc_range = Mock()
        
        mock_comtypes.CreateObject.return_value = mock_uia
        mock_uia.GetFocusedElement.return_value = mock_focused
        mock_focused.GetCurrentPattern.return_value = mock_text_pattern
        mock_text_pattern.DocumentRange = mock_doc_range
        
        # First attempt fails, second succeeds
        mock_doc_range.InsertText.side_effect = [
            Exception("Transient error"),
            None  # Success
        ]
        
        strategy = ImprovedWindowsUIAutomationStrategy(self.config)
        
        # Test injection with retry
        result = strategy.inject("Hello", self.app_info)
        
        # Should succeed after retry
        self.assertTrue(result)
        self.assertEqual(mock_doc_range.InsertText.call_count, 2)
        
    @patch('personalparakeet.windows_injection_improved.keyboard')
    def test_improved_keyboard_chunking(self, mock_keyboard):
        """Test improved keyboard strategy with text chunking"""
        from personalparakeet.windows_injection_improved import ImprovedWindowsKeyboardStrategy
        
        strategy = ImprovedWindowsKeyboardStrategy(self.config)
        
        # Test with long text that should be chunked
        long_text = "A" * 500  # Long text
        result = strategy.inject(long_text, self.app_info)
        
        # Should handle long text
        self.assertTrue(result)
        # Verify keyboard was used (might be multiple calls due to chunking)
        self.assertTrue(mock_keyboard.write.called)
        
    @patch('personalparakeet.windows_injection_improved.win32clipboard')
    @patch('personalparakeet.windows_injection_improved.keyboard')
    def test_improved_clipboard_verification(self, mock_keyboard, mock_clipboard):
        """Test improved clipboard strategy with verification"""
        from personalparakeet.windows_injection_improved import ImprovedWindowsClipboardStrategy
        
        # Mock clipboard operations
        mock_clipboard.GetClipboardData.side_effect = [
            "old content",  # Initial save
            "Hello World ",  # Verification after set
            "old content"   # Restore
        ]
        
        strategy = ImprovedWindowsClipboardStrategy(self.config)
        
        # Test injection
        result = strategy.inject("Hello World", self.app_info)
        
        # Should verify clipboard content
        self.assertTrue(result)
        # Should have multiple GetClipboardData calls for verification
        self.assertGreater(mock_clipboard.GetClipboardData.call_count, 1)
        
    def test_strategy_availability_checks(self):
        """Test strategy availability detection"""
        from personalparakeet.windows_injection import (
            WindowsUIAutomationStrategy,
            WindowsKeyboardStrategy,
            WindowsClipboardStrategy,
            WindowsSendInputStrategy
        )
        
        # All strategies should report as available on Windows
        strategies = [
            WindowsKeyboardStrategy(self.config),
            WindowsClipboardStrategy(self.config),
            WindowsSendInputStrategy(self.config)
        ]
        
        for strategy in strategies:
            self.assertTrue(strategy.is_available(), 
                          f"{strategy.__class__.__name__} should be available on Windows")
            
    @patch('personalparakeet.windows_injection.logger')
    def test_error_logging(self, mock_logger):
        """Test that errors are properly logged"""
        from personalparakeet.windows_injection import WindowsKeyboardStrategy
        
        with patch('personalparakeet.windows_injection.keyboard') as mock_keyboard:
            mock_keyboard.write.side_effect = Exception("Keyboard error")
            
            strategy = WindowsKeyboardStrategy(self.config)
            result = strategy.inject("Test", self.app_info)
            
            # Should fail gracefully
            self.assertFalse(result)
            # Should log error
            mock_logger.error.assert_called()


if __name__ == '__main__':
    unittest.main()