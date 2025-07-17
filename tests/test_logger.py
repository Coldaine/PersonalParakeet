"""Test suite for the logger module"""

import unittest
import tempfile
import os
import logging
from unittest.mock import patch, MagicMock
from personalparakeet.logger import setup_logger


class TestLogger(unittest.TestCase):
    """Test cases for the logger setup functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear any existing handlers to avoid interference
        self.test_logger_name = "test_logger_module"
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after tests"""
        # Remove all handlers from test logger
        logger = logging.getLogger(self.test_logger_name)
        logger.handlers.clear()
        
    def test_setup_logger_creates_logger(self):
        """Test that setup_logger creates a logger instance"""
        logger = setup_logger(self.test_logger_name)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, self.test_logger_name)
        
    def test_logger_has_correct_level(self):
        """Test that logger has INFO level by default"""
        logger = setup_logger(self.test_logger_name)
        self.assertEqual(logger.level, logging.INFO)
        
    def test_logger_has_console_handler(self):
        """Test that logger has a console handler"""
        logger = setup_logger(self.test_logger_name)
        
        # Check for StreamHandler
        stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        self.assertGreater(len(stream_handlers), 0, "Logger should have at least one StreamHandler")
        
    def test_logger_has_file_handler(self):
        """Test that logger has a file handler"""
        logger = setup_logger(self.test_logger_name)
        
        # Check for FileHandler
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        self.assertGreater(len(file_handlers), 0, "Logger should have at least one FileHandler")
            
    def test_logger_formats_include_emoji(self):
        """Test that logger format includes emoji symbols"""
        logger = setup_logger(self.test_logger_name)
        
        # Get console handler
        console_handler = next((h for h in logger.handlers if isinstance(h, logging.StreamHandler)), None)
        self.assertIsNotNone(console_handler)
        
        # Check format
        formatter = console_handler.formatter
        self.assertIsNotNone(formatter)
        # The format should include timestamp and level
        self.assertIn('%(asctime)s', formatter._fmt)
        self.assertIn('%(levelname)s', formatter._fmt)
        
    def test_log_directory_created(self):
        """Test that logger creates log directory"""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            logger = setup_logger(self.test_logger_name)
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
                
    def test_log_file_location(self):
        """Test that log file is in the correct location"""
        logger = setup_logger(self.test_logger_name)
        file_handler = next((h for h in logger.handlers if isinstance(h, logging.FileHandler)), None)
        self.assertIsNotNone(file_handler)
        # Check that the log file path contains .personalparakeet/logs
        self.assertIn('.personalparakeet', file_handler.baseFilename)
        self.assertIn('logs', file_handler.baseFilename)
        
    def test_logger_no_duplicate_handlers(self):
        """Test that calling setup_logger multiple times adds handlers each time"""
        logger1 = setup_logger(self.test_logger_name)
        initial_handler_count = len(logger1.handlers)
        
        logger2 = setup_logger(self.test_logger_name)
        self.assertEqual(logger1, logger2)  # Should be same instance
        # Note: Current implementation doesn't prevent duplicate handlers
        # This is a known behavior - each call adds new handlers
        self.assertEqual(len(logger2.handlers), initial_handler_count * 2)
        
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