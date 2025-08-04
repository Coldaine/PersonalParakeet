#!/usr/bin/env python3
"""
Dependency checker for PersonalParakeet
Tests all requirements without launching the UI
"""

import sys
import importlib
from pathlib import Path

def check_dependency(module_name, package_name=None):
    """Check if a module can be imported"""
    if package_name is None:
        package_name = module_name
    
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✓ {package_name}: {version}")
        return True
    except ImportError as e:
        print(f"✗ {package_name}: NOT INSTALLED - {e}")
        return False

def check_nemo_components():
    """Check NeMo specific components"""
    print("\nChecking NeMo components:")
    
    # Try importing NeMo step by step
    components = [
        ('torch', 'PyTorch'),
        ('hydra', 'Hydra-core'),
        ('omegaconf', 'OmegaConf'),
        ('lightning', 'PyTorch Lightning'),
        ('nemo', 'NeMo Core'),
        ('nemo.collections.asr', 'NeMo ASR')
    ]
    
    all_good = True
    for module, name in components:
        if not check_dependency(module, name):
            all_good = False
    
    # Check CUDA if PyTorch is available
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"✓ CUDA: Available ({torch.cuda.get_device_name(0)})")
        else:
            print(f"⚠ CUDA: Not available (CPU mode will be slower)")
    except:
        pass
    
    return all_good

def check_personalparakeet_modules():
    """Check if PersonalParakeet modules can be imported"""
    print("\nChecking PersonalParakeet modules:")
    
    modules = [
        'personalparakeet.config',
        'personalparakeet.core.stt_factory',
        'personalparakeet.audio_engine',
        'personalparakeet.ui.dictation_view'
    ]
    
    all_good = True
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            all_good = False
    
    return all_good

def test_stt_factory():
    """Test if STT factory can check availability"""
    print("\nTesting STT Factory:")
    
    try:
        from personalparakeet.core.stt_factory import STTFactory
        info = STTFactory.get_stt_info()
        
        print(f"NeMo available: {info.get('nemo_available', False)}")
        print(f"Backend: {info.get('backend', 'unknown')}")
        
        if info.get('cuda_available') is not None:
            print(f"CUDA available: {info.get('cuda_available')}")
            print(f"CUDA version: {info.get('cuda_version', 'N/A')}")
            print(f"Device: {info.get('device_name', 'N/A')}")
            print(f"PyTorch version: {info.get('pytorch_version', 'N/A')}")
        
        return info.get('nemo_available', False)
        
    except Exception as e:
        print(f"✗ STT Factory test failed: {e}")
        return False

def main():
    """Run all dependency checks"""
    print("PersonalParakeet Dependency Check")
    print("=" * 50)
    
    # Basic dependencies
    print("\nChecking basic dependencies:")
    basic_deps = [
        'flet',
        'sounddevice',
        'numpy',
        'scipy',
        'pyaudio',
        'dataclasses_json',
        'keyboard',
        'pynput',
        'pyperclip'
    ]
    
    basic_ok = all(check_dependency(dep) for dep in basic_deps)
    
    # NeMo components
    nemo_ok = check_nemo_components()
    
    # PersonalParakeet modules
    pp_ok = check_personalparakeet_modules()
    
    # STT Factory test
    stt_ok = test_stt_factory()
    
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"Basic dependencies: {'✓ OK' if basic_ok else '✗ FAILED'}")
    print(f"NeMo components: {'✓ OK' if nemo_ok else '✗ FAILED'}")
    print(f"PersonalParakeet modules: {'✓ OK' if pp_ok else '✗ FAILED'}")
    print(f"STT Factory: {'✓ OK' if stt_ok else '✗ FAILED'}")
    
    if not nemo_ok:
        print("\nTo fix NeMo issues:")
        print("1. Ensure conda environment is activated: conda activate personalparakeet")
        print("2. Install missing components:")
        print("   poetry add pytorch-lightning")
        print("   poetry run pip install nemo_toolkit[asr]")
    
    return 0 if all([basic_ok, nemo_ok, pp_ok, stt_ok]) else 1

if __name__ == "__main__":
    sys.exit(main())