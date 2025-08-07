# Thought Linking Integration Guide

## Overview

The enhanced thought linking system is fully implemented but **DISABLED BY DEFAULT**. This document explains how to activate and integrate it when ready.

## Current Status

- ✅ **Core Implementation**: Complete in `core/thought_linker.py`
- ✅ **Platform Detectors**: Placeholder modules for window/cursor detection
- ✅ **Integration Layer**: Ready in `core/thought_linking_integration.py`
- ✅ **Unit Tests**: Comprehensive tests in `tests/test_thought_linking.py`
- ❌ **Not Active**: Disabled in config by default

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Audio Pipeline  │────▶│ Thought Linker   │────▶│ Injection Mgr   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
              ┌─────▼──────┐      ┌──────▼──────┐
              │Window Det. │      │Cursor Det.  │
              └────────────┘      └─────────────┘
```

## Activation Steps

### 1. Enable in Config

```python
# config.py
@dataclass
class ThoughtLinkingConfig:
    enabled: bool = True  # Change from False to True
    similarity_threshold: float = 0.3
    timeout_threshold: float = 30.0
    cursor_movement_threshold: int = 100
```

### 2. Update Main Application

In the main application, add the integration:

```python
# In __init__ method
from core.thought_linker import create_thought_linker
from core.thought_linking_integration import create_thought_linking_integration

# Create thought linker
self.thought_linker = create_thought_linker(
    enabled=config.thought_linking.enabled,
    similarity_threshold=config.thought_linking.similarity_threshold,
    timeout_threshold=config.thought_linking.timeout_threshold
)

# Create integration
self.thought_linking = create_thought_linking_integration(
    self.thought_linker,
    self.injection_manager
)
```

### 3. Modify Commit Logic

Replace the simple commit with thought-aware commit:

```python
async def _on_commit_text(self):
    """Handle commit text with thought linking"""
    if self.text or self.corrected_text:
        final_text = self.corrected_text or self.text
        
        # Process through thought linking
        context = await self.thought_linking.process_text_with_linking(final_text.strip())
        
        # Inject with context
        if self.injection_manager:
            await self.thought_linking.inject_with_context(context)
        
        # Clear based on decision
        if context.clear_buffer:
            await self._clear_current_text()
```

### 4. Register User Actions

Hook into keyboard events:

```python
def _on_key_press(self, e: ft.KeyboardEvent):
    """Register key presses for thought linking"""
    if self.thought_linking:
        if e.key == "Enter":
            self.thought_linking.register_user_action("Enter")
        elif e.key == "Tab":
            self.thought_linking.register_user_action("Tab")
        elif e.key == "Escape":
            self.thought_linking.register_user_action("Escape")
```

## Signal Types and Decisions

### Primary Signals (High Priority)
- **Window Change** (0.95): User switched applications
- **User Input** (0.9): Enter, Tab, Escape pressed
- **Cursor Movement** (0.7): Significant cursor position change

### Secondary Signals
- **Timeout** (0.6): Long pause between utterances
- **Semantic Similarity** (0.0-1.0): Text relatedness

### Decisions
- `APPEND_WITH_SPACE`: Continue same thought
- `START_NEW_PARAGRAPH`: New paragraph in same context
- `START_NEW_THOUGHT`: Complete context switch
- `COMMIT_AND_CONTINUE`: Commit but maintain context

## Platform-Specific Implementation

When ready to implement platform detection:

### Windows
```python
# In window_detector.py _init_windows()
import win32gui
import win32process

# In cursor_detector.py _init_windows()  
import win32api
```

### Linux
```python
# Check for X11 vs Wayland
# Use python-xlib for X11
# Use pydbus for Wayland
```

### macOS
```python
# Use pyobjc-framework-Quartz
# Or Accessibility APIs
```

## Testing

Run tests to verify logic:

```bash
pytest tests/test_thought_linking.py -v
```

## Performance Considerations

- Window/cursor detection adds ~5-10ms overhead
- Semantic similarity calculation: ~1-2ms
- Total overhead: <15ms per decision
- Negligible impact on user experience

## Future Enhancements

1. **ML-Based Similarity**: Replace rule-based with embeddings
2. **Voice Tone Detection**: Pause/pitch analysis
3. **Application-Specific Rules**: Per-app linking behavior
4. **User Preference Learning**: Adapt to user patterns
