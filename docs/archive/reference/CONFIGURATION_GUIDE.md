# PersonalParakeet Configuration Guide

## Overview

PersonalParakeet uses a comprehensive configuration system that supports both JSON and YAML formats. This guide covers all configuration options and how to manage them.

## Configuration File Locations

PersonalParakeet searches for configuration files in the following order:

1. `~/.config/personalparakeet/config.json`
2. `~/.config/personalparakeet/config.yaml`
3. `~/.personalparakeet/config.json`
4. `~/.personalparakeet/config.yaml`
5. `./config.json` (current directory)
6. `./config.yaml` (current directory)

## Configuration Management Tool

The `config_tool.py` script provides a command-line interface for managing configurations:

### Basic Commands

```bash
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

# List configuration file locations
python config_tool.py locations
```

### Configuration File Formats

#### JSON Format
```json
{
  "model_name": "nvidia/parakeet-tdt-1.1b",
  "use_gpu": true,
  "audio_device_index": null,
  "chunk_duration": 1.0,
  "sample_rate": 16000,
  "toggle_hotkey": "F4",
  "enable_application_detection": true,
  "enable_monitoring": true,
  "stats_report_interval": 30,
  "enable_debug_logging": false,
  "log_level": "INFO",
  "injection": {
    "default_key_delay": 0.01,
    "clipboard_paste_delay": 0.1,
    "strategy_switch_delay": 0.05,
    "focus_acquisition_delay": 0.05,
    "windows_ui_automation_delay": 0.02,
    "linux_xtest_delay": 0.005,
    "kde_dbus_timeout": 5.0,
    "xdotool_timeout": 5.0,
    "max_clipboard_retries": 3,
    "clipboard_retry_delay": 0.1,
    "preferred_strategy_order": null,
    "enable_performance_optimization": true,
    "skip_consecutive_failures": 3
  },
  "application_profiles": {
    "notepad.exe": {
      "strategy_order": ["keyboard", "ui_automation", "clipboard"],
      "key_delay": 0.01
    },
    "code.exe": {
      "strategy_order": ["clipboard", "ui_automation", "keyboard"],
      "key_delay": 0.005
    }
  }
}
```

#### YAML Format
```yaml
model_name: nvidia/parakeet-tdt-1.1b
use_gpu: true
audio_device_index: null
chunk_duration: 1.0
sample_rate: 16000
toggle_hotkey: F4
enable_application_detection: true
enable_monitoring: true
stats_report_interval: 30
enable_debug_logging: false
log_level: INFO

injection:
  default_key_delay: 0.01
  clipboard_paste_delay: 0.1
  strategy_switch_delay: 0.05
  focus_acquisition_delay: 0.05
  windows_ui_automation_delay: 0.02
  linux_xtest_delay: 0.005
  kde_dbus_timeout: 5.0
  xdotool_timeout: 5.0
  max_clipboard_retries: 3
  clipboard_retry_delay: 0.1
  preferred_strategy_order: null
  enable_performance_optimization: true
  skip_consecutive_failures: 3

application_profiles:
  notepad.exe:
    strategy_order: [keyboard, ui_automation, clipboard]
    key_delay: 0.01
  code.exe:
    strategy_order: [clipboard, ui_automation, keyboard]
    key_delay: 0.005
```

## Configuration Options

### Model Settings

- **`model_name`** (string): NVIDIA NeMo model to use
  - Default: `"nvidia/parakeet-tdt-1.1b"`
  - Example: `"nvidia/parakeet-tdt-1.1b"`

- **`use_gpu`** (boolean): Enable GPU acceleration
  - Default: `true`
  - Values: `true`, `false`

### Audio Settings

- **`audio_device_index`** (integer or null): Audio input device index
  - Default: `null` (system default)
  - Example: `0`, `1`, `2`

- **`chunk_duration`** (float): Audio chunk duration in seconds
  - Default: `1.0`
  - Range: `0.1` to `10.0`

- **`sample_rate`** (integer): Audio sample rate in Hz
  - Default: `16000`
  - Valid values: `8000`, `16000`, `22050`, `44100`, `48000`

### Hotkey Settings

- **`toggle_hotkey`** (string): Key to toggle dictation on/off
  - Default: `"F4"`
  - Valid values: `"F1"` through `"F12"`

### Application Settings

- **`enable_application_detection`** (boolean): Enable automatic application detection
  - Default: `true`
  - Values: `true`, `false`

- **`application_profiles`** (object): Application-specific settings
  - Key: executable name (e.g., `"notepad.exe"`)
  - Value: profile configuration object

### Monitoring Settings

- **`enable_monitoring`** (boolean): Enable performance monitoring
  - Default: `true`
  - Values: `true`, `false`

- **`stats_report_interval`** (integer): Statistics reporting interval in seconds
  - Default: `30`
  - Range: `5` to `300`

### Debug Settings

- **`enable_debug_logging`** (boolean): Enable debug logging
  - Default: `false`
  - Values: `true`, `false`

