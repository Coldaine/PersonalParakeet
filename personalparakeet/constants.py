"""Constants used throughout PersonalParakeet"""

# Logging emojis (for console output)
class LogEmoji:
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "🔤"
    PROCESSING = "🔊"
    TARGET = "🎯"

# Default configuration values
DEFAULT_KEY_DELAY = 0.01
DEFAULT_CLIPBOARD_TIMEOUT = 5.0
DEFAULT_FOCUS_DELAY = 0.05

# Platform detection
WINDOWS_PLATFORMS = ['win32', 'cygwin', 'msys']
LINUX_PLATFORMS = ['linux', 'linux2']
MACOS_PLATFORMS = ['darwin']
