#!/usr/bin/env python3
"""
Unit tests for the ThoughtLinker module.
"""

import unittest
from unittest.mock import MagicMock

from personalparakeet.core.thought_linker import (
    ThoughtLinker,
    LinkingDecision,
    LinkingSignal,
    SignalType,
)


class TestThoughtLinker(unittest.TestCase):
    """Test suite for the ThoughtLinker class."""

    def setUp(self):
        """Set up a ThoughtLinker instance for testing."""
        self.thought_linker = ThoughtLinker(enabled=True)

    def test_make_decision_from_signals_window_change(self):
        """Test that a strong window change signal results in a new thought."""
        signals = [
            LinkingSignal(
                SignalType.WINDOW_CHANGE, 0.95, "Window changed"
            )
        ]
        decision = self.thought_linker._make_decision_from_signals(signals)
        self.assertEqual(decision, LinkingDecision.START_NEW_THOUGHT)

    def test_make_decision_from_signals_user_input(self):
        """Test that a strong user input signal results in a new paragraph."""
        signals = [
            LinkingSignal(SignalType.USER_INPUT, 0.9, "User pressed Enter")
        ]
        decision = self.thought_linker._make_decision_from_signals(signals)
        self.assertEqual(decision, LinkingDecision.START_NEW_PARAGRAPH)

    def test_make_decision_from_signals_cursor_movement(self):
        """Test that a significant cursor movement results in a new paragraph."""
        signals = [
            LinkingSignal(
                SignalType.CURSOR_MOVEMENT, 0.8, "Cursor moved 150 pixels"
            )
        ]
        decision = self.thought_linker._make_decision_from_signals(signals)
        self.assertEqual(decision, LinkingDecision.START_NEW_PARAGRAPH)

    def test_make_decision_from_signals_timeout(self):
        """Test that a timeout signal results in a new paragraph."""
        signals = [
            LinkingSignal(SignalType.TIMEOUT, 0.7, "35-second gap")
        ]
        decision = self.thought_linker._make_decision_from_signals(signals)
        self.assertEqual(decision, LinkingDecision.START_NEW_PARAGRAPH)

    def test_make_decision_from_signals_high_similarity(self):
        """Test that high semantic similarity results in appending."""
        signals = [
            LinkingSignal(
                SignalType.SEMANTIC_SIMILARITY, 0.8, "High similarity"
            )
        ]
        self.thought_linker.similarity_threshold = 0.5
        decision = self.thought_linker._make_decision_from_signals(signals)
        self.assertEqual(decision, LinkingDecision.APPEND_WITH_SPACE)

    def test_make_decision_from_signals_low_similarity(self):
        """Test that low semantic similarity results in a new paragraph."""
        signals = [
            LinkingSignal(
                SignalType.SEMANTIC_SIMILARITY, 0.2, "Low similarity"
            )
        ]
        self.thought_linker.similarity_threshold = 0.5
        decision = self.thought_linker._make_decision_from_signals(signals)
        self.assertEqual(decision, LinkingDecision.START_NEW_PARAGRAPH)

    def test_calculate_text_similarity_identical(self):
        """Test that identical texts have a high similarity score."""
        text = "this is a test sentence"
        similarity = self.thought_linker._calculate_text_similarity(text, text)
        self.assertGreater(similarity, 0.9)

    def test_calculate_text_similarity_different(self):
        """Test that completely different texts have a low similarity score."""
        text1 = "the cat sat on the mat"
        text2 = "the dog chewed on a bone"
        similarity = self.thought_linker._calculate_text_similarity(
            text1, text2
        )
        self.assertLess(similarity, 0.5)

    def test_calculate_text_similarity_overlap(self):
        """Test that texts with some overlap have a medium similarity score."""
        text1 = "this is the first sentence"
        text2 = "this is the second sentence"
        similarity = self.thought_linker._calculate_text_similarity(
            text1, text2
        )
        self.assertTrue(0.5 < similarity < 0.9)


if __name__ == "__main__":
    unittest.main()