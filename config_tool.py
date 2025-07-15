#!/usr/bin/env python3
"""Configuration management tool for PersonalParakeet

This tool provides command-line interface for managing PersonalParakeet configuration files.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any
from personalparakeet.config_manager import ConfigManager, get_config_manager
from personalparakeet.config import InjectionConfig
from personalparakeet.logger import setup_logger
from personalparakeet.constants import LogEmoji

logger = setup_logger(__name__)


def create_config_command(args):
    """Create a new configuration file"""
    config_manager = get_config_manager(args.config_path)
    
    if args.sample:
        output_path = args.output or 'config_sample.json'
        success = config_manager.create_sample_config(output_path)
        if success:
            print(f"{LogEmoji.SUCCESS} Sample configuration created at {output_path}")
        else:
            print(f"{LogEmoji.ERROR} Failed to create sample configuration")
            return 1
    else:
        # Create default config
        config_manager.load_config()
        success = config_manager.save_config()
        if success:
            print(f"{LogEmoji.SUCCESS} Default configuration created at {config_manager.config_path}")
        else:
            print(f"{LogEmoji.ERROR} Failed to create configuration")
            return 1
    
    return 0


def show_config_command(args):
    """Show current configuration"""
    config_manager = get_config_manager(args.config_path)
    config = config_manager.get_config()
    
    if args.format == 'json':
        print(json.dumps(config.to_dict(), indent=2))
    elif args.format == 'yaml':
        try:
            import yaml
            print(yaml.dump(config.to_dict(), default_flow_style=False))
        except ImportError:
            print(f"{LogEmoji.ERROR} YAML support not available. Install PyYAML.")
            return 1
    else:
        # Pretty print
        print(f"{LogEmoji.INFO} PersonalParakeet Configuration")
        print("=" * 50)
        
        config_dict = config.to_dict()
        _print_config_section("Model Settings", {
            "model_name": config_dict.get("model_name"),
            "use_gpu": config_dict.get("use_gpu")
        })
        
        _print_config_section("Audio Settings", {
            "audio_device_index": config_dict.get("audio_device_index"),
            "chunk_duration": config_dict.get("chunk_duration"),
            "sample_rate": config_dict.get("sample_rate")
        })
        
        _print_config_section("Hotkey Settings", {
            "toggle_hotkey": config_dict.get("toggle_hotkey")
        })
        
        _print_config_section("Injection Settings", config_dict.get("injection", {}))
        
        _print_config_section("Monitoring Settings", {
            "enable_monitoring": config_dict.get("enable_monitoring"),
            "stats_report_interval": config_dict.get("stats_report_interval")
        })
        
        app_profiles = config_dict.get("application_profiles", {})
        if app_profiles:
            _print_config_section("Application Profiles", app_profiles)
    
    return 0


def _print_config_section(title: str, config_dict: Dict[str, Any]):
    """Print a configuration section"""
    print(f"\n{LogEmoji.INFO} {title}:")
    for key, value in config_dict.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")


def validate_config_command(args):
    """Validate configuration file"""
    config_manager = get_config_manager(args.config_path)
    
    try:
        config = config_manager.get_config()
        is_valid = config.validate()
        
        if is_valid:
            print(f"{LogEmoji.SUCCESS} Configuration is valid")
            return 0
        else:
            print(f"{LogEmoji.ERROR} Configuration validation failed")
            return 1
    except Exception as e:
        print(f"{LogEmoji.ERROR} Error validating configuration: {e}")
        return 1


def update_config_command(args):
    """Update configuration values"""
    config_manager = get_config_manager(args.config_path)
    
    # Parse key-value pairs
    updates = {}
    for update in args.updates:
        if '=' not in update:
            print(f"{LogEmoji.ERROR} Invalid update format: {update}")
            print("Use format: key=value")
            return 1
        
        key, value = update.split('=', 1)
        
        # Try to parse value as JSON for complex types
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            # If not JSON, treat as string
            parsed_value = value
        
        # Handle nested keys (e.g., injection.default_key_delay)
        if '.' in key:
            parts = key.split('.')
            current = updates
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = parsed_value
        else:
            updates[key] = parsed_value
    
    # Apply updates
    success = config_manager.update_config(updates)
    if success:
        # Save updated configuration
        success = config_manager.save_config()
        if success:
            print(f"{LogEmoji.SUCCESS} Configuration updated and saved")
        else:
            print(f"{LogEmoji.ERROR} Configuration updated but failed to save")
            return 1
    else:
        print(f"{LogEmoji.ERROR} Failed to update configuration")
        return 1
    
    return 0


def reset_config_command(args):
    """Reset configuration to defaults"""
    config_manager = get_config_manager(args.config_path)
    
    if not args.force:
        response = input(f"{LogEmoji.WARNING} This will reset all configuration to defaults. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled")
            return 0
    
    # Create default config
    from personalparakeet.config_manager import PersonalParakeetConfig
    default_config = PersonalParakeetConfig(injection=InjectionConfig())
    
    success = config_manager.save_config(default_config)
    if success:
        print(f"{LogEmoji.SUCCESS} Configuration reset to defaults")
    else:
        print(f"{LogEmoji.ERROR} Failed to reset configuration")
        return 1
    
    return 0


def list_locations_command(args):
    """List configuration file locations"""
    config_manager = ConfigManager()
    
    print(f"{LogEmoji.INFO} Configuration File Locations")
    print("=" * 40)
    
    for i, location in enumerate(config_manager.DEFAULT_CONFIG_LOCATIONS, 1):
        exists = location.exists()
        status = "✓" if exists else "✗"
        print(f"{i:2d}. {status} {location}")
    
    # Show current active config
    current_config = get_config_manager()
    if current_config.config_path:
        print(f"\n{LogEmoji.INFO} Current active config: {current_config.config_path}")
    else:
        print(f"\n{LogEmoji.INFO} Using default configuration (no file)")
    
    return 0


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="PersonalParakeet Configuration Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a sample configuration file
  python config_tool.py create --sample
  
  # Show current configuration
  python config_tool.py show
  
  # Update configuration values
  python config_tool.py update injection.default_key_delay=0.02 toggle_hotkey=F5
  
  # Validate configuration
  python config_tool.py validate
  
  # Reset to defaults
  python config_tool.py reset --force
"""
    )
    
    # Global options
    parser.add_argument('--config-path', '-c', type=str,
                       help='Path to configuration file')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create configuration file')
    create_parser.add_argument('--sample', '-s', action='store_true',
                              help='Create sample configuration with examples')
    create_parser.add_argument('--output', '-o', type=str,
                              help='Output file path (default: config_sample.json)')
    create_parser.set_defaults(func=create_config_command)
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show current configuration')
    show_parser.add_argument('--format', '-f', choices=['pretty', 'json', 'yaml'],
                            default='pretty', help='Output format')
    show_parser.set_defaults(func=show_config_command)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')
    validate_parser.set_defaults(func=validate_config_command)
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update configuration values')
    update_parser.add_argument('updates', nargs='+', metavar='KEY=VALUE',
                              help='Configuration updates (e.g., injection.default_key_delay=0.02)')
    update_parser.set_defaults(func=update_config_command)
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset configuration to defaults')
    reset_parser.add_argument('--force', '-f', action='store_true',
                             help='Skip confirmation prompt')
    reset_parser.set_defaults(func=reset_config_command)
    
    # List locations command
    list_parser = subparsers.add_parser('locations', help='List configuration file locations')
    list_parser.set_defaults(func=list_locations_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        print(f"{LogEmoji.ERROR} Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())