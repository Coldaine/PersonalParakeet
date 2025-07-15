#!/usr/bin/env python3
"""Enhanced dictation system runner

This script runs the enhanced dictation system with improved text injection
strategies and comprehensive monitoring.
"""

import argparse
import signal
import sys
import time
from personalparakeet.dictation_enhanced import EnhancedDictationSystem
from personalparakeet.config import InjectionConfig
from personalparakeet.config_manager import get_config_manager
from personalparakeet.logger import setup_logger
from personalparakeet.constants import LogEmoji

logger = setup_logger(__name__)


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    print(f"\n{LogEmoji.INFO} Received interrupt signal. Stopping dictation...")
    if hasattr(signal_handler, 'system'):
        signal_handler.system.stop()
    sys.exit(0)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Enhanced PersonalParakeet Dictation System")
    
    # Audio options
    parser.add_argument("--device", "-d", type=int, 
                       help="Audio device index to use")
    parser.add_argument("--list-devices", "-l", action="store_true",
                       help="List available audio devices")
    
    # Injection options
    parser.add_argument("--test-injection", action="store_true",
                       help="Test injection strategies before starting")
    parser.add_argument("--strategy-order", nargs="+",
                       help="Force specific strategy order (e.g., ui_automation clipboard)")
    
    # Configuration options
    parser.add_argument("--config", "-c", type=str,
                       help="Path to configuration file")
    parser.add_argument("--key-delay", type=float,
                       help="Delay between keystrokes (overrides config)")
    parser.add_argument("--focus-delay", type=float,
                       help="Focus acquisition delay (overrides config)")
    parser.add_argument("--clipboard-delay", type=float,
                       help="Clipboard paste delay (overrides config)")
    
    # Monitoring options
    parser.add_argument("--stats-interval", type=int,
                       help="Statistics reporting interval in seconds (overrides config)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Handle list devices
    if args.list_devices:
        try:
            from personalparakeet.audio_devices import AudioDeviceManager
            AudioDeviceManager.print_input_devices()
        except ImportError as e:
            print(f"{LogEmoji.ERROR} Could not import audio device manager: {e}")
        return
    
    # Load configuration
    config_manager = get_config_manager(args.config)
    full_config = config_manager.get_config()
    
    # Apply command-line overrides
    if args.key_delay is not None:
        full_config.injection.default_key_delay = args.key_delay
    if args.focus_delay is not None:
        full_config.injection.focus_acquisition_delay = args.focus_delay
    if args.clipboard_delay is not None:
        full_config.injection.clipboard_paste_delay = args.clipboard_delay
    if args.stats_interval is not None:
        full_config.stats_report_interval = args.stats_interval
    if args.device is not None:
        full_config.audio_device_index = args.device
    if args.verbose:
        full_config.enable_debug_logging = True
    
    config = full_config.injection
    
    print(f"{LogEmoji.INFO} Starting Enhanced PersonalParakeet Dictation System")
    print("=" * 60)
    print(f"Config file: {config_manager.config_path or 'Default'}")
    print(f"Audio device: {full_config.audio_device_index or 'Default'}")
    print(f"Key delay: {config.default_key_delay}s")
    print(f"Focus delay: {config.focus_acquisition_delay}s")
    print(f"Clipboard delay: {config.clipboard_paste_delay}s")
    print(f"Model: {full_config.model_name}")
    print(f"Hotkey: {full_config.toggle_hotkey}")
    
    # Create enhanced dictation system
    try:
        system = EnhancedDictationSystem(
            model_name=full_config.model_name,
            device_index=full_config.audio_device_index,
            config=config
        )
        
        # Store system reference for signal handler
        signal_handler.system = system
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Test injection strategies if requested
        if args.test_injection:
            print(f"\n{LogEmoji.INFO} Testing injection strategies...")
            results = system.test_injection_strategies()
            
            working_strategies = [name for name, result in results.items() if result.success]
            if working_strategies:
                print(f"{LogEmoji.SUCCESS} Working strategies: {', '.join(working_strategies)}")
            else:
                print(f"{LogEmoji.WARNING} No strategies working! Check your system configuration.")
                return
        
        # Set custom strategy order if specified
        if args.strategy_order:
            system.set_strategy_order(args.strategy_order)
            print(f"{LogEmoji.INFO} Using custom strategy order: {args.strategy_order}")
        
        # Show initial statistics
        print(f"\n{LogEmoji.INFO} Available strategies: {', '.join(system.injection_manager.get_available_strategies())}")
        
        print(f"\n{LogEmoji.INFO} Starting dictation...")
        print(f"Press F4 to start/stop dictation")
        print(f"Press Ctrl+C to quit")
        print("-" * 60)
        
        # Start the system with monitoring
        system.start_with_injection_monitoring()
        
        # Keep the main thread alive
        try:
            while system.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        print(f"\n{LogEmoji.INFO} Stopping dictation system...")
        system.stop()
        
    except Exception as e:
        logger.error(f"{LogEmoji.ERROR} Failed to start dictation system: {e}")
        print(f"{LogEmoji.ERROR} Error: {e}")
        
        # Print helpful troubleshooting info
        print(f"\n{LogEmoji.INFO} Troubleshooting:")
        print("1. Check that your microphone is connected and working")
        print("2. Make sure you have the required dependencies installed")
        print("3. Try running with --list-devices to see available audio devices")
        print("4. Use --test-injection to verify injection strategies work")
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())