# personalparakeet/vad_engine.py
import numpy as np
from typing import Callable, Optional, Dict, Any
import threading
import time
from .config_manager import VADSettings

class VoiceActivityDetector:
    def __init__(self, 
                 vad_settings: VADSettings,
                 sample_rate: int = 16000,
                 frame_duration: float = 0.03):
        
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * frame_duration)
        # TODO: Implement sensitivity mapping to a float threshold
        self.silence_threshold = vad_settings.custom_threshold or 0.01 
        self.pause_threshold_seconds = vad_settings.pause_duration_ms / 1000.0
        
        # State tracking
        self.is_speaking = False
        self.silence_start_time = None
        self.last_speech_time = time.time()
        
        # Callbacks
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_end: Optional[Callable] = None
        self.on_pause_detected: Optional[Callable[[float], None]] = None
        
    def process_audio_frame(self, audio_data: np.ndarray) -> dict:
        """Process single audio frame and return VAD status"""
        # Calculate RMS energy
        rms_energy = np.sqrt(np.mean(audio_data ** 2))
        
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
                
                if pause_duration >= self.pause_threshold_seconds:
                    # Pause threshold reached
                    self.is_speaking = False
                    if self.on_pause_detected:
                        self.on_pause_detected(pause_duration)
                    if self.on_speech_end:
                        self.on_speech_end()
        
        return {
            'is_speech': is_speech,
            'rms_energy': rms_energy,
            'pause_duration': (current_time - self.silence_start_time) if self.silence_start_time else 0,
            'is_speaking': self.is_speaking
        }