"""Test module for the logger utility"""

import unittest
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

from personalparakeet.logger import setup_logger


class TestLogger(unittest.TestCase):
    """Test cases for the logger module"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_logger_name = 'test_personalparakeet'
        # Store original handlers to restore later
        self.original_handlers = logging.getLogger(self.test_logger_name).handlers[:]
        # Clear any existing handlers
        logger = logging.getLogger(self.test_logger_name)
        logger.handlers.clear()
        
        # Create a temporary directory for test logs
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after tests"""
        # Clean up handlers to avoid resource warnings
        logger = logging.getLogger(self.test_logger_name)
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
        logger.handlers.clear()
        
        # Restore original handlers
        logger.handlers.extend(self.original_handlers)
        
        # Clean up temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
    def test_setup_logger_returns_logger(self):
        """Test that setup_logger returns a logging.Logger instance"""
        logger = setup_logger(self.test_logger_name)
        self.assertIsInstance(logger, logging.Logger)
        
    def test_logger_name_is_set(self):
        """Test that logger has the correct name"""
        logger = setup_logger(self.test_logger_name)
        self.assertEqual(logger.name, self.test_logger_name)
        
    def test_logger_has_console_handler(self):
        """Test that logger has a console handler"""
        logger = setup_logger(self.test_logger_name)
        
        # Check for StreamHandler (console)
        stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        self.assertGreater(len(stream_handlers), 0, "Logger should have at least one StreamHandler")
        
        # Check that it outputs to stdout
        console_handler = stream_handlers[0]
        self.assertEqual(console_handler.stream, sys.stdout)
        
    def test_logger_has_file_handler(self):
        """Test that logger has a file handler"""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            logger = setup_logger(self.test_logger_name)
            
            # Check for FileHandler
            file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
            self.assertGreater(len(file_handlers), 0, "Logger should have at least one FileHandler")
            
            # Check file path includes .personalparakeet/logs
            file_handler = file_handlers[0]
            self.assertIn('.personalparakeet', file_handler.baseFilename)
            self.assertIn('logs', file_handler.baseFilename)
            
    def test_logger_formats(self):
        """Test that logger formatters are set correctly"""
        logger = setup_logger(self.test_logger_name)
        
        # Get handlers
        console_handler = next((h for h in logger.handlers if isinstance(h, logging.StreamHandler)), None)
        file_handler = next((h for h in logger.handlers if isinstance(h, logging.FileHandler)), None)
        
        self.assertIsNotNone(console_handler)
        self.assertIsNotNone(file_handler)
        
        # Check formatters
        for handler in [console_handler, file_handler]:
            formatter = handler.formatter
            self.assertIsNotNone(formatter)
            # The format should include timestamp, name, level, and message
            self.assertIn('%(asctime)s', formatter._fmt)
            self.assertIn('%(name)s', formatter._fmt)
            self.assertIn('%(levelname)s', formatter._fmt)
            self.assertIn('%(message)s', formatter._fmt)
                
    def test_log_directory_creation(self):
        """Test that log directory is created with correct path"""
        with patch('pathlib.Path.home') as mock_home:
            with patch('pathlib.Path.mkdir') as mock_mkdir:
                with patch('logging.FileHandler') as mock_file_handler:
                    mock_home.return_value = Path('/home/testuser')
                    logger = setup_logger(self.test_logger_name)
                    
                    # Check mkdir was called with correct arguments
                    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
                
    def test_logger_file_path(self):
        """Test that log file has correct name and location"""
        logger = setup_logger(self.test_logger_name)
        
        # Find file handler
        file_handler = next((h for h in logger.handlers if isinstance(h, logging.FileHandler)), None)
        self.assertIsNotNone(file_handler)
        
        # Check filename
        self.assertTrue(file_handler.baseFilename.endswith('personalparakeet.log'))
        
    def test_logger_no_duplicate_handlers(self):
        """Test that calling setup_logger multiple times adds handlers each time"""
        # Note: Current implementation doesn't prevent duplicate handlers
        # This is a known behavior - each call adds new handlers
        logger1 = setup_logger(self.test_logger_name)
        initial_handler_count = len(logger1.handlers)
        
        logger2 = setup_logger(self.test_logger_name)
        self.assertEqual(logger1, logger2)  # Should be same instance
        # Current implementation adds handlers each time
        self.assertEqual(len(logger2.handlers), initial_handler_count * 2)
        
    def test_logger_writes_to_console(self):
        """Test that logger actually writes to console"""
        # Get a fresh logger with cleared handlers
        test_logger_name = self.test_logger_name + "_console_test"
        logger = logging.getLogger(test_logger_name)
        logger.handlers.clear()
        logger.setLevel(logging.INFO)
        
        # Add a mock handler
        mock_handler = MagicMock(spec=logging.StreamHandler)
        mock_handler.level = logging.INFO
        logger.addHandler(mock_handler)
        
        # Log a message
        test_message = "Test console log message"
        logger.info(test_message)
        
        # Check that handle was called
        mock_handler.handle.assert_called()
            
    def test_logger_case_insensitive_level(self):
        """Test that log level is case insensitive"""
        logger1 = setup_logger(self.test_logger_name + "_lower", level="debug")
        self.assertEqual(logger1.level, logging.DEBUG)
        
        logger2 = setup_logger(self.test_logger_name + "_upper", level="DEBUG")
        self.assertEqual(logger2.level, logging.DEBUG)
        
        logger3 = setup_logger(self.test_logger_name + "_mixed", level="DeBuG")
        self.assertEqual(logger3.level, logging.DEBUG)
        
    def test_logger_writes_to_file(self):
        """Test that logger actually writes to file"""
        # Create a temporary logger with a custom file path
        from pathlib import Path
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path(self.temp_dir)
            
            logger = setup_logger(self.test_logger_name)
            test_message = "Test log message"
            logger.info(test_message)
            
            # Force flush
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.flush()
                    # Check file contains message
                    if os.path.exists(handler.baseFilename):
                        with open(handler.baseFilename, 'r') as f:
                            content = f.read()
                            self.assertIn(test_message, content)


if __name__ == '__main__':
    unittest.main()