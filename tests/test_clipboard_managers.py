"""Test suite for clipboard manager implementations"""

import unittest
import time
import subprocess
from unittest.mock import patch, MagicMock, call
from personalparakeet.clipboard_manager import ClipboardManager
from personalparakeet.linux_clipboard_manager import LinuxClipboardManager
from personalparakeet.windows_clipboard_manager import WindowsClipboardManager


class TestClipboardManagerBase(unittest.TestCase):
    """Test cases for the base ClipboardManager class"""
    
    def test_clipboard_manager_is_abstract(self):
        """Test that ClipboardManager cannot be instantiated directly"""
        with self.assertRaises(TypeError):
            ClipboardManager()
            
    def test_save_clipboard_is_abstract(self):
        """Test that save_clipboard must be implemented by subclasses"""
        # Create a minimal implementation
        class MinimalClipboard(ClipboardManager):
            def restore_clipboard(self, content):
                pass
                
        with self.assertRaises(TypeError):
            MinimalClipboard()
            
    def test_restore_clipboard_is_abstract(self):
        """Test that restore_clipboard must be implemented by subclasses"""
        # Create a minimal implementation
        class MinimalClipboard(ClipboardManager):
            def save_clipboard(self):
                pass
                
        with self.assertRaises(TypeError):
            MinimalClipboard()


