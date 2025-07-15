#!/usr/bin/env python3
"""
Fix RTX 5090 CUDA Compatibility Issue
Based on the comprehensive analysis document

This script implements the priority solution from Section 2:
Installing PyTorch nightly build with CUDA 12.8+ support
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def check_virtual_env():
    """Verify we're in the correct virtual environment"""
    venv_path = os.environ.get('VIRTUAL_ENV')
    expected_venv = os.path.join(os.getcwd(), '.venv')
    
    if not venv_path or os.path.normpath(venv_path) != os.path.normpath(expected_venv):
        print("❌ Virtual environment not active or incorrect")
        print("Please run: .venv\\Scripts\\Activate.ps1")
        return False
    
    print("✅ Virtual environment is active")
    return True

def uninstall_existing_pytorch():
    """Uninstall existing PyTorch to prevent conflicts"""
    packages_to_remove = [
        "torch", "torchvision", "torchaudio", 
        "pytorch", "pytorch-cuda"
    ]
    
    for package in packages_to_remove:
        command = f"pip uninstall -y {package}"
        run_command(command, f"Uninstalling {package} (if present)")

def install_pytorch_nightly():
    """Install PyTorch nightly build with CUDA 12.8+ support"""
    # This is the critical fix from the document
    command = "pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128"
    return run_command(command, "Installing PyTorch nightly build with CUDA 12.8+ support")

def verify_pytorch_installation():
    """Verify PyTorch installation and RTX 5090 compatibility"""
    verification_script = '''
import torch
print("--- PyTorch and CUDA Verification ---")
try:
    print(f"PyTorch Version: {torch.__version__}")
    
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")

    if cuda_available:
        print(f"CUDA Version (used by PyTorch): {torch.version.cuda}")
        
        device_count = torch.cuda.device_count()
        print(f"Number of GPUs: {device_count}")
        
        for i in range(device_count):
            print(f"\\n--- GPU {i} ---")
            device_name = torch.cuda.get_device_name(i)
            print(f"  Device Name: {device_name}")
            
            # Check for RTX 5090
            if "5090" in device_name:
                print("  ✅ RTX 5090 detected!")
            else:
                print(f"  ⚠️  Expected RTX 5090, but found: {device_name}")

            capability = torch.cuda.get_device_capability(i)
            print(f"  Device Compute Capability: {capability}")

            # Verify Compute Capability for Blackwell
            if capability == (12, 0):
                print("  ✅ Correct Compute Capability (12, 0) for RTX 5090!")
            else:
                print(f"  ⚠️  Expected Compute Capability (12, 0) for RTX 5090, but got {capability}")
            
            # Perform a simple tensor operation on the GPU
            try:
                tensor = torch.randn(3, 3).to(f"cuda:{i}")
                print(f"  ✅ Successfully created tensor on cuda:{i}")
                print(f"  Tensor shape: {tensor.shape}")
            except Exception as e:
                print(f"  ❌ Failed to create tensor on cuda:{i}: {e}")

    else:
        print("\\nERROR: PyTorch cannot find a CUDA-enabled GPU.")
        return False

except Exception as e:
    print(f"\\nAn error occurred during verification: {e}")
    return False

print("\\n--- Verification Complete ---")
return True
'''
    
    print("\n🧪 Verifying PyTorch installation...")
    try:
        result = subprocess.run([sys.executable, "-c", verification_script], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return "✅ Successfully created tensor" in result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Verification failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 RTX 5090 CUDA Compatibility Fix")
    print("=" * 50)
    print("Based on: RTX 5090 CUDA Compatibility Solutions")
    print("Implementing: Priority Solution (Section 2)")
    
    # Step 1: Check virtual environment
    if not check_virtual_env():
        return False
    
    # Step 2: Uninstall existing PyTorch
    print("\n📦 Step 1: Removing existing PyTorch installations")
    uninstall_existing_pytorch()
    
    # Step 3: Install PyTorch nightly (THE CRITICAL FIX)
    print("\n🌙 Step 2: Installing PyTorch nightly build")
    print("This is the critical fix for RTX 5090 Blackwell architecture support")
    if not install_pytorch_nightly():
        print("❌ Failed to install PyTorch nightly build")
        return False
    
    # Step 4: Verify installation
    print("\n✅ Step 3: Verifying installation")
    if verify_pytorch_installation():
        print("\n🎉 SUCCESS! RTX 5090 CUDA compatibility fixed!")
        print("You can now run: python dictation_simple_fixed.py")
        return True
    else:
        print("\n❌ Verification failed. Check the output above for issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)