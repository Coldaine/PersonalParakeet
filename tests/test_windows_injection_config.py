"""Test suite for Windows injection strategies with configuration"""

import unittest
import time
from unittest.mock import patch, MagicMock, call
from personalparakeet.config import InjectionConfig
from personalparakeet.windows_injection import (
    WindowsUIAutomationStrategy,
    WindowsKeyboardStrategy,
    WindowsClipboardStrategy,
    WindowsSendInputStrategy
)
from personalparakeet.text_injection import ApplicationInfo


class TestWindowsStrategiesWithConfig(unittest.TestCase):
    """Test that all Windows strategies properly use InjectionConfig"""
    
    def setUp(self):
        """Set up test environment"""
        self.custom_config = InjectionConfig(
            default_key_delay=0.02,
            focus_acquisition_delay=0.15,
            clipboard_paste_delay=0.25
        )
        self.app_info = ApplicationInfo(
            process_name="notepad.exe",
            window_title="Untitled - Notepad",
            window_class="Notepad"
        )
        
    def test_ui_automation_strategy_accepts_config(self):
        """Test WindowsUIAutomationStrategy accepts config parameter"""
        strategy = WindowsUIAutomationStrategy(config=self.custom_config)
        self.assertEqual(strategy.config, self.custom_config)
        
    def test_ui_automation_strategy_default_config(self):
        """Test WindowsUIAutomationStrategy uses default config when none provided"""
        strategy = WindowsUIAutomationStrategy()
        self.assertIsInstance(strategy.config, InjectionConfig)
        self.assertEqual(strategy.config.default_key_delay, 0.005)  # Default value
        
    @patch('keyboard.write')
    @patch('time.sleep')
    def test_keyboard_strategy_uses_config_delay(self, mock_sleep, mock_write):
        """Test WindowsKeyboardStrategy uses config focus delay"""
        strategy = WindowsKeyboardStrategy(config=self.custom_config)
        strategy.inject("test text", self.app_info)
        
        # Should use custom focus acquisition delay
        mock_sleep.assert_called_with(0.15)
        mock_write.assert_called_once_with("test text ")
        
    @patch('keyboard.write')
    @patch('time.sleep')
    def test_keyboard_strategy_default_delay(self, mock_sleep, mock_write):
        """Test WindowsKeyboardStrategy uses default delay when no config"""
        strategy = WindowsKeyboardStrategy()
        strategy.inject("test text", self.app_info)
        
        # Should use default focus acquisition delay
        mock_sleep.assert_called_with(0.05)
        
    @patch('win32clipboard.OpenClipboard')
    @patch('win32clipboard.EmptyClipboard')
    @patch('win32clipboard.SetClipboardText')
    @patch('win32clipboard.CloseClipboard')
    @patch('keyboard.send')
    @patch('time.sleep')
    def test_clipboard_strategy_uses_config_delay(self, mock_sleep, mock_send, 
                                                 mock_close, mock_set, mock_empty, mock_open):
        """Test WindowsClipboardStrategy uses config clipboard delay"""
        strategy = WindowsClipboardStrategy(config=self.custom_config)
        
        # Mock clipboard manager
        with patch.object(strategy, 'clipboard_manager') as mock_manager:
            mock_manager.save_clipboard.return_value = "old content"
            mock_manager.restore_clipboard.return_value = True
            
            strategy.inject("test text", self.app_info)
            
            # Should use custom clipboard paste delay
            self.assertIn(call(0.25), mock_sleep.call_args_list)
            
    @patch('win32clipboard.OpenClipboard')
    @patch('keyboard.send')
    @patch('time.sleep')
    def test_clipboard_strategy_default_delay(self, mock_sleep, mock_send, mock_open):
        """Test WindowsClipboardStrategy uses default delay when no config"""
        strategy = WindowsClipboardStrategy()
        
        with patch.object(strategy, 'clipboard_manager') as mock_manager:
            mock_manager.save_clipboard.return_value = "old"
            mock_manager.restore_clipboard.return_value = True
            
            strategy.inject("test", self.app_info)
            
            # Should use default clipboard paste delay
            self.assertIn(call(0.1), mock_sleep.call_args_list)
            
    def test_sendinput_strategy_accepts_config(self):
        """Test WindowsSendInputStrategy accepts config parameter"""
        strategy = WindowsSendInputStrategy(config=self.custom_config)
        self.assertEqual(strategy.config, self.custom_config)
        
    @patch('ctypes.windll.user32.SendInput')
    @patch('time.sleep')
    def test_sendinput_strategy_uses_config_delays(self, mock_sleep, mock_sendinput):
        """Test WindowsSendInputStrategy uses both focus and key delays from config"""
        strategy = WindowsSendInputStrategy(config=self.custom_config)
        
        # Mock successful SendInput
        mock_sendinput.return_value = 1
        
        # Inject single character to test
        strategy.inject("a", self.app_info)
        
        # Check sleep calls
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        
        # Should have focus acquisition delay first
        self.assertIn(0.15, sleep_calls)
        # Should have key delays between key down and up
        self.assertIn(0.02, sleep_calls)
        
    @patch('ctypes.windll.user32.SendInput')
    @patch('time.sleep')
    def test_sendinput_strategy_default_delays(self, mock_sleep, mock_sendinput):
        """Test WindowsSendInputStrategy uses default delays when no config"""
        strategy = WindowsSendInputStrategy()
        
        mock_sendinput.return_value = 1
        strategy.inject("a", self.app_info)
        
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        
        # Should use default delays
        self.assertIn(0.05, sleep_calls)  # focus acquisition
        self.assertIn(0.005, sleep_calls)  # key delay
        
    def test_all_strategies_config_immutable(self):
        """Test that config remains immutable across all strategies"""
        strategies = [
            WindowsUIAutomationStrategy(config=self.custom_config),
            WindowsKeyboardStrategy(config=self.custom_config),
            WindowsClipboardStrategy(config=self.custom_config),
            WindowsSendInputStrategy(config=self.custom_config)
        ]
        
        for strategy in strategies:
            # All should have the same config instance
            self.assertEqual(strategy.config, self.custom_config)
            
            # Config should be frozen (immutable)
            with self.assertRaises(Exception):  # FrozenInstanceError
                strategy.config.default_key_delay = 0.1
                
    def test_strategies_inheritance(self):
        """Test all strategies inherit from TextInjectionStrategy"""
        from personalparakeet.text_injection import TextInjectionStrategy
        
        strategies = [
            WindowsUIAutomationStrategy,
            WindowsKeyboardStrategy,
            WindowsClipboardStrategy,
            WindowsSendInputStrategy
        ]
        
        for strategy_class in strategies:
            self.assertTrue(issubclass(strategy_class, TextInjectionStrategy))
            
    @patch('keyboard.write')
    def test_config_affects_behavior(self):
        """Test that different configs actually change behavior"""
        fast_config = InjectionConfig(focus_acquisition_delay=0.01)
        slow_config = InjectionConfig(focus_acquisition_delay=0.5)
        
        fast_strategy = WindowsKeyboardStrategy(config=fast_config)
        slow_strategy = WindowsKeyboardStrategy(config=slow_config)
        
        with patch('time.sleep') as mock_sleep:
            fast_strategy.inject("test", self.app_info)
            fast_sleep_time = mock_sleep.call_args[0][0]
            
        with patch('time.sleep') as mock_sleep:
            slow_strategy.inject("test", self.app_info)
            slow_sleep_time = mock_sleep.call_args[0][0]
            
        # Slow strategy should have longer delay
        self.assertGreater(slow_sleep_time, fast_sleep_time)
        self.assertEqual(fast_sleep_time, 0.01)
        self.assertEqual(slow_sleep_time, 0.5)


if __name__ == '__main__':
    unittest.main()