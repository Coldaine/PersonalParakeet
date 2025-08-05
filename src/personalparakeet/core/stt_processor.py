#!/usr/bin/env python3
"""
STT Processor - Extracted Parakeet integration for PersonalParakeet v3
Ported from personalparakeet.dictation.SimpleDictation
"""

import logging
import asyncio
import time
import os
import torch
import numpy as np
from typing import Optional
from pathlib import Path

# Import NeMo for Parakeet model
import nemo.collections.asr as nemo_asr

from personalparakeet.config import V3Config
from .cuda_compatibility import CUDACompatibility, get_optimal_device

logger = logging.getLogger(__name__)


class STTProcessor:
    """
    Speech-to-Text processor using NVIDIA Parakeet-TDT model
    Extracted from the original SimpleDictation class
    """
    
    def __init__(self, config: V3Config):
        self.config = config
        self.model = None
        self.is_initialized = False
        self.device = None  # Will be set during initialization
        
        # Performance tracking
        self.transcription_count = 0
        self.total_transcription_time = 0.0
        self.transcription_times = []
        
    async def initialize(self):
        """Initialize the Parakeet STT model"""
        try:
            logger.info("Loading Parakeet-TDT-1.1B model...")
            start_time = time.time()
            
            # Set custom cache directory if configured
            if self.config.audio.model_cache_dir:
                cache_dir = Path(self.config.audio.model_cache_dir).expanduser().absolute()
                cache_dir.mkdir(parents=True, exist_ok=True)
                
                # Set environment variables for HuggingFace and Torch cache
                os.environ['HF_HOME'] = str(cache_dir / 'huggingface')
                os.environ['HUGGINGFACE_HUB_CACHE'] = str(cache_dir / 'huggingface' / 'hub')
                os.environ['TORCH_HOME'] = str(cache_dir / 'torch')
                os.environ['TRANSFORMERS_CACHE'] = str(cache_dir / 'transformers')
                
                logger.info(f"Using custom model cache directory: {cache_dir}")
                logger.info(f"HuggingFace cache: {os.environ['HUGGINGFACE_HUB_CACHE']}")
            
            # Check CUDA compatibility and apply fixes
            cuda_info = CUDACompatibility.check_and_apply_fixes()
            logger.info(f"CUDA compatibility check completed: {cuda_info}")
            
            # Determine device to use
            force_cpu = self.config.audio.stt_device == "cpu"
            self.device = get_optimal_device(force_cpu=force_cpu)
            logger.info(f"Using device: {self.device}")
            
            # Get model path from config
            model_path = self.config.audio.get_stt_model_path()
            
            # Load Parakeet model
            if model_path and Path(model_path).exists():
                logger.info(f"Loading model from: {model_path}")
                self.model = nemo_asr.models.ASRModel.restore_from(
                    model_path,
                    map_location=self.device
                )
            else:
                logger.info("Loading model from NVIDIA NGC...")
                self.model = nemo_asr.models.ASRModel.from_pretrained(
                    "nvidia/parakeet-tdt-1.1b",
                    map_location=self.device
                )
            
            # Apply optimizations
            if self.device == "cuda":
                self.model = self.model.to(dtype=torch.float16)
                logger.info("Using float16 for GPU memory efficiency")
            
            self.is_initialized = True
            load_time = time.time() - start_time
            logger.info(f"Parakeet model loaded successfully in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize STT processor: {e}")
            raise
    
    def transcribe(self, audio_chunk: np.ndarray) -> Optional[str]:
        """
        Transcribe audio chunk to text
        
        Args:
            audio_chunk: Audio data as numpy array (float32)
            
        Returns:
            Transcribed text or None if transcription fails
        """
        if not self.is_initialized or self.model is None:
            logger.error("STT processor not initialized")
            return None
        
        try:
            # Direct synchronous transcription (will run in worker thread)
            return self._transcribe_sync(audio_chunk)
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    def _transcribe_sync(self, audio_chunk: np.ndarray) -> Optional[str]:
        """Synchronous transcription (runs in thread pool)"""
        try:
            # Check audio level threshold
            max_level = np.max(np.abs(audio_chunk))
            if max_level < self.config.audio.stt_audio_threshold:
                # Skip transcription for silent audio
                return None
            
            with torch.inference_mode():
                # Ensure audio is in correct format for Parakeet
                if audio_chunk.dtype != np.float32:
                    audio_chunk = audio_chunk.astype(np.float32)
                
                # Log audio chunk info for debugging
                logger.debug(f"Audio chunk shape: {audio_chunk.shape}, dtype: {audio_chunk.dtype}, max: {np.max(np.abs(audio_chunk)):.4f}")
                
                # Ensure 1D array (Parakeet expects list of 1D arrays)
                if audio_chunk.ndim > 1:
                    audio_chunk = audio_chunk.flatten()
                
                # Transcribe with Parakeet
                start_time = time.time()
                result = self.model.transcribe([audio_chunk])
                transcription_time = time.time() - start_time
                
                # Track performance metrics
                self.transcription_count += 1
                self.total_transcription_time += transcription_time
                self.transcription_times.append(transcription_time)
                
                text = result[0].text if result and result[0].text else ""
                
                # Log performance metrics periodically
                if self.transcription_count % 50 == 0:
                    avg_time = self.total_transcription_time / self.transcription_count
                    recent_avg = sum(self.transcription_times[-10:]) / min(10, len(self.transcription_times))
                    logger.info(f"STT performance - Count: {self.transcription_count}, "
                              f"Avg time: {avg_time:.3f}s, Recent avg: {recent_avg:.3f}s, "
                              f"Current: {transcription_time:.3f}s")
                
                return text.strip() if text else None
                
        except torch.cuda.OutOfMemoryError:
            logger.error("GPU out of memory! Clearing cache...")
            torch.cuda.empty_cache()
            return None
        except Exception as e:
            logger.error(f"Sync transcription error: {e}")
            return None
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.model is not None:
                del self.model
                self.model = None
                
                # Only clear CUDA cache if we were using CUDA
                if self.device == "cuda" and torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                logger.info("STT processor cleaned up")
        except Exception as e:
            logger.warning(f"Error during STT cleanup: {e}")
        
        self.is_initialized = False