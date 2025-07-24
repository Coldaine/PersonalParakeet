"""Test suite for configuration classes"""

import unittest
from dataclasses import FrozenInstanceError
from personalparakeet.config import InjectionConfig


class TestInjectionConfig(unittest.TestCase):
    """Test cases for InjectionConfig dataclass"""
    
    def test_default_values(self):
        """Test that InjectionConfig has correct default values"""
        config = InjectionConfig()
        
        # Basic timing configuration
        self.assertEqual(config.default_key_delay, 0.01)
        self.assertEqual(config.clipboard_paste_delay, 0.1)
        self.assertEqual(config.strategy_switch_delay, 0.05)
        self.assertEqual(config.focus_acquisition_delay, 0.05)
        
        # Platform-specific delays
        self.assertEqual(config.windows_ui_automation_delay, 0.02)
        self.assertEqual(config.linux_xtest_delay, 0.005)
        self.assertEqual(config.kde_dbus_timeout, 5.0)
        self.assertEqual(config.xdotool_timeout, 5.0)
        
        # Retry configuration
        self.assertEqual(config.max_clipboard_retries, 3)
        self.assertEqual(config.clipboard_retry_delay, 0.1)
        
        # Strategy preferences
        self.assertIsNone(config.preferred_strategy_order)
        self.assertTrue(config.enable_performance_optimization)
        self.assertEqual(config.skip_consecutive_failures, 3)
        
        # Audio configuration
        self.assertIsNone(config.audio_device_index)
        self.assertEqual(config.chunk_duration, 1.0)
        self.assertEqual(config.sample_rate, 16000)
        
        # Monitoring settings
        self.assertTrue(config.enable_monitoring)
        self.assertEqual(config.stats_report_interval, 30)
        self.assertFalse(config.enable_debug_logging)
        
    def test_custom_values(self):
        """Test creating InjectionConfig with custom values"""
        config = InjectionConfig(
            default_key_delay=0.02,
            clipboard_paste_delay=0.2,
            focus_acquisition_delay=0.15,
            xdotool_timeout=10.0,
            max_clipboard_retries=5,
            clipboard_retry_delay=0.2,
            windows_ui_automation_delay=0.03,
            linux_xtest_delay=0.01,
            kde_dbus_timeout=10.0,
            preferred_strategy_order=['clipboard', 'keyboard'],
            enable_performance_optimization=False,
            skip_consecutive_failures=5,
            audio_device_index=1,
            chunk_duration=2.0,
            sample_rate=44100,
            enable_monitoring=False,
            stats_report_interval=60,
            enable_debug_logging=True
        )
        
        self.assertEqual(config.default_key_delay, 0.02)
        self.assertEqual(config.clipboard_paste_delay, 0.2)
        self.assertEqual(config.focus_acquisition_delay, 0.15)
        self.assertEqual(config.xdotool_timeout, 10.0)
        self.assertEqual(config.max_clipboard_retries, 5)
        self.assertEqual(config.clipboard_retry_delay, 0.2)
        self.assertEqual(config.windows_ui_automation_delay, 0.03)
        self.assertEqual(config.linux_xtest_delay, 0.01)
        self.assertEqual(config.kde_dbus_timeout, 10.0)
        self.assertEqual(config.preferred_strategy_order, ['clipboard', 'keyboard'])
        self.assertFalse(config.enable_performance_optimization)
        self.assertEqual(config.skip_consecutive_failures, 5)
        self.assertEqual(config.audio_device_index, 1)
        self.assertEqual(config.chunk_duration, 2.0)
        self.assertEqual(config.sample_rate, 44100)
        self.assertFalse(config.enable_monitoring)
        self.assertEqual(config.stats_report_interval, 60)
        self.assertTrue(config.enable_debug_logging)
        
    def test_from_dict(self):
        """Test creating InjectionConfig from dictionary"""
        config_dict = {
            'default_key_delay': 0.05,
            'clipboard_paste_delay': 0.3,
            'sample_rate': 22050,
            'enable_debug_logging': True,
            'unknown_field': 'should_be_ignored'  # This should be filtered out
        }
        
        config = InjectionConfig.from_dict(config_dict)
        
        # Custom values from dict
        self.assertEqual(config.default_key_delay, 0.05)
        self.assertEqual(config.clipboard_paste_delay, 0.3)
        self.assertEqual(config.sample_rate, 22050)
        self.assertTrue(config.enable_debug_logging)
        
        # Default values for non-specified fields
        self.assertEqual(config.focus_acquisition_delay, 0.05)
        self.assertEqual(config.chunk_duration, 1.0)
        
        # Ensure unknown fields don't exist
        self.assertFalse(hasattr(config, 'unknown_field'))
        
    def test_to_dict(self):
        """Test converting InjectionConfig to dictionary"""
        config = InjectionConfig(
            default_key_delay=0.02,
            sample_rate=48000,
            preferred_strategy_order=['ui_automation', 'clipboard']
        )
        
        config_dict = config.to_dict()
        
        # Check that dictionary contains all fields
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict['default_key_delay'], 0.02)
        self.assertEqual(config_dict['sample_rate'], 48000)
        self.assertEqual(config_dict['preferred_strategy_order'], ['ui_automation', 'clipboard'])
        
        # Check that default values are included
        self.assertEqual(config_dict['clipboard_paste_delay'], 0.1)
        self.assertEqual(config_dict['chunk_duration'], 1.0)
        
    def test_validate_valid_config(self):
        """Test validation of valid configuration"""
        config = InjectionConfig()
        self.assertTrue(config.validate())
        
        # Test with custom valid values
        config2 = InjectionConfig(
            default_key_delay=0.5,
            clipboard_paste_delay=3.0,
            sample_rate=44100,
            chunk_duration=5.0,
            max_clipboard_retries=5
        )
        self.assertTrue(config2.validate())
        
    def test_validate_invalid_key_delay(self):
        """Test validation fails for invalid key delay"""
        # Test delay too high
        config = InjectionConfig(default_key_delay=1.5)
        self.assertFalse(config.validate())
        
        # Test negative delay
        config = InjectionConfig(default_key_delay=-0.1)
        self.assertFalse(config.validate())
        
    def test_validate_invalid_clipboard_delay(self):
        """Test validation fails for invalid clipboard delay"""
        # Test delay too high
        config = InjectionConfig(clipboard_paste_delay=6.0)
        self.assertFalse(config.validate())
        
        # Test negative delay
        config = InjectionConfig(clipboard_paste_delay=-0.5)
        self.assertFalse(config.validate())
        
    def test_validate_invalid_sample_rate(self):
        """Test validation fails for non-standard sample rate"""
        config = InjectionConfig(sample_rate=12345)  # Non-standard rate
        self.assertFalse(config.validate())
        
    def test_validate_invalid_chunk_duration(self):
        """Test validation fails for invalid chunk duration"""
        # Test duration too small
        config = InjectionConfig(chunk_duration=0.05)
        self.assertFalse(config.validate())
        
        # Test duration too large
        config = InjectionConfig(chunk_duration=15.0)
        self.assertFalse(config.validate())
        
    def test_validate_invalid_clipboard_retries(self):
        """Test validation fails for invalid clipboard retries"""
        # Test retries too small
        config = InjectionConfig(max_clipboard_retries=0)
        self.assertFalse(config.validate())
        
        # Test retries too large
        config = InjectionConfig(max_clipboard_retries=15)
        self.assertFalse(config.validate())
        
    def test_config_equality(self):
        """Test equality comparison of InjectionConfig instances"""
        config1 = InjectionConfig()
        config2 = InjectionConfig()
        config3 = InjectionConfig(default_key_delay=0.02)
        
        # Same values should be equal
        self.assertEqual(config1, config2)
        
        # Different values should not be equal
        self.assertNotEqual(config1, config3)
        
    def test_config_repr(self):
        """Test string representation of InjectionConfig"""
        config = InjectionConfig(default_key_delay=0.01, sample_rate=44100)
        repr_str = repr(config)
        
        # Should contain class name and key values
        self.assertIn('InjectionConfig', repr_str)
        self.assertIn('default_key_delay=0.01', repr_str)
        self.assertIn('sample_rate=44100', repr_str)
        
    def test_type_annotations(self):
        """Test that type annotations are preserved"""
        annotations = InjectionConfig.__annotations__
        
        # Check float fields
        float_fields = [
            'default_key_delay', 'clipboard_paste_delay', 'strategy_switch_delay',
            'focus_acquisition_delay', 'windows_ui_automation_delay', 'linux_xtest_delay',
            'kde_dbus_timeout', 'xdotool_timeout', 'clipboard_retry_delay', 'chunk_duration'
        ]
        for field in float_fields:
            self.assertEqual(annotations[field], float)
            
        # Check int fields
        int_fields = ['max_clipboard_retries', 'skip_consecutive_failures', 
                      'sample_rate', 'stats_report_interval']
        for field in int_fields:
            self.assertEqual(annotations[field], int)
            
        # Check bool fields
        bool_fields = ['enable_performance_optimization', 'enable_monitoring', 
                       'enable_debug_logging']
        for field in bool_fields:
            self.assertEqual(annotations[field], bool)
            
    def test_round_trip_dict_conversion(self):
        """Test that dict->config->dict preserves values"""
        original_dict = {
            'default_key_delay': 0.123,
            'sample_rate': 48000,
            'preferred_strategy_order': ['keyboard', 'clipboard', 'ui_automation'],
            'enable_debug_logging': True
        }
        
        config = InjectionConfig.from_dict(original_dict)
        result_dict = config.to_dict()
        
        # Check that original values are preserved
        for key, value in original_dict.items():
            self.assertEqual(result_dict[key], value)


if __name__ == '__main__':
    unittest.main()