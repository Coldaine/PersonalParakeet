#!/usr/bin/env python3
"""
Audio Meter Module - Shared audio level visualization
Works for both terminal and GUI applications
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class AudioLevel:
    """Audio level measurement"""
    rms: float  # RMS level (0.0 to 1.0)
    peak: float  # Peak level (0.0 to 1.0)
    rms_db: float  # RMS in dB
    peak_db: float  # Peak in dB
    is_voice: bool  # Voice activity detected
    

class AudioMeter:
    """Audio level meter with various display formats"""
    
    def __init__(self, voice_threshold: float = 0.01):
        self.voice_threshold = voice_threshold
        self.history: List[AudioLevel] = []
        self.max_history = 100
        
    def measure(self, audio_data: np.ndarray) -> AudioLevel:
        """Measure audio levels from raw audio data"""
        # Ensure we have 1D audio
        if audio_data.ndim > 1:
            audio_data = audio_data[:, 0]
            
        # Calculate RMS and peak
        rms = np.sqrt(np.mean(audio_data**2))
        peak = np.max(np.abs(audio_data))
        
        # Convert to dB (with floor to avoid log(0))
        rms_db = 20 * np.log10(rms + 1e-10)
        peak_db = 20 * np.log10(peak + 1e-10)
        
        # Detect voice activity
        is_voice = rms > self.voice_threshold
        
        level = AudioLevel(
            rms=rms,
            peak=peak,
            rms_db=rms_db,
            peak_db=peak_db,
            is_voice=is_voice
        )
        
        # Store in history
        self.history.append(level)
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        return level
    
    def get_bar_meter(self, level: AudioLevel, width: int = 40) -> str:
        """Generate a text bar meter"""
        # Normalize RMS for display (adjust sensitivity)
        normalized = min(1.0, level.rms * 20)
        filled = int(normalized * width)
        
        # Use different characters for better visibility
        if level.is_voice:
            bar = "▓" * filled + "░" * (width - filled)
        else:
            bar = "▒" * filled + "░" * (width - filled)
            
        return f"[{bar}]"
    
    def get_ascii_meter(self, level: AudioLevel, width: int = 40) -> str:
        """Generate ASCII-only meter (no unicode)"""
        normalized = min(1.0, level.rms * 20)
        filled = int(normalized * width)
        
        if level.is_voice:
            bar = "#" * filled + "-" * (width - filled)
        else:
            bar = "=" * filled + "-" * (width - filled)
            
        return f"[{bar}]"
    
    def get_percentage_meter(self, level: AudioLevel) -> str:
        """Get percentage-based meter"""
        percentage = min(100, int(level.rms * 2000))
        return f"{percentage:3d}%"
    
    def get_level_indicator(self, level: AudioLevel) -> str:
        """Get a simple level indicator"""
        if level.rms_db > -20:
            return "████ LOUD"
        elif level.rms_db > -30:
            return "███░ GOOD"  
        elif level.rms_db > -40:
            return "██░░ SOFT"
        elif level.rms_db > -50:
            return "█░░░ QUIET"
        else:
            return "░░░░ SILENT"
    
    def get_status_line(self, level: AudioLevel, format: str = "unicode") -> str:
        """Get a complete status line for terminal display"""
        if level.is_voice:
            status = "🎤 SPEAKING"
        else:
            status = "   SILENCE "
            
        if format == "unicode":
            meter = self.get_bar_meter(level)
        else:
            meter = self.get_ascii_meter(level)
            
        return f"{status} {meter} RMS: {level.rms_db:6.1f} dB | Peak: {level.peak_db:6.1f} dB"
    
    def get_compact_status(self, level: AudioLevel) -> str:
        """Get a compact status for limited space"""
        indicator = self.get_level_indicator(level)
        percentage = self.get_percentage_meter(level)
        return f"{indicator} {percentage}"
    
    def get_sparkline(self, samples: int = 20) -> str:
        """Get a sparkline graph of recent levels"""
        if not self.history:
            return "⠀" * samples
            
        # Get recent RMS values
        recent = self.history[-samples:] if len(self.history) >= samples else self.history
        values = [l.rms for l in recent]
        
        # Pad if needed
        while len(values) < samples:
            values.insert(0, 0.0)
            
        # Convert to sparkline characters
        spark_chars = "⠀⠂⠆⠇⡇⡏⡟⡿"
        sparkline = ""
        
        for val in values:
            idx = int(min(7, val * 140))  # Scale to 0-7
            sparkline += spark_chars[idx]
            
        return sparkline