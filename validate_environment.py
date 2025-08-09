#!/usr/bin/env python3
"""
PersonalParakeet Environment Validation Script

This script validates that the development environment is correctly configured
for PersonalParakeet with RTX 5090 support.

Run with: poetry run python validate_environment.py
"""

import sys
import subprocess
import importlib
from pathlib import Path
from typing import Tuple, Optional

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}")


def print_status(name: str, status: bool, message: str = "") -> None:
    """Print a status line with color coding."""
    status_text = f"{GREEN}✓ PASS{RESET}" if status else f"{RED}✗ FAIL{RESET}"
    print(f"{name:.<40} {status_text}")
    if message:
        print(f"  {YELLOW}→ {message}{RESET}")


def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is 3.11.x."""
    version = sys.version_info
    if version.major == 3 and version.minor == 11:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Expected Python 3.11.x, got {version.major}.{version.minor}.{version.micro}"


def check_cuda_toolkit() -> Tuple[bool, str]:
    """Check if CUDA toolkit is installed and version."""
    try:
        result = subprocess.run(
            ["nvcc", "--version"], capture_output=True, text=True, check=True
        )
        output = result.stdout
        if "12.8" in output:
            return True, "CUDA 12.8 detected"
        elif "cuda" in output.lower():
            return False, "CUDA found but not version 12.8"
        return False, "CUDA version not detected"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, "nvcc not found - CUDA toolkit may not be installed"


def check_nvidia_driver() -> Tuple[bool, str]:
    """Check NVIDIA driver and GPU."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()
        if "RTX 5090" in output or "5090" in output:
            driver_version = output.split(",")[-1].strip()
            # Check if driver version is R570 or higher
            try:
                major_version = int(driver_version.split(".")[0])
                if major_version >= 570:
                    return True, f"RTX 5090 detected with driver {driver_version}"
                else:
                    return False, f"Driver {driver_version} is older than R570"
            except:
                return True, f"RTX 5090 detected with driver {driver_version}"
        return False, f"GPU detected: {output}, but not RTX 5090"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, "nvidia-smi not found - NVIDIA driver may not be installed"


def check_package(package_name: str, min_version: Optional[str] = None) -> Tuple[bool, str]:
    """Check if a Python package is installed and optionally its version."""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, "__version__", "unknown")
        
        if min_version and version != "unknown":
            # Simple version comparison (works for most cases)
            installed = version.split(".")
            required = min_version.split(".")
            if installed >= required:
                return True, f"Version {version}"
            else:
                return False, f"Version {version} < {min_version}"
        return True, f"Version {version}"
    except ImportError:
        return False, "Not installed"


def check_pytorch_cuda() -> Tuple[bool, str]:
    """Check PyTorch installation and CUDA support."""
    try:
        import torch
        
        if not torch.cuda.is_available():
            return False, f"PyTorch {torch.__version__} installed but CUDA not available"
        
        # Check for RTX 5090 support (sm_120)
        cuda_capability = torch.cuda.get_device_capability()
        device_name = torch.cuda.get_device_name(0)
        
        if cuda_capability == (12, 0):  # sm_120
            return True, f"PyTorch {torch.__version__} with {device_name} (sm_{cuda_capability[0]}{cuda_capability[1]})"
        else:
            return (
                False,
                f"PyTorch {torch.__version__} with {device_name} (sm_{cuda_capability[0]}{cuda_capability[1]}) - expected sm_120"
            )
            
    except ImportError:
        return False, "PyTorch not installed"
    except Exception as e:
        return False, f"Error checking PyTorch: {str(e)}"


def check_poetry_environment() -> Tuple[bool, str]:
    """Check if we're running inside Poetry environment."""
    # Check for POETRY_ACTIVE environment variable
    import os
    if os.environ.get("POETRY_ACTIVE") == "1":
        return True, "Poetry environment is active"
    
    # Alternative check: see if we're in a virtualenv managed by poetry
    if "pypoetry" in sys.prefix:
        return True, "Running in Poetry-managed environment"
        
    return False, "Not running in Poetry environment - use 'poetry run' or 'poetry shell'"


def check_nemo_toolkit() -> Tuple[bool, str]:
    """Check NeMo toolkit installation."""
    try:
        import nemo
        import nemo.collections.asr as nemo_asr
        return True, f"NeMo {nemo.__version__} with ASR support"
    except ImportError as e:
        if "nemo" in str(e):
            return False, "NeMo toolkit not installed"
        else:
            return False, f"NeMo installed but missing components: {str(e)}"


def main():
    """Run all validation checks."""
    print_header("PersonalParakeet Environment Validation")
    
    # Track overall status
    all_passed = True
    
    # System checks
    print(f"\n{BOLD}System Requirements:{RESET}")
    
    status, message = check_python_version()
    print_status("Python Version", status, message)
    all_passed &= status
    
    status, message = check_cuda_toolkit()
    print_status("CUDA Toolkit", status, message)
    all_passed &= status
    
    status, message = check_nvidia_driver()
    print_status("NVIDIA Driver & GPU", status, message)
    all_passed &= status
    
    # Poetry environment check
    print(f"\n{BOLD}Environment Management:{RESET}")
    
    status, message = check_poetry_environment()
    print_status("Poetry Environment", status, message)
    all_passed &= status
    
    # Core ML dependencies
    print(f"\n{BOLD}ML Dependencies:{RESET}")
    
    status, message = check_pytorch_cuda()
    print_status("PyTorch with CUDA", status, message)
    all_passed &= status
    
    status, message = check_package("torchvision")
    print_status("Torchvision", status, message)
    all_passed &= status
    
    status, message = check_package("torchaudio")
    print_status("Torchaudio", status, message)
    all_passed &= status
    
    status, message = check_nemo_toolkit()
    print_status("NeMo Toolkit", status, message)
    all_passed &= status
    
    status, message = check_package("lightning", "2.0.0")
    print_status("PyTorch Lightning", status, message)
    all_passed &= status
    
    # Audio dependencies
    print(f"\n{BOLD}Audio Processing:{RESET}")
    
    for package in ["sounddevice", "soundfile", "pyaudio"]:
        status, message = check_package(package)
        print_status(package.capitalize(), status, message)
        all_passed &= status
    
    # Application dependencies
    print(f"\n{BOLD}Application Dependencies:{RESET}")
    
    for package in ["numpy", "scipy", "hydra", "omegaconf"]:
        status, message = check_package(package)
        print_status(package.capitalize(), status, message)
        all_passed &= status
    
    # Final summary
    print_header("Validation Summary")
    
    if all_passed:
        print(f"{GREEN}{BOLD}✓ All checks passed!{RESET}")
        print(f"\n{GREEN}Your environment is correctly configured for PersonalParakeet.{RESET}")
        print(f"{GREEN}You can now run: poetry run personalparakeet{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}✗ Some checks failed!{RESET}")
        print(f"\n{RED}Please review the errors above and follow the setup instructions.{RESET}")
        print(f"{YELLOW}Refer to SETUP.md for detailed troubleshooting steps.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