class TestLinuxClipboardManager(unittest.TestCase):
    """Test cases for LinuxClipboardManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.manager = LinuxClipboardManager()
        
    @patch('subprocess.run')
    def test_detect_clipboard_tool_xclip(self, mock_run):
        """Test detection of xclip"""
        # First call fails (xclip), second succeeds (xsel), third fails (wl-copy)
        mock_run.side_effect = [
            MagicMock(returncode=0),  # xclip found
            subprocess.CalledProcessError(1, 'xsel'),
            subprocess.CalledProcessError(1, 'wl-copy')
        ]
        
        tool = self.manager._detect_clipboard_tool()
        self.assertEqual(tool, 'xclip')
        
    @patch('subprocess.run')
    def test_detect_clipboard_tool_xsel(self, mock_run):
        """Test detection of xsel"""
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, 'xclip'),
            MagicMock(returncode=0),  # xsel found
            subprocess.CalledProcessError(1, 'wl-copy')
        ]
        
        tool = self.manager._detect_clipboard_tool()
        self.assertEqual(tool, 'xsel')
        
    @patch('subprocess.run')
    def test_detect_clipboard_tool_wlcopy(self, mock_run):
        """Test detection of wl-copy"""
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, 'xclip'),
            subprocess.CalledProcessError(1, 'xsel'),
            MagicMock(returncode=0)  # wl-copy found
        ]
        
        tool = self.manager._detect_clipboard_tool()
        self.assertEqual(tool, 'wl-copy')
        
    @patch('subprocess.run')
    def test_detect_clipboard_tool_none_found(self, mock_run):
        """Test when no clipboard tool is found"""
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, 'xclip'),
            subprocess.CalledProcessError(1, 'xsel'),
            subprocess.CalledProcessError(1, 'wl-copy')
        ]
        
        tool = self.manager._detect_clipboard_tool()
        self.assertIsNone(tool)
        
    @patch('subprocess.run')
    def test_save_clipboard_with_xclip(self, mock_run):
        """Test saving clipboard with xclip"""
        self.manager.tool = 'xclip'
        mock_run.return_value = MagicMock(stdout='test content')
        
        content = self.manager.save_clipboard()
        self.assertEqual(content, 'test content')
        mock_run.assert_called_with(
            ['xclip', '-selection', 'clipboard', '-o'],
            capture_output=True,
            text=True,
            check=True
        )
        
    @patch('subprocess.run')
    def test_save_clipboard_with_xsel(self, mock_run):
        """Test saving clipboard with xsel"""
        self.manager.tool = 'xsel'
        mock_run.return_value = MagicMock(stdout='test content')
        
        content = self.manager.save_clipboard()
        self.assertEqual(content, 'test content')
        mock_run.assert_called_with(
            ['xsel', '--clipboard', '--output'],
            capture_output=True,
            text=True,
            check=True
        )
        
    @patch('subprocess.run')
    def test_save_clipboard_with_retry(self, mock_run):
        """Test save_clipboard with retry logic"""
        self.manager.tool = 'xclip'
        # First attempt fails, second succeeds
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, 'xclip'),
            MagicMock(stdout='test content')
        ]
        
        content = self.manager.save_clipboard()
        self.assertEqual(content, 'test content')
        self.assertEqual(mock_run.call_count, 2)
        
    @patch('subprocess.run')
    @patch('time.sleep')
    def test_save_clipboard_max_retries(self, mock_sleep, mock_run):
        """Test save_clipboard fails after max retries"""
        self.manager.tool = 'xclip'
        mock_run.side_effect = subprocess.CalledProcessError(1, 'xclip')
        
        content = self.manager.save_clipboard()
        self.assertIsNone(content)
        self.assertEqual(mock_run.call_count, 3)  # Initial + 2 retries
        
    @patch('subprocess.run')
    def test_restore_clipboard_with_xclip(self, mock_run):
        """Test restoring clipboard with xclip"""
        self.manager.tool = 'xclip'
        
        success = self.manager.restore_clipboard('test content')
        self.assertTrue(success)
        mock_run.assert_called_with(
            ['xclip', '-selection', 'clipboard'],
            input='test content',
            text=True,
            check=True
        )
        
    @patch('subprocess.run')
    def test_restore_clipboard_empty_content(self, mock_run):
        """Test restoring empty clipboard content"""
        self.manager.tool = 'xclip'
        
        success = self.manager.restore_clipboard('')
        self.assertTrue(success)
        self.assertEqual(mock_run.call_count, 0)  # Should not call subprocess for empty content
        
    @patch('subprocess.run')
    def test_restore_clipboard_no_tool(self, mock_run):
        """Test restore when no tool is available"""
        self.manager.tool = None
        
        success = self.manager.restore_clipboard('test')
        self.assertFalse(success)
        mock_run.assert_not_called()


class TestWindowsClipboardManager(unittest.TestCase):
    """Test cases for WindowsClipboardManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.manager = WindowsClipboardManager()
        
    @patch('win32clipboard.OpenClipboard')
    @patch('win32clipboard.GetClipboardData')
    @patch('win32clipboard.CloseClipboard')
    def test_save_clipboard_success(self, mock_close, mock_get, mock_open):
        """Test successful clipboard save on Windows"""
        mock_get.return_value = 'test content'
        
        content = self.manager.save_clipboard()
        self.assertEqual(content, 'test content')
        mock_open.assert_called_once()
        mock_get.assert_called_once()
        mock_close.assert_called_once()
        
    @patch('win32clipboard.OpenClipboard')
    @patch('win32clipboard.GetClipboardData')
    @patch('win32clipboard.CloseClipboard')
    def test_save_clipboard_empty(self, mock_close, mock_get, mock_open):
        """Test saving empty clipboard"""
        mock_get.side_effect = Exception("No data")
        
        content = self.manager.save_clipboard()
        self.assertEqual(content, '')
        mock_close.assert_called_once()
        
    @patch('win32clipboard.OpenClipboard')
    @patch('win32clipboard.GetClipboardData')
    @patch('win32clipboard.CloseClipboard')
    @patch('time.sleep')
    def test_save_clipboard_with_retry(self, mock_sleep, mock_close, mock_get, mock_open):
        """Test save with retry on Windows"""
        # First attempt fails, second succeeds
        mock_open.side_effect = [Exception("Clipboard busy"), None]
        mock_get.return_value = 'test content'
        
        content = self.manager.save_clipboard()
        self.assertEqual(content, 'test content')
        self.assertEqual(mock_open.call_count, 2)
        
    @patch('win32clipboard.OpenClipboard')
    @patch('win32clipboard.EmptyClipboard')
    @patch('win32clipboard.SetClipboardText')
    @patch('win32clipboard.CloseClipboard')
    def test_restore_clipboard_success(self, mock_close, mock_set, mock_empty, mock_open):
        """Test successful clipboard restore on Windows"""
        success = self.manager.restore_clipboard('test content')
        
        self.assertTrue(success)
        mock_open.assert_called_once()
        mock_empty.assert_called_once()
        mock_set.assert_called_once_with('test content')
        mock_close.assert_called_once()
        
    @patch('win32clipboard.OpenClipboard')
    @patch('win32clipboard.CloseClipboard')
    def test_restore_clipboard_empty_content(self, mock_close, mock_open):
        """Test restoring empty content"""
        success = self.manager.restore_clipboard('')
        
        self.assertTrue(success)
        # Should not open clipboard for empty content
        mock_open.assert_not_called()
        
    @patch('win32clipboard.OpenClipboard')
    @patch('win32clipboard.CloseClipboard')
    def test_restore_clipboard_failure(self, mock_close, mock_open):
        """Test restore failure handling"""
        mock_open.side_effect = Exception("Clipboard error")
        
        success = self.manager.restore_clipboard('test')
        self.assertFalse(success)
        # CloseClipboard should still be called in finally block
        mock_close.assert_called_once()


if __name__ == '__main__':
    unittest.main()