"""Unit tests for the enhanced dictation system"""

import unittest
import sys
from unittest.mock import Mock, patch, MagicMock

# Mock nemo module before importing dictation
sys.modules['nemo'] = MagicMock()
sys.modules['nemo.collections'] = MagicMock()
sys.modules['nemo.collections.asr'] = MagicMock()

from personalparakeet.dictation_enhanced import EnhancedDictationSystem
from personalparakeet.text_injection_enhanced import InjectionResult
from personalparakeet.config import InjectionConfig


class TestEnhancedDictationSystem(unittest.TestCase):
    """Test cases for the enhanced dictation system"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = InjectionConfig(
            default_key_delay=0.01,
            focus_acquisition_delay=0.1
        )
        
    @patch('personalparakeet.dictation_enhanced.EnhancedTextInjectionManager')
    @patch('personalparakeet.dictation.SimpleDictation.__init__')
    def test_initialization(self, mock_base_init, mock_injection_manager):
        """Test EnhancedDictationSystem initialization"""
        mock_base_init.return_value = None
        
        # Create system
        system = EnhancedDictationSystem(config=self.config)
        
        # Verify injection manager was created with config
        mock_injection_manager.assert_called_once_with(self.config)
        
        # Verify base class was initialized
        mock_base_init.assert_called_once_with("nvidia/parakeet-tdt-1.1b", None)
        
        # Verify statistics initialization
        self.assertEqual(system.injection_stats['total_injections'], 0)
        self.assertEqual(system.injection_stats['successful_injections'], 0)
        self.assertEqual(system.injection_stats['failed_injections'], 0)
        self.assertEqual(system.injection_stats['strategy_usage'], {})
        
    @patch('personalparakeet.dictation_enhanced.EnhancedTextInjectionManager')
    @patch('personalparakeet.dictation.SimpleDictation.__init__')
    def test_enhanced_text_output_success(self, mock_base_init, mock_injection_manager):
        """Test successful text output with injection"""
        mock_base_init.return_value = None
        
        # Create mock injection manager
        mock_manager_instance = Mock()
        mock_injection_manager.return_value = mock_manager_instance
        
        # Mock successful injection result
        mock_result = InjectionResult(
            success=True,
            strategy_used='keyboard',
            time_taken=0.123,
            error_message=None
        )
        mock_manager_instance.inject_text.return_value = mock_result
        
        # Create system and mock processor
        system = EnhancedDictationSystem()
        system.processor = Mock()
        
        # Test text output
        test_text = "Hello world"
        system._enhanced_text_output(test_text)
        
        # Verify injection was called
        mock_manager_instance.inject_text.assert_called_once_with(test_text)
        
        # Verify statistics updated
        self.assertEqual(system.injection_stats['total_injections'], 1)
        self.assertEqual(system.injection_stats['successful_injections'], 1)
        self.assertEqual(system.injection_stats['failed_injections'], 0)
        self.assertEqual(system.injection_stats['strategy_usage']['keyboard'], 1)
        
    @patch('personalparakeet.dictation_enhanced.EnhancedTextInjectionManager')
    @patch('personalparakeet.dictation.SimpleDictation.__init__')
    @patch('builtins.print')
    def test_enhanced_text_output_failure(self, mock_print, mock_base_init, mock_injection_manager):
        """Test failed text output with fallback"""
        mock_base_init.return_value = None
        
        # Create mock injection manager
        mock_manager_instance = Mock()
        mock_injection_manager.return_value = mock_manager_instance
        
        # Mock failed injection result
        mock_result = InjectionResult(
            success=False,
            strategy_used=None,
            time_taken=0.456,
            error_message="All strategies failed"
        )
        mock_manager_instance.inject_text.return_value = mock_result
        
        # Create system and mock processor
        system = EnhancedDictationSystem()
        system.processor = Mock()
        
        # Test text output
        test_text = "Hello world"
        system._enhanced_text_output(test_text)
        
        # Verify injection was called
        mock_manager_instance.inject_text.assert_called_once_with(test_text)
        
        # Verify statistics updated
        self.assertEqual(system.injection_stats['total_injections'], 1)
        self.assertEqual(system.injection_stats['successful_injections'], 0)
        self.assertEqual(system.injection_stats['failed_injections'], 1)
        
        # Verify fallback display was called
        mock_print.assert_called()
        
    @patch('personalparakeet.dictation_enhanced.EnhancedTextInjectionManager')
    @patch('personalparakeet.dictation.SimpleDictation.__init__')
    def test_empty_text_handling(self, mock_base_init, mock_injection_manager):
        """Test handling of empty text"""
        mock_base_init.return_value = None
        
        # Create mock injection manager
        mock_manager_instance = Mock()
        mock_injection_manager.return_value = mock_manager_instance
        
        # Create system and mock processor
        system = EnhancedDictationSystem()
        system.processor = Mock()
        
        # Test with empty text
        system._enhanced_text_output("")
        system._enhanced_text_output("   ")
        
        # Verify injection was NOT called for empty text
        mock_manager_instance.inject_text.assert_not_called()
        
        # Verify statistics not updated
        self.assertEqual(system.injection_stats['total_injections'], 0)
        
    @patch('personalparakeet.dictation_enhanced.EnhancedTextInjectionManager')
    @patch('personalparakeet.dictation.SimpleDictation.__init__')
    def test_get_injection_statistics(self, mock_base_init, mock_injection_manager):
        """Test statistics retrieval"""
        mock_base_init.return_value = None
        
        # Create mock injection manager
        mock_manager_instance = Mock()
        mock_injection_manager.return_value = mock_manager_instance
        
        # Mock performance stats
        mock_performance_stats = {
            'average_time': 0.15,
            'min_time': 0.05,
            'max_time': 0.25
        }
        mock_manager_instance.get_performance_stats.return_value = mock_performance_stats
        
        # Mock available strategies
        mock_strategies = ['keyboard', 'clipboard', 'ui_automation']
        mock_manager_instance.get_available_strategies.return_value = mock_strategies
        
        # Create system
        system = EnhancedDictationSystem()
        system.processor = Mock()
        
        # Set some injection stats
        system.injection_stats = {
            'total_injections': 10,
            'successful_injections': 8,
            'failed_injections': 2,
            'strategy_usage': {'keyboard': 5, 'clipboard': 3}
        }
        
        # Get statistics
        stats = system.get_injection_statistics()
        
        # Verify statistics
        self.assertEqual(stats['total_injections'], 10)
        self.assertEqual(stats['successful_injections'], 8)
        self.assertEqual(stats['failed_injections'], 2)
        self.assertEqual(stats['success_rate'], 0.8)
        self.assertEqual(stats['strategy_performance'], mock_performance_stats)
        self.assertEqual(stats['available_strategies'], mock_strategies)
        
    @patch('personalparakeet.dictation_enhanced.EnhancedTextInjectionManager')
    @patch('personalparakeet.dictation.SimpleDictation.__init__')
    def test_multiple_strategy_usage(self, mock_base_init, mock_injection_manager):
        """Test tracking of multiple strategy usage"""
        mock_base_init.return_value = None
        
        # Create mock injection manager
        mock_manager_instance = Mock()
        mock_injection_manager.return_value = mock_manager_instance
        
        # Create system
        system = EnhancedDictationSystem()
        system.processor = Mock()
        
        # Simulate different strategies being used
        strategies = ['keyboard', 'clipboard', 'keyboard', 'ui_automation', 'keyboard']
        
        for strategy in strategies:
            mock_result = InjectionResult(
                success=True,
                strategy_used=strategy,
                time_taken=0.1,
                error_message=None
            )
            mock_manager_instance.inject_text.return_value = mock_result
            system._enhanced_text_output("test")
        
        # Verify strategy usage counts
        self.assertEqual(system.injection_stats['strategy_usage']['keyboard'], 3)
        self.assertEqual(system.injection_stats['strategy_usage']['clipboard'], 1)
        self.assertEqual(system.injection_stats['strategy_usage']['ui_automation'], 1)
        
    @patch('personalparakeet.dictation_enhanced.EnhancedTextInjectionManager')
    @patch('personalparakeet.dictation.SimpleDictation.__init__')
    @patch('builtins.print')
    def test_fallback_display(self, mock_print, mock_base_init, mock_injection_manager):
        """Test fallback display functionality"""
        mock_base_init.return_value = None
        
        # Create system
        system = EnhancedDictationSystem()
        system.processor = Mock()
        
        # Test fallback display
        test_text = "Failed injection text"
        system._fallback_text_display(test_text)
        
        # Verify output was printed
        mock_print.assert_called()
        print_calls = mock_print.call_args_list
        
        # Should have printed warning and instructions
        self.assertGreater(len(print_calls), 0)
        
        # Check that the text was included in output
        full_output = ' '.join(str(call) for call in print_calls)
        self.assertIn(test_text, full_output)
        
    @patch('personalparakeet.dictation_enhanced.EnhancedTextInjectionManager')
    @patch('personalparakeet.dictation.SimpleDictation.__init__')
    def test_processor_callback_registration(self, mock_base_init, mock_injection_manager):
        """Test that text output callback is properly registered"""
        mock_base_init.return_value = None
        
        # Create mock processor
        mock_processor = Mock()
        
        # Create system
        system = EnhancedDictationSystem()
        system.processor = mock_processor
        
        # Verify callback was set
        mock_processor.set_text_output_callback.assert_called_once_with(system._enhanced_text_output)
        
    @patch('personalparakeet.dictation_enhanced.EnhancedTextInjectionManager')
    @patch('personalparakeet.dictation.SimpleDictation.__init__')
    def test_zero_division_in_statistics(self, mock_base_init, mock_injection_manager):
        """Test that statistics handle zero division correctly"""
        mock_base_init.return_value = None
        
        # Create mock injection manager
        mock_manager_instance = Mock()
        mock_injection_manager.return_value = mock_manager_instance
        mock_manager_instance.get_performance_stats.return_value = {}
        mock_manager_instance.get_available_strategies.return_value = []
        
        # Create system
        system = EnhancedDictationSystem()
        system.processor = Mock()
        
        # Get statistics with no injections
        stats = system.get_injection_statistics()
        
        # Verify success rate is 0 and not division error
        self.assertEqual(stats['success_rate'], 0.0)
        self.assertEqual(stats['total_injections'], 0)


if __name__ == '__main__':
    unittest.main()