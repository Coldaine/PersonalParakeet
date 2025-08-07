# Wayland Virtual Keyboard Protocol Implementation

## Overview

PersonalParakeet now includes a high-performance implementation of the Wayland Virtual Keyboard Protocol (`zwp_virtual_keyboard_v1`) optimized for real-time dictation with sub-5ms latency targets.

## Architecture

### Core Components

1. **VirtualKeyboardInjector** (`src/personalparakeet/core/virtual_keyboard_injector.py`)
   - Native ctypes-based implementation using libwayland-client
   - Direct protocol binding for maximum performance
   - Pre-computed key mappings for zero-lookup overhead
   - Microsecond-precision timing control

2. **WaylandInjector Integration** (`src/personalparakeet/core/wayland_injector.py`)
   - Virtual keyboard as highest priority injection method
   - Automatic fallback to existing methods (wtype, ydotool, etc.)
   - Lazy initialization for minimal startup overhead

3. **Performance Testing Suite** (`src/personalparakeet/tests/test_virtual_keyboard_performance.py`)
   - Comprehensive latency benchmarking
   - Memory efficiency validation
   - Success rate monitoring

## Performance Specifications

### Latency Targets
- **Single Character**: < 5ms average
- **Short Words (5 chars)**: < 10ms average  
- **Full Sentences**: < 50ms average
- **Special Characters**: < 30ms average (includes modifier handling)

### Memory Efficiency
- < 10MB growth during sustained operation
- Minimal allocation during hot path execution
- Pre-computed mappings to avoid runtime lookups

### Success Rate Targets
- **Single Characters**: > 95%
- **Words**: > 90%
- **Sentences**: > 85%
- **Special Characters**: > 80%

## Implementation Details

### ctypes Binding Architecture

```python
class WaylandLibrary:
    """Direct ctypes wrapper for libwayland-client"""
    
    def _setup_functions(self):
        # wl_display functions
        self.lib.wl_display_connect.argtypes = [ctypes.c_char_p]
        self.lib.wl_display_connect.restype = ctypes.c_void_p
        
        # Virtual keyboard protocol calls
        self.lib.wl_proxy_marshal.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
```

### Performance Optimizations

1. **Pre-computed Key Mappings**
   ```python
   def _build_key_map(self) -> Dict[str, int]:
       # Character to keycode mapping built at initialization
       # Zero runtime lookup overhead
   ```

2. **Optimized Event Generation**
   ```python
   def _text_to_key_events_optimized(self, text: str) -> List[KeyEvent]:
       # Microsecond-precision timestamps
       # Minimal object allocation
       # Batch event processing
   ```

3. **Direct Protocol Calls**
   ```python
   def _send_key_event_fast(self, event: KeyEvent) -> bool:
       # Direct zwp_virtual_keyboard_v1_key() via ctypes
       # No intermediate abstractions
   ```

## Integration Points

### WaylandInjector Priority Order

1. **VIRTUAL_KB** (zwp_virtual_keyboard_v1) - Native protocol
2. **WTYPE** - wlroots compositor tool
3. **YDOTOOL** - Generic Wayland input
4. **CLIPBOARD** - Copy/paste simulation
5. **XWAYLAND** - X11 compatibility layer
6. **UINPUT** - Direct kernel input (requires permissions)

### Automatic Detection

```python
def _check_virtual_keyboard_support(self) -> bool:
    """Check if virtual keyboard protocol is supported."""
    # Environment validation
    # Library availability check
    # Protocol capability detection
```

## Usage Examples

### Basic Text Injection

```python
from personalparakeet.core.virtual_keyboard_injector import VirtualKeyboardInjector

injector = VirtualKeyboardInjector()
if injector.is_available():
    success, error = injector.inject_text("Hello, World!")
    if success:
        print("Text injected successfully")
```

### Through WaylandInjector (Recommended)

```python
from personalparakeet.core.wayland_injector import WaylandInjector

injector = WaylandInjector()
# Will automatically use virtual keyboard if available
success, error = injector.inject_text("Dictated text here")
```

### Performance Testing

```python
from personalparakeet.tests.test_virtual_keyboard_performance import VirtualKeyboardPerformanceTest

test_suite = VirtualKeyboardPerformanceTest()
test_suite.setup_method()
test_suite.test_comprehensive_performance_suite()
```

## Compatibility

### Supported Compositors

- **GNOME/Mutter** - Full support expected
- **KDE/KWin** - Full support expected  
- **Sway** - Full support expected
- **Hyprland** - Full support expected
- **wlroots-based** - Full support expected
- **Weston** - Full support expected

### Requirements

- **Environment**: `XDG_SESSION_TYPE=wayland`
- **Display**: `WAYLAND_DISPLAY` set
- **Library**: `libwayland-client.so` available
- **Protocol**: Compositor must support `zwp_virtual_keyboard_v1`

### Fallback Behavior

If virtual keyboard protocol is unavailable, the system automatically falls back to:
1. External tools (wtype, ydotool)
2. Clipboard-based injection
3. XWayland compatibility layer
4. Unsafe mode (last resort)

## Performance Benchmarking

### Running Performance Tests

```bash
# Run full performance suite
python -m pytest src/personalparakeet/tests/test_virtual_keyboard_performance.py -v

# Run specific performance test
python src/personalparakeet/tests/test_virtual_keyboard_performance.py

# With detailed logging
python src/personalparakeet/tests/test_virtual_keyboard_performance.py 2>&1 | tee performance_results.log
```

### Expected Results

```
Performance Test Results: Single Character
==========================================
Iterations:       200
Success Rate:     98.5%
Latency Metrics (ms):
  Average:        2.147
  95th Percentile: 4.823
✅ PASSED: Average latency 2.147ms < 5ms target
```

## Troubleshooting

### Common Issues

1. **"Could not load libwayland-client"**
   ```bash
   # Install Wayland development libraries
   sudo apt install libwayland-dev
   ```

2. **"Virtual keyboard protocol not available"**
   - Check compositor support
   - Verify `XDG_SESSION_TYPE=wayland`
   - Ensure `WAYLAND_DISPLAY` is set

3. **High Latency Results**
   - Check system load
   - Verify compositor performance
   - Review ctypes library version

### Debug Commands

```python
# Check environment
import os
print(f"Session: {os.environ.get('XDG_SESSION_TYPE')}")
print(f"Display: {os.environ.get('WAYLAND_DISPLAY')}")

# Test library loading
from personalparakeet.core.virtual_keyboard_injector import WaylandLibrary
lib = WaylandLibrary()  # Should not raise exception
```

## Future Enhancements

### Planned Improvements

1. **Protocol Extensions**
   - Unicode input method support
   - Advanced modifier combinations
   - Custom keymap loading

2. **Performance Optimizations**
   - Memory pool allocation
   - Batch event submission
   - Async event processing

3. **Compatibility**
   - Additional compositor testing
   - Protocol version negotiation
   - Graceful degradation handling

### Research Areas

- **Sub-millisecond Latency**: Investigation into kernel bypass techniques
- **Hardware Acceleration**: GPU-assisted text processing
- **Protocol Extensions**: Custom Wayland protocol for dictation

## Technical References

- [Wayland Virtual Keyboard Protocol Specification](https://github.com/wayland-project/wayland-protocols/tree/main/unstable/virtual-keyboard)
- [libwayland-client Documentation](https://wayland.freedesktop.org/docs/html/apb.html)
- [Linux Input Event Codes](https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h)

## Contact & Support

For performance issues or protocol-specific questions, see:
- Project documentation in `docs/`
- Test results in performance logs
- Integration examples in `tests/`