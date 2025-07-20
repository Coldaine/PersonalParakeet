"""Test suite for constants module"""

import unittest
import platform
from personalparakeet.constants import LogEmoji, WINDOWS_PLATFORMS, LINUX_PLATFORMS, MACOS_PLATFORMS


class TestLogEmoji(unittest.TestCase):
    """Test cases for LogEmoji constants"""
    
    def test_emoji_values(self):
        """Test that all emoji constants have the expected values"""
        self.assertEqual(LogEmoji.INFO, "🔤")
        self.assertEqual(LogEmoji.SUCCESS, "✅")
        self.assertEqual(LogEmoji.WARNING, "⚠️")
        self.assertEqual(LogEmoji.ERROR, "❌")
        self.assertEqual(LogEmoji.PROCESSING, "🔊")
        self.assertEqual(LogEmoji.TARGET, "🎯")
        
    def test_emoji_types(self):
        """Test that all emoji constants are strings"""
        emoji_attrs = [attr for attr in dir(LogEmoji) if not attr.startswith('_')]
        
        for attr_name in emoji_attrs:
            emoji_value = getattr(LogEmoji, attr_name)
            self.assertIsInstance(emoji_value, str, f"{attr_name} should be a string")
            
    def test_emoji_not_empty(self):
        """Test that no emoji constant is empty"""
        emoji_attrs = [attr for attr in dir(LogEmoji) if not attr.startswith('_')]
        
        for attr_name in emoji_attrs:
            emoji_value = getattr(LogEmoji, attr_name)
            self.assertTrue(len(emoji_value) > 0, f"{attr_name} should not be empty")
            
    def test_emoji_uniqueness(self):
        """Test that all emoji constants are unique"""
        emoji_attrs = [attr for attr in dir(LogEmoji) if not attr.startswith('_')]
        emoji_values = [getattr(LogEmoji, attr) for attr in emoji_attrs]
        
        # Convert to set to check uniqueness
        unique_values = set(emoji_values)
        self.assertEqual(len(emoji_values), len(unique_values), "All emoji values should be unique")
        
    def test_emoji_constants_are_class_attributes(self):
        """Test that LogEmoji only contains class attributes, not instance methods"""
        # LogEmoji should not be instantiable if it's just a constants class
        emoji_instance = LogEmoji()  # This works because it's a regular class
        
        # All uppercase attributes should be the same on class and instance
        emoji_attrs = [attr for attr in dir(LogEmoji) if attr.isupper()]
        for attr in emoji_attrs:
            class_value = getattr(LogEmoji, attr)
            instance_value = getattr(emoji_instance, attr)
            self.assertEqual(class_value, instance_value)


class TestPlatformConstants(unittest.TestCase):
    """Test cases for platform detection constants"""
    
    def test_platform_constant_values(self):
        """Test that platform constants have expected values"""
        self.assertIn('win32', WINDOWS_PLATFORMS)
        self.assertIn('linux', LINUX_PLATFORMS)
        self.assertIn('darwin', MACOS_PLATFORMS)
        
    def test_platform_constants_are_lists(self):
        """Test that all platform constants are lists"""
        self.assertIsInstance(WINDOWS_PLATFORMS, list)
        self.assertIsInstance(LINUX_PLATFORMS, list)
        self.assertIsInstance(MACOS_PLATFORMS, list)
        
    def test_platform_constants_contain_strings(self):
        """Test that platform lists contain strings"""
        for platform in WINDOWS_PLATFORMS:
            self.assertIsInstance(platform, str)
        for platform in LINUX_PLATFORMS:
            self.assertIsInstance(platform, str)
        for platform in MACOS_PLATFORMS:
            self.assertIsInstance(platform, str)
        
    def test_platform_detection_logic(self):
        """Test that platform constants can detect current platform"""
        import sys
        current_platform = sys.platform
        
        # Check if current platform is in one of our lists
        platform_found = (
            current_platform in WINDOWS_PLATFORMS or
            current_platform in LINUX_PLATFORMS or
            current_platform in MACOS_PLATFORMS
        )
        self.assertTrue(platform_found, f"Platform {current_platform} not found in any platform list")
            
    def test_platform_lists_not_empty(self):
        """Test that platform lists are not empty"""
        self.assertTrue(len(WINDOWS_PLATFORMS) > 0)
        self.assertTrue(len(LINUX_PLATFORMS) > 0)
        self.assertTrue(len(MACOS_PLATFORMS) > 0)


class TestConstantsIntegration(unittest.TestCase):
    """Test integration between different constants"""
    
    def test_can_use_emoji_in_logging_context(self):
        """Test that emoji constants can be used in string formatting"""
        # Simulate a log message
        message = f"{LogEmoji.SUCCESS} Operation completed successfully"
        self.assertIn(LogEmoji.SUCCESS, message)
        self.assertIn("Operation completed", message)
        
    def test_can_use_platform_in_conditionals(self):
        """Test that platform constants work in conditional logic"""
        import sys
        
        # This simulates how the constants would be used
        if sys.platform in WINDOWS_PLATFORMS:
            platform_emoji = LogEmoji.INFO
        elif sys.platform in LINUX_PLATFORMS:
            platform_emoji = LogEmoji.PROCESSING
        else:
            platform_emoji = LogEmoji.TARGET
            
        self.assertIsInstance(platform_emoji, str)
        self.assertTrue(len(platform_emoji) > 0)
        
    def test_constants_module_imports(self):
        """Test that constants module exports what we expect"""
        from personalparakeet import constants
        
        # Check LogEmoji class is available
        self.assertTrue(hasattr(constants, 'LogEmoji'))
        
        # Check platform constants are available
        self.assertTrue(hasattr(constants, 'WINDOWS_PLATFORMS'))
        self.assertTrue(hasattr(constants, 'LINUX_PLATFORMS'))
        self.assertTrue(hasattr(constants, 'MACOS_PLATFORMS'))


if __name__ == '__main__':
    unittest.main()