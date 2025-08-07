#!/usr/bin/env python3
"""
Unit tests for the V3Config module.
"""
import json
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

import personalparakeet.config
from personalparakeet.config import V3Config

# Mark entire file as unit tests for CI selection
pytestmark = pytest.mark.unit


class TestConfig(unittest.TestCase):
    """Test suite for the V3Config class"""

    def test_default_config_loading(self):
        """Test that a default configuration is loaded when no file exists."""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            config = V3Config()
            self.assertEqual(config.audio.sample_rate, 16000)
            self.assertTrue(config.thought_linking.enabled)

    def test_config_loading_from_file(self):
        """Test that configuration is correctly loaded from a JSON file."""
        mock_config_data = {
            "audio": {"sample_rate": 8000},
            "thought_linking": {"enabled": False},
        }
        mock_file_content = json.dumps(mock_config_data)

        with (
            patch("pathlib.Path.exists") as mock_exists,
            patch("builtins.open", mock_open(read_data=mock_file_content)),
        ):
            mock_exists.return_value = True
            config = V3Config()
            self.assertEqual(config.audio.sample_rate, 8000)
            self.assertFalse(config.thought_linking.enabled)

    def test_config_saving_to_file(self):
        """Test that the configuration is correctly saved to a JSON file."""
        config = V3Config()
        config.audio.sample_rate = 22050
        config.vad.pause_threshold = 2.5

        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            config.save_to_file(Path("test_config.json"))

            # Get the content that was written to the mock file
            written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
            saved_config = json.loads(written_data)

            self.assertEqual(saved_config["audio"]["sample_rate"], 22050)
            self.assertEqual(saved_config["vad"]["pause_threshold"], 2.5)

    def test_valid_config_passes(self):
        """Test that a valid configuration passes validation."""
        config = V3Config()
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_invalid_sample_rate_raises_error(self):
        """Test that a non-positive sample rate raises a ValueError."""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            config = V3Config()
            config.audio.sample_rate = 0
            with self.assertRaises(ValueError):
                config.validate()

    def test_invalid_opacity_raises_error(self):
        """Test that an out-of-bounds opacity raises a ValueError."""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            config = V3Config()
            config.window.opacity = 1.1
            with self.assertRaises(ValueError):
                config.validate()


if __name__ == "__main__":
    unittest.main()
