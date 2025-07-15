"""
Configuration system for PersonalParakeet with TOML support and pre-defined profiles.
"""

import os
import toml
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


@dataclass
class ConfigurationProfile:
    """Configuration profile with all tunable parameters"""
    name: str
    description: str
    agreement_threshold: int = 2        # 1-5: consecutive agreements needed
    chunk_duration: float = 1.0         # 0.3-2.0s: audio chunk size
    max_pending_words: int = 15         # 5-30: buffer size
    word_timeout: float = 4.0           # 2.0-7.0s: force commit timeout
    position_tolerance: int = 2         # 1-3: word position flexibility
    audio_level_threshold: float = 0.01 # 0.001-0.1: minimum audio level

    def validate(self) -> List[str]:
        """Validate configuration parameters and return error messages"""
        errors = []
        
        if not (1 <= self.agreement_threshold <= 5):
            errors.append("agreement_threshold must be between 1 and 5")
        
        if not (0.3 <= self.chunk_duration <= 2.0):
            errors.append("chunk_duration must be between 0.3 and 2.0 seconds")
        
        if not (5 <= self.max_pending_words <= 30):
            errors.append("max_pending_words must be between 5 and 30")
        
        if not (2.0 <= self.word_timeout <= 7.0):
            errors.append("word_timeout must be between 2.0 and 7.0 seconds")
        
        if not (1 <= self.position_tolerance <= 3):
            errors.append("position_tolerance must be between 1 and 3")
        
        if not (0.001 <= self.audio_level_threshold <= 0.1):
            errors.append("audio_level_threshold must be between 0.001 and 0.1")
        
        return errors


# Pre-defined configuration profiles
FAST_CONVERSATION = ConfigurationProfile(
    name="fast_conversation",
    description="Optimized for quick responses in conversational settings",
    agreement_threshold=1,      # Immediate commitment
    chunk_duration=0.3,         # Short chunks for speed
    max_pending_words=8,        # Small buffer
    word_timeout=2.0,           # Quick timeout
    position_tolerance=3,       # Flexible matching
    audio_level_threshold=0.005 # Moderate sensitivity
)

BALANCED_MODE = ConfigurationProfile(
    name="balanced",
    description="Balanced accuracy and responsiveness for general use",
    agreement_threshold=2,      # Standard stability
    chunk_duration=1.0,         # Standard chunks
    max_pending_words=15,       # Moderate buffer
    word_timeout=4.0,           # Balanced timeout
    position_tolerance=2,       # Standard flexibility
    audio_level_threshold=0.01  # Default sensitivity
)

ACCURATE_DOCUMENT = ConfigurationProfile(
    name="accurate_document",
    description="Maximizes accuracy for formal document dictation",
    agreement_threshold=3,      # High stability requirement
    chunk_duration=2.0,         # Long chunks for context
    max_pending_words=30,       # Large buffer
    word_timeout=7.0,           # Extended timeout
    position_tolerance=1,       # Strict matching
    audio_level_threshold=0.02  # Reduced sensitivity
)

LOW_LATENCY = ConfigurationProfile(
    name="low_latency",
    description="Minimizes delay for real-time applications",
    agreement_threshold=1,      # Immediate commitment
    chunk_duration=0.5,         # Balanced for low latency
    max_pending_words=5,        # Minimal buffer
    word_timeout=2.5,           # Quick timeout
    position_tolerance=2,       # Moderate flexibility
    audio_level_threshold=0.001 # High sensitivity
)


@dataclass
class AudioConfig:
    """Audio system configuration"""
    device_pattern: str = ""           # Device name pattern to match
    sample_rate: int = 16000           # Sample rate for processing
    channels: int = 1                  # Mono audio
    silence_threshold: float = 0.01    # Minimum audio level to process


@dataclass
class HotkeyConfig:
    """Hotkey configuration"""
    toggle_dictation: str = "F4"
    llm_refinement: str = "F5"
    context_enhancement: str = "F1+F4"
    quit_application: str = "Ctrl+Alt+Q"


@dataclass
class SystemConfig:
    """Complete system configuration"""
    audio: AudioConfig = field(default_factory=AudioConfig)
    hotkeys: HotkeyConfig = field(default_factory=HotkeyConfig)
    active_profile: str = "balanced"
    

