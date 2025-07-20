#!/usr/bin/env python3
"""Test script for configuration system

This script tests the new configuration management system functionality.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personalparakeet.config import InjectionConfig
from personalparakeet.config_manager import ConfigManager, PersonalParakeetConfig
from personalparakeet.logger import setup_logger
from personalparakeet.constants import LogEmoji

logger = setup_logger(__name__)


def test_injection_config():
    """Test InjectionConfig functionality"""
    print(f"{LogEmoji.INFO} Testing InjectionConfig...")
    
    # Test default creation
    config = InjectionConfig()
    assert config.default_key_delay == 0.01
    assert config.sample_rate == 16000
    
    # Test validation
    assert config.validate() == True
    
    # Test to_dict and from_dict
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)
    
    restored_config = InjectionConfig.from_dict(config_dict)
    assert restored_config.default_key_delay == config.default_key_delay
    
    # Test invalid values
    invalid_config = InjectionConfig(default_key_delay=2.0)  # Invalid: > 1
    assert invalid_config.validate() == False
    
    print(f"{LogEmoji.SUCCESS} InjectionConfig tests passed")


def test_full_config():
    """Test PersonalParakeetConfig functionality"""
    print(f"{LogEmoji.INFO} Testing PersonalParakeetConfig...")
    
    # Test default creation
    injection_config = InjectionConfig()
    config = PersonalParakeetConfig(injection=injection_config)
    
    assert config.model_name == "nvidia/parakeet-tdt-1.1b"
    assert config.toggle_hotkey == "F4"
    assert config.use_gpu == True
    
    # Test validation
    assert config.validate() == True
    
    # Test to_dict and from_dict
    config_dict = config.to_dict()
    restored_config = PersonalParakeetConfig.from_dict(config_dict)
    
    assert restored_config.model_name == config.model_name
    assert restored_config.injection.default_key_delay == config.injection.default_key_delay
    
    # Test invalid values
    invalid_config = PersonalParakeetConfig(
        injection=injection_config,
        toggle_hotkey="INVALID_KEY"
    )
    assert invalid_config.validate() == False
    
    print(f"{LogEmoji.SUCCESS} PersonalParakeetConfig tests passed")


def test_config_manager():
    """Test ConfigManager functionality"""
    print(f"{LogEmoji.INFO} Testing ConfigManager...")
    
    # Use temporary directory for tests
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "test_config.json"
        
        # Test loading default config (no file exists)
        manager = ConfigManager(config_path)
        config = manager.load_config()
        
        assert isinstance(config, PersonalParakeetConfig)
        assert config.model_name == "nvidia/parakeet-tdt-1.1b"
        
        # Test saving config
        success = manager.save_config(config)
        assert success == True
        assert config_path.exists()
        
        # Test loading saved config
        manager2 = ConfigManager(config_path)
        loaded_config = manager2.load_config()
        
        assert loaded_config.model_name == config.model_name
        assert loaded_config.injection.default_key_delay == config.injection.default_key_delay
        
        # Test updating config
        updates = {
            "model_name": "test/model",
            "injection": {
                "default_key_delay": 0.02
            }
        }
        
        success = manager2.update_config(updates)
        assert success == True
        assert manager2.config.model_name == "test/model"
        assert manager2.config.injection.default_key_delay == 0.02
        
        # Test sample config creation
        sample_path = Path(temp_dir) / "sample_config.json"
        success = manager.create_sample_config(sample_path)
        assert success == True
        assert sample_path.exists()
        
        # Verify sample config is valid
        with open(sample_path, 'r') as f:
            sample_data = json.load(f)
        
        sample_config = PersonalParakeetConfig.from_dict(sample_data)
        assert sample_config.validate() == True
        
        print(f"{LogEmoji.SUCCESS} ConfigManager tests passed")


def test_yaml_support():
    """Test YAML configuration support"""
    print(f"{LogEmoji.INFO} Testing YAML support...")
    
    try:
        import yaml
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"
            
            # Create config and save as YAML
            manager = ConfigManager(config_path)
            config = manager.load_config()
            
            # Modify some values
            config.model_name = "test/yaml-model"
            config.injection.default_key_delay = 0.03
            
            success = manager.save_config(config)
            assert success == True
            assert config_path.exists()
            
            # Verify YAML format
            with open(config_path, 'r') as f:
                content = f.read()
            assert "model_name: test/yaml-model" in content
            
            # Test loading YAML
            manager2 = ConfigManager(config_path)
            loaded_config = manager2.load_config()
            
            assert loaded_config.model_name == "test/yaml-model"
            assert loaded_config.injection.default_key_delay == 0.03
            
            print(f"{LogEmoji.SUCCESS} YAML support tests passed")
    
    except ImportError:
        print(f"{LogEmoji.WARNING} YAML not available, skipping YAML tests")


def test_config_locations():
    """Test configuration file location detection"""
    print(f"{LogEmoji.INFO} Testing config locations...")
    
    manager = ConfigManager()
    
    # Test that default locations exist (as Path objects)
    assert len(manager.DEFAULT_CONFIG_LOCATIONS) > 0
    
    for location in manager.DEFAULT_CONFIG_LOCATIONS:
        assert isinstance(location, Path)
        # Parent directory should be valid (even if doesn't exist)
        assert location.parent.name != ""
    
    print(f"{LogEmoji.SUCCESS} Config location tests passed")


def test_validation_errors():
    """Test configuration validation error handling"""
    print(f"{LogEmoji.INFO} Testing validation errors...")
    
    # Test various invalid configurations
    invalid_configs = [
        # Invalid key delay
        {"injection": {"default_key_delay": 2.0}},
        # Invalid sample rate (in main config)
        {"sample_rate": 99999},
        # Invalid hotkey
        {"toggle_hotkey": "INVALID"},
        # Invalid log level
        {"log_level": "INVALID_LEVEL"}
    ]
    
    for i, invalid_config in enumerate(invalid_configs):
        # Need to provide a valid injection config as base
        base_config = {
            "injection": InjectionConfig().to_dict()
        }
        
        # Handle nested updates properly
        if "injection" in invalid_config:
            base_config["injection"].update(invalid_config["injection"])
        else:
            base_config.update(invalid_config)
        
        config = PersonalParakeetConfig.from_dict(base_config)
        is_valid = config.validate()
        print(f"  Test {i+1}: {invalid_config} -> valid: {is_valid}")
        assert is_valid == False, f"Config should be invalid: {invalid_config}"
    
    print(f"{LogEmoji.SUCCESS} Validation error tests passed")


def main():
    """Run all configuration system tests"""
    print(f"{LogEmoji.INFO} Running Configuration System Tests")
    print("=" * 50)
    
    test_functions = [
        test_injection_config,
        test_full_config,
        test_config_manager,
        test_yaml_support,
        test_config_locations,
        test_validation_errors
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"{LogEmoji.ERROR} {test_func.__name__} failed: {e}")
            failed += 1
    
    print(f"\n{LogEmoji.INFO} Test Results")
    print("=" * 30)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print(f"\n{LogEmoji.SUCCESS} All tests passed!")
        return 0
    else:
        print(f"\n{LogEmoji.ERROR} {failed} tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())