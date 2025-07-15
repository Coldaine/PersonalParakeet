"""PersonalParakeet - Real-Time Dictation System with LocalAgreement buffering."""

__version__ = "1.0.0"

# Import lightweight components first
from .local_agreement import TranscriptionProcessor, LocalAgreementBuffer

# Conditionally import heavy dependencies
__all__ = ['TranscriptionProcessor', 'LocalAgreementBuffer']

try:
    from .dictation import SimpleDictation
    __all__.append('SimpleDictation')
except ImportError:
    # Allow package to be imported even if heavy dependencies aren't available
    # This is useful for testing individual components
    pass