#!/usr/bin/env python3
"""
STT Factory - Creates real STT processors with hardware requirements
Real hardware always present - no mock implementations allowed
"""

import logging
from typing import TYPE_CHECKING

from personalparakeet.config import V3Config

logger = logging.getLogger(__name__)

# Type hints without importing at module level
if TYPE_CHECKING:
    from .stt_processor import STTProcessor


class STTFactory:
    """Factory for creating STT processors with real hardware"""

    _nemo_available = None  # Cache availability check

    @classmethod
    def check_nemo_availability(cls) -> bool:
        """Check if NeMo and PyTorch are available"""
        if cls._nemo_available is not None:
            return cls._nemo_available

        try:
            # Try importing required ML dependencies
            import nemo.collections.asr as nemo_asr
            import torch

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
            logger.error(f"✗ ML dependencies not available: {e}")
            logger.error("  Real hardware is required - no mock implementations allowed")
            logger.info("  To enable real STT: install NeMo toolkit")
            cls._nemo_available = False
            return False

    @classmethod
    def create_stt_processor(cls, config: V3Config) -> "STTProcessor":
        """
        Create real STT processor - hardware always present per CLAUDE.md

        Args:
            config: V3 configuration object

        Returns:
            Real STTProcessor only

        Raises:
            RuntimeError: If NeMo is not available (violates hardware requirements)
        """
        # Check if mock STT is requested
        if config.audio.use_mock_stt:
            logger.info("Mock STT requested - creating mock processor")
            from .mock_stt_processor import MockSTTProcessor

            return MockSTTProcessor(config)

        # Real hardware always present - check if ML dependencies available
        if not cls.check_nemo_availability():
            error_msg = (
                "CRITICAL: NeMo/PyTorch not available for real STT!\n"
                "PersonalParakeet requires ML dependencies for speech recognition.\n"
                "Real hardware is always present - no mock implementations allowed.\n"
                "\n"
                "To fix this:\n"
                "1. Install NeMo toolkit: pip install nemo_toolkit[all]\n"
                "\n"
                "See docs/ML_INSTALLATION_GUIDE.md for detailed instructions."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Create real STT processor
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
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    @classmethod
    def get_stt_info(cls) -> dict:
        """Get information about current STT configuration"""
        info = {
            "nemo_available": cls.check_nemo_availability(),
            "backend": "nemo" if cls._nemo_available else "mock",
        }

        if cls._nemo_available:
            try:
                import torch

                info.update(
                    {
                        "cuda_available": torch.cuda.is_available(),
                        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
                        "device_name": (
                            torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
                        ),
                        "pytorch_version": torch.__version__,
                    }
                )
            except:
                pass

        return info
