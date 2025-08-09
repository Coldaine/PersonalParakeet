
# PersonalParakeet v3 Architecture (Last updated: August 4, 2025)

## 1. Executive Summary

PersonalParakeet v3 is a hybrid Python-Rust, single-process, multi-threaded real-time dictation system using Rust+EGUI for the UI framework connected via PyO3 bridge. The v3 migration eliminates all WebSocket, IPC, and multi-process patterns, resulting in a stable, maintainable, and performant application. All UI, audio, and STT logic runs in a single process, with thread-safe communication via `queue.Queue`.

**Key Architectural Principles:**
- Hybrid Python-Rust, single-process, multi-threaded design
- Rust+EGUI for all UI components via PyO3 bridge (no React/Tauri remnants)
- Thread-safe producer-consumer pattern for audio and STT
- src-layout for maintainability
- Modern tooling: black, isort, ruff, mypy
- Dataclasses for all configuration

## 2. Architecture Decision Record

**Date:** July 26, 2025  
**Status:** Accepted  
**Decision:** Migrate to a single-process Rust+EGUI application with PyO3 bridge

### 2.1. Context and Problem
v2’s Tauri/WebSocket architecture caused race conditions, complex deployment, and poor maintainability. v3 solves these by unifying all logic in a single Python process.

### 2.2. Alternatives Considered
- Fix v2 (rejected: fundamental flaws remain)
- pywebview (rejected: still requires JS maintenance)
- Rust+EGUI (chosen: high-performance native UI, single process, PyO3 bridge)
- Native UI (rejected: dated appearance)

## 3. Technical Architecture

### 3.1. High-Level Design

```
[Single Python Process]
├── Rust+EGUI UI (Main Thread via PyO3)
├── Audio Producer Thread
├── STT Consumer Thread
├── Clarity Engine Thread (optional)
└── Shared Queue (thread-safe)
```

**Key modules:**
- `core/`: Business logic (audio, STT, injection, clarity, etc.)
- `ui/`: Python bridge to Rust+EGUI components
- `config.py`: Dataclass-based configuration and runtime profiles
- `main.py`: Single entry point

### 3.2. Configuration Profiles & Runtime Switching
PersonalParakeet v3 supports runtime configuration profiles (e.g., for speed, accuracy, conversation, document modes). Profiles are managed via dataclasses and can be switched at runtime (see `config.py`).

### 3.3. Enhanced Injection & Thought Linking
- **Enhanced Injection:** Multi-strategy text injection (UI Automation, Keyboard, Clipboard, etc.) is implemented, but some advanced strategies are still in progress.
- **Thought Linking:** Modular thought linking is partially integrated; further UI and workflow integration is planned.

### 3.4. Testing & Performance
- All tests use real hardware (no mocks/stubs)
- <150ms latency target (see TESTING docs)

## 4. Current Gaps & Next Steps
- Some features (advanced injection, thought linking, configuration UI) are partially implemented
- Performance benchmarks and automated latency tests are planned
- Linux support is partial; see STATUS.md for details

---

**Benefits**:
- **Simple**: No IPC, no serialization overhead.
- **Reliable**: Eliminates race conditions and synchronization issues.
- **Maintainable**: A single codebase in one language.

### 3.2. Design Principles

1.  **Simplicity First**: One language, one process, one executable.
2.  **Thread Safety**: Use producer-consumer patterns with `queue.Queue` for inter-thread communication.
3.  **Robustness**: Graceful degradation (e.g., mock STT if ML dependencies are unavailable) and isolated error handling in threads.

### 3.3. Threading Model

-   **Main Thread (Rust+EGUI UI)**: Handles all UI updates and user interactions via PyO3 bridge.
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
