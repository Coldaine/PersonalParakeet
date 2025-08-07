#!/usr/bin/env python3
"""
Thought Linker - PLACEHOLDER IMPLEMENTATION (NOT ACTIVE)

This is a complete but INACTIVE implementation of intelligent thought linking.
To activate: Set thought_linking.enabled = True in config

This module implements intelligent context-aware text linking that decides
whether consecutive utterances should be linked as a single thought or 
treated as separate paragraphs based on multiple contextual signals.
"""

import logging
import time
import difflib
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class LinkingDecision(Enum):
    """Decision types for thought linking"""

    COMMIT_AND_CONTINUE = "commit_and_continue"  # v3 addition - commit but keep context
    APPEND_WITH_SPACE = "append_with_space"  # Continue current thought
    START_NEW_PARAGRAPH = "start_new_paragraph"  # New paragraph, same context
    START_NEW_THOUGHT = "start_new_thought"  # Complete context switch


class SignalType(Enum):
    """Types of contextual signals"""

    USER_INPUT = "user_input"  # Enter, Tab, Escape pressed
    WINDOW_CHANGE = "window_change"  # Active application changed
    CURSOR_MOVEMENT = "cursor_movement"  # Cursor position changed significantly
    SEMANTIC_SIMILARITY = "semantic_similarity"  # Text similarity analysis
    TIMEOUT = "timeout"  # Time-based separation
    PUNCTUATION = "punctuation"  # Sentence-ending punctuation


@dataclass
class LinkingSignal:
    """Signal from thought linking analysis"""

    signal_type: SignalType
    strength: float  # 0.0 to 1.0
    description: str
    data: Optional[Dict[str, Any]] = None


@dataclass
class ThoughtContext:
    """Context information for thought-linking decisions"""

    text: str
    timestamp: float
    window_info: Optional[Dict[str, Any]] = None
    cursor_position: Optional[Tuple[int, int]] = None
    user_action: Optional[str] = None


