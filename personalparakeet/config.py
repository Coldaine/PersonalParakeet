from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from .logger import setup_logger

logger = setup_logger(__name__)

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
    xdotool_timeout: float = 5.0
    
    # Retry configuration
    max_clipboard_retries: int = 3
    clipboard_retry_delay: float = 0.1
    
    # Strategy preferences
    preferred_strategy_order: Optional[list] = None
    enable_performance_optimization: bool = True
    skip_consecutive_failures: int = 3
    
    # Audio configuration
    audio_device_index: Optional[int] = None
    chunk_duration: float = 1.0
    sample_rate: int = 16000
    
    # Monitoring settings
    enable_monitoring: bool = True
    stats_report_interval: int = 30
    enable_debug_logging: bool = False
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'InjectionConfig':
        """Create configuration from dictionary"""
        # Filter out unknown keys
        valid_keys = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_keys}
        return cls(**filtered_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    def validate(self) -> bool:
        """Validate configuration values"""
        try:
            # Validate timing values
            if self.default_key_delay < 0 or self.default_key_delay > 1:
                raise ValueError("default_key_delay must be between 0 and 1")
            
            if self.clipboard_paste_delay < 0 or self.clipboard_paste_delay > 5:
                raise ValueError("clipboard_paste_delay must be between 0 and 5")
            
            if self.sample_rate not in [8000, 16000, 22050, 44100, 48000]:
                raise ValueError("sample_rate must be a standard audio sample rate")
            
            if self.chunk_duration < 0.1 or self.chunk_duration > 10:
                raise ValueError("chunk_duration must be between 0.1 and 10 seconds")
            
            if self.max_clipboard_retries < 1 or self.max_clipboard_retries > 10:
                raise ValueError("max_clipboard_retries must be between 1 and 10")
            
            return True
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            return False