# Technical Plan for Migrating a Real-Time Text Injection System to Wayland

This document outlines a technical plan for migrating a real-time text injection system from the legacy X11 windowing system to the modern, secure Wayland protocol. The migration is complex due to Wayland's security-first design, which intentionally isolates applications and restricts global introspection and control.

## Core Challenges

*   **Security Model:** Wayland's core principle is client isolation. Unlike X11, one application cannot easily inspect or control another. This breaks traditional methods for active window detection and text injection.
*   **Compositor Fragmentation:** There is no single "Wayland." Different compositors (GNOME's Mutter, KDE's KWin, wlroots-based like Sway) implement different, often incompatible, APIs for advanced features. A one-size-fits-all solution is not possible.
*   **XWayland Compatibility:** Legacy X11 applications run in a compatibility layer called XWayland. The system must be able to interact with both native Wayland and XWayland applications.

## Proposed Architecture: A Multi-Tiered Fallback System

A resilient, multi-layered architecture is proposed to handle the fragmented ecosystem. The system will attempt strategies in order of preference, gracefully degrading to lower-level methods if higher-level ones fail.

**Critical First Step: Compositor Detection**
The system must first identify the running compositor (GNOME, KDE, or wlroots) to select the correct specialized tools. This is done by checking environment variables (`XDG_CURRENT_DESKTOP`) and running processes (`mutter`, `kwin_wayland`, `sway`).

### Tier 1: The Accessibility Layer (AT-SPI) - **Primary Strategy**

*   **Method:** Use the Assistive Technology Service Provider Interface (AT-SPI), a desktop-agnostic accessibility framework.
*   **Rationale:** This is the most robust and semantically correct approach. It interacts with UI elements (e.g., "text input field") rather than simulating raw key presses. It works across compositors for most applications built with GTK and Qt.
*   **Tools:** `pyatspi2` Python library.

### Tier 2: Compositor-Specific Layer - **Fallback Strategy**

If AT-SPI fails, the system uses APIs specific to the detected compositor.

*   **GNOME/Mutter:**
    *   **Method:** Use a dedicated GNOME Shell extension (`focused-window-dbus`) that exposes focused window information over D-Bus.
    *   **Tools:** `dbus-next` Python library to communicate with the extension.
*   **KDE/KWin:**
    *   **Status:** ✅ **Completed**
    *   **Implementation:** A dedicated `KDEWaylandManager` module has been implemented. It uses a robust fallback chain:
        1.  **`kdotool`:** Preferred method for simplicity and reliability.
        2.  **D-Bus:** Native Python fallback using `dbus-next` if `kdotool` is not available.
        3.  **`ydotool` / Clipboard:** Further fallbacks for maximum compatibility.
    *   **Method:** Leverage the KWin Scripting API, controlled via D-Bus.
    *   **Tools:** `kdotool`, `dbus-next`, `ydotool`, `wl-clipboard`.
*   **wlroots (Sway, Hyprland):**
    *   **Method:** Use the `wlr-foreign-toplevel-management` Wayland protocol for window information and `zwp_virtual_keyboard_v1` for input.
    *   **Tools:** `swaymsg` (for Sway IPC), `wtype` command-line utility, or `pywayland` library.

### Tier 3: Low-Level/Universal Layer - **Final Fallback**

*   **Method 1: Kernel Input (`uinput`)**
    *   **Description:** Create a virtual keyboard device at the kernel level.
    *   **Pros:** Universal, bypasses the compositor entirely.
    *   **Cons:** Requires root privileges, which is a significant security concern.
    *   **Tools:** `ydotool`.
*   **Method 2: Clipboard Manipulation**
    *   **Description:** Copy text to the clipboard and simulate a "paste" command (Ctrl+V).
    *   **Pros:** Simple concept.
    *   **Cons:** Highly unreliable, disruptive to the user's clipboard, and depends on the application's paste handling.
    *   **Tools:** `wl-clipboard` and an input simulator like `ydotool` or `wtype`.

## Testing and Validation

A comprehensive testing strategy is required across different environments:
*   **Environments:** Separate virtual machines for GNOME, KDE, and a wlroots-based compositor (e.g., Sway).
*   **Test Cases:** A matrix of target applications (GTK, Qt, XWayland, Electron) and actions (detection, ASCII/Unicode injection).
*   **Debugging Tools:** `accerciser` (for AT-SPI), `d-feet`/`qdbusviewer` (for D-Bus), and `WAYLAND_DEBUG=1` (for protocol-level issues).

## Conclusion

The recommended architecture prioritizes the most stable, secure, and semantically correct methods first (AT-SPI). By layering compositor-specific fallbacks and, as a last resort, low-level techniques, the system can achieve robust and reliable text injection in the modern, fragmented Wayland ecosystem.
