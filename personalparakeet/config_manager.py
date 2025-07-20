"""Configuration management for PersonalParakeet

This module provides comprehensive configuration management including:
- JSON and YAML configuration file support
- Configuration validation
- Default configuration creation
- Runtime configuration updates
"""

import json
import yaml
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Union
from pathlib import Path
from .config import InjectionConfig
from .logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class VADSettings:
    enabled: bool = True
    sensitivity: str = "medium"  # low/medium/high preset
    custom_threshold: Optional[float] = None
    pause_duration_ms: int = 1500
    adaptive_mode: bool = True
    breathing_detection: bool = True
    background_noise_adaptation: bool = True

@dataclass
class PersonalParakeetConfig:
    """Complete configuration for PersonalParakeet system"""
    injection: InjectionConfig
    vad: VADSettings = VADSettings()
    
    # Model settings
    model_name: str = "nvidia/parakeet-tdt-1.1b"
    use_gpu: bool = True
    
    # Audio settings
    audio_device_index: Optional[int] = None
    chunk_duration: float = 1.0
    sample_rate: int = 16000
    
    # Hotkey settings
    toggle_hotkey: str = "F4"
    
    # Application settings
    enable_application_detection: bool = True
    application_profiles: Dict[str, Dict[str, Any]] = None
    
    # Monitoring settings
    enable_monitoring: bool = True
    stats_report_interval: int = 30
    
    # Debug settings
    enable_debug_logging: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Post-init processing"""
        if self.application_profiles is None:
            self.application_profiles = {}
        
        if self.vad is None:
            self.vad = VADSettings()

        # Sync audio settings with injection config
        if self.audio_device_index is not None:
            self.injection.audio_device_index = self.audio_device_index
        
        self.injection.chunk_duration = self.chunk_duration
        self.injection.sample_rate = self.sample_rate
        self.injection.enable_monitoring = self.enable_monitoring
        self.injection.stats_report_interval = self.stats_report_interval
        self.injection.enable_debug_logging = self.enable_debug_logging
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PersonalParakeetConfig':
        """Create configuration from dictionary"""
        # Extract injection config
        injection_dict = config_dict.get('injection', {})
        injection_config = InjectionConfig.from_dict(injection_dict)
        
        # Extract VAD config
        vad_dict = config_dict.get('vad', {})
        vad_config = VADSettings(**vad_dict)

        # Remove injection and VAD from main dict
        main_dict = config_dict.copy()
        main_dict.pop('injection', None)
        main_dict.pop('vad', None)
        
        # Filter out unknown keys
        valid_keys = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_dict = {k: v for k, v in main_dict.items() if k in valid_keys}
        
        return cls(injection=injection_config, vad=vad_config, **filtered_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        result = asdict(self)
        return result
    
    def validate(self) -> bool:
        """Validate all configuration values"""
        try:
            # Validate injection config
            if not self.injection.validate():
                return False
            
            # Validate audio settings
            if self.sample_rate not in [8000, 16000, 22050, 44100, 48000]:
                raise ValueError("sample_rate must be a standard audio sample rate")
            
            if self.chunk_duration < 0.1 or self.chunk_duration > 10:
                raise ValueError("chunk_duration must be between 0.1 and 10 seconds")
            
            # Validate hotkey
            valid_hotkeys = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
            if self.toggle_hotkey not in valid_hotkeys:
                raise ValueError(f"toggle_hotkey must be one of: {valid_hotkeys}")
            
            # Validate log level
            valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.log_level not in valid_log_levels:
                raise ValueError(f"log_level must be one of: {valid_log_levels}")
            
            return True
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            return False


class ConfigManager:
    """Manages configuration file loading, saving, and validation"""
    
    DEFAULT_CONFIG_LOCATIONS = [
        Path.home() / '.config' / 'personalparakeet' / 'config.json',
        Path.home() / '.config' / 'personalparakeet' / 'config.yaml',
        Path.home() / '.personalparakeet' / 'config.json',
        Path.home() / '.personalparakeet' / 'config.yaml',
        Path.cwd() / 'config.json',
        Path.cwd() / 'config.yaml'
    ]
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize configuration manager"""
        self.config_path = Path(config_path) if config_path else None
        self.config: Optional[PersonalParakeetConfig] = None
    
    def load_config(self) -> PersonalParakeetConfig:
        """Load configuration from file or create default"""
        if self.config_path and self.config_path.exists():
            config_data = self._load_config_file(self.config_path)
            self.config = PersonalParakeetConfig.from_dict(config_data)
        else:
            # Try default locations
            for config_path in self.DEFAULT_CONFIG_LOCATIONS:
                if config_path.exists():
                    logger.info(f"Loading config from {config_path}")
                    config_data = self._load_config_file(config_path)
                    self.config = PersonalParakeetConfig.from_dict(config_data)
                    self.config_path = config_path
                    break
            else:
                # No config file found, create default
                logger.info("No config file found, using default configuration")
                self.config = PersonalParakeetConfig(injection=InjectionConfig(), vad=VADSettings())
        
        # Validate configuration
        if not self.config.validate():
            logger.warning("Configuration validation failed, using default values")
            self.config = PersonalParakeetConfig(injection=InjectionConfig(), vad=VADSettings())
        
        return self.config
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    return json.load(f)
                elif config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading config file: {e}")
    
    def save_config(self, config: Optional[PersonalParakeetConfig] = None) -> bool:
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        if config is None:
            logger.error("No configuration to save")
            return False
        
        # Validate before saving
        if not config.validate():
            logger.error("Configuration validation failed, not saving")
            return False
        
        # Determine config path
        config_path = self.config_path
        if not config_path:
            config_path = self.DEFAULT_CONFIG_LOCATIONS[0]
        
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            config_data = config.to_dict()
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                elif config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
                else:
                    # Default to JSON
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {config_path}")
            self.config_path = config_path
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def create_sample_config(self, output_path: Optional[Union[str, Path]] = None) -> bool:
        """Create a sample configuration file"""
        if output_path is None:
            output_path = Path.cwd() / 'config_sample.json'
        else:
            output_path = Path(output_path)
        
        # Create sample config with comments
        sample_config = PersonalParakeetConfig(injection=InjectionConfig(), vad=VADSettings())
        
        # Add sample application profiles
        sample_config.application_profiles = {
            "notepad.exe": {
                "strategy_order": ["keyboard", "ui_automation", "clipboard"],
                "key_delay": 0.01
            },
            "code.exe": {
                "strategy_order": ["clipboard", "ui_automation", "keyboard"],
                "key_delay": 0.005
            },
            "chrome.exe": {
                "strategy_order": ["keyboard", "ui_automation", "send_input"],
                "key_delay": 0.008
            }
        }
        
        try:
            config_data = sample_config.to_dict()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Sample configuration created at {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating sample configuration: {e}")
            return False
    
    def get_config(self) -> PersonalParakeetConfig:
        """Get current configuration"""
        if self.config is None:
            self.load_config()
        return self.config
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        if self.config is None:
            self.load_config()
        
        try:
            # Convert current config to dict
            config_dict = self.config.to_dict()
            
            # Apply updates (nested updates supported)
            def deep_update(original, updates):
                for key, value in updates.items():
                    if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                        deep_update(original[key], value)
                    else:
                        original[key] = value
            
            deep_update(config_dict, updates)
            
            # Create new config and validate
            new_config = PersonalParakeetConfig.from_dict(config_dict)
            if not new_config.validate():
                logger.error("Updated configuration failed validation")
                return False
            
            self.config = new_config
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False


# Global configuration manager instance
_config_manager = None


def get_config_manager(config_path: Optional[Union[str, Path]] = None) -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def get_config() -> PersonalParakeetConfig:
    """Get current configuration"""
    return get_config_manager().get_config()


def save_config(config: Optional[PersonalParakeetConfig] = None) -> bool:
    """Save configuration to file"""
    return get_config_manager().save_config(config)


def create_sample__config(output_path: Optional[Union[str, Path]] = None) -> bool:
    """Create a sample configuration file"""
    return get_config_manager().create_sample_config(output_path)


def update_config(updates: Dict[str, Any]) -> bool:
    """Update configuration with new values"""
    return get_config_manager().update_config(updates)
