"""Test GPU/CUDA functionality."""

import time

import numpy as np
import pytest
import torch

from ..core.base_hardware_test import BaseHardwareTest


class TestGPUCuda(BaseHardwareTest):
    """Test GPU and CUDA functionality."""

    @pytest.mark.hardware
    def test_cuda_availability(self):
        """Test CUDA availability and basic info."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")

        print(f"\nCUDA Information:")
        print(f"  PyTorch version: {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        print(f"  CUDA version: {torch.version.cuda}")
        print(f"  cuDNN version: {torch.backends.cudnn.version()}")
        print(f"  Device count: {torch.cuda.device_count()}")

        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"\nGPU {i}: {props.name}")
            print(f"  Compute capability: {props.major}.{props.minor}")
            print(f"  Memory: {props.total_memory / 1024**3:.1f} GB")
            print(f"  Multiprocessors: {props.multi_processor_count}")

    @pytest.mark.hardware
    @pytest.mark.gpu_intensive
    def test_gpu_memory_allocation(self, skip_if_no_gpu):
        """Test GPU memory allocation and deallocation."""
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

        initial_memory = torch.cuda.memory_allocated()

        # Allocate tensors of different sizes
        sizes = [(1000, 1000), (2000, 2000), (4000, 4000)]
        tensors = []

        for size in sizes:
            tensor = torch.randn(size, device="cuda")
            tensors.append(tensor)

            current_memory = torch.cuda.memory_allocated()
            tensor_memory = current_memory - initial_memory
            expected_memory = np.prod(size) * 4  # float32

            print(f"\nAllocated {size} tensor:")
            print(f"  Memory used: {tensor_memory / 1024**2:.1f} MB")
            print(f"  Expected: {expected_memory / 1024**2:.1f} MB")

            # Allow for some overhead
            assert (
                tensor_memory < expected_memory * 1.5
            ), f"Excessive memory usage for {size} tensor"

        # Test deallocation
        peak_memory = torch.cuda.max_memory_allocated()
        del tensors
        torch.cuda.empty_cache()

        final_memory = torch.cuda.memory_allocated()
        print(f"\nMemory after cleanup:")
        print(f"  Peak usage: {peak_memory / 1024**2:.1f} MB")
        print(f"  Final usage: {final_memory / 1024**2:.1f} MB")

        assert (
            final_memory < peak_memory
        ), f"Memory not properly deallocated. Expected < {peak_memory}, but was {final_memory}"

    @pytest.mark.hardware
    @pytest.mark.gpu_intensive
    def test_gpu_computation_speed(self, skip_if_no_gpu):
        """Test GPU computation speed vs CPU."""
        sizes = [(1000, 1000), (2000, 2000)]

        for size in sizes:
            # CPU timing
            a_cpu = torch.randn(size)
            b_cpu = torch.randn(size)

            start = time.time()
            for _ in range(10):
                c_cpu = torch.matmul(a_cpu, b_cpu)
            cpu_time = time.time() - start

            # GPU timing (include transfer time)
            torch.cuda.synchronize()
            start = time.time()
            a_gpu = a_cpu.cuda()
            b_gpu = b_cpu.cuda()
            for _ in range(10):
                c_gpu = torch.matmul(a_gpu, b_gpu)
            torch.cuda.synchronize()
            gpu_time = time.time() - start

            speedup = cpu_time / gpu_time

            print(f"\nMatrix multiplication {size}:")
            print(f"  CPU time: {cpu_time:.3f}s")
            print(f"  GPU time: {gpu_time:.3f}s")
            print(f"  Speedup: {speedup:.1f}x")

            # GPU should be faster for reasonable sizes
            if np.prod(size) > 1000000:  # 1M elements
                assert speedup > 1.0, f"GPU slower than CPU for {size}"

    @pytest.mark.hardware
    @pytest.mark.gpu_intensive
    def test_gpu_data_transfer(self, skip_if_no_gpu):
        """Test data transfer speeds between CPU and GPU."""
        sizes_mb = [1, 10, 100]

        for size_mb in sizes_mb:
            elements = int(size_mb * 1024 * 1024 / 4)  # float32
            data = torch.randn(elements)

            # CPU to GPU
            torch.cuda.synchronize()
            start = time.time()
            data_gpu = data.cuda()
            torch.cuda.synchronize()
            upload_time = time.time() - start
            upload_speed = size_mb / upload_time

            # GPU to CPU
            torch.cuda.synchronize()
            start = time.time()
            data_cpu = data_gpu.cpu()
            torch.cuda.synchronize()
            download_time = time.time() - start
            download_speed = size_mb / download_time

            print(f"\nData transfer {size_mb} MB:")
            print(f"  Upload: {upload_speed:.1f} MB/s")
            print(f"  Download: {download_speed:.1f} MB/s")

            # Reasonable transfer speeds (>100 MB/s for PCIe)
            assert upload_speed > 100, f"Upload too slow: {upload_speed:.1f} MB/s"
            assert download_speed > 100, f"Download too slow: {download_speed:.1f} MB/s"

    @pytest.mark.hardware
    @pytest.mark.gpu_intensive
    @pytest.mark.slow
    def test_gpu_stress(self, skip_if_no_gpu):
        """Stress test GPU with continuous operations."""
        print("\nRunning GPU stress test for 10 seconds...")

        # Monitor memory and errors
        errors = 0
        max_memory = 0
        operations = 0

        start_time = time.time()
        while time.time() - start_time < 10.0:
            try:
                # Random operation
                size = np.random.randint(100, 1000)
                a = torch.randn(size, size, device="cuda")
                b = torch.randn(size, size, device="cuda")

                # Compute
                c = torch.matmul(a, b)
                d = torch.nn.functional.relu(c)
                e = d.sum()

                # Force synchronization
                e.item()

                operations += 1
                max_memory = max(max_memory, torch.cuda.memory_allocated())

                # Cleanup
                del a, b, c, d, e

            except Exception as e:
                errors += 1
                print(f"Error during stress test: {e}")
                torch.cuda.empty_cache()

        duration = time.time() - start_time

        print(f"\nStress test results:")
        print(f"  Duration: {duration:.1f}s")
        print(f"  Operations: {operations}")
        print(f"  Operations/sec: {operations/duration:.1f}")
        print(f"  Errors: {errors}")
        print(f"  Peak memory: {max_memory / 1024**2:.1f} MB")

        assert errors == 0, f"Errors during stress test: {errors}"
        assert operations > 100, f"Too few operations completed: {operations}"
