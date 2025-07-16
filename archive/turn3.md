# Implementation Instructions for Code Review Improvements

Based on the revised code review, here are detailed implementation instructions for addressing the remaining valid issues:

## 1. Replace print() with Proper Logging

### Implementation Steps:
1. Create a new file `personalparakeet/logger.py`:
   ```python
   import logging
   import sys
   from pathlib import Path
   
   def setup_logger(name: str = "personalparakeet", level: str = "INFO") -> logging.Logger:
       """Setup logger with console and file handlers"""
       logger = logging.getLogger(name)
       logger.setLevel(getattr(logging, level.upper()))
       
       # Console handler with emojis
       console = logging.StreamHandler(sys.stdout)
       console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
       console.setFormatter(console_format)
       
       # File handler without emojis
       log_dir = Path.home() / ".personalparakeet" / "logs"
       log_dir.mkdir(parents=True, exist_ok=True)
       file_handler = logging.FileHandler(log_dir / "personalparakeet.log")
       file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
       file_handler.setFormatter(file_format)
       
       logger.addHandler(console)
       logger.addHandler(file_handler)
       return logger
   ```

2. Update each module to use logging:
   - Import: `from .logger import setup_logger`
   - Initialize: `logger = setup_logger(__name__)`
   - Replace all `print()` calls with appropriate log levels:
     - `print(f"✅ ...")` → `logger.info("...")`
     - `print(f"❌ ...")` → `logger.error("...")`
     - `print(f"⚠️  ...")` → `logger.warning("...")`
     - `print(f"🔤 ...")` → `logger.debug("...")`

## 2. Fix KDE Magic Numbers

### File: `personalparakeet/kde_injection.py`
Replace lines 68-69:
```python
# OLD:
self.xtest.fake_input(self.display, 6, keycode)  # KeyPress
self.xtest.fake_input(self.display, 7, keycode)  # KeyRelease

# NEW:
from Xlib import X
# Then use:
self.xtest.fake_input(self.display, X.KeyPress, keycode)
self.xtest.fake_input(self.display, X.KeyRelease, keycode)
```

## 3. Improve Clipboard Restoration Safety

### File: `personalparakeet/windows_injection.py` and `personalparakeet/linux_injection.py`

Add a more robust clipboard restoration mechanism:

```python
class ClipboardManager:
    """Safely manage clipboard save/restore operations"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 0.1):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.original_content = None
        self.original_format = None
        
    def save_clipboard(self) -> bool:
        """Save current clipboard with multiple attempts"""
        for attempt in range(self.max_retries):
            try:
                # Platform-specific save implementation
                self.original_content = self._get_clipboard_content()
                self.original_format = self._get_clipboard_format()
                return True
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to save clipboard after {self.max_retries} attempts: {e}")
                    return False
                time.sleep(self.retry_delay)
        return False
    
    def restore_clipboard(self) -> bool:
        """Restore clipboard with verification"""
        if self.original_content is None:
            return True  # Nothing to restore
            
        for attempt in range(self.max_retries):
            try:
                self._set_clipboard_content(self.original_content, self.original_format)
                # Verify restoration
                if self._get_clipboard_content() == self.original_content:
                    return True
            except Exception as e:
                logger.warning(f"Clipboard restore attempt {attempt + 1} failed: {e}")
                
            time.sleep(self.retry_delay)
            
        # Final fallback: notify user
        logger.error("Failed to restore clipboard. Original content may be lost.")
        return False
```

## 4. Refactor Long Methods

### File: `personalparakeet/text_injection.py`

Break down `_get_strategy_order()` into smaller methods:

