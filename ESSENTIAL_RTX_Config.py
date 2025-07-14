# RTX 5090/3090 Dual GPU Configuration
# Essential GPU optimization code for PersonalParakeet

import torch
import os
import gc
from typing import Dict, Optional

class DualGPUManager:
    """Manages dual RTX GPU setup for Parakeet + Ollama"""
    
    def __init__(self, parakeet_gpu: int = 0, ollama_gpu: int = 1):
        self.parakeet_gpu = parakeet_gpu  # RTX 5090
        self.ollama_gpu = ollama_gpu      # RTX 3090
        self._setup_gpu_optimization()
    
    def _setup_gpu_optimization(self):
        """Setup optimized GPU configuration for dual RTX setup"""
        # RTX 5090 - Primary GPU optimization
        with torch.cuda.device(self.parakeet_gpu):
            torch.cuda.set_per_process_memory_fraction(0.85)  # 85% of 32GB
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
        
        # RTX 3090 - Secondary GPU optimization  
        with torch.cuda.device(self.ollama_gpu):
            torch.cuda.set_per_process_memory_fraction(0.75)  # 75% of 24GB
            torch.backends.cudnn.deterministic = True
    
    def optimize_gpu_memory(self):
        """Enhanced multi-GPU memory management"""
        # Clear both GPUs explicitly
        for device_id in [self.parakeet_gpu, self.ollama_gpu]:
            with torch.cuda.device(f'cuda:{device_id}'):
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        
        # Force garbage collection
        gc.collect()
    
    def get_parakeet_config(self) -> Dict:
        """Get optimized configuration for Parakeet model"""
        return {
            'device': f'cuda:{self.parakeet_gpu}',
            'precision': torch.float16,  # FP16 for RTX performance
            'batch_size': 12,            # Optimized for RTX 5090
            'compile_model': True,       # torch.compile for 20-30% speedup
            'memory_format': torch.channels_last,
            'cudnn_benchmark': True
        }
    
    def get_ollama_config(self) -> Dict:
        """Get optimized configuration for Ollama LLM"""
        return {
            'device': f'cuda:{self.ollama_gpu}',
            'precision': torch.float16,
            'num_gpu': 1,
            'main_gpu': self.ollama_gpu,
            'gpu_memory_utilization': 0.75
        }

def setup_parakeet_model(gpu_manager: DualGPUManager):
    """Setup Parakeet model with RTX 5090 optimization"""
    config = gpu_manager.get_parakeet_config()
    
    # Set device
    torch.cuda.set_device(config['device'])
    
    # Model loading with optimization
    model_config = {
        'device': config['device'],
        'precision': config['precision'],
        'batch_size': config['batch_size']
    }
    
    # Memory optimization
    torch.cuda.empty_cache()
    
    return model_config

def setup_ollama_environment(gpu_manager: DualGPUManager):
    """Setup environment variables for Ollama on RTX 3090"""
    config = gpu_manager.get_ollama_config()
    
    # Set environment variables for Ollama
    os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_manager.ollama_gpu)
    os.environ['OLLAMA_GPU_MEMORY_UTILIZATION'] = str(config['gpu_memory_utilization'])
    
    return config

# Adaptive batch sizing based on GPU memory
class AdaptiveBatchProcessor:
    """Adaptive batch processing for RTX GPUs"""
    
    def __init__(self, gpu_id: int = 0):
        self.gpu_id = gpu_id
        self.base_batch_size = 8 if gpu_id == 0 else 6  # RTX 5090 vs 3090
    
    def get_optimal_batch_size(self) -> int:
        """Get optimal batch size based on available GPU memory"""
        try:
            # Get current memory usage
            memory_info = torch.cuda.mem_get_info(self.gpu_id)
            available_memory = memory_info[0]  # Available memory in bytes
            total_memory = memory_info[1]      # Total memory in bytes
            
            memory_usage_ratio = 1 - (available_memory / total_memory)
            
            # Adaptive batch sizing
            if self.gpu_id == 0:  # RTX 5090
                if memory_usage_ratio < 0.7:
                    return 12  # Aggressive batching
                elif memory_usage_ratio < 0.8:
                    return 8
                else:
                    return 4
            else:  # RTX 3090
                if memory_usage_ratio < 0.6:
                    return 8
                elif memory_usage_ratio < 0.75:
                    return 6
                else:
                    return 3
                    
        except Exception:
            # Fallback to base batch size
            return self.base_batch_size
    
    def optimize_for_streaming(self) -> Dict:
        """Get streaming-optimized configuration"""
        return {
            'batch_size': self.get_optimal_batch_size(),
            'batch_timeout_ms': 10 if self.gpu_id == 0 else 12,  # RTX 5090 faster
            'max_sequence_length': 8192,
            'use_kv_cache': True
        }

