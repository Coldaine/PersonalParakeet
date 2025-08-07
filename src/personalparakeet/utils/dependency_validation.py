"""Dependency validation utilities for PersonalParakeet."""

import sys
from typing import Any, Dict, List, Optional


class DependencyValidator:
    """Validates and manages optional dependencies."""

    def __init__(self):
        self._dependency_cache: Dict[str, bool] = {}

    def check_dependency(self, module_name: str, pip_package: Optional[str] = None) -> bool:
        """
        Check if a dependency is available.

        Args:
            module_name: Python module name to import
            pip_package: Pip package name (if different from module name)

        Returns:
            True if dependency is available, False otherwise
        """
        if module_name in self._dependency_cache:
            return self._dependency_cache[module_name]

        try:
            __import__(module_name)
            self._dependency_cache[module_name] = True
            return True
        except ImportError:
            self._dependency_cache[module_name] = False
            return False

    def check_audio_dependencies(self) -> Dict[str, bool]:
        """Check audio-related dependencies."""
        return {
            "pyaudio": self.check_dependency("pyaudio", "pyaudio"),
            "sounddevice": self.check_dependency("sounddevice", "sounddevice"),
            "soundfile": self.check_dependency("soundfile", "soundfile"),
        }

    def check_ml_dependencies(self) -> Dict[str, bool]:
        """Check ML-related dependencies."""
        return {
            "torch": self.check_dependency("torch", "torch"),
            "nemo": self.check_dependency("nemo", "nemo-toolkit"),
        }

    def check_system_dependencies(self) -> Dict[str, bool]:
        """Check system-related dependencies."""
        return {
            "keyboard": self.check_dependency("keyboard", "keyboard"),
            "pynput": self.check_dependency("pynput", "pynput"),
            "pyperclip": self.check_dependency("pyperclip", "pyperclip"),
            "psutil": self.check_dependency("psutil", "psutil"),
        }

    def get_missing_dependencies(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """Get list of missing dependencies by category."""
        missing = {}

        if category is None or category == "audio":
            audio_deps = self.check_audio_dependencies()
            missing_audio = [dep for dep, available in audio_deps.items() if not available]
            if missing_audio:
                missing["audio"] = missing_audio

        if category is None or category == "ml":
            ml_deps = self.check_ml_dependencies()
            missing_ml = [dep for dep, available in ml_deps.items() if not available]
            if missing_ml:
                missing["ml"] = missing_ml

        if category is None or category == "system":
            system_deps = self.check_system_dependencies()
            missing_system = [dep for dep, available in system_deps.items() if not available]
            if missing_system:
                missing["system"] = missing_system

        return missing

    def generate_install_commands(self, category: Optional[str] = None) -> List[str]:
        """Generate pip install commands for missing dependencies."""
        missing = self.get_missing_dependencies(category)
        commands = []

        for cat, deps in missing.items():
            for dep in deps:
                if cat == "audio":
                    if dep == "pyaudio":
                        commands.append("pip install pyaudio")
                    elif dep == "sounddevice":
                        commands.append("pip install sounddevice")
                    elif dep == "soundfile":
                        commands.append("pip install soundfile")
                elif cat == "ml":
                    if dep == "torch":
                        commands.append("pip install torch")
                    elif dep == "nemo":
                        commands.append("pip install nemo-toolkit[asr]")
                elif cat == "system":
                    if dep == "keyboard":
                        commands.append("pip install keyboard")
                    elif dep == "pynput":
                        commands.append("pip install pynput")
                    elif dep == "pyperclip":
                        commands.append("pip install pyperclip")
                    elif dep == "psutil":
                        commands.append("pip install psutil")

        return commands

    def print_dependency_report(self, category: Optional[str] = None) -> None:
        """Print a dependency report to stdout."""
        missing = self.get_missing_dependencies(category)

        if not missing:
            print("✓ All dependencies are available")
            return

        print("Missing dependencies:")
        for cat, deps in missing.items():
            print(f"  {cat.upper()}: {', '.join(deps)}")

        commands = self.generate_install_commands(category)
        if commands:
            print("\nTo install missing dependencies:")
            for cmd in commands:
                print(f"  {cmd}")


# Global validator instance
_validator = None


def get_validator() -> DependencyValidator:
    """Get the global dependency validator instance."""
    global _validator
    if _validator is None:
        _validator = DependencyValidator()
    return _validator


def check_audio_dependencies() -> Dict[str, bool]:
    """Check audio dependencies (convenience function)."""
    return get_validator().check_audio_dependencies()


def require_audio_dependency(module_name: str, pip_package: Optional[str] = None):
    """Decorator to require an audio dependency."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            validator = get_validator()
            if not validator.check_dependency(module_name, pip_package):
                missing = validator.get_missing_dependencies("audio")
                if module_name in missing.get("audio", []):
                    raise ImportError(
                        f"Required audio dependency '{module_name}' is not available. "
                        f"Install with: pip install {pip_package or module_name}"
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def optional_import(module_name: str, pip_package: Optional[str] = None):
    """
    Optionally import a module with helpful error message.

    Args:
        module_name: Python module name to import
        pip_package: Pip package name (if different from module name)

    Returns:
        Module if available, None otherwise
    """
    validator = get_validator()
    if validator.check_dependency(module_name, pip_package):
        return __import__(module_name)
    else:
        return None
