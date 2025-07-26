#!/usr/bin/env python3
"""
CUDA Compatibility Module for PersonalParakeet v3
Handles GPU detection, CUDA version compatibility, and RTX 5090 special cases
"""

import subprocess
import logging
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CUDAInfo:
    """CUDA system information"""
    available: bool
    driver_version: Optional[str] = None
    runtime_version: Optional[str] = None
    gpu_name: Optional[str] = None
    gpu_memory_mb: Optional[int] = None
    compute_capability: Optional[Tuple[int, int]] = None
    pytorch_cuda_version: Optional[str] = None
    is_rtx_5090: bool = False
    needs_special_config: bool = False
    recommendations: list = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


class CUDACompatibility:
    """Check and handle CUDA compatibility issues"""
    
    @staticmethod
    def get_cuda_info() -> CUDAInfo:
        """Get comprehensive CUDA information"""
        info = CUDAInfo(available=False)
        
        # Check nvidia-smi first
        nvidia_info = CUDACompatibility._check_nvidia_smi()
        if nvidia_info:
            info.driver_version = nvidia_info.get('driver_version')
            info.gpu_name = nvidia_info.get('gpu_name')
            info.gpu_memory_mb = nvidia_info.get('memory_mb')
            
            # Check for RTX 5090
            if info.gpu_name and '5090' in info.gpu_name:
                info.is_rtx_5090 = True
                info.needs_special_config = True
                info.recommendations.append(
                    "RTX 5090 detected - may require PyTorch nightly for CUDA 12.8+ support"
                )
        
        # Check PyTorch CUDA
        pytorch_info = CUDACompatibility._check_pytorch_cuda()
        if pytorch_info:
            info.available = pytorch_info.get('available', False)
            info.pytorch_cuda_version = pytorch_info.get('cuda_version')
            info.runtime_version = pytorch_info.get('cuda_runtime_version')
            
            if not info.gpu_name and pytorch_info.get('device_name'):
                info.gpu_name = pytorch_info['device_name']
                if '5090' in info.gpu_name:
                    info.is_rtx_5090 = True
                    info.needs_special_config = True
            
            # Check compute capability
            if pytorch_info.get('compute_capability'):
                info.compute_capability = pytorch_info['compute_capability']
                
                # RTX 5090 has compute capability 8.9
                if info.compute_capability == (8, 9):
                    info.is_rtx_5090 = True
                    info.needs_special_config = True
        
        # Add compatibility recommendations
        CUDACompatibility._add_recommendations(info)
        
        return info
    
    @staticmethod
    def _check_nvidia_smi() -> Optional[Dict]:
        """Check nvidia-smi for GPU information"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,driver_version,memory.total', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                parts = output.split(', ')
                
                if len(parts) >= 3:
                    memory_str = parts[2].replace(' MiB', '')
                    return {
                        'gpu_name': parts[0],
                        'driver_version': parts[1],
                        'memory_mb': int(memory_str) if memory_str.isdigit() else None
                    }
        except Exception as e:
            logger.debug(f"nvidia-smi check failed: {e}")
        
        return None
    
    @staticmethod
    def _check_pytorch_cuda() -> Optional[Dict]:
        """Check PyTorch CUDA availability"""
        try:
            import torch
            
            if not torch.cuda.is_available():
                return {'available': False}
            
            info = {
                'available': True,
                'cuda_version': torch.version.cuda,
                'device_count': torch.cuda.device_count(),
                'device_name': torch.cuda.get_device_name(0),
                'cuda_runtime_version': torch.version.cuda,
            }
            
            # Get compute capability
            if hasattr(torch.cuda, 'get_device_capability'):
                major, minor = torch.cuda.get_device_capability(0)
                info['compute_capability'] = (major, minor)
            
            # Get memory info
            if hasattr(torch.cuda, 'get_device_properties'):
                props = torch.cuda.get_device_properties(0)
                info['total_memory_mb'] = props.total_memory // (1024 * 1024)
            
            return info
            
        except ImportError:
            logger.debug("PyTorch not available")
            return None
        except Exception as e:
            logger.debug(f"PyTorch CUDA check failed: {e}")
            return None
    
    @staticmethod
    def _add_recommendations(info: CUDAInfo):
        """Add compatibility recommendations based on detected hardware"""
        
        if not info.available:
            info.recommendations.append(
                "No CUDA available - will use CPU (slower performance)"
            )
            return
        
        # Check CUDA version compatibility
        if info.pytorch_cuda_version:
            cuda_major = int(info.pytorch_cuda_version.split('.')[0])
            
            if cuda_major < 11:
                info.recommendations.append(
                    "CUDA version is old - consider upgrading PyTorch"
                )
            elif cuda_major >= 12 and info.is_rtx_5090:
                info.recommendations.append(
                    "CUDA 12.x detected with RTX 5090 - ensure PyTorch supports your CUDA version"
                )
        
        # Memory recommendations
        if info.gpu_memory_mb:
            if info.gpu_memory_mb < 4096:
                info.recommendations.append(
                    f"Limited GPU memory ({info.gpu_memory_mb}MB) - may need to use smaller batch sizes"
                )
            elif info.gpu_memory_mb >= 16384:
                info.recommendations.append(
                    f"High GPU memory available ({info.gpu_memory_mb}MB) - can use larger batch sizes"
                )
    
    @staticmethod
    def get_pytorch_install_command(cuda_info: CUDAInfo) -> str:
        """Get recommended PyTorch installation command"""
        
        if not cuda_info.available:
            return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
        
        if cuda_info.is_rtx_5090 or cuda_info.needs_special_config:
            # RTX 5090 needs latest CUDA support
            return "pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121"
        
        # Standard CUDA versions
        if cuda_info.pytorch_cuda_version:
            cuda_major = int(cuda_info.pytorch_cuda_version.split('.')[0])
            cuda_minor = int(cuda_info.pytorch_cuda_version.split('.')[1])
            
            if cuda_major >= 12:
                return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
            elif cuda_major == 11 and cuda_minor >= 8:
                return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
            elif cuda_major == 11:
                return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117"
        
        # Default to CUDA 11.8
        return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
    
    @staticmethod
    def apply_rtx_5090_fixes():
        """Apply RTX 5090 specific fixes"""
        try:
            # Set environment variables for better compatibility
            os.environ['TORCH_CUDA_ARCH_LIST'] = '8.9'  # RTX 5090 compute capability
            os.environ['CUDA_LAUNCH_BLOCKING'] = '1'     # For debugging
            
            logger.info("Applied RTX 5090 compatibility settings")
            
            # Try to import and configure PyTorch
            try:
                import torch
                
                # Force CUDA synchronization for stability
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                    
                    # Set memory fraction to avoid OOM
                    torch.cuda.set_per_process_memory_fraction(0.8)
                    
                    logger.info("RTX 5090 PyTorch configuration applied")
                    
            except ImportError:
                logger.warning("PyTorch not installed - skipping RTX 5090 PyTorch fixes")
                
        except Exception as e:
            logger.error(f"Failed to apply RTX 5090 fixes: {e}")
    
    @staticmethod
    def check_and_apply_fixes() -> CUDAInfo:
        """Check CUDA compatibility and apply necessary fixes"""
        cuda_info = CUDACompatibility.get_cuda_info()
        
        # Log the findings
        logger.info(f"CUDA Available: {cuda_info.available}")
        if cuda_info.gpu_name:
            logger.info(f"GPU: {cuda_info.gpu_name}")
        if cuda_info.pytorch_cuda_version:
            logger.info(f"PyTorch CUDA: {cuda_info.pytorch_cuda_version}")
        
        # Apply RTX 5090 fixes if needed
        if cuda_info.is_rtx_5090:
            logger.warning("RTX 5090 detected - applying compatibility fixes")
            CUDACompatibility.apply_rtx_5090_fixes()
        
        # Log recommendations
        for rec in cuda_info.recommendations:
            logger.info(f"Recommendation: {rec}")
        
        return cuda_info


def get_optimal_device(force_cpu: bool = False) -> str:
    """
    Get optimal device for STT processing
    
    Args:
        force_cpu: Force CPU usage even if CUDA available
        
    Returns:
        'cuda' or 'cpu'
    """
    if force_cpu:
        return 'cpu'
    
    cuda_info = CUDACompatibility.get_cuda_info()
    
    if cuda_info.available:
        # Additional checks for stable CUDA usage
        try:
            import torch
            
            # Test CUDA allocation
            test_tensor = torch.zeros(1, device='cuda')
            del test_tensor
            
            return 'cuda'
            
        except Exception as e:
            logger.warning(f"CUDA test failed, falling back to CPU: {e}")
            return 'cpu'
    
    return 'cpu'