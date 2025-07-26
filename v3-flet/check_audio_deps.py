#!/usr/bin/env python3
"""
Check audio dependencies for PersonalParakeet v3
"""

import sys
import subprocess

def check_module(module_name):
    """Check if a Python module is installed"""
    try:
        __import__(module_name)
        return True, "Installed"
    except ImportError as e:
        return False, str(e)

def check_system_audio():
    """Check system audio capabilities"""
    print("\n=== System Audio Check ===")
    
    # Check platform
    import platform
    system = platform.system()
    print(f"Operating System: {system}")
    print(f"Python Version: {sys.version}")
    
    # Linux-specific checks
    if system == "Linux":
        print("\nLinux Audio Subsystems:")
        
        # Check for ALSA
        try:
            result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ ALSA is available")
                print("  Audio devices found via ALSA")
            else:
                print("✗ ALSA not found or no devices")
        except FileNotFoundError:
            print("✗ ALSA tools not installed")
        
        # Check for PulseAudio
        try:
            result = subprocess.run(['pactl', 'info'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ PulseAudio is available")
            else:
                print("✗ PulseAudio not running")
        except FileNotFoundError:
            print("✗ PulseAudio not installed")
        
        # Check for PipeWire
        try:
            result = subprocess.run(['pw-cli', 'info'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ PipeWire is available")
            else:
                print("✗ PipeWire not running")
        except FileNotFoundError:
            print("✗ PipeWire not installed")

def main():
    """Check all audio-related dependencies"""
    print("PersonalParakeet v3 - Audio Dependencies Check")
    print("=" * 60)
    
    # Check Python audio modules
    modules_to_check = [
        ("sounddevice", "Primary audio I/O library"),
        ("numpy", "Array processing for audio"),
        ("pyaudio", "Alternative audio I/O"),
        ("wave", "WAV file support"),
        ("audioop", "Audio operations"),
        ("soundfile", "Audio file I/O"),
        ("scipy", "Signal processing"),
    ]
    
    print("\n=== Python Audio Modules ===")
    installed_count = 0
    
    for module, description in modules_to_check:
        status, message = check_module(module)
        if status:
            print(f"✓ {module:<15} - {description}")
            installed_count += 1
        else:
            print(f"✗ {module:<15} - {description} [{message}]")
    
    print(f"\nModules installed: {installed_count}/{len(modules_to_check)}")
    
    # Check system audio
    check_system_audio()
    
    # Try basic numpy audio generation
    print("\n=== Testing Basic Audio Generation ===")
    try:
        import numpy as np
        
        # Generate a test tone
        sample_rate = 16000
        duration = 1.0
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        print(f"✓ Generated test tone: {frequency}Hz, {duration}s, {len(audio)} samples")
        print(f"  Audio array shape: {audio.shape}")
        print(f"  Min/Max values: {audio.min():.3f} / {audio.max():.3f}")
        
    except Exception as e:
        print(f"✗ Failed to generate test audio: {e}")
    
    # Installation instructions
    print("\n=== Installation Instructions ===")
    if installed_count < len(modules_to_check):
        print("\nTo install missing audio dependencies:")
        print("  pip install sounddevice numpy")
        print("\nFor full audio support:")
        print("  pip install sounddevice numpy scipy soundfile")
        print("\nOn Linux, you may also need:")
        print("  sudo apt-get install libportaudio2 python3-dev")
        print("  (or equivalent for your distribution)")
    else:
        print("\n✓ All audio dependencies are installed!")
    
    # Check if we're in WSL
    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                print("\n⚠ WARNING: Running in WSL detected!")
                print("  Audio support in WSL is limited.")
                print("  Consider running on native Windows or Linux.")
    except:
        pass


if __name__ == "__main__":
    main()