"""Integration tests for the text injection system"""

import unittest
from unittest.mock import patch, MagicMock, call
from personalparakeet.text_injection import TextInjectionManager, ApplicationInfo
from personalparakeet.config import InjectionConfig
from personalparakeet.text_injection import Platform


class TestTextInjectionIntegration(unittest.TestCase):
    """Integration tests for the complete text injection flow"""
    
    def setUp(self):
        """Set up test environment"""
        self.custom_config = InjectionConfig(
            default_key_delay=0.01,
            focus_acquisition_delay=0.1,
            clipboard_paste_delay=0.2
        )
        
    @patch('platform.system')
    def test_manager_initialization_windows(self, mock_platform):
        """Test TextInjectionManager initialization on Windows"""
        mock_platform.return_value = 'Windows'
        
        manager = TextInjectionManager(config=self.custom_config)
        
        self.assertEqual(manager.platform_info.platform, Platform.WINDOWS)
        self.assertEqual(manager.config, self.custom_config)
        self.assertIsNotNone(manager.strategies)
        
    @patch('platform.system')
    def test_manager_initialization_linux(self, mock_platform):
        """Test TextInjectionManager initialization on Linux"""
        mock_platform.return_value = 'Linux'
        
        manager = TextInjectionManager(config=self.custom_config)
        
        self.assertEqual(manager.platform_info.platform, Platform.LINUX)
        self.assertEqual(manager.config, self.custom_config)
        
    @patch('platform.system')
    @patch('subprocess.run')
    def test_inject_text_tries_strategies_in_order(self, mock_run, mock_platform):
        """Test that inject_text tries strategies in the correct order"""
        mock_platform.return_value = 'Windows'
        manager = TextInjectionManager()
        
        # Mock all strategies to fail except the last one
        with patch.object(manager, 'strategies') as mock_strategies:
            strategy1 = MagicMock()
            strategy1.name = "Strategy1"
            strategy1.is_available.return_value = True
            strategy1.inject.return_value = False
            
            strategy2 = MagicMock()
            strategy2.name = "Strategy2"
            strategy2.is_available.return_value = True
            strategy2.inject.return_value = False
            
            strategy3 = MagicMock()
            strategy3.name = "Strategy3"
            strategy3.is_available.return_value = True
            strategy3.inject.return_value = True  # This one succeeds
            
            mock_strategies.values.return_value = [strategy1, strategy2, strategy3]
            
            result = manager.inject_text("test text")
            
            # Should have tried all strategies in order
            strategy1.inject.assert_called_once_with("test text ", None)
            strategy2.inject.assert_called_once_with("test text ", None)
            strategy3.inject.assert_called_once_with("test text ", None)
            
            self.assertTrue(result)
            
    @patch('platform.system')
    def test_inject_text_skips_unavailable_strategies(self, mock_platform):
        """Test that unavailable strategies are skipped"""
        mock_platform.return_value = 'Windows'
        manager = TextInjectionManager()
        
        with patch.object(manager, 'strategies') as mock_strategies:
            strategy1 = MagicMock()
            strategy1.is_available.return_value = False  # Not available
            strategy1.inject.return_value = False
            
            strategy2 = MagicMock()
            strategy2.is_available.return_value = True
            strategy2.inject.return_value = True
            
            mock_strategies.values.return_value = [strategy1, strategy2]
            
            result = manager.inject_text("test")
            
            # Should not have called inject on unavailable strategy
            strategy1.inject.assert_not_called()
            strategy2.inject.assert_called_once()
            
            self.assertTrue(result)
            
    @patch('platform.system')
    def test_inject_text_with_app_info(self, mock_platform):
        """Test injection with ApplicationInfo"""
        mock_platform.return_value = 'Windows'
        manager = TextInjectionManager()
        
        app_info = ApplicationInfo(
            process_name="notepad.exe",
            window_title="Test Document",
            window_class="Notepad"
        )
        
        with patch.object(manager, 'strategies') as mock_strategies:
            strategy = MagicMock()
            strategy.is_available.return_value = True
            strategy.inject.return_value = True
            mock_strategies.values.return_value = [strategy]
            
            result = manager.inject_text("test", app_info)
            
            # Should pass app_info to strategy
            strategy.inject.assert_called_once_with("test ", app_info)
            self.assertTrue(result)
            
    @patch('platform.system')
    def test_inject_text_all_strategies_fail(self, mock_platform):
        """Test when all injection strategies fail"""
        mock_platform.return_value = 'Windows'
        manager = TextInjectionManager()
        
        with patch.object(manager, 'strategies') as mock_strategies:
            strategy1 = MagicMock()
            strategy1.is_available.return_value = True
            strategy1.inject.return_value = False
            
            strategy2 = MagicMock()
            strategy2.is_available.return_value = True
            strategy2.inject.return_value = False
            
            mock_strategies.values.return_value = [strategy1, strategy2]
            
            result = manager.inject_text("test")
            
            self.assertFalse(result)
            
    @patch('platform.system')
    def test_config_propagates_to_strategies(self, mock_platform):
        """Test that custom config propagates to all strategies"""
        mock_platform.return_value = 'Windows'
        
        # Use real initialization to test config propagation
        manager = TextInjectionManager(config=self.custom_config)
        
        # Check that strategies received the custom config
        for strategy in manager.strategies.values():
            if hasattr(strategy, 'config'):
                self.assertEqual(strategy.config, self.custom_config)
                
    @patch('platform.system')
    def test_strategy_order_methods(self, mock_platform):
        """Test the refactored strategy order methods"""
        mock_platform.return_value = 'Windows'
        manager = TextInjectionManager()
        
        # Test Windows strategy order
        windows_order = manager._get_windows_strategy_order(None)
        self.assertIsInstance(windows_order, list)
        self.assertIn('windows_ui_automation', windows_order)
        
        # Test with specific app
        app_info = ApplicationInfo(process_name="terminal.exe")
        terminal_order = manager._get_windows_strategy_order(app_info)
        # Terminal apps might have different order
        self.assertIsInstance(terminal_order, list)
        
    @patch('platform.system')
    @patch('subprocess.run')
    def test_linux_kde_detection(self, mock_run, mock_platform):
        """Test KDE detection on Linux"""
        mock_platform.return_value = 'Linux'
        
        # Mock successful KDE detection
        mock_run.return_value = MagicMock(returncode=0)
        
        manager = TextInjectionManager()
        
        # Should have tried to detect KDE
        mock_run.assert_called()
        
    @patch('platform.system')
    def test_inject_empty_text(self, mock_platform):
        """Test injecting empty text"""
        mock_platform.return_value = 'Windows'
        manager = TextInjectionManager()
        
        with patch.object(manager, 'strategies') as mock_strategies:
            strategy = MagicMock()
            strategy.is_available.return_value = True
            strategy.inject.return_value = True
            mock_strategies.values.return_value = [strategy]
            
            result = manager.inject_text("")
            
            # Should still add space
            strategy.inject.assert_called_once_with(" ", None)
            
    @patch('platform.system')
    def test_inject_text_with_special_characters(self, mock_platform):
        """Test injecting text with special characters"""
        mock_platform.return_value = 'Windows'
        manager = TextInjectionManager()
        
        special_text = "Hello\nWorld\t@#$%"
        
        with patch.object(manager, 'strategies') as mock_strategies:
            strategy = MagicMock()
            strategy.is_available.return_value = True
            strategy.inject.return_value = True
            mock_strategies.values.return_value = [strategy]
            
            result = manager.inject_text(special_text)
            
            strategy.inject.assert_called_once_with(special_text + " ", None)
            self.assertTrue(result)
            
    @patch('platform.system')
    def test_logging_integration(self, mock_platform):
        """Test that logging is properly integrated"""
        mock_platform.return_value = 'Windows'
        
        with patch('personalparakeet.text_injection.logger') as mock_logger:
            manager = TextInjectionManager()
            
            # Should log initialization
            mock_logger.info.assert_called()
            
            # Test injection with logging
            with patch.object(manager, 'strategies') as mock_strategies:
                strategy = MagicMock()
                strategy.name = "TestStrategy"
                strategy.is_available.return_value = True
                strategy.inject.return_value = True
                mock_strategies.values.return_value = [strategy]
                
                manager.inject_text("test")
                
                # Should log success
                success_calls = [call for call in mock_logger.info.call_args_list 
                               if "Success" in str(call) or "success" in str(call)]
                self.assertGreater(len(success_calls), 0)


if __name__ == '__main__':
    unittest.main()