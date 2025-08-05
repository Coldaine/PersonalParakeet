#!/bin/bash
# Setup script for Wayland text injection support

set -e

echo "PersonalParakeet Wayland Injection Setup"
echo "========================================"
echo

# Detect package manager
if command -v apt &> /dev/null; then
    PKG_MGR="apt"
    INSTALL_CMD="sudo apt install -y"
elif command -v dnf &> /dev/null; then
    PKG_MGR="dnf"
    INSTALL_CMD="sudo dnf install -y"
elif command -v pacman &> /dev/null; then
    PKG_MGR="pacman"
    INSTALL_CMD="sudo pacman -S --noconfirm"
elif command -v zypper &> /dev/null; then
    PKG_MGR="zypper"
    INSTALL_CMD="sudo zypper install -y"
else
    echo "❌ Unsupported package manager"
    exit 1
fi

echo "📦 Detected package manager: $PKG_MGR"

# Function to check if running on Wayland
check_wayland() {
    if [[ "$XDG_SESSION_TYPE" == "wayland" ]] || [[ -n "$WAYLAND_DISPLAY" ]]; then
        echo "✅ Running on Wayland"
        return 0
    else
        echo "⚠️  Not running on Wayland (session type: $XDG_SESSION_TYPE)"
        return 1
    fi
}

# Function to detect compositor
detect_compositor() {
    if [[ "$XDG_CURRENT_DESKTOP" == *"GNOME"* ]]; then
        echo "GNOME (Mutter)"
    elif [[ "$XDG_CURRENT_DESKTOP" == *"KDE"* ]]; then
        echo "KDE (KWin)"
    elif command -v sway &> /dev/null && pgrep -x sway > /dev/null; then
        echo "Sway"
    elif command -v hyprctl &> /dev/null; then
        echo "Hyprland"
    else
        echo "Unknown"
    fi
}

# Install ydotool
install_ydotool() {
    echo
    echo "📦 Installing ydotool..."
    
    case $PKG_MGR in
        apt)
            # For Ubuntu/Debian, might need to build from source
            if ! $INSTALL_CMD ydotool 2>/dev/null; then
                echo "ydotool not in repos, building from source..."
                $INSTALL_CMD build-essential cmake libboost-program-options-dev
                
                # Clone and build
                TEMP_DIR=$(mktemp -d)
                cd "$TEMP_DIR"
                git clone https://github.com/ReimuNotMoe/ydotool.git
                cd ydotool
                mkdir build && cd build
                cmake ..
                make
                sudo make install
                cd - > /dev/null
                rm -rf "$TEMP_DIR"
            fi
            ;;
        *)
            $INSTALL_CMD ydotool
            ;;
    esac
    
    # Add user to input group
    echo "Adding $USER to input group..."
    sudo usermod -a -G input "$USER"
    
    # Create systemd service for ydotoold
    echo "Creating ydotoold service..."
    sudo tee /etc/systemd/system/ydotoold.service > /dev/null << EOF
[Unit]
Description=ydotoold daemon
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/local/bin/ydotoold
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable and start service
    sudo systemctl daemon-reload
    sudo systemctl enable ydotoold
    sudo systemctl start ydotoold
    
    echo "✅ ydotool installed and configured"
}

# Install wtype (for wlroots compositors)
install_wtype() {
    echo
    echo "📦 Installing wtype..."
    
    case $PKG_MGR in
        apt)
            $INSTALL_CMD wtype || {
                echo "wtype not in repos, building from source..."
                $INSTALL_CMD build-essential meson wayland-protocols libwayland-dev
                
                TEMP_DIR=$(mktemp -d)
                cd "$TEMP_DIR"
                git clone https://github.com/atx/wtype.git
                cd wtype
                meson build
                ninja -C build
                sudo ninja -C build install
                cd - > /dev/null
                rm -rf "$TEMP_DIR"
            }
            ;;
        *)
            $INSTALL_CMD wtype
            ;;
    esac
    
    echo "✅ wtype installed"
}

# Install wl-clipboard
install_wl_clipboard() {
    echo
    echo "📦 Installing wl-clipboard..."
    $INSTALL_CMD wl-clipboard
    echo "✅ wl-clipboard installed"
}

# Main setup
main() {
    check_wayland || {
        echo "⚠️  Warning: Setup will continue but injection may not work until you're on Wayland"
    }
    
    echo
    echo "🔍 Detected compositor: $(detect_compositor)"
    echo
    
    # Check what's already installed
    echo "Checking installed tools..."
    HAS_YDOTOOL=$(command -v ydotool &> /dev/null && echo "yes" || echo "no")
    HAS_WTYPE=$(command -v wtype &> /dev/null && echo "yes" || echo "no")
    HAS_WL_COPY=$(command -v wl-copy &> /dev/null && echo "yes" || echo "no")
    
    echo "  ydotool: $HAS_YDOTOOL"
    echo "  wtype: $HAS_WTYPE"
    echo "  wl-clipboard: $HAS_WL_COPY"
    
    # Install missing tools
    if [[ "$HAS_YDOTOOL" == "no" ]]; then
        install_ydotool
    else
        echo "✅ ydotool already installed"
        
        # Check if daemon is running
        if ! pgrep -x ydotoold > /dev/null; then
            echo "Starting ydotoold daemon..."
            sudo systemctl start ydotoold || ydotoold &
        fi
    fi
    
    # Install wtype for wlroots compositors
    COMPOSITOR=$(detect_compositor)
    if [[ "$COMPOSITOR" == "Sway" ]] || [[ "$COMPOSITOR" == "Hyprland" ]]; then
        if [[ "$HAS_WTYPE" == "no" ]]; then
            install_wtype
        else
            echo "✅ wtype already installed"
        fi
    fi
    
    # Always install wl-clipboard as fallback
    if [[ "$HAS_WL_COPY" == "no" ]]; then
        install_wl_clipboard
    else
        echo "✅ wl-clipboard already installed"
    fi
    
    echo
    echo "✅ Setup complete!"
    echo
    echo "⚠️  IMPORTANT: You need to logout and login again for group changes to take effect!"
    echo
    echo "After logging back in, test with:"
    echo "  python test_wayland_injection.py"
}

# Run main
main