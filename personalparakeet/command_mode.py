"""
Command Mode Engine for PersonalParakeet v2

This module implements the "Command Mode" feature described in the architectural brief.
It uses a two-step activation pattern to ensure reliable command execution without false positives:

1. User says activation phrase ("Parakeet Command")
2. System enters command listening mode with visual feedback
3. User says the actual command
4. System executes command and returns to normal mode

Architecture Philosophy:
- Strict two-step pattern prioritizes reliability over conversational fluidity
- Clear visual feedback for command states
- Configurable activation phrase for user preference
- Comprehensive logging for debugging
"""

import time
import logging
import re
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum


class CommandModeState(Enum):
    """Command mode states"""
    INACTIVE = "inactive"              # Normal dictation mode
    LISTENING_FOR_ACTIVATION = "listening_for_activation"  # Always listening for activation phrase
    WAITING_FOR_COMMAND = "waiting_for_command"            # Activation detected, waiting for command
    EXECUTING_COMMAND = "executing_command"                # Command being executed


class CommandConfidence(Enum):
    """Command detection confidence levels"""
    HIGH = "high"       # 0.8-1.0 - Execute immediately
    MEDIUM = "medium"   # 0.6-0.8 - Execute with confirmation
    LOW = "low"         # 0.3-0.6 - Request clarification
    NONE = "none"       # 0.0-0.3 - Not a command


@dataclass
class CommandMatch:
    """Represents a detected command match"""
    command_id: str
    confidence: float
    original_text: str
    matched_pattern: str
    parameters: Dict[str, Any]
    description: str


@dataclass
class CommandDefinition:
    """Definition of a voice command"""
    command_id: str
    patterns: List[str]  # Regex patterns that match this command
    description: str
    parameters: Dict[str, Any] = None
    confidence_threshold: float = 0.7


