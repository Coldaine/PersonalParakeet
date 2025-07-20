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
            print(f"\n--- GPU {i} ---")
            device_name = torch.cuda.get_device_name(i)
            print(f"  Device Name: {device_name}")
            
            # Check for RTX 5090
            if "5090" not in device_name:
                print("  WARNING: Expected RTX 5090, but a different GPU was found.")

            capability = torch.cuda.get_device_capability(i)
            print(f"  Device Compute Capability: {capability}")

            # Verify Compute Capability for Blackwell
            if capability != (12, 0):
                print(f"  WARNING: Expected Compute Capability (12, 0) for RTX 5090, but got {capability}.")
            
            # Perform a simple tensor operation on the GPU
            tensor = torch.randn(3, 3).to(f"cuda:{i}")
            print(f"  Successfully created a tensor on cuda:{i}")
            print(f"  Tensor: \n{tensor}")

    else:
        print("\nERROR: PyTorch cannot find a CUDA-enabled GPU. The installation may be incorrect.")

except Exception as e:
    print(f"\nAn error occurred during verification: {e}")

print("\n--- Verification Complete ---")