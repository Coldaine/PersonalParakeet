#!/usr/bin/env python3
"""
Configuration system for PersonalParakeet v3 using dataclasses
Replaces JSON-based config with type-safe dataclass configuration
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
import logging
import json
from pathlib import Path
import threading

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


@dataclass
class ConfigurationProfile:
    """Complete configuration profile with all settings"""
    name: str
    description: str
    
    # Component configs
    audio: AudioConfig
    vad: VADConfig
    clarity: ClarityConfig
    window: WindowConfig
    
    # Profile metadata
    optimized_for: str  # "speed", "accuracy", "conversation", "document"
    target_latency_ms: float
    memory_usage_mb: int


def create_fast_conversation_profile() -> ConfigurationProfile:
    """Create profile optimized for fast conversation"""
    return ConfigurationProfile(
        name="Fast Conversation",
        description="Low latency, moderate accuracy for real-time conversation",
        audio=AudioConfig(
            sample_rate=16000,
            chunk_size=4000,  # Smaller chunks for lower latency
            silence_threshold=0.02
        ),
        vad=VADConfig(
            silence_threshold=0.02,
            pause_threshold=1.0,  # Shorter pause detection
            frame_duration=0.02
        ),
        clarity=ClarityConfig(
            enabled=True,
            rule_based_only=True,  # Faster rule-based corrections
            target_latency_ms=30.0
        ),
        window=WindowConfig(
            default_width=600,
            default_height=150,
            opacity=0.95,
            always_on_top=True,
            frameless=True,
            resizable=True
        ),
        optimized_for="conversation",
        target_latency_ms=100.0,
        memory_usage_mb=512
    )


def create_balanced_profile() -> ConfigurationProfile:
    """Create balanced profile for general use"""
    return ConfigurationProfile(
        name="Balanced",
        description="Default balanced settings for most use cases",
        audio=AudioConfig(
            sample_rate=16000,
            chunk_size=8000,
            silence_threshold=0.01
        ),
        vad=VADConfig(
            silence_threshold=0.01,
            pause_threshold=1.5,
            frame_duration=0.03
        ),
        clarity=ClarityConfig(
            enabled=True,
            rule_based_only=True,
            target_latency_ms=50.0
        ),
        window=WindowConfig(
            default_width=600,
            default_height=150,
            opacity=0.95,
            always_on_top=True,
            frameless=True,
            resizable=True
        ),
        optimized_for="balanced",
        target_latency_ms=200.0,
        memory_usage_mb=1024
    )


def create_accurate_document_profile() -> ConfigurationProfile:
    """Create profile optimized for document transcription accuracy"""
    return ConfigurationProfile(
        name="Accurate Document",
        description="High accuracy, higher latency acceptable for document transcription",
        audio=AudioConfig(
            sample_rate=22050,  # Higher sample rate for better quality
            chunk_size=16000,   # Larger chunks for better processing
            silence_threshold=0.005
        ),
        vad=VADConfig(
            silence_threshold=0.005,
            pause_threshold=2.0,  # Longer pause for document context
            frame_duration=0.03
        ),
        clarity=ClarityConfig(
            enabled=True,
            rule_based_only=False,  # Full clarity processing
            target_latency_ms=100.0
        ),
        window=WindowConfig(
            default_width=600,
            default_height=150,
            opacity=0.95,
            always_on_top=True,
            frameless=True,
            resizable=True
        ),
        optimized_for="document",
        target_latency_ms=500.0,
        memory_usage_mb=2048
    )


def create_low_latency_profile() -> ConfigurationProfile:
    """Create profile for minimal delay, basic corrections only"""
    return ConfigurationProfile(
        name="Low-Latency",
        description="Minimal delay, basic corrections only for maximum speed",
        audio=AudioConfig(
            sample_rate=16000,
            chunk_size=2000,  # Very small chunks
            silence_threshold=0.03
        ),
        vad=VADConfig(
            silence_threshold=0.03,
            pause_threshold=0.8,  # Very short pause detection
            frame_duration=0.02
        ),
        clarity=ClarityConfig(
            enabled=False,  # Disable clarity for speed
            rule_based_only=True,
            target_latency_ms=20.0
        ),
        window=WindowConfig(
            default_width=600,
            default_height=150,
            opacity=0.95,
            always_on_top=True,
            frameless=True,
            resizable=True
        ),
        optimized_for="speed",
        target_latency_ms=50.0,
        memory_usage_mb=256
    )


class ProfileManager:
    """Manages configuration profiles with runtime switching"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.profiles_dir = config_dir / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        self._current_profile: ConfigurationProfile = create_balanced_profile()
        self._profile_lock = threading.Lock()
        self._observers = []
        
        # Load saved profiles
        self._load_profiles()
    
    def _load_profiles(self):
        """Load profiles from disk"""
        # Ensure standard profiles exist
        standard_profiles = [
            create_fast_conversation_profile(),
            create_balanced_profile(),
            create_accurate_document_profile(),
            create_low_latency_profile()
        ]
        
        for profile in standard_profiles:
            profile_path = self.profiles_dir / f"{profile.name.lower().replace(' ', '_')}.json"
            if not profile_path.exists():
                self.save_profile(profile)
    
    def load_profile(self, profile_name: str) -> ConfigurationProfile:
        """Load a profile by name"""
        profile_path = self.profiles_dir / f"{profile_name.lower().replace(' ', '_')}.json"
        
        if profile_path.exists():
            try:
                with open(profile_path, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct profile from saved data
                audio = AudioConfig(**data['audio'])
                vad = VADConfig(**data['vad'])
                clarity = ClarityConfig(**data['clarity'])
                window = WindowConfig(**data['window'])
                
                return ConfigurationProfile(
                    name=data['name'],
                    description=data['description'],
                    audio=audio,
                    vad=vad,
                    clarity=clarity,
                    window=window,
                    optimized_for=data['optimized_for'],
                    target_latency_ms=data['target_latency_ms'],
                    memory_usage_mb=data['memory_usage_mb']
                )
            except Exception as e:
                logger.error(f"Failed to load profile {profile_name}: {e}")
        
        # Return standard profile if file doesn't exist or failed to load
        profile_map = {
            "fast_conversation": create_fast_conversation_profile,
            "balanced": create_balanced_profile,
            "accurate_document": create_accurate_document_profile,
            "low_latency": create_low_latency_profile
        }
        
        return profile_map.get(profile_name.lower().replace(' ', '_'), create_balanced_profile)()
    
    def save_profile(self, profile: ConfigurationProfile) -> bool:
        """Save a profile to disk"""
        try:
            profile_path = self.profiles_dir / f"{profile.name.lower().replace(' ', '_')}.json"
            with open(profile_path, 'w') as f:
                json.dump(asdict(profile), f, indent=2)
            logger.info(f"Profile saved: {profile.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save profile {profile.name}: {e}")
            return False
    
    def list_available_profiles(self) -> List[str]:
        """List all available profile names"""
        profiles = []
        
        # Add standard profiles
        standard_profiles = [
            "Fast Conversation",
            "Balanced",
            "Accurate Document",
            "Low-Latency"
        ]
        profiles.extend(standard_profiles)
        
        # Add custom profiles from disk
        for profile_file in self.profiles_dir.glob("*.json"):
            if profile_file.stem not in [p.lower().replace(' ', '_') for p in standard_profiles]:
                profiles.append(profile_file.stem.replace('_', ' ').title())
        
        return sorted(set(profiles))
    
    def get_current_profile(self) -> ConfigurationProfile:
        """Get the current active profile"""
        with self._profile_lock:
            return self._current_profile
    
    def switch_profile(self, profile_name: str) -> bool:
        """Switch to a different profile"""
        try:
            new_profile = self.load_profile(profile_name)
            errors = self.validate_profile(new_profile)
            
            if errors:
                logger.error(f"Profile validation failed: {errors}")
                return False
            
            with self._profile_lock:
                old_profile = self._current_profile
                self._current_profile = new_profile
                
                # Notify observers
                for observer in self._observers:
                    try:
                        observer.on_profile_changed(new_profile, old_profile)
                    except Exception as e:
                        logger.error(f"Profile change observer failed: {e}")
            
            logger.info(f"Switched to profile: {profile_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch profile to {profile_name}: {e}")
            return False
    
    def validate_profile(self, profile: ConfigurationProfile) -> List[str]:
        """Validate a configuration profile"""
        errors = []
        
        # Audio validation
        if profile.audio.sample_rate not in [8000, 16000, 22050]:
            errors.append(f"Invalid sample rate: {profile.audio.sample_rate}")
        
        if profile.audio.chunk_size <= 0:
            errors.append(f"Invalid chunk size: {profile.audio.chunk_size}")
        
        # VAD validation
        if not 0.5 <= profile.vad.pause_threshold <= 5.0:
            errors.append(f"Pause threshold out of range: {profile.vad.pause_threshold}")
        
        # Performance validation
        if profile.target_latency_ms <= 0:
            errors.append(f"Invalid target latency: {profile.target_latency_ms}")
        
        if profile.memory_usage_mb <= 0:
            errors.append(f"Invalid memory usage: {profile.memory_usage_mb}")
        
        return errors
    
    def add_observer(self, observer):
        """Add a profile change observer"""
        self._observers.append(observer)
    
    def remove_observer(self, observer):
        """Remove a profile change observer"""
        if observer in self._observers:
            self._observers.remove(observer)


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