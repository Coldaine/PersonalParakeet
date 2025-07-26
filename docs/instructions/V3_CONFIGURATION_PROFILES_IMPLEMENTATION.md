# PersonalParakeet v3 Configuration Profiles Implementation Guide

## Overview

This document provides high-level implementation instructions for porting the v2 configuration profile system to v3 Flet architecture. This is a **Week 2 Critical Foundation** task that can be done in parallel with Enhanced Application Detection.

**Status**: 40% Complete (Basic dataclass config exists)  
**Estimated Effort**: 2 days  
**Priority**: ⭐⭐⭐ Critical

## Current State Analysis

### ✅ What v3 Already Has
- Basic dataclass configuration in `v3-flet/config.py`
- Type-safe configuration structures:
  - `AudioConfig`, `VADConfig`, `ClarityConfig`, `WindowConfig`
- JSON loading/saving functionality
- Integration with main Flet app

### ❌ What's Missing (Port from v2)
- **Configuration Profiles** - Predefined sets of optimized parameters
- **Runtime Profile Switching** - Change profiles without restart
- **Profile Management** - Creation, validation, persistence
- **Application-Specific Profiles** - Per-app configuration overrides

## Implementation Tasks

### Task 1: Port Configuration Profiles (Day 1)

**Source**: `personalparakeet/config_manager.py` lines 21-50  
**Target**: Enhance `v3-flet/config.py`

#### 1.1 Add Profile Dataclasses
```python
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
```

#### 1.2 Define Standard Profiles
Port these exact profiles from v2:
- **Fast Conversation** - Low latency, moderate accuracy
- **Balanced** - Default balanced settings
- **Accurate Document** - High accuracy, higher latency acceptable
- **Low-Latency** - Minimal delay, basic corrections only

#### 1.3 Profile Factory Functions
```python
def create_fast_conversation_profile() -> ConfigurationProfile:
def create_balanced_profile() -> ConfigurationProfile:
def create_accurate_document_profile() -> ConfigurationProfile:
def create_low_latency_profile() -> ConfigurationProfile:
```

### Task 2: Profile Management System (Day 1.5)

**Source**: `personalparakeet/config_manager.py` lines 95-150  
**Target**: New `ProfileManager` class in `v3-flet/config.py`

#### 2.1 ProfileManager Class
```python
class ProfileManager:
    """Manages configuration profiles with runtime switching"""
    
    def __init__(self, config_dir: Path):
    def load_profile(self, profile_name: str) -> ConfigurationProfile:
    def save_profile(self, profile: ConfigurationProfile) -> bool:
    def list_available_profiles(self) -> List[str]:
    def get_current_profile(self) -> ConfigurationProfile:
    def switch_profile(self, profile_name: str) -> bool:
    def validate_profile(self, profile: ConfigurationProfile) -> List[str]:
```

#### 2.2 Runtime Profile Switching
- **Thread-safe profile updates** - Use locks for concurrent access
- **Component notification** - Notify audio, VAD, clarity engines of changes
- **Graceful fallback** - If profile switch fails, maintain current settings
- **Validation** - Validate profile before applying changes

### Task 3: Integration with Flet App (Day 2)

**Target**: Enhance `v3-flet/main.py` and UI components

#### 3.1 Main App Integration
```python
class PersonalParakeetApp:
    def __init__(self):
        self.profile_manager = ProfileManager(config_dir)
        self.current_profile = self.profile_manager.get_current_profile()
```

#### 3.2 UI Profile Selection
Add to `v3-flet/ui/components.py`:
```python
class ProfileSelector(ft.UserControl):
    """Dropdown for selecting configuration profiles"""
    
    def build(self):
        return ft.Dropdown(
            options=[ft.dropdown.Option(name) for name in profiles],
            on_change=self.on_profile_change
        )
```

#### 3.3 Runtime Application
- **Hot-swap components** - Update audio, VAD, clarity settings without restart
- **UI feedback** - Show current profile in status bar
- **Persistence** - Save last selected profile as default

## Technical Specifications

### Profile Parameters to Port

From v2 `PersonalParakeetConfig` and `VADSettings`:

```python
# Audio settings
sample_rate: int = 16000
chunk_duration: float = 1.0
audio_device_index: Optional[int] = None

# VAD settings
sensitivity: str = "medium"  # low/medium/high
custom_threshold: Optional[float] = None
pause_duration_ms: int = 1500
adaptive_mode: bool = True

# Model settings  
model_name: str = "nvidia/parakeet-tdt-1.1b"
use_gpu: bool = True

# Performance targets
target_latency_ms: float
max_memory_mb: int
```

