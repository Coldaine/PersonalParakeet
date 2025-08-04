import torch
try:
    import nvidia_ml_py3 as pynvml
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    print(f"NVML GPU Memory: {info.used/1024**2:.0f}MB used")
except ImportError:
    print("nvidia-ml-py3 not installed")
except Exception as e:
    print(f"NVML error: {e}")

if torch.cuda.is_available():
    torch.cuda.init()
    print(f"PyTorch sees GPU: {torch.cuda.get_device_name(0)}")
    tensor = torch.randn(2000, 2000).cuda()
    print(f"PyTorch GPU memory after allocation: {torch.cuda.memory_allocated()/1024**2:.1f}MB")
else:
    print("CUDA not available to PyTorch")