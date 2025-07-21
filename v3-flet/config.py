#!/usr/bin/env python3
"""
Configuration system for PersonalParakeet v3 using dataclasses
Replaces JSON-based config with type-safe dataclass configuration
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio processing configuration"""
    sample_rate: int = 16000
    chunk_size: int = 8000  # 0.5s chunks for responsive processing
    device_index: Optional[int] = None
    silence_threshold: float = 0.01


@dataclass
class VADConfig:
    """Voice Activity Detection configuration"""
    silence_threshold: float = 0.01
    pause_threshold: float = 1.5  # seconds before pause is detected
    frame_duration: float = 0.03


@dataclass
class ClarityConfig:
    """Clarity Engine configuration"""
    enabled: bool = True
    rule_based_only: bool = True
    target_latency_ms: float = 50.0


@dataclass
class WindowConfig:
    """Window and UI configuration"""
    default_width: int = 600
    default_height: int = 150
    opacity: float = 0.95
    always_on_top: bool = True
    frameless: bool = True
    resizable: bool = True


@dataclass
class ThoughtLinkingConfig:
    """Thought linking configuration (future feature)"""
    enabled: bool = False
    similarity_threshold: float = 0.3
    timeout_threshold: float = 30.0


@dataclass
class CommandModeConfig:
    """Command mode configuration (future feature)"""
    enabled: bool = False
    activation_phrase: str = "parakeet command"
    confidence_threshold: float = 0.8
    timeout: float = 5.0


@dataclass
class V3Config:
    """Main configuration class for PersonalParakeet v3"""
    audio: AudioConfig
    vad: VADConfig
    clarity: ClarityConfig
    window: WindowConfig
    thought_linking: ThoughtLinkingConfig
    command_mode: CommandModeConfig
    
    def __init__(self):
        # Initialize with default values
        self.audio = AudioConfig()
        self.vad = VADConfig()
        self.clarity = ClarityConfig()
        self.window = WindowConfig()
        self.thought_linking = ThoughtLinkingConfig()
        self.command_mode = CommandModeConfig()
        
        # Try to load from config file
        self._load_from_file()
    
    def _load_from_file(self):
        """Load configuration from JSON file if it exists"""
        config_path = Path("config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                self._update_from_dict(data)
                logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                logger.info("Using default configuration")
        else:
            logger.info("No config file found, using defaults")
    
    def _update_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary"""
        # Update audio config
        if 'audio' in data:
            audio_data = data['audio']
            self.audio.sample_rate = audio_data.get('sample_rate', self.audio.sample_rate)
            self.audio.device_index = audio_data.get('audio_device_index')  # Legacy key
            self.audio.silence_threshold = audio_data.get('silence_threshold', self.audio.silence_threshold)
        
        # Update VAD config
        if 'vad' in data:
            vad_data = data['vad']
            self.vad.silence_threshold = vad_data.get('custom_threshold', self.vad.silence_threshold)
            self.vad.pause_threshold = vad_data.get('pause_duration_ms', 1500) / 1000.0  # Convert ms to s
        
        # Update clarity config
        if 'clarity' in data:
            clarity_data = data['clarity']
            self.clarity.enabled = clarity_data.get('enabled', self.clarity.enabled)
        
        # Handle legacy config format
        if 'audio_device_index' in data:
            self.audio.device_index = data['audio_device_index']
        if 'sample_rate' in data:
            self.audio.sample_rate = data['sample_rate']
    
    def save_to_file(self, path: Optional[Path] = None):
        """Save configuration to JSON file"""
        if path is None:
            path = Path("config.json")
        
        try:
            with open(path, 'w') as f:
                json.dump(asdict(self), f, indent=2)
            logger.info(f"Configuration saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save config to {path}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    def update_audio_device(self, device_index: Optional[int]):
        """Update audio device index"""
        self.audio.device_index = device_index
        logger.info(f"Audio device updated to index {device_index}")
    
    def update_vad_settings(self, silence_threshold: Optional[float] = None, 
                           pause_threshold: Optional[float] = None):
        """Update VAD settings"""
        if silence_threshold is not None:
            self.vad.silence_threshold = silence_threshold
        if pause_threshold is not None:
            self.vad.pause_threshold = pause_threshold
        logger.info("VAD settings updated")
    
    def update_window_settings(self, width: Optional[int] = None, 
                              height: Optional[int] = None,
                              opacity: Optional[float] = None):
        """Update window settings"""
        if width is not None:
            self.window.default_width = width
        if height is not None:
            self.window.default_height = height
        if opacity is not None:
            self.window.opacity = opacity
        logger.info("Window settings updated")
    
    def toggle_clarity(self) -> bool:
        """Toggle Clarity Engine and return new state"""
        self.clarity.enabled = not self.clarity.enabled
        logger.info(f"Clarity Engine {'enabled' if self.clarity.enabled else 'disabled'}")
        return self.clarity.enabled
    
    def toggle_command_mode(self) -> bool:
        """Toggle Command Mode and return new state"""
        self.command_mode.enabled = not self.command_mode.enabled
        logger.info(f"Command Mode {'enabled' if self.command_mode.enabled else 'disabled'}")
        return self.command_mode.enabled


class ConfigManager:
    """Configuration manager for backward compatibility"""
    
    def __init__(self):
        self.config = V3Config()
    
    def get_config(self) -> V3Config:
        """Get the current configuration"""
        return self.config
    
    def save_config(self):
        """Save configuration to file"""
        self.config.save_to_file()
    
    def reload_config(self):
        """Reload configuration from file"""
        self.config = V3Config()


# Create global config instance for easy access
config = V3Config()


def get_config() -> V3Config:
    """Get the global configuration instance"""
    return config