#!/usr/bin/env python3
"""
AudioEngine - Producer-Consumer Audio Pipeline for PersonalParakeet v3
Replaces WebSocket architecture with direct function calls
"""

import asyncio
import logging
import threading
import queue
import time
from typing import Callable, Optional

import sounddevice as sd
import numpy as np

from core.stt_processor_mock import STTProcessor  # Using mock for testing without NeMo
from core.clarity_engine import ClarityEngine
from core.vad_engine import VoiceActivityDetector
from core.command_processor import CommandProcessor, create_command_processor
from config import V3Config

logger = logging.getLogger(__name__)


class AudioEngine:
    """
    Audio processing engine with producer-consumer architecture
    Manages audio capture, STT processing, and text corrections
    """
    
    def __init__(self, config: V3Config, event_loop=None):
        self.config = config
        self.event_loop = event_loop
        self.is_running = False
        self.is_listening = False
        
        # Audio processing
        self.audio_queue = queue.Queue(maxsize=50)
        self.audio_stream = None
        self.audio_thread = None
        
        # Core components
        self.stt_processor = None
        self.clarity_engine = None
        self.vad_engine = None
        self.command_processor = None
        
        # Callbacks for UI updates (set by DictationView)
        self.on_raw_transcription = None
        self.on_corrected_transcription = None
        self.on_pause_detected = None
        self.on_vad_status = None
        self.on_error = None
        self.on_command_mode_status = None
        
        # State tracking
        self.current_text = ""
        self.clarity_enabled = True
        
    async def initialize(self):
        """Initialize all audio processing components"""
        try:
            logger.info("Initializing AudioEngine...")
            
            # Initialize STT processor
            self.stt_processor = STTProcessor(self.config)
            await self.stt_processor.initialize()
            
            # Initialize Clarity Engine
            self.clarity_engine = ClarityEngine(enable_rule_based=True)
            await self.clarity_engine.initialize()
            self.clarity_engine.start_worker()
            
            # Initialize VAD Engine
            self.vad_engine = VoiceActivityDetector(
                sample_rate=self.config.audio.sample_rate,
                silence_threshold=self.config.vad.silence_threshold,
                pause_threshold=self.config.vad.pause_threshold
            )
            self.vad_engine.on_pause_detected = self._handle_pause_detected
            
            # Initialize Command Processor
            self.command_processor = create_command_processor(
                activation_phrase=self.config.command_mode.activation_phrase,
                activation_confidence_threshold=self.config.command_mode.confidence_threshold,
                command_timeout=self.config.command_mode.timeout
            )
            
            # Set up command processor callbacks
            self.command_processor.on_command_mode_status_changed = self._on_command_mode_status_changed
            self.command_processor.on_activation_detected = self._on_command_activation_detected
            self.command_processor.on_command_executed = self._on_command_executed
            self.command_processor.on_command_timeout = self._on_command_timeout
            
            # Set up audio/visual feedback callbacks
            self.command_processor.on_audio_feedback = self._on_audio_feedback
            self.command_processor.on_visual_feedback = self._on_visual_feedback
            
            # Set up confirmation callback
            self.command_processor.on_confirmation_request = self._on_confirmation_request
            
            # Set up specific command callbacks
            self.command_processor.on_commit_text = self._on_commit_text_command
            self.command_processor.on_clear_text = self._on_clear_text_command
            self.command_processor.on_toggle_clarity = self._on_toggle_clarity_command
            self.command_processor.on_enable_clarity = self._on_enable_clarity_command
            self.command_processor.on_disable_clarity = self._on_disable_clarity_command
            
            self.is_running = True
            logger.info("AudioEngine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AudioEngine: {e}")
            raise
    
    async def start(self):
        """Start audio processing"""
        if not self.is_running:
            raise RuntimeError("AudioEngine not initialized")
        
        if self.is_listening:
            logger.warning("Already listening")
            return
            
        logger.info("Starting audio processing...")
        
        # Start audio processing thread
        self.audio_thread = threading.Thread(target=self._audio_processing_loop, daemon=True)
        self.audio_thread.start()
        
        # Start audio stream
        self.audio_stream = sd.InputStream(
            device=self.config.audio.device_index,
            samplerate=self.config.audio.sample_rate,
            channels=1,
            dtype=np.float32,
            callback=self._audio_callback,
            blocksize=self.config.audio.chunk_size
        )
        self.audio_stream.start()
        
        self.is_listening = True
        logger.info("Audio processing started")
    
    async def stop(self):
        """Stop audio processing"""
        if not self.is_listening:
            return
            
        logger.info("Stopping audio processing...")
        self.is_listening = False
        
        # Stop audio stream
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None
        
        # Wait for processing thread
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2.0)
        
        # Clear audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
        logger.info("Audio processing stopped")
    
    def _audio_callback(self, indata, frames, time, status):
        """Audio input callback - producer side of pipeline"""
        if status:
            logger.warning(f"Audio status: {status}")
        
        if self.is_listening:
            try:
                # Convert to float32 and add to queue
                audio_chunk = indata[:, 0].astype(np.float32)
                
                if not self.audio_queue.full():
                    self.audio_queue.put(audio_chunk.copy())
                else:
                    logger.warning("Audio queue full, dropping chunk")
                    
            except Exception as e:
                logger.error(f"Audio callback error: {e}")
    
    def _audio_processing_loop(self):
        """Background audio processing - consumer side of pipeline"""
        logger.info("Audio processing loop started")
        
        while self.is_listening:
            try:
                # Get audio chunk from queue
                audio_chunk = self.audio_queue.get(timeout=0.5)
                
                # Process VAD
                vad_status = self.vad_engine.process_audio_frame(audio_chunk)
                self._update_vad_status(vad_status)
                
                # Check if audio is loud enough for STT
                max_level = np.max(np.abs(audio_chunk))
                if max_level < self.config.audio.silence_threshold:
                    continue
                
                # Process through STT (synchronous in worker thread)
                text = self._process_stt_sync(audio_chunk)
                if text and text.strip():
                    self._handle_transcription(text)
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Audio processing error: {e}")
                if self.on_error:
                    asyncio.run_coroutine_threadsafe(
                        self.on_error(f"Audio processing error: {e}"),
                        asyncio.get_event_loop()
                    )
        
        logger.info("Audio processing loop stopped")
    
    def _process_stt_sync(self, audio_chunk: np.ndarray) -> Optional[str]:
        """Process audio through STT model"""
        try:
            return self.stt_processor.transcribe(audio_chunk)
        except Exception as e:
            logger.error(f"STT processing error: {e}")
            return None
    
    def _handle_transcription(self, text: str):
        """Handle raw transcription from STT"""
        # Process through Command Processor first if enabled
        if self.command_processor and self.config.command_mode.enabled:
            command_match = self.command_processor.process_speech(text)
            if command_match:
                # Command was processed, don't continue with normal transcription
                return
        
        self.current_text = text
        
        # Send raw transcription to UI
        if self.on_raw_transcription:
            asyncio.run_coroutine_threadsafe(
                self.on_raw_transcription(text),
                asyncio.get_event_loop()
            )
        
        # Process through Clarity Engine if enabled
        if self.clarity_enabled and self.clarity_engine.is_initialized:
            self.clarity_engine.update_context(text)
            corrected_text = self.clarity_engine.correct_text_sync(text)
            if corrected_text != text:
                # Create result object to match expected interface
                class CorrectionResult:
                    def __init__(self, original, corrected):
                        self.original_text = original
                        self.corrected_text = corrected
                
                result = CorrectionResult(text, corrected_text)
                asyncio.run_coroutine_threadsafe(
                    self._on_correction_complete(result),
                    self.event_loop or asyncio.get_event_loop()
                )
    
    async def _on_correction_complete(self, result):
        """Handle completed correction from Clarity Engine"""
        # Update current text with corrected version
        self.current_text = result.corrected_text
        
        # Send corrected text to UI
        if self.on_corrected_transcription:
            asyncio.run_coroutine_threadsafe(
                self.on_corrected_transcription(result),
                asyncio.get_event_loop()
            )
        
        # Log performance
        if result.processing_time_ms > 150:
            logger.warning(f"Correction took {result.processing_time_ms:.1f}ms")
    
    def _handle_pause_detected(self, pause_duration: float):
        """Handle pause detection from VAD"""
        if self.current_text.strip():
            logger.info(f"Pause detected ({pause_duration:.2f}s), triggering commit")
            
            if self.on_pause_detected:
                asyncio.run_coroutine_threadsafe(
                    self.on_pause_detected(pause_duration, self.current_text),
                    asyncio.get_event_loop()
                )
    
    def _update_vad_status(self, vad_status: dict):
        """Update VAD status in UI"""
        if self.on_vad_status:
            asyncio.run_coroutine_threadsafe(
                self.on_vad_status(vad_status),
                asyncio.get_event_loop()
            )
    
    # Public control methods
    
    def set_clarity_enabled(self, enabled: bool):
        """Enable/disable Clarity Engine"""
        self.clarity_enabled = enabled
        logger.info(f"Clarity Engine {'enabled' if enabled else 'disabled'}")
    
    def clear_current_text(self):
        """Clear current text and context"""
        self.current_text = ""
        if self.clarity_engine:
            self.clarity_engine.clear_context()
    
    def get_current_text(self) -> str:
        """Get current transcribed text"""
        return self.current_text
    
    # Callback setters (called by DictationView during initialization)
    
    def set_raw_transcription_callback(self, callback: Callable[[str], None]):
        self.on_raw_transcription = callback
    
    def set_corrected_transcription_callback(self, callback: Callable):
        self.on_corrected_transcription = callback
    
    def set_pause_detected_callback(self, callback: Callable[[float, str], None]):
        self.on_pause_detected = callback
    
    def set_vad_status_callback(self, callback: Callable[[dict], None]):
        self.on_vad_status = callback
    
    def set_error_callback(self, callback: Callable[[str], None]):
        self.on_error = callback
    
    def set_command_mode_status_callback(self, callback: Callable[[bool], None]):
        """Set callback for command mode status changes"""
        self.on_command_mode_status = callback
    
    # Command processor callbacks
    
    def _on_command_mode_status_changed(self, is_active: bool):
        """Handle command mode status changes"""
        if self.on_command_mode_status:
            asyncio.run_coroutine_threadsafe(
                self.on_command_mode_status(is_active),
                asyncio.get_event_loop()
            )
    
    def _on_command_activation_detected(self):
        """Handle command activation detection"""
        # This could trigger a UI update to show command mode is active
        logger.info("Command mode activated - waiting for command")
    
    def _on_command_executed(self, command_match):
        """Handle command execution"""
        logger.info(f"Command executed: {command_match.command_id}")
        # Handle specific commands that affect the audio engine directly
        if command_match.command_id == "clear_text":
            self.clear_current_text()
        elif command_match.command_id == "commit_text":
            # This would be handled by the UI, but we can log it
            pass
    
    def _on_command_timeout(self):
        """Handle command timeout"""
        logger.info("Command mode timeout - returning to normal mode")
    
    def _on_audio_feedback(self, feedback_type: str):
        """Handle audio feedback requests"""
        logger.info(f"Audio feedback requested: {feedback_type}")
        # For now, we'll just log the feedback request
        # In a full implementation, this would play actual sounds
        # using a library like pygame or playsound
        if feedback_type == "activation":
            logger.info("Playing activation sound")
            # TODO: Play activation sound (e.g., double beep)
        elif feedback_type == "command_executed":
            logger.info("Playing command executed sound")
            # TODO: Play command executed sound (e.g., single beep)
        elif feedback_type == "return_to_normal":
            logger.info("Playing return to normal sound")
            # TODO: Play return to normal sound (e.g., descending tone)
        elif feedback_type == "error":
            logger.info("Playing error sound")
            # TODO: Play error sound (e.g., low tone)
    
    def _on_visual_feedback(self, feedback_type: str):
        """Handle visual feedback requests"""
        logger.info(f"Visual feedback requested: {feedback_type}")
        # TODO: Implement actual visual feedback
        # This would typically trigger UI updates through callbacks
    
    def _on_confirmation_request(self, command_id: str, description: str):
        """Handle confirmation requests for destructive commands"""
        logger.info(f"Confirmation requested for command '{command_id}': {description}")
        # TODO: Implement actual confirmation mechanism
        # This would typically trigger a UI dialog or voice prompt
    
    # Specific command callbacks
    
    def _on_commit_text_command(self):
        """Handle commit text command"""
        logger.info("Commit text command received")
        # This will be handled by the UI, but we can log it
    
    def _on_clear_text_command(self):
        """Handle clear text command"""
        logger.info("Clear text command received")
        self.clear_current_text()
    
    def _on_toggle_clarity_command(self):
        """Handle toggle clarity command"""
        logger.info("Toggle clarity command received")
        self.set_clarity_enabled(not self.clarity_enabled)
    
    def _on_enable_clarity_command(self):
        """Handle enable clarity command"""
        logger.info("Enable clarity command received")
        self.set_clarity_enabled(True)
    
    def _on_disable_clarity_command(self):
        """Handle disable clarity command"""
        logger.info("Disable clarity command received")
        self.set_clarity_enabled(False)
    
    # Public methods for command mode control
    
    def set_command_mode_enabled(self, enabled: bool):
        """Enable/disable command mode"""
        self.config.command_mode.enabled = enabled
        logger.info(f"Command mode {'enabled' if enabled else 'disabled'}")