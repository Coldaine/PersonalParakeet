#!/usr/bin/env python3
"""
Test script to verify hybrid Poetry/Conda installation
"""

import sys
import os
import subprocess

def check_command(cmd, name):
    """Check if a command exists"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.returncode == 0
    except:
        return False

def check_python_package(package):
    """Check if a Python package is installed"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    print("🦜 PersonalParakeet v3 - Hybrid Installation Test")
    print("=" * 50)
    print()
    
    # Check Poetry environment
    print("📦 Checking Poetry environment...")
    in_poetry = os.environ.get('POETRY_ACTIVE') == '1'
    print(f"   Poetry shell active: {'✅ Yes' if in_poetry else '❌ No'}")
    
    # Check Conda environment
    print("\n🐍 Checking Conda environment...")
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    in_conda = conda_env is not None
    print(f"   Conda environment: {'✅ ' + conda_env if in_conda else '❌ Not activated'}")
    
    # Check Python packages (should work with just Poetry)
    print("\n📚 Checking Python packages...")
    packages = {
        'flet': 'Flet UI framework',
        'sounddevice': 'Audio capture',
        'numpy': 'Numerical computing',
        'scipy': 'Scientific computing',
        'keyboard': 'Keyboard control',
        'pyperclip': 'Clipboard access'
    }
    
    all_python_ok = True
    for pkg, desc in packages.items():
        installed = check_python_package(pkg)
        print(f"   {pkg}: {'✅' if installed else '❌'} {desc}")
        if not installed:
            all_python_ok = False
    
    # Check ML packages (only if Conda is active)
    print("\n🧠 Checking ML packages...")
    if in_conda and conda_env == 'personalparakeet':
        ml_packages = {
            'torch': 'PyTorch',
            'torchaudio': 'PyTorch Audio',
            'nemo': 'NVIDIA NeMo toolkit'
        }
        
        all_ml_ok = True
        for pkg, desc in ml_packages.items():
            installed = check_python_package(pkg)
            print(f"   {pkg}: {'✅' if installed else '❌'} {desc}")
            if not installed:
                all_ml_ok = False
                
        # Check CUDA if PyTorch is available
        if check_python_package('torch'):
            import torch
            cuda_available = torch.cuda.is_available()
            print(f"   CUDA: {'✅ Available' if cuda_available else '❌ Not available'}")
            if cuda_available:
                print(f"   GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("   ⚠️  Conda environment 'personalparakeet' not active")
        print("   To test ML packages, run: conda activate personalparakeet")
        all_ml_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary:")
    
    if all_python_ok:
        print("✅ Python dependencies: All installed")
    else:
        print("❌ Python dependencies: Some missing - run: poetry install")
    
    if in_conda and all_ml_ok:
        print("✅ ML dependencies: All installed")
    elif not in_conda:
        print("⚠️  ML dependencies: Not tested (activate conda environment)")
    else:
        print("❌ ML dependencies: Some missing - check environment.yml")
    
    # Configuration check
    print("\n⚙️  Configuration:")
    if os.path.exists('config.json'):
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        use_mock = config.get('audio', {}).get('use_mock_stt', True)
        print(f"   Mock STT: {'✅ Enabled' if use_mock else '❌ Disabled (requires ML deps)'}")
    else:
        print("   ⚠️  No config.json found")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if not in_poetry:
        print("   - Run: poetry shell")
    if not in_conda and not all_python_ok:
        print("   - For ML support: conda activate personalparakeet")
    if all_python_ok and (in_conda or use_mock):
        print("   - Ready to run: python main.py")

if __name__ == "__main__":
    main()