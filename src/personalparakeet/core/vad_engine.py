#!/usr/bin/env python3
"""
VAD Engine - Direct port from personalparakeet.vad_engine
Voice Activity Detection with callback support
"""

import threading
import time
from typing import Callable, Optional

import numpy as np


class VoiceActivityDetector:
    """Voice Activity Detector with pause detection and callbacks"""

    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration: float = 0.03,
        silence_threshold: float = 0.01,
        pause_threshold: float = 1.5,
    ):

        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * frame_duration)
        self.silence_threshold = silence_threshold
        self.pause_threshold = pause_threshold

        # State tracking
        self.is_speaking = False
        self.silence_start_time = None
        self.last_speech_time = time.time()

        # Callbacks (adapted for direct function calls instead of WebSocket)
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_end: Optional[Callable] = None
        self.on_pause_detected: Optional[Callable[[float], None]] = None

    def process_audio_frame(self, audio_data: np.ndarray) -> dict:
        """Process single audio frame and return VAD status"""
        # Calculate RMS energy
        rms_energy = np.sqrt(np.mean(audio_data**2))

        # Determine if currently speaking
        is_speech = rms_energy > self.silence_threshold

        current_time = time.time()

        if is_speech:
            if not self.is_speaking:
                # Speech started
                self.is_speaking = True
                self.silence_start_time = None
                if self.on_speech_start:
                    self.on_speech_start()

            self.last_speech_time = current_time

        else:
            if self.is_speaking:
                # Potential pause/end of speech
                if self.silence_start_time is None:
                    self.silence_start_time = current_time

                pause_duration = current_time - self.silence_start_time

                if pause_duration >= self.pause_threshold:
                    # Pause threshold reached
                    self.is_speaking = False
                    if self.on_pause_detected:
                        self.on_pause_detected(pause_duration)
                    if self.on_speech_end:
                        self.on_speech_end()

        return {
            "is_speech": is_speech,
            "rms_energy": rms_energy,
            "pause_duration": (
                (current_time - self.silence_start_time) if self.silence_start_time else 0
            ),
            "is_speaking": self.is_speaking,
        }