### Profile Validation Rules

1. **Audio**: Sample rate must be 8000, 16000, or 22050
2. **VAD**: Pause duration 500ms-5000ms range
3. **Latency**: Target latency must be achievable with hardware
4. **Memory**: Memory limit must be reasonable for system

### Threading Safety

- **Profile switching must be thread-safe** - Use `threading.Lock()`
- **Component updates must be atomic** - Either all succeed or none
- **UI updates must be async** - Use `page.update_async()` for Flet

## Implementation Patterns

### Pattern 1: Profile Inheritance
```python
# Base profile with common settings
base_profile = create_balanced_profile()

# Specialized profile inheriting from base
fast_profile = dataclasses.replace(
    base_profile,
    name="Fast Conversation",
    vad=dataclasses.replace(base_profile.vad, pause_duration_ms=1000)
)
```

### Pattern 2: Component Notification
```python
def switch_profile(self, profile_name: str) -> bool:
    new_profile = self.load_profile(profile_name)
    
    # Validate before applying
    errors = self.validate_profile(new_profile)
    if errors:
        return False
    
    # Apply to all components atomically
    with self.profile_lock:
        self.audio_engine.update_config(new_profile.audio)
        self.vad_engine.update_config(new_profile.vad)
        self.clarity_engine.update_config(new_profile.clarity)
        
    return True
```

### Pattern 3: Flet UI Updates
```python
async def on_profile_change(self, e):
    """Handle profile selection in UI"""
    success = self.profile_manager.switch_profile(e.control.value)
    
    if success:
        self.status_text.value = f"Profile: {e.control.value}"
        self.status_text.color = "green"
    else:
        self.status_text.value = "Profile switch failed"
        self.status_text.color = "red"
        
    await self.page.update_async()
```

## Testing Requirements

### Unit Tests
- Test profile creation and validation
- Test profile switching logic
- Test component notification system

### Integration Tests  
- Test profile switching during active dictation
- Test profile persistence across app restarts
- Test UI profile selection workflow

### Performance Tests
- Measure profile switch time (<100ms target)
- Verify no audio dropouts during switch
- Confirm memory usage stays within profile limits

## Success Criteria

### Functional Requirements
- ✅ All 4 standard profiles working (Fast, Balanced, Accurate, Low-Latency)
- ✅ Runtime profile switching without restart
- ✅ Profile persistence across sessions
- ✅ Profile selection UI in Flet app

### Performance Requirements  
- ✅ Profile switch time <100ms
- ✅ No audio dropouts during switch
- ✅ Thread-safe concurrent access
- ✅ Memory usage within profile limits

### User Experience Requirements
- ✅ Clear profile descriptions in UI
- ✅ Immediate feedback on profile changes
- ✅ Graceful error handling for invalid profiles
- ✅ Backward compatibility with existing v2 config files

## Dependencies and Blockers

### Dependencies
- ✅ Basic v3 Flet app structure (exists)
- ✅ Core dataclass configuration (exists)
- ✅ Component integration patterns (exists)

### No Blockers
- **Independent of Application Detection** - Can be implemented in parallel
- **Independent of Text Injection** - Pure configuration management
- **Well-defined scope** - Port existing working v2 functionality

## Files to Modify

### Primary Files
- `v3-flet/config.py` - Add profiles and ProfileManager
- `v3-flet/main.py` - Integrate ProfileManager
- `v3-flet/ui/components.py` - Add ProfileSelector widget

### Supporting Files
- `v3-flet/core/audio_engine.py` - Add config update method
- `v3-flet/core/vad_engine.py` - Add config update method  
- `v3-flet/core/clarity_engine.py` - Add config update method

### Test Files
- Create `v3-flet/tests/test_profiles.py`
- Add profile tests to existing integration tests

## Implementation Priority

1. **Day 1 Morning**: Port profile dataclasses and factory functions
2. **Day 1 Afternoon**: Implement ProfileManager class with validation
3. **Day 2 Morning**: Add Flet UI components and integration
4. **Day 2 Afternoon**: Testing and performance validation

This task is **perfectly parallel** to Enhanced Application Detection - they share no dependencies and use different skill sets (data management vs system integration).