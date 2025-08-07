"""Hardware validation utilities for tests."""

import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch

# Import dependency validation
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
from personalparakeet.utils.dependency_validation import get_validator

# Check dependencies on initialization
_validator = get_validator()
AUDIO_DEPS_AVAILABLE = _validator.check_audio_dependencies()
PYAUDIO_AVAILABLE = AUDIO_DEPS_AVAILABLE.get("pyaudio", False)
SOUNDDDEVICE_AVAILABLE = AUDIO_DEPS_AVAILABLE.get("sounddevice", False)
SOUNDFILE_AVAILABLE = AUDIO_DEPS_AVAILABLE.get("soundfile", False)

# Optional imports for hardware dependencies
if PYAUDIO_AVAILABLE:
    import pyaudio
else:
    pyaudio = None


class HardwareValidator:
    """Validates hardware availability and capabilities."""

    def __init__(self):
        self._validation_cache: Dict[str, Any] = {}

    def validate_all(self) -> Dict[str, Any]:
        """Validate all hardware components."""
        return {
            "audio": self.validate_audio(),
            "gpu": self.validate_gpu(),
            "system": self.validate_system(),
            "windows": (
                self.validate_windows() if platform.system() == "Windows" else {"available": False}
            ),
        }

    def validate_audio(self) -> Dict[str, Any]:
        """Validate audio hardware availability."""
        if "audio" in self._validation_cache:
            return self._validation_cache["audio"]

        result = {
            "available": False,
            "devices": [],
            "default_device": None,
            "sample_rates": [],
            "error": None,
        }

        if not AUDIO_DEPS_AVAILABLE:
            result["error"] = "Audio dependencies not available. Install with: pip install pyaudio"
            self._validation_cache["audio"] = result
            return result

        try:
            pa = pyaudio.PyAudio()

            # Get device count
            device_count = pa.get_device_count()
            result["available"] = device_count > 0

            # Enumerate devices
            for i in range(device_count):
                try:
                    info = pa.get_device_info_by_index(i)
                    if int(info.get("maxInputChannels", 0)) > 0:
                        result["devices"].append(
                            {
                                "index": i,
                                "name": info["name"],
                                "channels": info["maxInputChannels"],
                                "sample_rate": int(info["defaultSampleRate"]),
                            }
                        )

                        # Set default device
                        try:
                            default_info = pa.get_default_input_device_info()
                            if info.get("index") == default_info.get("index"):
                                result["default_device"] = i
                        except Exception:
                            # If no default input device, use first available
                            if result["default_device"] is None and len(result["devices"]) == 1:
                                result["default_device"] = i
                except Exception:
                    continue

            # Test common sample rates
            if result["default_device"] is not None:
                for rate in [16000, 44100, 48000]:
                    try:
                        stream = pa.open(
                            rate=rate,
                            channels=1,
                            format=pyaudio.paInt16,
                            input=True,
                            input_device_index=result["default_device"],
                            frames_per_buffer=1024,
                        )
                        stream.close()
                        result["sample_rates"].append(rate)
                    except Exception:
                        continue

            pa.terminate()

        except Exception as e:
            result["error"] = str(e)

        self._validation_cache["audio"] = result
        return result

    def validate_gpu(self) -> Dict[str, Any]:
        """Validate GPU/CUDA availability."""
        if "gpu" in self._validation_cache:
            return self._validation_cache["gpu"]

        result = {"available": False, "cuda_available": False, "device_count": 0, "devices": []}

        try:
            result["cuda_available"] = torch.cuda.is_available()

            if result["cuda_available"]:
                result["available"] = True
                result["device_count"] = torch.cuda.device_count()

                for i in range(result["device_count"]):
                    props = torch.cuda.get_device_properties(i)
                    result["devices"].append(
                        {
                            "index": i,
                            "name": props.name,
                            "memory_gb": props.total_memory / 1e9,
                            "compute_capability": f"{props.major}.{props.minor}",
                            "multiprocessors": props.multi_processor_count,
                        }
                    )

            # Check for other GPU types (e.g., MPS on macOS)
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                result["available"] = True
                result["mps_available"] = True

        except Exception as e:
            result["error"] = str(e)

        self._validation_cache["gpu"] = result
        return result

    def validate_system(self) -> Dict[str, Any]:
        """Validate system capabilities."""
        if "system" in self._validation_cache:
            return self._validation_cache["system"]

        result = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "cpu_count": None,
            "memory_gb": None,
        }

        try:
            import psutil

            result["cpu_count"] = psutil.cpu_count()
            result["memory_gb"] = psutil.virtual_memory().total / 1e9
        except ImportError:
            # Fallback if psutil not available
            import os

            result["cpu_count"] = os.cpu_count()

        self._validation_cache["system"] = result
        return result

    def validate_windows(self) -> Dict[str, Any]:
        """Validate Windows-specific features."""
        if "windows" in self._validation_cache:
            return self._validation_cache["windows"]

        result = {
            "available": platform.system() == "Windows",
            "version": None,
            "pygetwindow_available": False,
            "win32_available": False,
        }

        if not result["available"]:
            return result

        try:
            result["version"] = platform.win32_ver()[0]

            # Check pygetwindow
            try:
                import pygetwindow

                result["pygetwindow_available"] = True
            except ImportError:
                pass

            # Check win32 modules
            try:
                import win32api
                import win32con

                result["win32_available"] = True
            except ImportError:
                pass

        except Exception as e:
            result["error"] = str(e)

        self._validation_cache["windows"] = result
        return result

    def get_current_state(self) -> Dict[str, Any]:
        """Get current hardware state snapshot."""
        state = {"timestamp": time.time()}

        # Add GPU state if available
        if torch.cuda.is_available():
            state["gpu"] = {
                "memory_allocated": torch.cuda.memory_allocated() / 1e9,
                "memory_reserved": torch.cuda.memory_reserved() / 1e9,
            }

        # Add system state
        try:
            import psutil

            state["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
            }
        except ImportError:
            pass

        return state

    def generate_report(self) -> str:
        """Generate hardware validation report."""
        validation = self.validate_all()

        report = ["Hardware Validation Report", "=" * 50, ""]

        # Audio section
        report.append("Audio Devices:")
        if validation["audio"]["available"]:
            for device in validation["audio"]["devices"]:
                report.append(
                    f"  - {device['name']} ({device['channels']} channels, {device['sample_rate']}Hz)"
                )
        else:
            report.append("  - No audio devices found")

        # GPU section
        report.append("\nGPU/CUDA:")
        if validation["gpu"]["available"]:
            for device in validation["gpu"]["devices"]:
                report.append(f"  - {device['name']} ({device['memory_gb']:.1f}GB)")
        else:
            report.append("  - No GPU available")

        # System section
        report.append("\nSystem:")
        sys = validation["system"]
        report.append(f"  - Platform: {sys['platform']} {sys['platform_version']}")
        report.append(f"  - Python: {sys['python_version']}")
        report.append(f"  - CPUs: {sys['cpu_count']}")
        if sys["memory_gb"]:
            report.append(f"  - Memory: {sys['memory_gb']:.1f}GB")

        return "\n".join(report)
