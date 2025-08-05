#!/usr/bin/env python3
"""Analyze all imports in the PersonalParakeet codebase."""

import ast
import os
from pathlib import Path
from collections import defaultdict
import json

def extract_imports(file_path):
    """Extract all imports from a Python file."""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return imports

def categorize_import(import_name):
    """Categorize an import by type."""
    # Standard library
    stdlib = {
        'os', 'sys', 'time', 'datetime', 'json', 'asyncio', 'threading',
        'queue', 'pathlib', 'typing', 'dataclasses', 'enum', 'logging',
        'subprocess', 'platform', 'collections', 'functools', 'itertools',
        'contextlib', 'warnings', 'traceback', 're', 'math', 'random',
        'io', 'struct', 'wave', 'tempfile', 'shutil', 'copy', 'pickle',
        'base64', 'hashlib', 'uuid', 'urllib', 'http', 'socket', 'ssl',
        'abc', 'inspect', 'importlib', 'types', 'weakref', 'gc',
        'multiprocessing', 'concurrent', 'asyncio', 'selectors'
    }
    
    # ML/AI packages
    ml_packages = {
        'torch', 'torchvision', 'torchaudio', 'nemo', 'pytorch_lightning',
        'torchmetrics', 'transformers', 'whisper', 'openai_whisper',
        'silero', 'webrtcvad'
    }
    
    # Scientific/numeric
    scientific = {
        'numpy', 'scipy', 'numba', 'pandas', 'matplotlib', 'seaborn',
        'sklearn', 'scikit-learn', 'networkx'
    }
    
    # Audio processing
    audio = {
        'sounddevice', 'soundfile', 'pyaudio', 'librosa', 'audioread',
        'pydub', 'wave'
    }
    
    # UI/Graphics
    ui = {
        'flet', 'tkinter', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
        'kivy', 'pygame', 'pyglet'
    }
    
    # System interaction
    system = {
        'keyboard', 'pynput', 'pyperclip', 'pyautogui', 'mouse',
        'screeninfo', 'mss', 'psutil', 'pywin32', 'win32api',
        'win32con', 'win32gui', 'ctypes'
    }
    
    # Data/Config
    data_config = {
        'dataclasses_json', 'omegaconf', 'hydra', 'configparser',
        'yaml', 'toml', 'dotenv', 'python-dotenv', 'pydantic'
    }
    
    # Development/Testing
    dev = {
        'pytest', 'unittest', 'mock', 'black', 'isort', 'flake8',
        'mypy', 'ruff', 'coverage', 'tox', 'pytest-asyncio',
        'pytest-cov', 'hypothesis'
    }
    
    # Utility/Misc
    utility = {
        'rich', 'click', 'typer', 'tqdm', 'colorama', 'termcolor',
        'requests', 'httpx', 'aiohttp', 'urllib3', 'certifi',
        'packaging', 'setuptools', 'pip', 'wheel', 'cython',
        'fsspec', 'filelock', 'wrapt', 'decorator', 'six'
    }
    
    if import_name in stdlib:
        return 'stdlib'
    elif import_name in ml_packages:
        return 'ml'
    elif import_name in scientific:
        return 'scientific'
    elif import_name in audio:
        return 'audio'
    elif import_name in ui:
        return 'ui'
    elif import_name in system:
        return 'system'
    elif import_name in data_config:
        return 'data_config'
    elif import_name in dev:
        return 'dev'
    elif import_name in utility:
        return 'utility'
    elif import_name.startswith('personalparakeet'):
        return 'internal'
    else:
        return 'unknown'

def main():
    """Analyze all imports in the codebase."""
    base_path = Path('/mnt/windows_e/_projects/PersonalParakeet')
    src_path = base_path / 'src'
    tests_path = base_path / 'tests'
    
    # Track imports by file and category
    file_imports = {}
    category_imports = defaultdict(set)
    all_imports = set()
    
    # Analyze src directory
    print("Analyzing src directory...")
    for py_file in src_path.rglob('*.py'):
        imports = extract_imports(py_file)
        if imports:
            rel_path = py_file.relative_to(base_path)
            file_imports[str(rel_path)] = sorted(imports)
            all_imports.update(imports)
            
            for imp in imports:
                category = categorize_import(imp)
                category_imports[category].add(imp)
    
    # Analyze tests directory
    print("Analyzing tests directory...")
    for py_file in tests_path.rglob('*.py'):
        imports = extract_imports(py_file)
        if imports:
            rel_path = py_file.relative_to(base_path)
            file_imports[str(rel_path)] = sorted(imports)
            all_imports.update(imports)
            
            for imp in imports:
                category = categorize_import(imp)
                category_imports[category].add(imp)
    
    # Create analysis report
    report = {
        'total_unique_imports': len(all_imports),
        'imports_by_category': {k: sorted(v) for k, v in category_imports.items()},
        'category_counts': {k: len(v) for k, v in category_imports.items()},
        'all_imports': sorted(all_imports),
        'file_imports': file_imports
    }
    
    # Save report
    with open(base_path / 'import_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n=== Import Analysis Summary ===")
    print(f"Total unique imports: {report['total_unique_imports']}")
    print("\nImports by category:")
    for category, count in sorted(report['category_counts'].items()):
        print(f"  {category}: {count}")
    
    print("\n=== Critical ML/AI Imports ===")
    for imp in sorted(category_imports['ml']):
        print(f"  - {imp}")
    
    print("\n=== Audio Processing Imports ===")
    for imp in sorted(category_imports['audio']):
        print(f"  - {imp}")
    
    print("\n=== Unknown/External Imports ===")
    for imp in sorted(category_imports['unknown']):
        print(f"  - {imp}")

if __name__ == '__main__':
    main()