"""Test suite for constants module"""

import unittest
import platform
from personalparakeet.constants import LogEmoji, PLATFORM_WINDOWS, PLATFORM_LINUX, PLATFORM_MAC, PLATFORM_UNKNOWN


class TestLogEmoji(unittest.TestCase):
    """Test cases for LogEmoji constants"""
    
    def test_emoji_values(self):
        """Test that all emoji constants have the expected values"""
        self.assertEqual(LogEmoji.INFO, "ℹ️")
        self.assertEqual(LogEmoji.SUCCESS, "✅")
        self.assertEqual(LogEmoji.WARNING, "⚠️")
        self.assertEqual(LogEmoji.ERROR, "❌")
        self.assertEqual(LogEmoji.DEBUG, "🔍")
        self.assertEqual(LogEmoji.KEYBOARD, "⌨️")
        self.assertEqual(LogEmoji.CLIPBOARD, "📋")
        self.assertEqual(LogEmoji.WINDOW, "🪟")
        self.assertEqual(LogEmoji.LINUX, "🐧")
        self.assertEqual(LogEmoji.SPEECH, "🎙️")
        
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
        self.assertEqual(PLATFORM_WINDOWS, "windows")
        self.assertEqual(PLATFORM_LINUX, "linux")
        self.assertEqual(PLATFORM_MAC, "darwin")
        self.assertEqual(PLATFORM_UNKNOWN, "unknown")
        
    def test_platform_constants_are_strings(self):
        """Test that all platform constants are strings"""
        self.assertIsInstance(PLATFORM_WINDOWS, str)
        self.assertIsInstance(PLATFORM_LINUX, str)
        self.assertIsInstance(PLATFORM_MAC, str)
        self.assertIsInstance(PLATFORM_UNKNOWN, str)
        
    def test_platform_constants_lowercase(self):
        """Test that platform constants are lowercase"""
        self.assertEqual(PLATFORM_WINDOWS, PLATFORM_WINDOWS.lower())
        self.assertEqual(PLATFORM_LINUX, PLATFORM_LINUX.lower())
        self.assertEqual(PLATFORM_MAC, PLATFORM_MAC.lower())
        self.assertEqual(PLATFORM_UNKNOWN, PLATFORM_UNKNOWN.lower())
        
    def test_platform_detection_logic(self):
        """Test that platform constants match Python's platform detection"""
        current_platform = platform.system().lower()
        
        if current_platform == "windows":
            self.assertEqual(current_platform, PLATFORM_WINDOWS)
        elif current_platform == "linux":
            self.assertEqual(current_platform, PLATFORM_LINUX)
        elif current_platform == "darwin":
            self.assertEqual(current_platform, PLATFORM_MAC)
        else:
            # For any other platform, we can't test the exact match
            self.assertIn(current_platform, [PLATFORM_WINDOWS, PLATFORM_LINUX, PLATFORM_MAC, PLATFORM_UNKNOWN])
            
    def test_platform_constants_unique(self):
        """Test that all platform constants are unique"""
        platforms = [PLATFORM_WINDOWS, PLATFORM_LINUX, PLATFORM_MAC, PLATFORM_UNKNOWN]
        unique_platforms = set(platforms)
        self.assertEqual(len(platforms), len(unique_platforms), "All platform constants should be unique")
        
    def test_platform_constants_not_empty(self):
        """Test that no platform constant is empty"""
        self.assertTrue(len(PLATFORM_WINDOWS) > 0)
        self.assertTrue(len(PLATFORM_LINUX) > 0)
        self.assertTrue(len(PLATFORM_MAC) > 0)
        self.assertTrue(len(PLATFORM_UNKNOWN) > 0)


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
        current_platform = platform.system().lower()
        
        # This simulates how the constants would be used
        if current_platform == PLATFORM_WINDOWS:
            platform_emoji = LogEmoji.WINDOW
        elif current_platform == PLATFORM_LINUX:
            platform_emoji = LogEmoji.LINUX
        else:
            platform_emoji = LogEmoji.INFO
            
        self.assertIsInstance(platform_emoji, str)
        self.assertTrue(len(platform_emoji) > 0)
        
    def test_constants_module_imports(self):
        """Test that constants module exports what we expect"""
        from personalparakeet import constants
        
        # Check LogEmoji class is available
        self.assertTrue(hasattr(constants, 'LogEmoji'))
        
        # Check platform constants are available
        self.assertTrue(hasattr(constants, 'PLATFORM_WINDOWS'))
        self.assertTrue(hasattr(constants, 'PLATFORM_LINUX'))
        self.assertTrue(hasattr(constants, 'PLATFORM_MAC'))
        self.assertTrue(hasattr(constants, 'PLATFORM_UNKNOWN'))


if __name__ == '__main__':
    unittest.main()