class ThoughtLinker:
    """
    Intelligent thought linking system - PLACEHOLDER (NOT ACTIVE)

    When enabled, analyzes contextual signals to determine how consecutive
    utterances should be linked together.
    """

    def __init__(
        self,
        cursor_movement_threshold: int = 100,
        similarity_threshold: float = 0.3,
        timeout_threshold: float = 30.0,
        enabled: bool = False,
    ):
        """
        Initialize the thought linker

        Args:
            cursor_movement_threshold: Pixels of cursor movement to trigger new thought
            similarity_threshold: Minimum similarity to consider texts related
            timeout_threshold: Seconds after which to start new thought
            enabled: Whether thought linking is active (default: False)
        """
        self.enabled = enabled
        self.cursor_movement_threshold = cursor_movement_threshold
        self.similarity_threshold = similarity_threshold
        self.timeout_threshold = timeout_threshold

        # Context tracking
        self.previous_context: Optional[ThoughtContext] = None
        self.user_actions: List[str] = []  # Track recent user actions

        # Platform-specific detectors (lazy loaded)
        self._window_detector = None
        self._cursor_detector = None

        # Import detectors if enabled
        if self.enabled:
            self._initialize_detectors()

        logger.info(f"ThoughtLinker initialized (enabled={enabled})")

    def _initialize_detectors(self):
        """Initialize platform-specific detectors"""
        try:
            from .window_detector import create_window_detector
            from .cursor_detector import create_cursor_detector

            self._window_detector = create_window_detector(enabled=True)
            self._cursor_detector = create_cursor_detector(
                enabled=True, movement_threshold=self.cursor_movement_threshold
            )

            logger.debug("Platform detectors initialized")
        except ImportError as e:
            logger.warning(f"Failed to import detectors: {e}")

    def should_link_thoughts(self, text: str) -> Tuple[LinkingDecision, List[LinkingSignal]]:
        """
        Determine how to commit current text based on context

        Args:
            text: The newly transcribed text

        Returns:
            Tuple of (decision, signals_considered)
        """
        # PLACEHOLDER: If disabled, return simple default behavior
        if not self.enabled:
            return self._simple_decision(text)

        # Full implementation follows (currently inactive)
        current_time = time.time()
        signals = []

        # Create current context
        current_context = ThoughtContext(
            text=text,
            timestamp=current_time,
            window_info=self._get_current_window_info(),
            cursor_position=self._get_cursor_position(),
        )

        # If no previous context, always start new thought
        if self.previous_context is None:
            self.previous_context = current_context
            return LinkingDecision.START_NEW_THOUGHT, signals

        # Collect all signals
        signals.extend(self._check_all_signals(current_context))

        # Make decision based on strongest signal
        decision = self._make_decision_from_signals(signals)

        # Update context
        self.previous_context = current_context

        return decision, signals

    def _simple_decision(self, text: str) -> Tuple[LinkingDecision, List[LinkingSignal]]:
        """Simple decision making when thought linking is disabled"""
        signals = []

        # Simple heuristic: if text ends with punctuation, start new thought
        if text.strip().endswith((".", "!", "?")):
            signals.append(
                LinkingSignal(
                    signal_type=SignalType.PUNCTUATION,
                    strength=0.8,
                    description="Text ends with sentence punctuation",
                )
            )
            return LinkingDecision.START_NEW_THOUGHT, signals

        # Default: continue current thought
        signals.append(
            LinkingSignal(
                signal_type=SignalType.PUNCTUATION,
                strength=0.5,
                description="Default commit and continue",
            )
        )
        return LinkingDecision.COMMIT_AND_CONTINUE, signals

    def _check_all_signals(self, current_context: ThoughtContext) -> List[LinkingSignal]:
        """Collect all contextual signals"""
        signals = []

        # Primary signals (high priority)
        if user_signal := self._check_user_actions():
            signals.append(user_signal)

        if window_signal := self._check_window_change(current_context):
            signals.append(window_signal)

        if cursor_signal := self._check_cursor_movement(current_context):
            signals.append(cursor_signal)

        if timeout_signal := self._check_timeout(current_context):
            signals.append(timeout_signal)

        # Secondary signals
        if similarity_signal := self._check_semantic_similarity(current_context):
            signals.append(similarity_signal)

        return signals

    def _make_decision_from_signals(self, signals: List[LinkingSignal]) -> LinkingDecision:
        """Make linking decision based on collected signals"""
        if not signals:
            return LinkingDecision.APPEND_WITH_SPACE

        # Find strongest signal
        strongest = max(signals, key=lambda s: s.strength)

        # Decision logic based on signal type and strength
        if strongest.signal_type == SignalType.WINDOW_CHANGE and strongest.strength >= 0.9:
            return LinkingDecision.START_NEW_THOUGHT
        elif strongest.signal_type == SignalType.USER_INPUT and strongest.strength >= 0.8:
            return LinkingDecision.START_NEW_PARAGRAPH
        elif strongest.signal_type == SignalType.CURSOR_MOVEMENT and strongest.strength >= 0.7:
            return LinkingDecision.START_NEW_PARAGRAPH
        elif strongest.signal_type == SignalType.TIMEOUT and strongest.strength >= 0.6:
            return LinkingDecision.START_NEW_PARAGRAPH
        elif strongest.signal_type == SignalType.SEMANTIC_SIMILARITY:
            if strongest.strength >= self.similarity_threshold:
                return LinkingDecision.APPEND_WITH_SPACE
            else:
                return LinkingDecision.START_NEW_PARAGRAPH
        else:
            return LinkingDecision.APPEND_WITH_SPACE

    def _check_user_actions(self) -> Optional[LinkingSignal]:
        """Check if user performed any actions that indicate new thought"""
        if not self.user_actions:
            return None

        recent_action = self.user_actions[-1]

        # Strong separation actions
        if recent_action.lower() in ["enter", "return", "tab", "escape"]:
            return LinkingSignal(
                signal_type=SignalType.USER_INPUT,
                strength=0.9,
                description=f"User pressed {recent_action}",
                data={"action": recent_action},
            )

        # Moderate separation actions
        if recent_action.lower() in ["ctrl+enter", "shift+enter"]:
            return LinkingSignal(
                signal_type=SignalType.USER_INPUT,
                strength=0.7,
                description=f"User pressed {recent_action}",
                data={"action": recent_action},
            )

        return None

    def _check_window_change(self, current_context: ThoughtContext) -> Optional[LinkingSignal]:
        """Check if the active window has changed"""
        if not self._window_detector:
            return None

        # Check if window changed
        if self._window_detector.has_window_changed():
            window_context = self._window_detector.get_window_context()

            return LinkingSignal(
                signal_type=SignalType.WINDOW_CHANGE,
                strength=0.95,
                description="Active window changed",
                data=window_context,
            )

        return None

    def _check_cursor_movement(self, current_context: ThoughtContext) -> Optional[LinkingSignal]:
        """Check if cursor has moved significantly"""
        if not self._cursor_detector:
            return None

        # Check for significant movement
        has_moved, distance = self._cursor_detector.check_significant_movement()

        if has_moved:
            strength = self._cursor_detector.get_movement_signal_strength(distance)

            return LinkingSignal(
                signal_type=SignalType.CURSOR_MOVEMENT,
                strength=strength,
                description=f"Cursor moved {distance:.0f} pixels",
                data=self._cursor_detector.get_cursor_context(),
            )

        return None

    def _check_timeout(self, current_context: ThoughtContext) -> Optional[LinkingSignal]:
        """Check if too much time has passed since last text"""
        if not self.previous_context:
            return None

        time_diff = current_context.timestamp - self.previous_context.timestamp

        if time_diff >= self.timeout_threshold:
            # Calculate strength based on time difference
            strength = min(0.8, time_diff / (self.timeout_threshold * 2))

            return LinkingSignal(
                signal_type=SignalType.TIMEOUT,
                strength=strength,
                description=f"Time gap of {time_diff:.1f} seconds",
                data={"time_difference": time_diff},
            )

        return None

    def _check_semantic_similarity(
        self, current_context: ThoughtContext
    ) -> Optional[LinkingSignal]:
        """Check semantic similarity between current and previous text"""
        if not self.previous_context:
            return None

        prev_text = self.previous_context.text.lower().strip()
        curr_text = current_context.text.lower().strip()

        if not prev_text or not curr_text:
            return None

        # Calculate similarity
        similarity = self._calculate_text_similarity(prev_text, curr_text)

        return LinkingSignal(
            signal_type=SignalType.SEMANTIC_SIMILARITY,
            strength=similarity,
            description=f"Text similarity: {similarity:.2f}",
            data={"similarity": similarity, "previous_text": prev_text, "current_text": curr_text},
        )

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings

        Uses a combination of:
        1. Sequence similarity (SequenceMatcher)
        2. Word overlap
        3. Common phrases

        Returns:
            Similarity score from 0.0 to 1.0
        """
        # NOTE: This is a heuristic-based similarity score, not a deep semantic
        # comparison. It's designed to be fast and good enough for real-time decisions.

        # 1. Sequence similarity
        seq_similarity = difflib.SequenceMatcher(None, text1, text2).ratio()

        # 2. Word overlap
        words1 = set(text1.split())
        words2 = set(text2.split())

        if len(words1) == 0 and len(words2) == 0:
            word_overlap = 1.0
        elif len(words1) == 0 or len(words2) == 0:
            word_overlap = 0.0
        else:
            common_words = words1.intersection(words2)
            word_overlap = len(common_words) / max(len(words1), len(words2))

        # 3. Check for continuing thought patterns
        continuation_bonus = 0.0

        # Common continuation patterns
        continuation_patterns = [
            # Current text continues previous thought
            (text2.startswith(("and", "but", "however", "also", "then", "so")), 0.3),
            (text2.startswith(("because", "since", "although", "while", "if")), 0.2),
            # Previous text seems incomplete
            (text1.endswith((",", "and", "but", "or", "with", "for", "to")), 0.2),
            # Similar sentence structure
            (len(words1) > 0 and len(words2) > 0 and words1.issubset(words2.union(words1)), 0.1),
        ]

        for condition, bonus in continuation_patterns:
            if condition:
                continuation_bonus = max(continuation_bonus, bonus)

        # Weighted combination
        final_similarity = seq_similarity * 0.4 + word_overlap * 0.4 + continuation_bonus * 0.2

        return min(1.0, final_similarity)

    def _get_current_window_info(self) -> Optional[Dict[str, Any]]:
        """Get current window information"""
        if not self._window_detector:
            return None

        window_info = self._window_detector.get_current_window()
        if window_info:
            return {
                "process_name": window_info.process_name,
                "window_title": window_info.window_title,
                "window_class": window_info.window_class,
                "app_type": window_info.app_type,
            }
        return None

    def _get_cursor_position(self) -> Optional[Tuple[int, int]]:
        """Get current cursor position"""
        if not self._cursor_detector:
            return None

        return self._cursor_detector.get_cursor_position()

    def register_user_action(self, action: str):
        """
        Register a user action (Enter, Tab, Escape, etc.)

        Args:
            action: The user action that occurred
        """
        self.user_actions.append(action)
        # Keep only recent actions (last 5)
        if len(self.user_actions) > 5:
            self.user_actions.pop(0)

        logger.debug(f"User action registered: {action}")

    def clear_context(self):
        """Clear all context (useful when starting fresh)"""
        self.previous_context = None
        self.user_actions.clear()
        logger.debug("Thought linking context cleared")

    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about current state"""
        return {
            "enabled": self.enabled,
            "has_previous_context": self.previous_context is not None,
            "recent_user_actions": self.user_actions.copy(),
            "thresholds": {
                "cursor_movement": self.cursor_movement_threshold,
                "similarity": self.similarity_threshold,
                "timeout": self.timeout_threshold,
            },
        }


def create_thought_linker(**kwargs) -> ThoughtLinker:
    """Factory function for thought linker (matches original interface)"""
    return ThoughtLinker(**kwargs)
