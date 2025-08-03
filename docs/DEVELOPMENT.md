# PersonalParakeet v3 - Development Guide

This guide provides a complete overview of the setup, development, and contribution process for PersonalParakeet v3.

---

## 1. Environment Setup

### 1.1. Prerequisites

-   **Python**: 3.11+ is required.
-   **GPU**: An NVIDIA GPU is recommended for real-time STT. CPU-only mode is supported for development.
-   **CUDA**: CUDA 11.8+ for GPU acceleration.
-   **Poetry**: For dependency management.

### 1.2. Python Version Considerations

-   The project targets Python 3.11+ (as specified in `.python-version`).
-   While the system may run on newer versions like 3.13, some ML packages (like NVIDIA NeMo) have strict version compatibility requirements. It is recommended to use a Python version as close to the target as possible.

### 1.3. Installation

This project uses **Poetry** for dependency management. It is the recommended way to set up the development environment.

1.  **Install Poetry**:

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2.  **Clone and Install Dependencies**:

    ```bash
    git clone <repository>
    cd PersonalParakeet/v3-flet

    # Install core dependencies (includes mock STT)
    poetry install

    # To include ML dependencies for real STT
    poetry install --with ml

    # Activate the virtual environment
    poetry shell
    ```

### 1.4. GPU/CUDA Setup

For modern GPUs like the RTX 5090, you may need a nightly build of PyTorch:

```bash
# Install PyTorch with CUDA 12.1 support
poetry run pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 1.5. ML Stack Verification

After installation, verify your setup:

```bash
python ml_stack_check.py
```

---

## 2. Project Structure

The project follows the `src-layout` structure, which is not yet fully implemented but is the goal of the ongoing refactoring.

```
v3-flet/
├── main.py
├── config.py
├── core/
│   ├── stt_processor.py
│   ├── clarity_engine.py
│   └── ...
├── ui/
│   └── dictation_view.py
└── tests/
```

---

## 3. Development Commands

### 3.1. Running the Application

```bash
# With Poetry
poetry run python main.py

# Or, within an activated poetry shell
python main.py
```

### 3.2. Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific tests
poetry run pytest tests/test_audio_headless.py
```

### 3.3. Code Quality

```bash
# Format code
poetry run black . --line-length 100
poetry run isort . --profile black

# Lint and type-check
poetry run ruff check .
poetry run mypy .
```

---

## 4. Configuration Profiles

The system uses configuration profiles to manage different sets of parameters for various use cases. This system is currently being ported from v2.

### 4.1. Profile Definitions

-   **Fast Conversation**: Low latency, moderate accuracy.
-   **Balanced**: Default settings for general use.
-   **Accurate Document**: High accuracy, higher latency.
-   **Low-Latency**: Minimal delay, for specific real-time applications.

### 4.2. Profile Management

A `ProfileManager` class in `config.py` will handle loading, saving, and switching profiles at runtime. The UI will include a dropdown to select the active profile.

### 4.3. Runtime Switching

-   Profile switching will be thread-safe.
-   Components (audio, VAD, etc.) will be notified of configuration changes to adapt their behavior without a restart.

---

## 5. Development Patterns

### 5.1. Threading Architecture

-   **Producer-Consumer**: The audio engine is a producer that puts audio chunks into a queue. The STT processor is a consumer that takes chunks from the queue.
-   **Thread-Safe UI Updates**: All UI updates from background threads **must** use `asyncio.run_coroutine_threadsafe(coro, page.loop)` to avoid race conditions.

### 5.2. Flet UI Patterns

-   UI components are defined in the `ui/` directory.
-   The main UI is built in the `DictationView` class.
-   UI updates should be done asynchronously via `await page.update_async()`.

### 5.3. Migration Guidelines (from v2)

-   **Remove WebSocket Code**: Replace `websocket.send()` with direct function calls or async UI updates.
-   **Replace `subprocess`**: Use `threading.Thread` for background tasks.
-   **Use Flet State**: Replace React-style state management with Flet's reactive components.

---

## 6. Troubleshooting

-   **CUDA Issues**: If you see `RuntimeError: No CUDA GPUs available`, verify your PyTorch and CUDA installation. Use `nvidia-smi` and `python -c "import torch; print(torch.cuda.is_available())"` to debug.
-   **Audio Issues**: If you have no audio input, use `python -c "import sounddevice as sd; print(sd.query_devices())"` to list devices and check permissions.
-   **Import Errors**: Ensure you have installed all dependencies with `poetry install` and that you are in the correct virtual environment (`poetry shell`).

---

## 7. Contributing

1.  Create a feature branch.
2.  Install dependencies: `poetry install --with dev,ml`.
3.  Make changes, following existing code patterns.
4.  Run tests: `poetry run pytest`.
5.  Format and lint your code.
6.  Create a pull request.
