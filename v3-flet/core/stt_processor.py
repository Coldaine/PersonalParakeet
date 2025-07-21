#!/usr/bin/env python3
"""
STT Processor - Extracted Parakeet integration for PersonalParakeet v3
Ported from personalparakeet.dictation.SimpleDictation
"""

import logging
import asyncio
import torch
import numpy as np
from typing import Optional

# Import NeMo for Parakeet model
import nemo.collections.asr as nemo_asr

from config import V3Config

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
        
    async def initialize(self):
        """Initialize the Parakeet STT model"""
        try:
            logger.info("Loading Parakeet-TDT-1.1B model...")
            
            # Import CUDA fix for RTX 5090 compatibility
            try:
                import sys
                from pathlib import Path
                sys.path.append(str(Path(__file__).parent.parent.parent))
                from personalparakeet.cuda_fix import ensure_cuda_available
                ensure_cuda_available()
                logger.info("CUDA compatibility ensured")
            except ImportError:
                logger.warning("CUDA fix not available, proceeding with default CUDA setup")
            
            # Load Parakeet model
            self.model = nemo_asr.models.ASRModel.from_pretrained(
                "nvidia/parakeet-tdt-1.1b",
                map_location="cuda"
            ).to(dtype=torch.float16)
            
            self.is_initialized = True
            logger.info("Parakeet model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize STT processor: {e}")
            raise
    
    async def transcribe(self, audio_chunk: np.ndarray) -> Optional[str]:
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
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._transcribe_sync, audio_chunk)
            return result
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    def _transcribe_sync(self, audio_chunk: np.ndarray) -> Optional[str]:
        """Synchronous transcription (runs in thread pool)"""
        try:
            with torch.inference_mode():
                # Ensure audio is in correct format for Parakeet
                if audio_chunk.dtype != np.float32:
                    audio_chunk = audio_chunk.astype(np.float32)
                
                # Transcribe with Parakeet
                result = self.model.transcribe([audio_chunk])
                text = result[0].text if result and result[0].text else ""
                
                return text.strip() if text else None
                
        except torch.cuda.OutOfMemoryError:
            logger.error("GPU out of memory! Clearing cache...")
            torch.cuda.empty_cache()
            return None
        except Exception as e:
            logger.error(f"Sync transcription error: {e}")
            return None
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.model is not None:
                del self.model
                self.model = None
                torch.cuda.empty_cache()
                logger.info("STT processor cleaned up")
        except Exception as e:
            logger.warning(f"Error during STT cleanup: {e}")
        
        self.is_initialized = False