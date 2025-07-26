"""
Intelligent Thought-Linking Engine for PersonalParakeet v2

This module implements the "Intelligent Thought-Linking" feature described in the 
architectural brief. It decides whether consecutive utterances should be linked 
as a single thought or treated as separate paragraphs.

Architecture Philosophy:
- Primary signals (high priority): User actions, window changes, cursor movement
- Secondary signal (lower priority): Semantic similarity analysis
- Transparent decision making with logging for debugging
"""

import time
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
import difflib

# Try to import application detection for window change detection
try:
    from .application_detection import detect_current_application, ApplicationInfo
    WINDOW_DETECTION_AVAILABLE = True
except ImportError:
    WINDOW_DETECTION_AVAILABLE = False

# Try to import cursor position detection
try:
    import win32gui
    import win32api
    CURSOR_DETECTION_AVAILABLE = True
except ImportError:
    CURSOR_DETECTION_AVAILABLE = False


class LinkingDecision(Enum):
    """Possible thought-linking decisions"""
    APPEND_WITH_SPACE = "append_with_space"
    START_NEW_PARAGRAPH = "start_new_paragraph"
    START_NEW_THOUGHT = "start_new_thought"


class SignalType(Enum):
    """Types of contextual signals"""
    USER_INPUT = "user_input"          # Enter, Tab, Escape pressed
    WINDOW_CHANGE = "window_change"    # Active application changed
    CURSOR_MOVEMENT = "cursor_movement" # Cursor position changed significantly
    SEMANTIC_SIMILARITY = "semantic_similarity"  # Text similarity analysis
    TIMEOUT = "timeout"                # Time-based separation


@dataclass
class ThoughtContext:
    """Context information for thought-linking decisions"""
    text: str
    timestamp: float
    window_info: Optional[Dict[str, Any]] = None
    cursor_position: Optional[Tuple[int, int]] = None
    user_action: Optional[str] = None


@dataclass
class LinkingSignal:
    """A contextual signal that influences linking decisions"""
    signal_type: SignalType
    strength: float  # 0.0 to 1.0
    description: str
    data: Optional[Dict[str, Any]] = None


