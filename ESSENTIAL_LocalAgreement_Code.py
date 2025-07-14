# LocalAgreement Buffer - Core Implementation
# Essential code for committed vs pending text logic

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import deque, defaultdict

@dataclass
class TextState:
    """Represents the current state of text processing."""
    committed: str = ""
    pending: str = ""
    full_text: str = ""
    newly_committed: str = ""
    confidence_score: float = 0.0
    processing_time_ms: float = 0.0

class LocalAgreementBuffer:
    """
    LocalAgreement-n text buffering system for real-time transcription.
    
    Prevents jarring text rewrites by tracking word stability across
    multiple transcription updates and only committing text that has
    achieved sufficient agreement.
    """
    
    def __init__(self, 
                 agreement_threshold: int = 3,
                 max_pending_words: int = 20,
                 word_timeout_seconds: float = 5.0,
                 position_tolerance: int = 2):
        """
        Initialize the LocalAgreement buffer.
        
        Args:
            agreement_threshold: Number of consecutive agreements needed to commit text
            max_pending_words: Maximum number of pending words to track
            word_timeout_seconds: Time after which pending words are automatically committed
            position_tolerance: Allow word position shifts within this range
        """
        self.agreement_threshold = agreement_threshold
        self.max_pending_words = max_pending_words
        self.word_timeout_seconds = word_timeout_seconds
        self.position_tolerance = position_tolerance
        
        # Core state
        self.committed_text = ""
        self.pending_words: List[str] = []
        
        # Agreement tracking: position -> word -> count
        self.word_agreements: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Timestamp tracking for timeout handling
        self.word_timestamps: Dict[Tuple[int, str], float] = {}
        
        # History for debugging and analysis
        self.transcription_history: deque = deque(maxlen=10)
        
        # Performance metrics
        self.total_updates = 0
        self.words_committed = 0
    
    def update_transcription(self, new_transcription: str) -> TextState:
        """
        Process a new transcription and update the buffer state.
        
        Args:
            new_transcription: The latest transcription result
            
        Returns:
            TextState object containing committed/pending text and metadata
        """
        start_time = time.time()
        
        # Normalize input
        words = self._normalize_transcription(new_transcription)
        
        # Track this update
        self.total_updates += 1
        self.transcription_history.append({
            'words': words,
            'timestamp': start_time,
            'raw_text': new_transcription
        })
        
        # Process word agreements
        newly_committed = self._process_word_agreements(words)
        
        # Handle timeouts
        self._handle_word_timeouts(start_time)
        
        # Update pending text
        self._update_pending_words(words)
        
        # Calculate metrics
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        confidence = self._calculate_confidence_score()
        
        # Create result state
        state = TextState(
            committed=self.committed_text,
            pending=" ".join(self.pending_words),
            full_text=self.committed_text + " " + " ".join(self.pending_words),
            newly_committed=newly_committed,
            confidence_score=confidence,
            processing_time_ms=processing_time
        )
        
        return state
    
    def _normalize_transcription(self, text: str) -> List[str]:
        """Normalize transcription text into clean word list."""
        # Basic cleaning - extend as needed
        text = text.strip().lower()
        # Remove common transcription artifacts
        text = text.replace("[unk]", "").replace("<unk>", "")
        # Split into words and filter empty
        words = [word.strip() for word in text.split() if word.strip()]
        return words
    
    def _process_word_agreements(self, words: List[str]) -> str:
        """
        Process word agreements and identify newly committed text.
        
        Returns:
            String of newly committed text
        """
        newly_committed_words = []
        current_time = time.time()
        
        # Track agreements for each word position
        for position, word in enumerate(words):
            # Increment agreement count
            self.word_agreements[position][word] += 1
            self.word_timestamps[(position, word)] = current_time
            
            # Check if this word position has reached agreement threshold
            if self.word_agreements[position][word] >= self.agreement_threshold:
                # Check if this extends our committed text
                if self._can_commit_word_at_position(position, word):
                    newly_committed_words.append(word)
                    self.words_committed += 1
        
        # Update committed text with newly committed words
        if newly_committed_words:
            new_committed_text = " ".join(newly_committed_words)
            if self.committed_text:
                self.committed_text += " " + new_committed_text
            else:
                self.committed_text = new_committed_text
                
            # Clean up agreement tracking for committed positions
            self._cleanup_committed_positions(len(newly_committed_words))
            
            return new_committed_text
        
        return ""
    
    def _can_commit_word_at_position(self, position: int, word: str) -> bool:
        """
        Determine if a word at a given position can be committed.
        
        This ensures we commit words in order and handle position shifts gracefully.
        """
        # Calculate expected position based on current committed text
        committed_word_count = len(self.committed_text.split()) if self.committed_text else 0
        
        # Allow some position tolerance for handling transcription variations
        expected_position_min = committed_word_count
        expected_position_max = committed_word_count + self.position_tolerance
        
        return expected_position_min <= position <= expected_position_max
    
    def _handle_word_timeouts(self, current_time: float):
        """Force commit words that have been pending too long."""
        if not self.word_timeout_seconds:
            return
            
        timed_out_words = []
        
        for (position, word), timestamp in list(self.word_timestamps.items()):
            if current_time - timestamp > self.word_timeout_seconds:
                if self._can_commit_word_at_position(position, word):
                    timed_out_words.append((position, word))
        
        # Commit timed out words
        for position, word in sorted(timed_out_words):
            if self.committed_text:
                self.committed_text += " " + word
            else:
                self.committed_text = word
            self.words_committed += 1
            
            # Clean up
            del self.word_timestamps[(position, word)]
            if position in self.word_agreements:
                self.word_agreements[position].clear()
    
    def _update_pending_words(self, words: List[str]):
        """Update the pending words list based on current transcription."""
        committed_word_count = len(self.committed_text.split()) if self.committed_text else 0
        
        # Pending words are those beyond the committed portion
        if len(words) > committed_word_count:
            self.pending_words = words[committed_word_count:]
        else:
            self.pending_words = []
        
        # Limit pending words to prevent unbounded growth
        if len(self.pending_words) > self.max_pending_words:
            self.pending_words = self.pending_words[:self.max_pending_words]
    
    def _cleanup_committed_positions(self, num_committed: int):
        """Clean up agreement tracking for positions that have been committed."""
        committed_word_count = len(self.committed_text.split()) if self.committed_text else 0
        positions_to_clean = range(committed_word_count - num_committed, committed_word_count)
        
        for position in positions_to_clean:
            if position in self.word_agreements:
                del self.word_agreements[position]
        
        # Clean up timestamps for committed positions
        for (pos, word) in list(self.word_timestamps.keys()):
            if pos in positions_to_clean:
                del self.word_timestamps[(pos, word)]
    
    def _calculate_confidence_score(self) -> float:
        """Calculate a confidence score based on agreement patterns."""
        if not self.word_agreements:
            return 0.0
        
        total_positions = len(self.word_agreements)
        high_agreement_positions = 0
        
        for position_agreements in self.word_agreements.values():
            if position_agreements:
                max_agreement = max(position_agreements.values())
                if max_agreement >= self.agreement_threshold - 1:
                    high_agreement_positions += 1
        
        return high_agreement_positions / total_positions if total_positions > 0 else 0.0
    
    def reset_session(self):
        """Reset the buffer for a new dictation session."""
        self.committed_text = ""
        self.pending_words = []
        self.word_agreements.clear()
        self.word_timestamps.clear()
        self.transcription_history.clear()

