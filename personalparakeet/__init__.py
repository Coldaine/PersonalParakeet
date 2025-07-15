"""PersonalParakeet - Real-Time Dictation System with LocalAgreement buffering."""

__version__ = "1.0.0"

# Main exports
from .dictation import SimpleDictation
from .local_agreement import TranscriptionProcessor, LocalAgreementBuffer

__all__ = ['SimpleDictation', 'TranscriptionProcessor', 'LocalAgreementBuffer']