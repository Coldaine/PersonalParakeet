#!/usr/bin/env python3
"""
STT Factory - Dynamic STT processor selection with graceful fallback
Provides automatic fallback to mock STT if NeMo/PyTorch are not available
"""

import logging
from typing import TYPE_CHECKING, Union
from config import V3Config

logger = logging.getLogger(__name__)

# Type hints without importing at module level
if TYPE_CHECKING:
    from .stt_processor import STTProcessor
    from .stt_processor_mock import STTProcessor as MockSTTProcessor


class STTFactory:
    """Factory for creating STT processors with automatic fallback"""
    
    _nemo_available = None  # Cache availability check
    
    @classmethod
    def check_nemo_availability(cls) -> bool:
        """Check if NeMo and PyTorch are available"""
        if cls._nemo_available is not None:
            return cls._nemo_available
            
        try:
            # Try importing required ML dependencies
            import torch
            import nemo.collections.asr as nemo_asr
            
            # Check CUDA availability
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                logger.info(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
            else:
                logger.warning("⚠ CUDA not available - will use CPU (slower)")
            
            logger.info("✓ NeMo and PyTorch are available")
            cls._nemo_available = True
            return True
            
        except ImportError as e:
            logger.warning(f"✗ ML dependencies not available: {e}")
            logger.warning("  Falling back to mock STT processor")
            logger.info("  To enable real STT: poetry install --with ml")
            cls._nemo_available = False
            return False
    
    @classmethod
    def create_stt_processor(cls, config: V3Config) -> Union['STTProcessor', 'MockSTTProcessor']:
        """
        Create appropriate STT processor based on availability and configuration
        
        Args:
            config: V3 configuration object
            
        Returns:
            Either real STTProcessor or MockSTTProcessor
            
        Raises:
            RuntimeError: If NeMo is not available and mock mode not explicitly requested
        """
        # Check if user explicitly wants mock STT
        use_mock = getattr(config.audio, 'use_mock_stt', False)
        
        if use_mock:
            logger.info("Using mock STT processor (explicitly configured)")
            from .stt_processor_mock import STTProcessor as MockSTTProcessor
            return MockSTTProcessor(config)
        
        # User expects real STT - check if available
        if not cls.check_nemo_availability():
            error_msg = (
                "CRITICAL: NeMo/PyTorch not available for real STT!\n"
                "PersonalParakeet requires ML dependencies for speech recognition.\n"
                "\n"
                "To fix this:\n"
                "1. Install ML dependencies: poetry install --with ml\n"
                "2. Or force mock mode: set 'use_mock_stt': true in config\n"
                "\n"
                "See docs/ML_INSTALLATION_GUIDE.md for detailed instructions."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Try to create real STT processor
        try:
            logger.info("Creating real STT processor with NeMo")
            from .stt_processor import STTProcessor
            return STTProcessor(config)
        except Exception as e:
            error_msg = (
                f"CRITICAL: Failed to create STT processor: {e}\n"
                "\n"
                "The ML dependencies are installed but STT initialization failed.\n"
                "Check the logs for specific errors.\n"
                "\n"
                "Common causes:\n"
                "- Insufficient GPU memory\n"
                "- CUDA version mismatch\n"
                "- Corrupted model download\n"
                "\n"
                "To use mock mode instead, set 'use_mock_stt': true in config."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    @classmethod
    def get_stt_info(cls) -> dict:
        """Get information about current STT configuration"""
        info = {
            'nemo_available': cls.check_nemo_availability(),
            'backend': 'nemo' if cls._nemo_available else 'mock',
        }
        
        if cls._nemo_available:
            try:
                import torch
                info.update({
                    'cuda_available': torch.cuda.is_available(),
                    'cuda_version': torch.version.cuda if torch.cuda.is_available() else None,
                    'device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU',
                    'pytorch_version': torch.__version__,
                })
            except:
                pass
                
        return info