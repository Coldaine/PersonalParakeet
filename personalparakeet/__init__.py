"""PersonalParakeet v2 - Real-Time Dictation System with Dictation View."""

__version__ = "2.0.0"

# Import v2 components
from .clarity_engine import ClarityEngine
from .thought_linking import IntelligentThoughtLinker  
from .command_mode import CommandModeEngine

# Core v2 components
__all__ = ['ClarityEngine', 'IntelligentThoughtLinker', 'CommandModeEngine']

# Conditionally import heavy dependencies
try:
    from .dictation import SimpleDictation
    __all__.append('SimpleDictation')
except ImportError:
    # Allow package to be imported even if heavy dependencies aren't available
    # This is useful for testing individual components
    pass