
# PersonalParakeet v3 - Development Guide (Last updated: August 4, 2025)

This guide provides a complete overview of the setup, development, and contribution process for PersonalParakeet v3.

---

## 1. Environment Setup

### 1.1. Prerequisites

- **Python**: 3.11+ is required (3.11.x recommended for ML compatibility)
- **GPU**: NVIDIA GPU recommended for real-time STT (CPU-only mode supported)
- **CUDA**: CUDA 11.8+ for GPU acceleration
- **Conda**: For environment management
- **Poetry**: For dependency management

### 1.2. Python Version Considerations

- The project targets Python 3.11+ (see `.python-version`)
- Some ML packages (e.g., NVIDIA NeMo) have strict version compatibility; use the recommended Python version

### 1.3. Installation

This project uses a hybrid **Conda + Poetry** setup.

1. **Clone and Create Conda Environment**:
    ```bash
    git clone <repository>
    cd PersonalParakeet
    conda env create -f environment.yml
    conda activate personalparakeet
    ```
2. **Install Application Dependencies with Poetry**:
    ```bash
    poetry install
    ```
3. **Activate the Virtual Environment**:
    ```bash
    poetry shell
    ```

### 1.4. ML Stack Verification

After installation, verify your setup:
```bash
python -m personalparakeet.scripts.ml_stack_check
```

---

## 2. Project Structure

The project follows a modern `src-layout` structure:

```
src/personalparakeet/
├── core/           # Business logic only
├── ui/             # Flet components only
├── main.py         # Single entry point
└── config.py       # Dataclass configuration
```

## 3. Code Style & Patterns

- Use **dataclasses** for all configuration
- Type hints are required throughout
- Use **async/await** only for UI updates (Flet)
- Follow proven patterns in `docs/archive/legacy/V3_PROVEN_CODE_LIBRARY.md`
- Use `queue.Queue` for thread-safe communication (never direct cross-thread UI access)

## 4. Configuration Profiles

- All configuration is managed via dataclasses in `config.py`
- Runtime profile switching is supported (see ProfileManager in `config.py`)
- Add new profiles by extending the `ConfigurationProfile` dataclass

## 5. Testing

- All tests use real hardware (no mocks/stubs)
- Run tests with:
    ```bash
    poetry run pytest tests/
    ```
- See `docs/TESTING_IMPLEMENTATION_SUMMARY.md` for details

## 6. Contribution & PR Checklist

- [ ] Code follows single-process, thread-safe architecture
- [ ] All new features are documented in the appropriate `.md` files
- [ ] Dependencies are updated in both `requirements.txt` and documentation
- [ ] Tests are added/updated for new features
- [ ] Documentation is cross-checked for accuracy and completeness

---
src/
└── personalparakeet/
    ├── __main__.py
    ├── main.py
    ├── config.py
    ├── core/
    │   ├── stt_processor.py
    │   ├── clarity_engine.py
    │   └── ...
    ├── ui/
    │   └── dictation_view.py
    └── ...
tests/
```

---

## 3. Development Commands

### 3.1. Running the Application

```bash
# With Poetry
poetry run personalparakeet

# Or, within an activated poetry shell
python -m personalparakeet
```

### 3.2. Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific tests
poetry run pytest tests/test_audio_engine.py
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
