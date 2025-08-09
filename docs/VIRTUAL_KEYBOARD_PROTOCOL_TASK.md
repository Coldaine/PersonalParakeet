# Wayland Virtual Keyboard Protocol Implementation Task

## Overview
Implement native Wayland virtual keyboard protocol (zwp_virtual_keyboard_v1) for PersonalParakeet's text injection system. This is the most secure and performant method for text input on Wayland.

## Background
PersonalParakeet currently has several text injection methods for Wayland:
- ✅ ydotool (working, ~5-20ms latency)
- ✅ wtype (working, ~5-20ms latency)
- ✅ clipboard injection (working, ~150-300ms latency)
- ✅ unsafe mode with sudo/aggressive methods
- ❌ Virtual keyboard protocol (not implemented - YOUR TASK)

## Task Requirements

### 1. Research Phase
- Study the zwp_virtual_keyboard_v1 protocol specification
- Understand Wayland protocol bindings for Python
- Research existing implementations (e.g., wtype source code)
- Identify compositor support (GNOME, KDE, Sway)

### 2. Implementation Requirements

#### Core Implementation
Create `/src/personalparakeet/core/virtual_keyboard_injector.py` with:

```python
class VirtualKeyboardInjector:
    """Native Wayland virtual keyboard protocol implementation."""
    
    def __init__(self):
        """Initialize Wayland connection and virtual keyboard."""
        # Connect to Wayland display
        # Get virtual keyboard manager
        # Create virtual keyboard instance
        
    def inject_text(self, text: str) -> Tuple[bool, Optional[str]]:
        """Inject text using virtual keyboard protocol."""
        # Send key events for each character
        # Handle modifiers (shift, ctrl, etc.)
        # Return success/failure
        
    def inject_key(self, key: str, modifiers: List[str] = None):
        """Send individual key press/release events."""
        # Map key to keycode
        # Send key press event
        # Send key release event
```

#### Integration Points
1. Update `/src/personalparakeet/core/wayland_injector.py`:
   - Add virtual keyboard detection in `_detect_capabilities()`
   - Add virtual keyboard method to `inject_text()`
   - Prioritize virtual keyboard over other methods

2. Update method enum in wayland_injector.py:
   ```python
   class InjectionMethod(Enum):
       VIRTUAL_KEYBOARD = "virtual_keyboard"  # Add this
       YDOTOOL = "ydotool"
       WTYPE = "wtype"
       # ... etc
   ```

### 3. Technical Considerations

#### Python Wayland Bindings
Research and choose appropriate library:
- pywayland - Pure Python Wayland protocol implementation
- python-wayland - Alternative bindings
- Consider using ctypes to interface with libwayland-client directly

#### Protocol Implementation
```
1. Connect to Wayland display
2. Bind to zwp_virtual_keyboard_manager_v1
3. Create virtual keyboard with seat
4. For each character:
   - Map to Linux keycode
   - Send key press event with timestamp
   - Send key release event
5. Handle special keys and modifiers
```

#### Key Mapping
- Map Unicode characters to Linux keycodes
- Handle special characters requiring modifiers
- Support for non-ASCII text (consider using compose sequences)

### 4. Testing Requirements

Create `/src/personalparakeet/tests/test_virtual_keyboard.py`:
```python
def test_virtual_keyboard_available():
    """Test if virtual keyboard protocol is available."""
    
def test_inject_simple_text():
    """Test injecting simple ASCII text."""
    
def test_inject_special_characters():
    """Test special characters and modifiers."""
    
def test_performance():
    """Verify <5ms injection latency."""
```

### 5. Expected Challenges

1. **Python Bindings**: Limited Python support for Wayland protocols
   - May need to create minimal bindings using ctypes
   - Consider embedding C code if necessary

2. **Compositor Support**: Not all compositors support the protocol
   - Must gracefully fall back to other methods
   - Test on GNOME, KDE, and Sway

3. **Key Mapping**: Complex Unicode to keycode conversion
   - May need to use XKB libraries
   - Handle different keyboard layouts

### 6. Success Criteria

- [ ] Virtual keyboard protocol detected when available
- [ ] Text injection works on GNOME/Mutter
- [ ] Text injection works on KDE/KWin  
- [ ] Text injection works on Sway/wlroots
- [ ] Latency < 5ms (faster than ydotool/wtype)
- [ ] Graceful fallback when protocol unavailable
- [ ] No sudo/root permissions required
- [ ] Supports full Unicode text input

### 7. Resources

- [Wayland Protocol Spec - Virtual Keyboard](https://wayland.app/protocols/virtual-keyboard-unstable-v1)
- [wtype source code](https://github.com/atx/wtype) - Reference implementation in C
- [pywayland documentation](https://pywayland.readthedocs.io/)
- [Linux keycodes](https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h)

### 8. Implementation Strategy

1. **Start Simple**: Get basic ASCII text working first
2. **Incremental**: Add special characters, then Unicode
3. **Test Early**: Use `test_virtual_keyboard.py` throughout
4. **Fallback Safe**: Ensure it doesn't break existing methods

### 9. Code Quality Requirements

- Type hints for all functions
- Comprehensive docstrings
- Error handling with specific exceptions
- Debug logging for troubleshooting
- Follow project's code style (Black, isort, ruff)

### 10. Deliverables

1. `virtual_keyboard_injector.py` - Core implementation
2. `test_virtual_keyboard.py` - Test suite
3. Updated `wayland_injector.py` - Integration
4. Documentation updates in `WAYLAND_INJECTION_RESEARCH.md`
5. Performance benchmarks comparing all methods

## Getting Started

```bash
# Activate environment
conda activate personalparakeet

# Install any additional dependencies
poetry add pywayland  # If using pywayland

# Create the implementation file
touch src/personalparakeet/core/virtual_keyboard_injector.py

# Start with basic structure and iterate
```

## Notes for Implementation

- This is for personal use, so some security compromises are acceptable
- Prioritize functionality over perfect security
- The user has RTX 5090 and high-end hardware - use it
- Existing methods work, so this is an enhancement, not critical
- Can use test_wayland_injection.py as reference for testing

Good luck! The virtual keyboard protocol is the "proper" way to do text injection on Wayland, so getting this working will make PersonalParakeet's injection system complete.