# Simple GPU detection and fallback
def detect_available_gpus() -> Dict[str, bool]:
    """Detect available RTX GPUs"""
    gpu_info = {
        'rtx_5090_available': False,
        'rtx_3090_available': False,
        'cuda_available': torch.cuda.is_available(),
        'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
    }
    
    if gpu_info['cuda_available']:
        for i in range(gpu_info['gpu_count']):
            gpu_name = torch.cuda.get_device_name(i).lower()
            if 'rtx 5090' in gpu_name or '5090' in gpu_name:
                gpu_info['rtx_5090_available'] = True
            elif 'rtx 3090' in gpu_name or '3090' in gpu_name:
                gpu_info['rtx_3090_available'] = True
    
    return gpu_info

# Configuration presets for different hardware setups
HARDWARE_CONFIGS = {
    'dual_rtx': {
        'parakeet_gpu': 0,      # RTX 5090
        'ollama_gpu': 1,        # RTX 3090
        'parakeet_batch_size': 12,
        'ollama_memory_fraction': 0.75,
        'enable_mixed_precision': True
    },
    'single_rtx_5090': {
        'parakeet_gpu': 0,
        'ollama_gpu': 0,        # Shared GPU
        'parakeet_batch_size': 8,
        'ollama_memory_fraction': 0.4,  # Conservative sharing
        'enable_mixed_precision': True
    },
    'single_rtx_3090': {
        'parakeet_gpu': 0,
        'ollama_gpu': 0,
        'parakeet_batch_size': 6,
        'ollama_memory_fraction': 0.3,
        'enable_mixed_precision': True
    },
    'cpu_fallback': {
        'parakeet_gpu': -1,     # CPU
        'ollama_gpu': -1,       # CPU
        'parakeet_batch_size': 2,
        'enable_mixed_precision': False
    }
}

def get_recommended_config() -> Dict:
    """Get recommended configuration based on available hardware"""
    gpu_info = detect_available_gpus()
    
    if gpu_info['rtx_5090_available'] and gpu_info['rtx_3090_available']:
        return HARDWARE_CONFIGS['dual_rtx']
    elif gpu_info['rtx_5090_available']:
        return HARDWARE_CONFIGS['single_rtx_5090']
    elif gpu_info['rtx_3090_available']:
        return HARDWARE_CONFIGS['single_rtx_3090']
    else:
        return HARDWARE_CONFIGS['cpu_fallback']

# Example usage
if __name__ == "__main__":
    # Detect hardware and get recommended config
    recommended = get_recommended_config()
    print(f"Recommended configuration: {recommended}")
    
    # Setup dual GPU manager
    if recommended['parakeet_gpu'] >= 0:
        gpu_manager = DualGPUManager(
            parakeet_gpu=recommended['parakeet_gpu'],
            ollama_gpu=recommended['ollama_gpu']
        )
        
        # Get configurations
        parakeet_config = gpu_manager.get_parakeet_config()
        ollama_config = gpu_manager.get_ollama_config()
        
        print(f"Parakeet config: {parakeet_config}")
        print(f"Ollama config: {ollama_config}")
        
        # Optimize memory
        gpu_manager.optimize_gpu_memory()
        
        print("GPU optimization complete")
    else:
        print("No CUDA GPUs available, using CPU fallback")
