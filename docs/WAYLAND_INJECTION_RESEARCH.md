# Wayland Text Injection Research

## The Wayland Challenge
Wayland's security model prevents traditional X11-style input injection by design. Each application is isolated, and there's no global input mechanism like X11's XTest extension.

## Possible Approaches (Even "Dirty" Ones)

### 1. ydotool - Virtual Input Device
**How it works**: Creates a virtual input device at the kernel level
**Requirements**: 
- Run as root OR add user to `input` group
- `ydotool` daemon running
**Security**: Requires elevated permissions

```bash
# Installation
sudo apt install ydotool
sudo usermod -a -G input $USER
# Logout/login required

# Usage
ydotool type "Hello World"
```

### 2. wtype - Wayland-native typing
**How it works**: Uses Wayland protocols where available
**Limitations**: Only works on wlroots-based compositors (Sway, River, etc.)
**Security**: Uses compositor's permission model

```bash
# Installation
sudo apt install wtype

# Usage
wtype "Hello World"
```

### 3. XWayland Compatibility Layer
**How it works**: Run the app through XWayland, use X11 injection
**Limitations**: Only works for X11 apps running under XWayland
**Trick**: Force apps to use XWayland with env vars

```bash
# Force X11 backend
GDK_BACKEND=x11 ./app
QT_QPA_PLATFORM=xcb ./app
```

### 4. Virtual Keyboard Protocol
**How it works**: Implement Wayland's virtual keyboard protocol
**Requirements**: Compositor must support `zwp_virtual_keyboard_v1`
**Implementation**: Complex but "proper" Wayland way

### 5. Input Method Framework (Dirty but Works)
**How it works**: Register as an input method (like virtual keyboards)
**Examples**: 
- Fcitx5 modules
- IBus extensions
- Maliit plugins

### 6. Compositor-Specific Hacks

#### GNOME/Mutter
- Use GNOME's accessibility APIs
- DBus interface for some input
- `gdbus` commands for certain actions

#### KDE/KWin
- KWin scripts can inject input
- DBus interfaces available
- More permissive than GNOME

#### Sway/wlroots
- Most flexible for custom protocols
- Supports virtual keyboard protocol
- Can use `swaymsg` for some actions

### 7. The Nuclear Option - uinput
**How it works**: Direct kernel-level input injection
**Requirements**: Root or special permissions
**Implementation**: Create virtual keyboard device

```python
import evdev
from evdev import UInput, ecodes as e

# Create virtual keyboard
ui = UInput()

# Type text
for char in "Hello":
    # Convert char to keycode and inject
    ui.write(e.EV_KEY, keycode, 1)  # press
    ui.write(e.EV_KEY, keycode, 0)  # release
    ui.syn()
```

### 8. Clipboard Injection Fallback
**How it works**: Copy to clipboard, then simulate Ctrl+V
**Limitations**: Overwrites clipboard, requires paste support
**Tools**: `wl-copy` + `ydotool`/`wtype`

### 9. AT-SPI2 (Accessibility)
**How it works**: Use accessibility framework
**Support**: Varies by application
**Implementation**: Complex but sometimes works

### 10. Custom Wayland Protocol Extension
**How it works**: Fork compositor, add custom protocol
**Practicality**: Only for personal use
**Benefit**: Complete control

## Recommended Implementation Strategy

1. **Detection Phase**:
   - Check if running under Wayland
   - Detect compositor type (GNOME, KDE, wlroots, etc.)
   - Check available tools (ydotool, wtype, etc.)

2. **Fallback Chain**:
   ```
   Try in order:
   1. wtype (if wlroots)
   2. ydotool (if daemon running)
   3. Virtual keyboard protocol
   4. Clipboard injection
   5. XWayland detection + X11 injection
   6. Fail with helpful error
   ```

3. **Setup Script**:
   - Auto-install ydotool/wtype
   - Configure permissions
   - Start ydotool daemon
   - Test injection methods

## Security Considerations
Since this is for personal use:
- Running ydotool daemon is acceptable
- Adding user to input group is fine
- Using root/sudo for setup is OK
- Modifying compositor configs is possible