# Integration helper class
class TranscriptionProcessor:
    """
    Higher-level processor that integrates LocalAgreement buffering
    with the existing Parakeet transcription system.
    """
    
    def __init__(self, 
                 agreement_threshold: int = 3,
                 enable_visual_feedback: bool = True):
        self.buffer = LocalAgreementBuffer(agreement_threshold=agreement_threshold)
        self.enable_visual_feedback = enable_visual_feedback
        
        # Callback hooks for integration
        self.on_committed_text = None  # Called when new text is committed
        self.on_state_update = None    # Called on every state update
        
    def process_transcription(self, raw_transcription: str) -> TextState:
        """Process a raw transcription through the agreement buffer."""
        state = self.buffer.update_transcription(raw_transcription)
        
        # Trigger callbacks
        if self.on_state_update:
            self.on_state_update(state)
            
        if state.newly_committed and self.on_committed_text:
            self.on_committed_text(state.newly_committed)
        
        # Visual feedback (optional)
        if self.enable_visual_feedback and state.newly_committed:
            print(f"✅ Committed: '{state.newly_committed}'")
            if state.pending:
                print(f"⏳ Pending: '{state.pending}'")
        
        return state
    
    def set_text_output_callback(self, callback):
        """Set callback for when new text should be output to the system."""
        self.on_committed_text = callback
    
    def get_display_text(self) -> Tuple[str, str]:
        """Get text formatted for display (committed, pending)."""
        return self.buffer.committed_text, " ".join(self.buffer.pending_words)

# Basic usage example
if __name__ == "__main__":
    processor = TranscriptionProcessor(agreement_threshold=3)
    
    # Set up text output callback
    def output_committed_text(text):
        print(f"OUTPUT: {text}")
    
    processor.set_text_output_callback(output_committed_text)
    
    # Simulate transcription updates
    transcriptions = [
        "hello",
        "hello world",
        "hello world this",
        "hello world this is", 
        "hello world this is a test"
    ]
    
    for transcription in transcriptions:
        state = processor.process_transcription(transcription)
        print(f"Committed: '{state.committed}' | Pending: '{state.pending}'")