class ConfigurationManager:
    """Manages configuration profiles and runtime settings"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        # Set default config directory to user's home
        if config_dir is None:
            config_dir = Path.home() / ".personalparakeet"
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.toml"
        
        # Built-in profiles
        self.builtin_profiles: Dict[str, ConfigurationProfile] = {
            "fast_conversation": FAST_CONVERSATION,
            "balanced": BALANCED_MODE,
            "accurate_document": ACCURATE_DOCUMENT,
            "low_latency": LOW_LATENCY
        }
        
        # Custom profiles loaded from config
        self.custom_profiles: Dict[str, ConfigurationProfile] = {}
        
        # System configuration
        self.system_config = SystemConfig()
        
        # Current active profile
        self.active_profile_name = "balanced"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.load_from_file()
    
    def get_active_profile(self) -> ConfigurationProfile:
        """Get the currently active configuration profile"""
        return self.get_profile(self.active_profile_name)
    
    def get_profile(self, profile_name: str) -> ConfigurationProfile:
        """Get a specific configuration profile"""
        if profile_name in self.builtin_profiles:
            return self.builtin_profiles[profile_name]
        elif profile_name in self.custom_profiles:
            return self.custom_profiles[profile_name]
        else:
            print(f"⚠️  Profile '{profile_name}' not found, using balanced mode")
            return self.builtin_profiles["balanced"]
    
    def list_available_profiles(self) -> List[str]:
        """List all available profile names"""
        builtin = list(self.builtin_profiles.keys())
        custom = list(self.custom_profiles.keys())
        return builtin + custom
    
    def switch_profile(self, profile_name: str) -> bool:
        """Switch to a different configuration profile"""
        if profile_name in self.builtin_profiles or profile_name in self.custom_profiles:
            self.active_profile_name = profile_name
            self.system_config.active_profile = profile_name
            print(f"🔄 Switched to profile: {profile_name}")
            return True
        else:
            print(f"❌ Profile '{profile_name}' not found")
            return False
    
    def save_custom_profile(self, profile: ConfigurationProfile) -> bool:
        """Save a custom configuration profile"""
        # Validate the profile
        errors = profile.validate()
        if errors:
            print(f"❌ Invalid profile configuration:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        # Save to custom profiles
        self.custom_profiles[profile.name] = profile
        print(f"✅ Saved custom profile: {profile.name}")
        return True
    
    def delete_custom_profile(self, profile_name: str) -> bool:
        """Delete a custom configuration profile"""
        if profile_name in self.custom_profiles:
            del self.custom_profiles[profile_name]
            print(f"🗑️  Deleted custom profile: {profile_name}")
            return True
        else:
            print(f"❌ Custom profile '{profile_name}' not found")
            return False
    
    def validate_profile(self, profile: ConfigurationProfile) -> List[str]:
        """Validate a configuration profile"""
        return profile.validate()
    
    def load_from_file(self) -> bool:
        """Load configuration from TOML file"""
        if not self.config_file.exists():
            print(f"📄 No config file found, creating default: {self.config_file}")
            return self.save_to_file()
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = toml.load(f)
            
            # Load system configuration
            if 'system' in config_data:
                system_data = config_data['system']
                
                # Load audio config
                if 'audio' in system_data:
                    audio_data = system_data['audio']
                    self.system_config.audio = AudioConfig(**audio_data)
                
                # Load hotkey config
                if 'hotkeys' in system_data:
                    hotkey_data = system_data['hotkeys']
                    self.system_config.hotkeys = HotkeyConfig(**hotkey_data)
                
                # Load active profile
                if 'active_profile' in system_data:
                    self.active_profile_name = system_data['active_profile']
                    self.system_config.active_profile = self.active_profile_name
            
            # Load custom profiles
            if 'profiles' in config_data:
                for profile_name, profile_data in config_data['profiles'].items():
                    profile = ConfigurationProfile(
                        name=profile_name,
                        **profile_data
                    )
                    self.custom_profiles[profile_name] = profile
            
            print(f"✅ Configuration loaded from: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            print(f"   Using default configuration")
            return False
    
    def save_to_file(self) -> bool:
        """Save configuration to TOML file"""
        try:
            config_data = {
                'system': {
                    'audio': asdict(self.system_config.audio),
                    'hotkeys': asdict(self.system_config.hotkeys),
                    'active_profile': self.active_profile_name
                },
                'profiles': {}
            }
            
            # Save custom profiles
            for profile_name, profile in self.custom_profiles.items():
                profile_dict = asdict(profile)
                # Remove name from the dict since it's the key
                profile_dict.pop('name', None)
                config_data['profiles'][profile_name] = profile_dict
            
            with open(self.config_file, 'w') as f:
                toml.dump(config_data, f)
            
            print(f"✅ Configuration saved to: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return False
    
    def get_system_config(self) -> SystemConfig:
        """Get the system configuration"""
        return self.system_config
    
    def update_audio_config(self, **kwargs) -> None:
        """Update audio configuration"""
        for key, value in kwargs.items():
            if hasattr(self.system_config.audio, key):
                setattr(self.system_config.audio, key, value)
    
    def update_hotkey_config(self, **kwargs) -> None:
        """Update hotkey configuration"""
        for key, value in kwargs.items():
            if hasattr(self.system_config.hotkeys, key):
                setattr(self.system_config.hotkeys, key, value)
    
    def export_profile(self, profile_name: str, file_path: Path) -> bool:
        """Export a profile to a separate TOML file"""
        profile = self.get_profile(profile_name)
        if not profile:
            return False
        
        try:
            profile_data = asdict(profile)
            with open(file_path, 'w') as f:
                toml.dump({'profile': profile_data}, f)
            
            print(f"✅ Profile exported to: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting profile: {e}")
            return False
    
    def import_profile(self, file_path: Path) -> Optional[ConfigurationProfile]:
        """Import a profile from a TOML file"""
        try:
            with open(file_path, 'r') as f:
                data = toml.load(f)
            
            if 'profile' not in data:
                print(f"❌ Invalid profile file format")
                return None
            
            profile_data = data['profile']
            profile = ConfigurationProfile(**profile_data)
            
            # Validate the profile
            errors = profile.validate()
            if errors:
                print(f"❌ Invalid imported profile:")
                for error in errors:
                    print(f"   - {error}")
                return None
            
            print(f"✅ Profile imported: {profile.name}")
            return profile
            
        except Exception as e:
            print(f"❌ Error importing profile: {e}")
            return None