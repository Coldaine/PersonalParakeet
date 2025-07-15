"""
Audio device selection and management utilities
"""

import sounddevice as sd
from typing import List, Dict, Optional, Tuple
import sys


class AudioDeviceManager:
    """Manages audio device selection and information"""
    
    @staticmethod
    def list_input_devices() -> List[Dict]:
        """
        List all available audio input devices
        
        Returns:
            List of dicts with device information
        """
        devices = []
        for idx, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                devices.append({
                    'index': idx,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate'],
                    'is_default': idx == sd.default.device[0]
                })
        return devices
    
    @staticmethod
    def print_input_devices():
        """Print a formatted list of input devices"""
        print("\n🎤 Available Audio Input Devices:")
        print("=" * 60)
        
        devices = AudioDeviceManager.list_input_devices()
        if not devices:
            print("❌ No audio input devices found!")
            return
        
        for device in devices:
            default_marker = " (DEFAULT)" if device['is_default'] else ""
            print(f"  [{device['index']}] {device['name']}{default_marker}")
            print(f"      Channels: {device['channels']}, Sample Rate: {device['sample_rate']} Hz")
        
        print("=" * 60)
    
    @staticmethod
    def find_device_by_name(name_pattern: str) -> Optional[int]:
        """
        Find device index by partial name match (case-insensitive)
        
        Args:
            name_pattern: Partial device name to search for
            
        Returns:
            Device index if found, None otherwise
        """
        name_pattern = name_pattern.lower()
        devices = AudioDeviceManager.list_input_devices()
        
        for device in devices:
            if name_pattern in device['name'].lower():
                return device['index']
        
        return None
    
    @staticmethod
    def get_device_info(device_index: Optional[int] = None) -> Dict:
        """
        Get detailed info about a specific device
        
        Args:
            device_index: Device index (None for default)
            
        Returns:
            Device information dict
        """
        try:
            if device_index is None:
                device_index = sd.default.device[0]
            
            device = sd.query_devices(device_index)
            if device['max_input_channels'] == 0:
                raise ValueError(f"Device {device_index} is not an input device")
                
            return {
                'index': device_index,
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': device['default_samplerate'],
                'latency': device['default_low_input_latency']
            }
            
        except Exception as e:
            raise ValueError(f"Invalid device index {device_index}: {e}")
    
    @staticmethod
    def validate_device(device_index: Optional[int] = None) -> Tuple[bool, str]:
        """
        Validate that a device can be used for recording
        
        Args:
            device_index: Device to validate (None for default)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            info = AudioDeviceManager.get_device_info(device_index)
            
            # Test opening the device
            test_stream = sd.InputStream(
                device=device_index,
                channels=1,
                samplerate=16000,
                blocksize=1024
            )
            test_stream.close()
            
            return True, f"Device '{info['name']}' is ready"
            
        except Exception as e:
            return False, f"Device validation failed: {str(e)}"
    
    @staticmethod
    def select_device_interactive() -> Optional[int]:
        """
        Interactive device selection from command line
        
        Returns:
            Selected device index or None if cancelled
        """
        AudioDeviceManager.print_input_devices()
        
        devices = AudioDeviceManager.list_input_devices()
        if not devices:
            return None
        
        while True:
            try:
                choice = input("\nSelect device number (or Enter for default, 'q' to quit): ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                if choice == '':
                    # Use default device
                    default_device = next((d['index'] for d in devices if d['is_default']), None)
                    if default_device is not None:
                        print(f"✅ Using default device")
                        return default_device
                
                device_index = int(choice)
                
                # Validate the choice
                if any(d['index'] == device_index for d in devices):
                    valid, msg = AudioDeviceManager.validate_device(device_index)
                    if valid:
                        print(f"✅ {msg}")
                        return device_index
                    else:
                        print(f"❌ {msg}")
                else:
                    print(f"❌ Invalid device number. Please choose from the list.")
                    
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\n❌ Selection cancelled")
                return None


# Quick test functionality
if __name__ == "__main__":
    print("🧪 Testing Audio Device Manager")
    
    # List devices
    AudioDeviceManager.print_input_devices()
    
    # Test device search
    print("\n🔍 Testing device search:")
    test_names = ["microphone", "headset", "webcam", "default"]
    for name in test_names:
        idx = AudioDeviceManager.find_device_by_name(name)
        if idx is not None:
            info = AudioDeviceManager.get_device_info(idx)
            print(f"  Found '{name}': {info['name']} (index {idx})")
    
    # Interactive selection
    print("\n🎯 Testing interactive selection:")
    selected = AudioDeviceManager.select_device_interactive()
    if selected is not None:
        print(f"\nYou selected device index: {selected}")