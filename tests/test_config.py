"""Test suite for configuration classes"""

import unittest
from dataclasses import FrozenInstanceError
from personalparakeet.config import InjectionConfig


class TestInjectionConfig(unittest.TestCase):
    """Test cases for InjectionConfig dataclass"""
    
    def test_default_values(self):
        """Test that InjectionConfig has correct default values"""
        config = InjectionConfig()
        
        self.assertEqual(config.default_key_delay, 0.005)
        self.assertEqual(config.word_delay, 0.05)
        self.assertEqual(config.clipboard_paste_delay, 0.1)
        self.assertEqual(config.focus_acquisition_delay, 0.05)
        self.assertEqual(config.xdotool_timeout, 2.0)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_delay, 0.1)
        
    def test_custom_values(self):
        """Test creating InjectionConfig with custom values"""
        config = InjectionConfig(
            default_key_delay=0.01,
            word_delay=0.1,
            clipboard_paste_delay=0.2,
            focus_acquisition_delay=0.15,
            xdotool_timeout=5.0,
            max_retries=5,
            retry_delay=0.2
        )
        
        self.assertEqual(config.default_key_delay, 0.01)
        self.assertEqual(config.word_delay, 0.1)
        self.assertEqual(config.clipboard_paste_delay, 0.2)
        self.assertEqual(config.focus_acquisition_delay, 0.15)
        self.assertEqual(config.xdotool_timeout, 5.0)
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.retry_delay, 0.2)
        
    def test_partial_custom_values(self):
        """Test creating InjectionConfig with some custom values"""
        config = InjectionConfig(
            default_key_delay=0.02,
            max_retries=10
        )
        
        # Custom values
        self.assertEqual(config.default_key_delay, 0.02)
        self.assertEqual(config.max_retries, 10)
        
        # Default values
        self.assertEqual(config.word_delay, 0.05)
        self.assertEqual(config.clipboard_paste_delay, 0.1)
        self.assertEqual(config.focus_acquisition_delay, 0.05)
        self.assertEqual(config.xdotool_timeout, 2.0)
        self.assertEqual(config.retry_delay, 0.1)
        
    def test_config_is_frozen(self):
        """Test that InjectionConfig is immutable (frozen)"""
        config = InjectionConfig()
        
        # Attempting to modify should raise FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            config.default_key_delay = 0.1
            
        with self.assertRaises(FrozenInstanceError):
            config.max_retries = 10
            
    def test_config_equality(self):
        """Test equality comparison of InjectionConfig instances"""
        config1 = InjectionConfig()
        config2 = InjectionConfig()
        config3 = InjectionConfig(default_key_delay=0.01)
        
        # Same values should be equal
        self.assertEqual(config1, config2)
        
        # Different values should not be equal
        self.assertNotEqual(config1, config3)
        
    def test_config_repr(self):
        """Test string representation of InjectionConfig"""
        config = InjectionConfig(default_key_delay=0.01)
        repr_str = repr(config)
        
        # Should contain class name and key values
        self.assertIn('InjectionConfig', repr_str)
        self.assertIn('default_key_delay=0.01', repr_str)
        self.assertIn('max_retries=3', repr_str)
        
    def test_config_hashable(self):
        """Test that InjectionConfig instances are hashable"""
        config1 = InjectionConfig()
        config2 = InjectionConfig()
        config3 = InjectionConfig(default_key_delay=0.01)
        
        # Should be able to use as dict keys or in sets
        config_set = {config1, config2, config3}
        # config1 and config2 are equal, so set should have 2 items
        self.assertEqual(len(config_set), 2)
        
        # Should work as dict keys
        config_dict = {
            config1: "default",
            config3: "custom"
        }
        self.assertEqual(len(config_dict), 2)
        
    def test_negative_values_allowed(self):
        """Test that negative values are allowed (though not recommended)"""
        # This tests that we don't have validation that prevents negative values
        # In practice, negative delays wouldn't make sense, but the dataclass doesn't enforce this
        config = InjectionConfig(default_key_delay=-0.1)
        self.assertEqual(config.default_key_delay, -0.1)
        
    def test_zero_values_allowed(self):
        """Test that zero values are allowed"""
        config = InjectionConfig(
            default_key_delay=0,
            word_delay=0,
            clipboard_paste_delay=0,
            focus_acquisition_delay=0,
            xdotool_timeout=0,
            max_retries=0,
            retry_delay=0
        )
        
        self.assertEqual(config.default_key_delay, 0)
        self.assertEqual(config.word_delay, 0)
        self.assertEqual(config.max_retries, 0)
        
    def test_type_annotations(self):
        """Test that type annotations are preserved"""
        # This is more of a documentation test
        annotations = InjectionConfig.__annotations__
        
        self.assertEqual(annotations['default_key_delay'], float)
        self.assertEqual(annotations['word_delay'], float)
        self.assertEqual(annotations['clipboard_paste_delay'], float)
        self.assertEqual(annotations['focus_acquisition_delay'], float)
        self.assertEqual(annotations['xdotool_timeout'], float)
        self.assertEqual(annotations['max_retries'], int)
        self.assertEqual(annotations['retry_delay'], float)


if __name__ == '__main__':
    unittest.main()