- **`log_level`** (string): Logging level
  - Default: `"INFO"`
  - Valid values: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`

### Injection Settings

All injection settings are under the `injection` object:

#### Timing Settings

- **`default_key_delay`** (float): Delay between keystrokes in seconds
  - Default: `0.01`
  - Range: `0.0` to `1.0`

- **`clipboard_paste_delay`** (float): Delay after clipboard operations in seconds
  - Default: `0.1`
  - Range: `0.0` to `5.0`

- **`strategy_switch_delay`** (float): Delay when switching strategies in seconds
  - Default: `0.05`
  - Range: `0.0` to `1.0`

- **`focus_acquisition_delay`** (float): Delay to ensure window focus in seconds
  - Default: `0.05`
  - Range: `0.0` to `1.0`

#### Platform-Specific Settings

- **`windows_ui_automation_delay`** (float): Windows UI Automation delay in seconds
  - Default: `0.02`

- **`linux_xtest_delay`** (float): Linux XTest delay in seconds
  - Default: `0.005`

- **`kde_dbus_timeout`** (float): KDE DBUS timeout in seconds
  - Default: `5.0`

- **`xdotool_timeout`** (float): xdotool timeout in seconds
  - Default: `5.0`

#### Retry Settings

- **`max_clipboard_retries`** (integer): Maximum clipboard operation retries
  - Default: `3`
  - Range: `1` to `10`

- **`clipboard_retry_delay`** (float): Delay between clipboard retries in seconds
  - Default: `0.1`

#### Strategy Settings

- **`preferred_strategy_order`** (array or null): Preferred injection strategy order
  - Default: `null` (automatic optimization)
  - Example: `["ui_automation", "keyboard", "clipboard"]`

- **`enable_performance_optimization`** (boolean): Enable performance-based strategy reordering
  - Default: `true`
  - Values: `true`, `false`

- **`skip_consecutive_failures`** (integer): Skip strategy after consecutive failures
  - Default: `3`
  - Range: `1` to `10`

## Application Profiles

Application profiles allow you to customize behavior for specific applications:

```json
{
  "application_profiles": {
    "notepad.exe": {
      "strategy_order": ["keyboard", "ui_automation", "clipboard"],
      "key_delay": 0.01
    },
    "code.exe": {
      "strategy_order": ["clipboard", "ui_automation", "keyboard"],
      "key_delay": 0.005
    },
    "chrome.exe": {
      "strategy_order": ["keyboard", "ui_automation", "send_input"],
      "key_delay": 0.008
    }
  }
}
```

### Profile Settings

- **`strategy_order`** (array): Preferred strategy order for this application
- **`key_delay`** (float): Custom key delay for this application

## Command-Line Overrides

You can override configuration values using command-line arguments:

```bash
# Override audio device
python run_enhanced_dictation.py --device 1

# Override timing settings
python run_enhanced_dictation.py --key-delay 0.02 --focus-delay 0.1

# Use custom configuration file
python run_enhanced_dictation.py --config /path/to/config.json

# Enable verbose logging
python run_enhanced_dictation.py --verbose
```

## Configuration Validation

The configuration system includes comprehensive validation:

### Automatic Validation
- Configuration files are validated when loaded
- Invalid configurations fall back to defaults
- Validation errors are logged

### Manual Validation
```bash
# Validate current configuration
python config_tool.py validate

# Validate specific configuration file
python config_tool.py -c /path/to/config.json validate
```

### Validation Rules

- **Timing values**: Must be positive and within reasonable ranges
- **Audio settings**: Sample rates must be standard values
- **Hotkeys**: Must be valid function keys (F1-F12)
- **Log levels**: Must be valid Python logging levels
- **Strategy orders**: Must contain valid strategy names

## Runtime Configuration Updates

Configuration can be updated at runtime:

```python
from personalparakeet.config_manager import get_config_manager

# Get configuration manager
config_manager = get_config_manager()

# Update configuration
updates = {
    "injection": {
        "default_key_delay": 0.02
    },
    "toggle_hotkey": "F5"
}

success = config_manager.update_config(updates)
if success:
    config_manager.save_config()
```

## Best Practices

### Configuration Management

1. **Use version control**: Keep configuration files in version control
2. **Environment-specific configs**: Use different configs for different environments
3. **Backup configurations**: Keep backups of working configurations
4. **Validate regularly**: Run validation after making changes

### Performance Tuning

1. **Start with defaults**: Use default values as a baseline
2. **Test incrementally**: Make small changes and test
3. **Monitor performance**: Use monitoring to track improvements
4. **Application-specific tuning**: Customize for frequently used applications

### Security Considerations

1. **File permissions**: Ensure configuration files have appropriate permissions
2. **Sensitive data**: Don't store sensitive information in configuration files
3. **Validation**: Always validate configuration before use
4. **Defaults**: Use secure defaults for all settings

## Troubleshooting

### Common Issues

1. **Configuration not found**: Check file locations and permissions
2. **Validation errors**: Review validation rules and fix invalid values
3. **Performance issues**: Adjust timing settings and strategy order
4. **Application compatibility**: Create custom application profiles

### Debug Configuration

```json
{
  "enable_debug_logging": true,
  "log_level": "DEBUG",
  "injection": {
    "enable_debug_logging": true
  }
}
```

This enables detailed logging for troubleshooting configuration issues.

## Migration Guide

### From Basic Configuration

If you're upgrading from a basic configuration system:

1. **Backup existing settings**: Save your current configuration
2. **Create new config**: Use `config_tool.py create --sample`
3. **Migrate values**: Copy your custom values to the new format
4. **Validate**: Run `config_tool.py validate` to ensure correctness
5. **Test**: Test the system with your new configuration

### Configuration Format Changes

Configuration format changes are handled automatically:
- Unknown keys are ignored
- Missing keys use default values
- Invalid values fall back to defaults
- Validation ensures compatibility

This comprehensive configuration system provides flexibility while maintaining reliability and ease of use.