```python
def _get_strategy_order(self, app_info: Optional[ApplicationInfo]) -> list:
    """Determine optimal strategy order based on platform and application"""
    if self.platform_info.platform == Platform.WINDOWS:
        return self._get_windows_strategy_order(app_info)
    elif self.platform_info.platform == Platform.LINUX:
        return self._get_linux_strategy_order(app_info)
    else:
        return ['basic_keyboard']

def _get_windows_strategy_order(self, app_info: Optional[ApplicationInfo]) -> list:
    """Get Windows-specific strategy order"""
    if not app_info:
        return ['ui_automation', 'keyboard', 'clipboard', 'basic_keyboard']
        
    # Application-specific optimizations
    strategies_by_app = {
        ApplicationType.EDITOR: ['clipboard', 'ui_automation', 'keyboard', 'basic_keyboard'],
        ApplicationType.IDE: ['clipboard', 'ui_automation', 'keyboard', 'basic_keyboard'],
        ApplicationType.TERMINAL: ['ui_automation', 'keyboard', 'basic_keyboard'],
        ApplicationType.BROWSER: ['keyboard', 'ui_automation', 'basic_keyboard'],
    }
    
    return strategies_by_app.get(
        app_info.app_type, 
        ['ui_automation', 'keyboard', 'clipboard', 'basic_keyboard']
    )

def _get_linux_strategy_order(self, app_info: Optional[ApplicationInfo]) -> list:
    """Get Linux-specific strategy order"""
    if self.platform_info.desktop_env == DesktopEnvironment.KDE:
        return self._get_kde_strategy_order(app_info)
    elif self.platform_info.session_type == SessionType.X11:
        return self._get_x11_strategy_order(app_info)
    else:  # Wayland
        return ['atspi', 'clipboard', 'basic_keyboard']

def _get_kde_strategy_order(self, app_info: Optional[ApplicationInfo]) -> list:
    """Get KDE-specific strategy order"""
    if app_info and app_info.app_type in (ApplicationType.EDITOR, ApplicationType.IDE):
        return ['clipboard', 'kde_simple', 'xtest', 'xdotool', 'basic_keyboard']
    return ['kde_simple', 'xtest', 'xdotool', 'clipboard', 'basic_keyboard']

def _get_x11_strategy_order(self, app_info: Optional[ApplicationInfo]) -> list:
    """Get X11-specific strategy order"""
    if app_info and app_info.app_type in (ApplicationType.EDITOR, ApplicationType.IDE):
        return ['clipboard', 'xtest', 'xdotool', 'basic_keyboard']
    return ['xtest', 'xdotool', 'clipboard', 'basic_keyboard']
```

## 5. Make Delays Configurable

### File: `personalparakeet/config.py`

Add injection configuration:

```python
@dataclass
class InjectionConfig:
    """Configuration for text injection timing and behavior"""
    default_key_delay: float = 0.01  # Delay between keystrokes
    clipboard_paste_delay: float = 0.1  # Delay after clipboard operations
    strategy_switch_delay: float = 0.05  # Delay when switching strategies
    focus_acquisition_delay: float = 0.05  # Delay to ensure window focus
    
    # Platform-specific delays
    windows_ui_automation_delay: float = 0.02
    linux_xtest_delay: float = 0.005
    kde_dbus_timeout: float = 5.0
    
    # Retry configuration
    max_clipboard_retries: int = 3
    clipboard_retry_delay: float = 0.1
```

Then update all `time.sleep()` calls to use these configuration values:
```python
# In TextInjectionManager.__init__():
self.config = config_manager.get_injection_config()

# Replace hard-coded delays:
time.sleep(0.05)  # OLD
time.sleep(self.config.focus_acquisition_delay)  # NEW
```

## 6. Enhance Documentation

### Add comprehensive docstrings following this template:

```python
def inject_text(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
    """Inject text using the best available strategy.
    
    This method automatically selects the optimal injection strategy based on
    the current platform and target application. It implements a fallback chain
    to ensure text is injected even if the preferred method fails.
    
    Args:
        text: The text to inject into the active application
        app_info: Optional information about the target application. If not
                 provided, will attempt to auto-detect the active window.
    
    Returns:
        bool: True if injection succeeded, False if all strategies failed
        
    Raises:
        None: All exceptions are caught and logged. Failures result in
              fallback attempts rather than exceptions.
              
    Example:
        >>> injector = TextInjectionManager()
        >>> success = injector.inject_text("Hello, World!")
        >>> if not success:
        ...     print("All injection strategies failed")
    
    Note:
        The method adds a trailing space to the injected text to ensure
        proper word separation in continuous dictation scenarios.
    """
```

## 7. Additional Improvements

### Create a constants file `personalparakeet/constants.py`:
```python
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
```

## Implementation Priority:
1. **Quick wins** (1 hour):
   - Fix KDE magic numbers
   - Create constants file
   
2. **Medium effort** (2-3 hours):
   - Implement logging framework
   - Refactor long methods
   
3. **More complex** (3-4 hours):
   - Implement robust clipboard manager
   - Add comprehensive documentation
   - Make delays configurable

## Testing After Implementation:
1. Run existing tests to ensure no regressions
2. Test clipboard safety with simulated failures
3. Verify logging output in both console and file
4. Test with different delay configurations
5. Ensure all platform-specific code paths still work

These improvements will significantly enhance code quality, maintainability, and production readiness without changing the core architecture that's already working well.