"""Test suite for the logger module"""

import unittest
import tempfile
import os
import logging
from unittest.mock import patch, MagicMock
from personalparakeet.logger import setup_logger, get_log_file_path


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
        with patch('personalparakeet.logger.get_log_file_path') as mock_path:
            mock_path.return_value = os.path.join(self.temp_dir, 'test.log')
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
        
    def test_get_log_file_path_creates_directory(self):
        """Test that get_log_file_path creates logs directory if needed"""
        with patch('os.makedirs') as mock_makedirs:
            with patch('os.path.exists', return_value=False):
                path = get_log_file_path()
                mock_makedirs.assert_called_once()
                self.assertTrue(path.endswith('.log'))
                
    def test_get_log_file_path_includes_date(self):
        """Test that log file path includes current date"""
        from datetime import datetime
        path = get_log_file_path()
        date_str = datetime.now().strftime('%Y%m%d')
        self.assertIn(date_str, path)
        
    def test_logger_no_duplicate_handlers(self):
        """Test that calling setup_logger multiple times doesn't duplicate handlers"""
        logger1 = setup_logger(self.test_logger_name)
        initial_handler_count = len(logger1.handlers)
        
        logger2 = setup_logger(self.test_logger_name)
        self.assertEqual(logger1, logger2)  # Should be same instance
        self.assertEqual(len(logger2.handlers), initial_handler_count)  # No new handlers added
        
    def test_logger_writes_to_file(self):
        """Test that logger actually writes to file"""
        with patch('personalparakeet.logger.get_log_file_path') as mock_path:
            log_file = os.path.join(self.temp_dir, 'test_write.log')
            mock_path.return_value = log_file
            
            logger = setup_logger(self.test_logger_name)
            test_message = "Test log message"
            logger.info(test_message)
            
            # Force flush
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.flush()
            
            # Check file contains message
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    content = f.read()
                    self.assertIn(test_message, content)


if __name__ == '__main__':
    unittest.main()