class IntelligentThoughtLinker:
    """
    Intelligent Thought-Linking Engine
    
    Analyzes contextual signals to determine how consecutive utterances 
    should be linked together.
    """
    
    def __init__(self, 
                 cursor_movement_threshold: int = 100,
                 similarity_threshold: float = 0.3,
                 timeout_threshold: float = 30.0):
        """
        Initialize the thought linker
        
        Args:
            cursor_movement_threshold: Pixels of cursor movement to trigger new thought
            similarity_threshold: Minimum similarity to consider texts related
            timeout_threshold: Seconds after which to start new thought
        """
        self.cursor_movement_threshold = cursor_movement_threshold
        self.similarity_threshold = similarity_threshold  
        self.timeout_threshold = timeout_threshold
        
        # Context tracking
        self.previous_context: Optional[ThoughtContext] = None
        self.user_actions: List[str] = []  # Track recent user actions
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Intelligent Thought Linker initialized")
        
        # Log capability status
        self.logger.info(f"Window detection: {WINDOW_DETECTION_AVAILABLE}")
        self.logger.info(f"Cursor detection: {CURSOR_DETECTION_AVAILABLE}")
    
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
        
        self.logger.debug(f"User action registered: {action}")
    
    def should_link_thoughts(self, new_text: str) -> Tuple[LinkingDecision, List[LinkingSignal]]:
        """
        Determine how the new text should be linked with previous context
        
        Args:
            new_text: The newly transcribed text
            
        Returns:
            Tuple of (decision, signals_considered)
        """
        current_time = time.time()
        signals = []
        
        # Create current context
        current_context = ThoughtContext(
            text=new_text,
            timestamp=current_time,
            window_info=self._get_current_window_info(),
            cursor_position=self._get_cursor_position()
        )
        
        # If no previous context, always start new thought
        if self.previous_context is None:
            self.previous_context = current_context
            return LinkingDecision.START_NEW_THOUGHT, signals
        
        # PRIMARY SIGNALS (High Priority)
        
        # 1. Check for recent user actions
        user_signal = self._check_user_actions()
        if user_signal:
            signals.append(user_signal)
            if user_signal.strength >= 0.8:  # Strong user signal
                self.previous_context = current_context
                return LinkingDecision.START_NEW_PARAGRAPH, signals
        
        # 2. Check for window changes
        window_signal = self._check_window_change(current_context)
        if window_signal:
            signals.append(window_signal)
            if window_signal.strength >= 0.9:  # Strong window change signal
                self.previous_context = current_context
                return LinkingDecision.START_NEW_THOUGHT, signals
        
        # 3. Check for significant cursor movement
        cursor_signal = self._check_cursor_movement(current_context)
        if cursor_signal:
            signals.append(cursor_signal)
            if cursor_signal.strength >= 0.7:  # Strong cursor movement signal
                self.previous_context = current_context
                return LinkingDecision.START_NEW_PARAGRAPH, signals
        
        # 4. Check for timeout
        timeout_signal = self._check_timeout(current_context)
        if timeout_signal:
            signals.append(timeout_signal)
            if timeout_signal.strength >= 0.6:  # Moderate timeout signal
                self.previous_context = current_context
                return LinkingDecision.START_NEW_PARAGRAPH, signals
        
        # SECONDARY SIGNAL (Lower Priority)
        
        # 5. Semantic similarity check
        similarity_signal = self._check_semantic_similarity(current_context)
        if similarity_signal:
            signals.append(similarity_signal)
            
            # If texts are highly related, append with space
            if similarity_signal.strength >= self.similarity_threshold:
                self.previous_context = current_context
                return LinkingDecision.APPEND_WITH_SPACE, signals
            else:
                # Not very related, start new paragraph
                self.previous_context = current_context
                return LinkingDecision.START_NEW_PARAGRAPH, signals
        
        # DEFAULT: If no strong signals, append with space
        self.previous_context = current_context
        return LinkingDecision.APPEND_WITH_SPACE, signals
    
    def _check_user_actions(self) -> Optional[LinkingSignal]:
        """Check if user performed any actions that indicate new thought"""
        if not self.user_actions:
            return None
        
        recent_action = self.user_actions[-1]
        
        # Strong separation actions
        if recent_action.lower() in ['enter', 'return', 'tab', 'escape']:
            return LinkingSignal(
                signal_type=SignalType.USER_INPUT,
                strength=0.9,
                description=f"User pressed {recent_action}",
                data={"action": recent_action}
            )
        
        # Moderate separation actions
        if recent_action.lower() in ['ctrl+enter', 'shift+enter']:
            return LinkingSignal(
                signal_type=SignalType.USER_INPUT,
                strength=0.7,
                description=f"User pressed {recent_action}",
                data={"action": recent_action}
            )
        
        return None
    
    def _check_window_change(self, current_context: ThoughtContext) -> Optional[LinkingSignal]:
        """Check if the active window has changed"""
        if not WINDOW_DETECTION_AVAILABLE:
            return None
        
        if not self.previous_context or not self.previous_context.window_info:
            return None
        
        current_window = current_context.window_info
        previous_window = self.previous_context.window_info
        
        if not current_window or not previous_window:
            return None
        
        # Check for window change
        if (current_window.get('process_name') != previous_window.get('process_name') or
            current_window.get('window_title') != previous_window.get('window_title')):
            
            return LinkingSignal(
                signal_type=SignalType.WINDOW_CHANGE,
                strength=0.95,
                description=f"Window changed from {previous_window.get('process_name')} to {current_window.get('process_name')}",
                data={"previous": previous_window, "current": current_window}
            )
        
        return None
    
    def _check_cursor_movement(self, current_context: ThoughtContext) -> Optional[LinkingSignal]:
        """Check if cursor has moved significantly"""
        if not CURSOR_DETECTION_AVAILABLE:
            return None
        
        if (not self.previous_context or 
            not self.previous_context.cursor_position or 
            not current_context.cursor_position):
            return None
        
        prev_x, prev_y = self.previous_context.cursor_position
        curr_x, curr_y = current_context.cursor_position
        
        # Calculate distance moved
        distance = ((curr_x - prev_x) ** 2 + (curr_y - prev_y) ** 2) ** 0.5
        
        if distance >= self.cursor_movement_threshold:
            # Calculate strength based on distance
            strength = min(0.8, distance / (self.cursor_movement_threshold * 2))
            
            return LinkingSignal(
                signal_type=SignalType.CURSOR_MOVEMENT,
                strength=strength,
                description=f"Cursor moved {distance:.0f} pixels",
                data={"distance": distance, "previous": self.previous_context.cursor_position, "current": current_context.cursor_position}
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
                data={"time_difference": time_diff}
            )
        
        return None
    
    def _check_semantic_similarity(self, current_context: ThoughtContext) -> Optional[LinkingSignal]:
        """Check semantic similarity between current and previous text"""
        if not self.previous_context:
            return None
        
        prev_text = self.previous_context.text.lower().strip()
        curr_text = current_context.text.lower().strip()
        
        if not prev_text or not curr_text:
            return None
        
        # Use simple similarity based on common words and sequence matching
        similarity = self._calculate_text_similarity(prev_text, curr_text)
        
        return LinkingSignal(
            signal_type=SignalType.SEMANTIC_SIMILARITY,
            strength=similarity,
            description=f"Text similarity: {similarity:.2f}",
            data={"similarity": similarity, "previous_text": prev_text, "current_text": curr_text}
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
            (text2.startswith(('and', 'but', 'however', 'also', 'then', 'so')), 0.3),
            (text2.startswith(('because', 'since', 'although', 'while', 'if')), 0.2),
            # Previous text seems incomplete
            (text1.endswith((',', 'and', 'but', 'or', 'with', 'for', 'to')), 0.2),
            # Similar sentence structure
            (len(words1) > 0 and len(words2) > 0 and words1.issubset(words2.union(words1)), 0.1)
        ]
        
        for condition, bonus in continuation_patterns:
            if condition:
                continuation_bonus = max(continuation_bonus, bonus)
        
        # Weighted combination
        final_similarity = (seq_similarity * 0.4 + 
                          word_overlap * 0.4 + 
                          continuation_bonus * 0.2)
        
        return min(1.0, final_similarity)
    
    def _get_current_window_info(self) -> Optional[Dict[str, Any]]:
        """Get current window information"""
        if not WINDOW_DETECTION_AVAILABLE:
            return None
        
        try:
            app_info = detect_current_application()
            return {
                'process_name': app_info.process_name,
                'window_title': app_info.window_title,
                'window_class': getattr(app_info, 'window_class', ''),
                'app_type': app_info.app_type.name if hasattr(app_info.app_type, 'name') else str(app_info.app_type)
            }
        except Exception as e:
            self.logger.warning(f"Failed to get window info: {e}")
            return None
    
    def _get_cursor_position(self) -> Optional[Tuple[int, int]]:
        """Get current cursor position"""
        if not CURSOR_DETECTION_AVAILABLE:
            return None
        
        try:
            x, y = win32api.GetCursorPos()
            return (x, y)
        except Exception as e:
            self.logger.warning(f"Failed to get cursor position: {e}")
            return None
    
    def clear_context(self):
        """Clear all context (useful when starting fresh)"""
        self.previous_context = None
        self.user_actions.clear()
        self.logger.debug("Thought linking context cleared")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about current state"""
        return {
            'has_previous_context': self.previous_context is not None,
            'recent_user_actions': self.user_actions.copy(),
            'window_detection_available': WINDOW_DETECTION_AVAILABLE,
            'cursor_detection_available': CURSOR_DETECTION_AVAILABLE,
            'thresholds': {
                'cursor_movement': self.cursor_movement_threshold,
                'similarity': self.similarity_threshold,
                'timeout': self.timeout_threshold
            }
        }


# Convenience function for easy integration
def create_thought_linker(**kwargs) -> IntelligentThoughtLinker:
    """Create a new IntelligentThoughtLinker with optional configuration"""
    return IntelligentThoughtLinker(**kwargs)