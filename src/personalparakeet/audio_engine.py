#!/usr/bin/env python3
"""
AudioEngine - Producer-Consumer Audio Pipeline for PersonalParakeet v3
Replaces WebSocket architecture with direct function calls
"""

import asyncio
import logging
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Optional

import numpy as np

# Import dependency validation
sys.path.append(str(Path(__file__).parent.parent / "src"))
from personalparakeet.utils.dependency_validation import get_validator

# Check dependencies on initialization
_validator = get_validator()
AUDIO_DEPS_AVAILABLE = _validator.check_audio_dependencies()
SOUNDDDEVICE_AVAILABLE = AUDIO_DEPS_AVAILABLE.get("sounddevice", False)

# Optional imports for hardware dependencies
if SOUNDDDEVICE_AVAILABLE:
    import sounddevice as sd
else:
    sd = None

from personalparakeet.core.stt_factory import STTFactory
from personalparakeet.core.clarity_engine import ClarityEngine
from personalparakeet.core.vad_engine import VoiceActivityDetector
from personalparakeet.core.audio_resampler import AudioResampler, ResamplerConfig
from personalparakeet.config import V3Config

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
        self.resampler = None
        
        # Callbacks for UI updates (set by DictationView)
        self.on_raw_transcription = None
        self.on_corrected_transcription = None
        self.on_pause_detected = None
        self.on_vad_status = None
        self.on_error = None
        
        # State tracking
        self.current_text = ""
        self.clarity_enabled = True
        
    async def initialize(self):
        """Initialize all audio processing components"""
        try:
            logger.info("Initializing AudioEngine...")
            
            # Initialize STT processor using factory
            self.stt_processor = STTFactory.create_stt_processor(self.config)
            await self.stt_processor.initialize()
            
            # Initialize Clarity Engine
            self.clarity_engine = ClarityEngine(enable_rule_based=True)
            await self.clarity_engine.initialize()
            self.clarity_engine.start_worker()
            
            # Initialize VAD Engine (using model sample rate)
            self.vad_engine = VoiceActivityDetector(
                sample_rate=self.config.audio.model_sample_rate,
                silence_threshold=self.config.vad.silence_threshold,
                pause_threshold=self.config.vad.pause_threshold
            )
            self.vad_engine.on_pause_detected = self._handle_pause_detected
            
            # Initialize resampler if needed
            if self.config.audio.enable_resampling and \
               self.config.audio.capture_sample_rate != self.config.audio.model_sample_rate:
                self.resampler = AudioResampler(
                    ResamplerConfig(
                        input_rate=self.config.audio.capture_sample_rate,
                        output_rate=self.config.audio.model_sample_rate,
                        quality=self.config.audio.resample_quality
                    )
                )
                logger.info(f"Resampler initialized: {self.config.audio.capture_sample_rate}Hz -> {self.config.audio.model_sample_rate}Hz")
            
            self.is_running = True
            logger.info("AudioEngine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AudioEngine: {e}")
            raise
    
    async def start(self):
        """Start audio processing"""
        if not self.is_running:
            raise RuntimeError("AudioEngine not initialized")
        
        if not SOUNDDDEVICE_AVAILABLE:
            raise RuntimeError("sounddevice library not available. Install with: pip install sounddevice")
        
        if self.is_listening:
            logger.warning("Already listening")
            return
            
        logger.info("Starting audio processing...")
        
        # Start audio processing thread
        self.audio_thread = threading.Thread(target=self._audio_processing_loop, daemon=True)
        self.audio_thread.start()
        
        # Start audio stream at capture sample rate
        self.audio_stream = sd.InputStream(
            device=self.config.audio.device_index,
            samplerate=self.config.audio.capture_sample_rate,
            channels=1,
            dtype=np.float32,
            callback=self._audio_callback,
            blocksize=int(self.config.audio.chunk_size * self.config.audio.capture_sample_rate / self.config.audio.model_sample_rate)
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
                # Get audio chunk from queue (at capture sample rate)
                audio_chunk = self.audio_queue.get(timeout=0.5)
                
                # Resample if needed
                if self.resampler:
                    audio_chunk = self.resampler.resample_chunk(audio_chunk)
                
                # Process VAD (expects model sample rate)
                if self.vad_engine:
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
                    try:
                        if asyncio.iscoroutinefunction(self.on_error):
                            asyncio.run_coroutine_threadsafe(
                                self.on_error(f"Audio processing error: {e}"),
                                asyncio.get_event_loop()
                            )
                        else:
                            self.on_error(f"Audio processing error: {e}")
                    except Exception as callback_error:
                        logger.error(f"Error callback failed: {callback_error}")
        
        logger.info("Audio processing loop stopped")
    
    def _process_stt_sync(self, audio_chunk: np.ndarray) -> Optional[str]:
        """Process audio through STT model"""
        try:
            if self.stt_processor:
                logger.debug(f"Calling STT transcribe with chunk shape: {audio_chunk.shape}")
                start_time = time.time()
                result = self.stt_processor.transcribe(audio_chunk)
                elapsed = time.time() - start_time
                logger.debug(f"STT transcribe took {elapsed:.3f}s, result: {result}")
                return result
            return None
        except Exception as e:
            logger.error(f"STT processing error: {e}", exc_info=True)
            return None
    
    def _handle_transcription(self, text: str):
        """Handle raw transcription from STT"""
        self.current_text = text
        
        # Send raw transcription to UI
        if self.on_raw_transcription:
            try:
                if asyncio.iscoroutinefunction(self.on_raw_transcription):
                    asyncio.run_coroutine_threadsafe(
                        self.on_raw_transcription(text),
                        asyncio.get_event_loop()
                    )
                else:
                    self.on_raw_transcription(text)
            except Exception as e:
                logger.error(f"Raw transcription callback failed: {e}")
        
        # Process through Clarity Engine if enabled
        if self.clarity_enabled and self.clarity_engine and hasattr(self.clarity_engine, 'is_initialized') and self.clarity_engine.is_initialized:
            self.clarity_engine.update_context(text)
            corrected_text = self.clarity_engine.correct_text_sync(text)
            if corrected_text != text:
                # Create result object to match expected interface
                class CorrectionResult:
                    def __init__(self, original, corrected):
                        self.original_text = original
                        self.corrected_text = corrected
                        self.processing_time_ms = 0.0
                        self.confidence = 0.9
                        self.corrections_made = [(original, corrected)] if original != corrected else []
                
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
            try:
                if asyncio.iscoroutinefunction(self.on_corrected_transcription):
                    asyncio.run_coroutine_threadsafe(
                        self.on_corrected_transcription(result),
                        asyncio.get_event_loop()
                    )
                else:
                    self.on_corrected_transcription(result)
            except Exception as e:
                logger.error(f"Corrected transcription callback failed: {e}")
        
        # Log performance
        if hasattr(result, 'processing_time_ms') and result.processing_time_ms > 150:
            logger.warning(f"Correction took {result.processing_time_ms:.1f}ms")
    
    def _handle_pause_detected(self, pause_duration: float):
        """Handle pause detection from VAD"""
        if self.current_text.strip():
            logger.info(f"Pause detected ({pause_duration:.2f}s), triggering commit")
            
            if self.on_pause_detected:
                try:
                    if asyncio.iscoroutinefunction(self.on_pause_detected):
                        asyncio.run_coroutine_threadsafe(
                            self.on_pause_detected(pause_duration, self.current_text),
                            asyncio.get_event_loop()
                        )
                    else:
                        self.on_pause_detected(pause_duration, self.current_text)
                except Exception as e:
                    logger.error(f"Pause detected callback failed: {e}")
    
    def _update_vad_status(self, vad_status: dict):
        """Update VAD status in UI"""
        if self.on_vad_status:
            try:
                if asyncio.iscoroutinefunction(self.on_vad_status):
                    asyncio.run_coroutine_threadsafe(
                        self.on_vad_status(vad_status),
                        asyncio.get_event_loop()
                    )
                else:
                    self.on_vad_status(vad_status)
            except Exception as e:
                logger.error(f"VAD status callback failed: {e}")
    
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
