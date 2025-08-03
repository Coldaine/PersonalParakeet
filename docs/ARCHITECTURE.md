# PersonalParakeet v3 Architecture

## 1. Executive Summary

PersonalParakeet v3 represents a complete architectural overhaul from the problematic two-process Tauri/WebSocket system to a unified **single-process Flet application**. This migration addresses critical stability, deployment, and maintenance issues while preserving all v2 features. The core of the architecture is a pure Python, single-process solution that eliminates all inter-process communication (IPC) complexity.

**Key Decisions**:
- Migrate to **Flet** for a pure Python UI.
- Adopt a **single-process, multi-threaded architecture**.
- Implement a **src-layout** for a clean, maintainable project structure.
- Use **Poetry** for dependency management and packaging.
- Standardize on modern tooling: **black, isort, ruff, mypy**.

## 2. Architecture Decision Record

**Date**: July 26, 2025
**Status**: Accepted
**Decision**: Migrate PersonalParakeet to a single-process Flet application.

### 2.1. Context and Problem

PersonalParakeet v2's architecture led to critical issues:
- **Process synchronization failures**: WebSocket race conditions between the Tauri frontend and Python backend.
- **Complex deployment**: Required Node.js, Rust, and Python toolchains.
- **Shell/path conflicts**: `npm` using Git Bash caused startup failures.
- **User feedback**: "Process management nightmare."

### 2.2. Considered Alternatives

1.  **Fix Current Architecture** ❌
    -   **Pros**: Preserves existing code.
    -   **Cons**: Fundamental architectural flaws remain.
    -   **Verdict**: Treating symptoms, not the disease.
2.  **pywebview** 🤔
    -   **Pros**: Preserves React UI, single process.
    -   **Cons**: Still requires JavaScript maintenance.
    -   **Verdict**: Good option but not optimal.
3.  **Flet** ✅ **CHOSEN**
    -   **Pros**: Pure Python, single process, Material Design, simple deployment.
    -   **Cons**: Complete UI rewrite, larger bundle (~50MB).
    -   **Verdict**: Best balance of simplicity and functionality.
4.  **Native UI (Tkinter, etc.)** ❌
    -   **Pros**: Smaller executable.
    -   **Cons**: Dated appearance, poor developer experience.
    -   **Verdict**: Not suitable for a modern application.

## 3. Technical Architecture

### 3.1. High-Level Design

The v3 architecture is a single Python process that manages the UI, audio processing, and STT inference in separate threads.

```
[Single Python Process]
├── Flet UI (Main Thread)
├── Audio Producer Thread
├── STT Consumer Thread
└── Shared Queue (thread-safe)
```

**Benefits**:
- **Simple**: No IPC, no serialization overhead.
- **Reliable**: Eliminates race conditions and synchronization issues.
- **Maintainable**: A single codebase in one language.

### 3.2. Design Principles

1.  **Simplicity First**: One language, one process, one executable.
2.  **Thread Safety**: Use producer-consumer patterns with `queue.Queue` for inter-thread communication.
3.  **Robustness**: Graceful degradation (e.g., mock STT if ML dependencies are unavailable) and isolated error handling in threads.

### 3.3. Threading Model

-   **Main Thread (Flet UI)**: Handles all UI updates and user interactions.
-   **Audio Producer Thread**: Managed by a `sounddevice` callback. Its only job is to put audio chunks into a thread-safe queue.
-   **STT Consumer Thread**: Pulls audio chunks from the queue, runs Parakeet inference, and sends results to the main thread for UI updates via `asyncio.run_coroutine_threadsafe()`.

```python
# Producer (audio callback)
def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

# Consumer (STT worker)
def stt_worker(page):
    while True:
        chunk = audio_queue.get()
        text = model.transcribe(chunk)
        # Thread-safe UI update
        asyncio.run_coroutine_threadsafe(
            update_ui(text), page.loop
        )
```

### 3.4. Critical Architecture Constraints

-   **❌ FORBIDDEN PATTERNS**:
    -   WebSocket servers or clients.
    -   `subprocess` calls for UI components.
    -   Multi-process architecture.
    -   Direct cross-thread UI access.
    -   Any Tauri/React/Node.js dependencies.
-   **✅ REQUIRED PATTERNS**:
    -   Producer-consumer with `queue.Queue`.
    -   `asyncio.run_coroutine_threadsafe()` for UI updates.
    -   Dataclass-based configuration.
    -   Direct function calls between components.

## 4. Project Structure (Src-Layout)

To improve maintainability and separate the library code from tests and scripts, the project will adopt a `src-layout`.

```
personalparakeet/
├── src/
│   └── personalparakeet/
│       ├── __init__.py
│       ├── __main__.py
│       ├── audio/
│       ├── core/
│       ├── ui/
│       └── config/
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── scripts/
├── pyproject.toml
├── poetry.lock
├── Makefile
└── README.md
```

## 5. Configuration Management

-   **Single Source of Truth**: A single `pyproject.toml` will manage all project metadata, dependencies, and tool configurations.
-   **Application Configuration**: A dataclass-based system (`config.py`) will be used for application settings, loaded from a user-specific location (e.g., `~/.config/personalparakeet/config.json`).

## 6. Refactoring and Migration Plan

### Phase 1: Preparation
1.  **Backup**: Create a new git branch `refactor/modern-structure`.
2.  **Scaffold**: Create the new `src-layout` directory structure.

### Phase 2: Code Migration
1.  **Move Files**: Relocate files from the legacy structure to the new `src/personalparakeet/` structure.
2.  **Update Imports**: Change all imports to be absolute, reflecting the new structure (e.g., `from personalparakeet.core.module import ...`).

### Phase 3: Configuration Consolidation
1.  **Create Unified `pyproject.toml`**: Merge settings from the root and legacy `pyproject.toml` files.
2.  **Setup Tooling**: Configure `black`, `isort`, `ruff`, and `mypy` in the unified `pyproject.toml`.

### Phase 4: CI/CD and Documentation
1.  **Update CI**: Modify `.github/workflows/ci.yml` to work with the new structure and Poetry commands.
2.  **Update Docs**: Revise all documentation (`README.md`, `DEVELOPMENT.md`, etc.) to reflect the new structure, installation, and usage commands.

## 7. Benefits of this Architecture

1.  **Maintainability**: A clear and standard project structure.
2.  **Testability**: A dedicated `tests/` directory, separate from the source code.
3.  **Distributability**: Easy to build and distribute as a package via Poetry.
4.  **Developer Experience**: Modern, standardized tooling improves code quality and consistency.
5.  **Collaboration**: A familiar structure makes it easier for new contributors to get started.
