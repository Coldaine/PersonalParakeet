"""Test suite for clipboard manager implementations"""

import unittest
import time
import subprocess
from unittest.mock import patch, MagicMock, call
from personalparakeet.clipboard_manager import ClipboardManager
from personalparakeet.windows_clipboard_manager import WindowsClipboardManager
import sys


class TestClipboardManagerBase(unittest.TestCase):
    """Test cases for the base ClipboardManager class"""
    
    def test_clipboard_manager_requires_implementation(self):
        """Test that ClipboardManager requires subclass implementation"""
        # Create a minimal implementation that doesn't implement required methods
        class MinimalClipboard(ClipboardManager):
            pass
                
        clipboard = MinimalClipboard()
        
        # These should raise NotImplementedError
        with self.assertRaises(NotImplementedError):
            clipboard._get_clipboard_content()
            
        with self.assertRaises(NotImplementedError):
            clipboard._get_clipboard_format()
            
        with self.assertRaises(NotImplementedError):
            clipboard._set_clipboard_content("test", None)


@unittest.skipIf(sys.platform == "win32", "Linux tests skipped on Windows")
class TestLinuxClipboardManager(unittest.TestCase):
    """Test cases for LinuxClipboardManager"""
    
    def setUp(self):
        """Set up test environment"""
        from personalparakeet.linux_clipboard_manager import LinuxClipboardManager
        self.manager = LinuxClipboardManager()
        
    def test_linux_clipboard_skipped_on_windows(self):
        """Test that Linux clipboard tests are properly skipped on Windows"""
        self.skipTest("Linux clipboard tests are skipped on Windows")


class TestWindowsClipboardManager(unittest.TestCase):
    """Test cases for WindowsClipboardManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.manager = WindowsClipboardManager()
        
    @patch('win32clipboard.OpenClipboard')
    @patch('win32clipboard.IsClipboardFormatAvailable')
    @patch('win32clipboard.GetClipboardData')
    @patch('win32clipboard.CloseClipboard')
    def test_save_clipboard_success(self, mock_close, mock_get, mock_available, mock_open):
        """Test successful clipboard save on Windows"""
        mock_available.return_value = True
        mock_get.return_value = 'test content'
        
        success = self.manager.save_clipboard()
        self.assertTrue(success)
        self.assertEqual(self.manager.original_content, 'test content')
        mock_open.assert_called_once()
        mock_get.assert_called_once()
        mock_close.assert_called_once()
        
    @patch('win32clipboard.OpenClipboard')
    @patch('win32clipboard.IsClipboardFormatAvailable')
    @patch('win32clipboard.CloseClipboard')
    def test_save_clipboard_empty(self, mock_close, mock_available, mock_open):
        """Test saving empty clipboard"""
        mock_available.return_value = False
        
        success = self.manager.save_clipboard()
        self.assertTrue(success)
        self.assertIsNone(self.manager.original_content)
        mock_close.assert_called_once()
        
    @patch('personalparakeet.windows_clipboard_manager.WindowsClipboardManager._get_clipboard_content')
    @patch('personalparakeet.windows_clipboard_manager.WindowsClipboardManager._get_clipboard_format')
    def test_save_clipboard_with_none_content(self, mock_format, mock_content):
        """Test saving clipboard when content is None (empty clipboard)"""
        # Clipboard returns None (empty)
        mock_content.return_value = None
        mock_format.return_value = 13  # CF_UNICODETEXT
        
        success = self.manager.save_clipboard()
        self.assertTrue(success)
        self.assertIsNone(self.manager.original_content)
        self.assertEqual(self.manager.original_format, 13)
        
    @patch('win32clipboard.OpenClipboard')
    @patch('win32clipboard.EmptyClipboard')
    @patch('win32clipboard.SetClipboardData')
    @patch('win32clipboard.CloseClipboard')
    @patch('win32clipboard.IsClipboardFormatAvailable')
    @patch('win32clipboard.GetClipboardData')
    def test_restore_clipboard_success(self, mock_get, mock_available, mock_close, mock_set, mock_empty, mock_open):
        """Test successful clipboard restore on Windows"""
        # First save some content
        self.manager.original_content = 'test content'
        self.manager.original_format = 13  # CF_UNICODETEXT
        
        # Mock verification
        mock_available.return_value = True
        mock_get.return_value = 'test content'
        
        success = self.manager.restore_clipboard()
        
        self.assertTrue(success)
        mock_empty.assert_called_once()
        mock_set.assert_called_once_with(13, 'test content')
        
    def test_restore_clipboard_nothing_to_restore(self):
        """Test restoring when nothing was saved"""
        # Don't save anything first
        success = self.manager.restore_clipboard()
        
        self.assertTrue(success)  # Should succeed with nothing to restore
        
    @patch('win32clipboard.OpenClipboard')
    @patch('win32clipboard.CloseClipboard')
    @patch('time.sleep')
    def test_restore_clipboard_failure(self, mock_sleep, mock_close, mock_open):
        """Test restore failure handling"""
        # Set up content to restore
        self.manager.original_content = 'test content'
        self.manager.original_format = 13
        
        mock_open.side_effect = Exception("Clipboard error")
        
        success = self.manager.restore_clipboard()
        self.assertFalse(success)
        # Should retry 3 times
        self.assertEqual(mock_open.call_count, 3)


if __name__ == '__main__':
    unittest.main()