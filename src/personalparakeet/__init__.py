"""
PersonalParakeet - Real-time dictation system with transparent floating UI.

A modern Python package for speech-to-text dictation with advanced text injection capabilities.
"""

__version__ = "3.0.0"
__author__ = "PersonalParakeet Team"
__email__ = "team@personalparakeet.dev"

from .main import PersonalParakeetV3, main

__all__ = ["PersonalParakeetV3", "main", "__version__"]