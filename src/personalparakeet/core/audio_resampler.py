#!/usr/bin/env python3
"""
Audio resampling module for PersonalParakeet
Handles efficient CPU-based resampling from capture rate to model rate
"""

import numpy as np
from scipy import signal
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ResamplerConfig:
    """Resampler configuration"""

    input_rate: int
    output_rate: int
    quality: str = "high"  # "fast", "balanced", "high"
    chunk_size: Optional[int] = None


class AudioResampler:
    """Efficient audio resampler using polyphase filtering"""

    def __init__(self, config: ResamplerConfig):
        self.config = config
        self.input_rate = config.input_rate
        self.output_rate = config.output_rate

        # Calculate resampling ratio
        self.ratio = self.output_rate / self.input_rate

        # For 44100 -> 16000, we can use ratio 160/441 for exact conversion
        if self.input_rate == 44100 and self.output_rate == 16000:
            self.up = 160
            self.down = 441
            logger.info(f"Using exact ratio {self.up}/{self.down} for 44.1k->16k conversion")
        else:
            # Find reasonable up/down factors
            from math import gcd

            g = gcd(self.input_rate, self.output_rate)
            self.up = self.output_rate // g
            self.down = self.input_rate // g
            logger.info(f"Resampling ratio: {self.up}/{self.down} ({self.ratio:.4f})")

        # Buffer for maintaining continuity between chunks
        self.buffer = np.array([], dtype=np.float32)

        # Pre-design filter based on quality setting
        self._design_filter()

        logger.info(f"AudioResampler initialized: {self.input_rate}Hz -> {self.output_rate}Hz")

    def _design_filter(self):
        """Design anti-aliasing filter based on quality setting"""
        if self.config.quality == "fast":
            # Simple decimation, lower quality but fast
            self.filter_length = 64
        elif self.config.quality == "balanced":
            # Good quality/performance trade-off
            self.filter_length = 128
        else:  # "high"
            # Best quality, slightly more CPU
            self.filter_length = 256

        # Design lowpass filter
        cutoff = min(self.input_rate, self.output_rate) / 2.0
        nyquist = self.input_rate / 2.0
        self.filter = signal.firwin(self.filter_length, cutoff / nyquist, window="hamming")

    def resample_chunk(self, audio_chunk: np.ndarray) -> np.ndarray:
        """
        Resample a chunk of audio while maintaining continuity

        Args:
            audio_chunk: Input audio at capture_sample_rate

        Returns:
            Resampled audio at model_sample_rate
        """
        if len(audio_chunk) == 0:
            return np.array([], dtype=np.float32)

        # Ensure float32
        if audio_chunk.dtype != np.float32:
            audio_chunk = audio_chunk.astype(np.float32)

        # For exact ratio (44.1k -> 16k), use resample_poly
        if self.up == 160 and self.down == 441:
            try:
                # Concatenate with buffer for continuity
                if len(self.buffer) > 0:
                    audio_chunk = np.concatenate([self.buffer, audio_chunk])
                    self.buffer = np.array([], dtype=np.float32)

                # Resample using polyphase method
                resampled = signal.resample_poly(
                    audio_chunk, self.up, self.down, window=self.filter
                )

                return resampled.astype(np.float32)

            except Exception as e:
                logger.error(f"Resampling error: {e}")
                # Fallback to simple decimation
                indices = np.round(np.arange(0, len(audio_chunk), 1 / self.ratio)).astype(int)
                indices = indices[indices < len(audio_chunk)]
                return audio_chunk[indices]

        else:
            # General case resampling
            target_length = int(len(audio_chunk) * self.ratio)
            resampled = signal.resample(audio_chunk, target_length)
            return resampled.astype(np.float32)

    def get_output_size(self, input_size: int) -> int:
        """Calculate output size for a given input size"""
        return int(input_size * self.ratio)

    def reset(self):
        """Reset internal buffers"""
        self.buffer = np.array([], dtype=np.float32)
        logger.debug("Resampler buffers reset")