class CommandModeEngine:
    """
    Command Mode Engine with "Parakeet Command" activation pattern
    
    Implements reliable voice command detection using a two-step activation process
    to minimize false positives while maintaining accuracy.
    """
    
    def __init__(self, 
                 activation_phrase: str = "parakeet command",
                 activation_confidence_threshold: float = 0.8,
                 command_timeout: float = 5.0):
        """
        Initialize Command Mode Engine
        
        Args:
            activation_phrase: The phrase that activates command mode
            activation_confidence_threshold: Minimum confidence for activation detection
            command_timeout: Seconds to wait for command after activation
        """
        self.activation_phrase = activation_phrase.lower()
        self.activation_confidence_threshold = activation_confidence_threshold
        self.command_timeout = command_timeout
        
        # Setup logging with defensive initialization FIRST
        self.logger = logging.getLogger(__name__)
        
        # Ensure basic logging is configured
        if not self.logger.handlers and not logging.getLogger().handlers:
            logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        
        # State management
        self.state = CommandModeState.LISTENING_FOR_ACTIVATION
        self.activation_time: Optional[float] = None
        self.last_command_result: Optional[Dict[str, Any]] = None
        
        # Command registry (after logger is set up)
        self.commands: Dict[str, CommandDefinition] = {}
        self._register_default_commands()
        
        # Callbacks
        self.on_activation_detected: Optional[Callable] = None
        self.on_command_executed: Optional[Callable] = None
        self.on_command_timeout: Optional[Callable] = None
        self.on_state_changed: Optional[Callable] = None
        
        self.logger.info(f"Command Mode Engine initialized with activation phrase: '{self.activation_phrase}'")
    
    def _register_default_commands(self):
        """Register default voice commands"""
        default_commands = [
            # Text management commands
            CommandDefinition(
                command_id="commit_text",
                patterns=[
                    r'\b(?:commit|send|enter)\s+text\b',
                    r'\b(?:commit|send|enter)\s+it\b',
                    r'\bcommit\b',
                    r'\bsend\s+it\b'
                ],
                description="Commit current text and inject into application"
            ),
            CommandDefinition(
                command_id="clear_text", 
                patterns=[
                    r'\b(?:clear|delete|erase)\s+text\b',
                    r'\b(?:clear|delete|erase)\s+it\b',
                    r'\bclear\s+all\b',
                    r'\bdelete\s+everything\b'
                ],
                description="Clear current text without committing"
            ),
            
            # Clarity Engine commands
            CommandDefinition(
                command_id="enable_clarity",
                patterns=[
                    r'\b(?:enable|turn\s+on)\s+clarity\b',
                    r'\b(?:enable|turn\s+on)\s+corrections\b'
                ],
                description="Enable Clarity Engine text corrections"
            ),
            CommandDefinition(
                command_id="disable_clarity",
                patterns=[
                    r'\b(?:disable|turn\s+off)\s+clarity\b',
                    r'\b(?:disable|turn\s+off)\s+corrections\b'
                ],
                description="Disable Clarity Engine text corrections"
            ),
            CommandDefinition(
                command_id="toggle_clarity",
                patterns=[
                    r'\btoggle\s+clarity\b',
                    r'\btoggle\s+corrections\b'
                ],
                description="Toggle Clarity Engine on/off"
            ),
            
            # Dictation control commands
            CommandDefinition(
                command_id="start_listening",
                patterns=[
                    r'\b(?:start|begin)\s+(?:listening|dictation)\b',
                    r'\bstart\s+recording\b'
                ],
                description="Start dictation system"
            ),
            CommandDefinition(
                command_id="stop_listening",
                patterns=[
                    r'\b(?:stop|end)\s+(?:listening|dictation)\b',
                    r'\bstop\s+recording\b'
                ],
                description="Stop dictation system"
            ),
            
            # Mode control commands
            CommandDefinition(
                command_id="exit_command_mode",
                patterns=[
                    r'\b(?:exit|cancel|nevermind)\b',
                    r'\bgo\s+back\b',
                    r'\breturn\s+to\s+normal\b'
                ],
                description="Exit command mode and return to normal dictation"
            ),
            
            # System commands
            CommandDefinition(
                command_id="show_status",
                patterns=[
                    r'\b(?:show|get)\s+status\b',
                    r'\bwhat\'s\s+the\s+status\b'
                ],
                description="Show current system status"
            )
        ]
        
        for cmd in default_commands:
            self.register_command(cmd)
    
    def register_command(self, command: CommandDefinition):
        """Register a new voice command"""
        self.commands[command.command_id] = command
        self.logger.debug(f"Registered command: {command.command_id}")
    
    def unregister_command(self, command_id: str):
        """Remove a voice command"""
        if command_id in self.commands:
            del self.commands[command_id]
            self.logger.debug(f"Unregistered command: {command_id}")
    
    def process_speech(self, text: str) -> Optional[CommandMatch]:
        """
        Process speech input through the command mode state machine
        
        Args:
            text: Transcribed speech text
            
        Returns:
            CommandMatch if a command was detected and executed, None otherwise
        """
        text_lower = text.lower().strip()
        
        if self.state == CommandModeState.LISTENING_FOR_ACTIVATION:
            return self._check_for_activation(text_lower)
        
        elif self.state == CommandModeState.WAITING_FOR_COMMAND:
            return self._process_command(text_lower)
        
        # In other states, don't process speech for commands
        return None
    
    def _check_for_activation(self, text: str) -> Optional[CommandMatch]:
        """Check if text contains the activation phrase"""
        # Simple activation phrase detection
        activation_confidence = self._calculate_activation_confidence(text)
        
        if activation_confidence >= self.activation_confidence_threshold:
            self.logger.info(f"Activation phrase detected with confidence {activation_confidence:.2f}")
            self._transition_to_command_mode()
            
            # Return a special activation match
            return CommandMatch(
                command_id="activation_detected",
                confidence=activation_confidence,
                original_text=text,
                matched_pattern=self.activation_phrase,
                parameters={},
                description="Command mode activated"
            )
        
        return None
    
    def _calculate_activation_confidence(self, text: str) -> float:
        """Calculate confidence that text contains activation phrase"""
        # Exact match gets highest confidence
        if self.activation_phrase in text:
            return 1.0
        
        # Fuzzy matching for variations
        activation_words = self.activation_phrase.split()
        text_words = text.split()
        
        # Check if all activation words are present
        matches = 0
        for activation_word in activation_words:
            for text_word in text_words:
                # Allow for slight variations
                if (activation_word in text_word or 
                    text_word in activation_word or
                    self._words_similar(activation_word, text_word)):
                    matches += 1
                    break
        
        # Calculate confidence based on word matching
        word_confidence = matches / len(activation_words)
        
        # Bonus for correct word order
        order_bonus = 0.0
        if matches == len(activation_words):
            # Check if words appear in roughly the same order
            activation_positions = []
            for activation_word in activation_words:
                for i, text_word in enumerate(text_words):
                    if (activation_word in text_word or 
                        text_word in activation_word or
                        self._words_similar(activation_word, text_word)):
                        activation_positions.append(i)
                        break
            
            # If positions are in order, give bonus
            if len(activation_positions) == len(activation_words):
                if all(activation_positions[i] <= activation_positions[i+1] 
                      for i in range(len(activation_positions)-1)):
                    order_bonus = 0.2
        
        return min(1.0, word_confidence + order_bonus)
    
    def _words_similar(self, word1: str, word2: str) -> bool:
        """Check if two words are similar (for handling speech recognition errors)"""
        # Simple similarity check for common speech recognition errors
        if len(word1) < 3 or len(word2) < 3:
            return word1 == word2
        
        # Check if one word is contained in the other
        if word1 in word2 or word2 in word1:
            return True
        
        # Check for common substitutions
        substitutions = {
            'parakeet': ['parrot', 'parachute', 'paraquet', 'parrakeet'],
            'command': ['commend', 'commands', 'comment']
        }
        
        for canonical, variants in substitutions.items():
            if word1 == canonical and word2 in variants:
                return True
            if word2 == canonical and word1 in variants:
                return True
        
        return False
    
    def _transition_to_command_mode(self):
        """Transition to command waiting state"""
        self.state = CommandModeState.WAITING_FOR_COMMAND
        self.activation_time = time.time()
        
        self.logger.info("Entered command waiting mode")
        
        # Trigger callback for UI feedback
        if self.on_activation_detected:
            self.on_activation_detected()
        
        if self.on_state_changed:
            self.on_state_changed(self.state)
    
    def _process_command(self, text: str) -> Optional[CommandMatch]:
        """Process text as a potential command"""
        # Check for timeout
        if self.activation_time and (time.time() - self.activation_time) > self.command_timeout:
            self.logger.info("Command mode timeout - returning to normal mode")
            self._return_to_normal_mode()
            if self.on_command_timeout:
                self.on_command_timeout()
            return None
        
        # Try to match against registered commands
        best_match = None
        best_confidence = 0.0
        
        for command_id, command_def in self.commands.items():
            confidence = self._calculate_command_confidence(text, command_def)
            
            if confidence > best_confidence and confidence >= command_def.confidence_threshold:
                best_confidence = confidence
                best_match = CommandMatch(
                    command_id=command_id,
                    confidence=confidence,
                    original_text=text,
                    matched_pattern="",  # Would need to track which pattern matched
                    parameters={},
                    description=command_def.description
                )
        
        if best_match:
            self.logger.info(f"Command detected: {best_match.command_id} (confidence: {best_match.confidence:.2f})")
            self._execute_command(best_match)
            return best_match
        else:
            self.logger.info(f"No command matched for: '{text}'")
            # Return to normal mode after failed command
            self._return_to_normal_mode()
            return None
    
    def _calculate_command_confidence(self, text: str, command_def: CommandDefinition) -> float:
        """Calculate confidence that text matches a command definition"""
        best_confidence = 0.0
        
        for pattern in command_def.patterns:
            try:
                # Check for regex match
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Calculate confidence based on match quality
                    match_length = len(match.group(0))
                    text_length = len(text)
                    
                    # Higher confidence for matches that cover more of the text
                    coverage = match_length / text_length
                    confidence = min(1.0, coverage + 0.3)  # Boost for any match
                    
                    best_confidence = max(best_confidence, confidence)
                    
            except re.error:
                self.logger.warning(f"Invalid regex pattern: {pattern}")
                continue
        
        return best_confidence
    
    def _execute_command(self, command_match: CommandMatch):
        """Execute a detected command"""
        self.state = CommandModeState.EXECUTING_COMMAND
        
        try:
            # Store result for callback
            self.last_command_result = {
                "command_id": command_match.command_id,
                "confidence": command_match.confidence,
                "original_text": command_match.original_text,
                "status": "success",
                "description": command_match.description
            }
            
            # Trigger execution callback
            if self.on_command_executed:
                self.on_command_executed(command_match)
            
            self.logger.info(f"Command executed: {command_match.command_id}")
            
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            self.last_command_result = {
                "command_id": command_match.command_id,
                "confidence": command_match.confidence,
                "original_text": command_match.original_text,
                "status": "error",
                "error": str(e)
            }
        
        finally:
            # Always return to normal mode after command execution
            self._return_to_normal_mode()
    
    def _return_to_normal_mode(self):
        """Return to normal dictation mode"""
        self.state = CommandModeState.LISTENING_FOR_ACTIVATION
        self.activation_time = None
        
        self.logger.debug("Returned to normal dictation mode")
        
        if self.on_state_changed:
            self.on_state_changed(self.state)
    
    def force_exit_command_mode(self):
        """Force exit from command mode (useful for emergency situations)"""
        self.logger.info("Force exit from command mode")
        self._return_to_normal_mode()
    
    def is_in_command_mode(self) -> bool:
        """Check if currently in command mode"""
        return self.state in [CommandModeState.WAITING_FOR_COMMAND, CommandModeState.EXECUTING_COMMAND]
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information"""
        return {
            "state": self.state.value,
            "activation_phrase": self.activation_phrase,
            "is_in_command_mode": self.is_in_command_mode(),
            "activation_time": self.activation_time,
            "command_timeout": self.command_timeout,
            "last_command_result": self.last_command_result,
            "registered_commands": list(self.commands.keys())
        }


# Convenience function for easy integration
def create_command_mode_engine(**kwargs) -> CommandModeEngine:
    """Create a new CommandModeEngine with optional configuration"""
    return CommandModeEngine(**kwargs)