# Code Style and Conventions - PersonalParakeet v2

## Python Style Configuration
- **Formatter**: Black with 100-character line length
- **Import Sorting**: isort with black profile  
- **Type Checking**: mypy enabled (python_version = "3.11")
- **Target Version**: Python 3.11+ (per .python-version file)

## v2 Architecture Conventions
- **Dictation View UI**: Tauri/React frontend with glass morphism effects
- **WebSocket Backend**: Python WebSocket server (`dictation_websocket_bridge.py`)
- **Real-time Communication**: WebSocket protocol for live transcription updates
- **Clarity Engine**: Built-in text corrections for accuracy improvements

## Project Structure (v2)
- **Main Entry**: `start_dictation_view.py` - Complete system launcher
- **Backend Core**: `dictation_websocket_bridge.py` - WebSocket server with STT integration
- **Frontend**: `dictation-view-ui/` - Tauri application with React components
- **Core Package**: `personalparakeet/` - STT, Clarity Engine, VAD modules
- **Testing**: `tests/` with audio, integration, and manual verification tests

## Code Organization Patterns
- **Modular WebSocket Architecture**: Clean separation of frontend/backend
- **Cross-platform Support**: Windows primary, designed for expansion
- **Direct NeMo Integration**: Avoid wrapper layers, use direct model loading
- **Real-time Processing**: Chunk-based audio with GPU acceleration
- **Clarity Engine Priority**: Fast rule-based corrections over complex AI

## Development Constraints
- **v2 Dictation View Focus**: All development centers on modern UI approach
- **Tauri/React Frontend**: Modern web technologies for transparent UI
- **WebSocket Communication**: Real-time updates between components  
- **Windows Compatibility**: All features must work on target platform
- **GPU Acceleration**: NVIDIA CUDA support essential for performance

## Naming Conventions
- **Files**: Snake_case (e.g., `dictation_websocket_bridge.py`, `clarity_engine.py`)
- **Classes**: PascalCase (e.g., `DictationView`, `ClarityEngine`)
- **Functions/Variables**: Snake_case
- **Constants**: UPPER_SNAKE_CASE
- **UI Components**: PascalCase React components

## Documentation Standards
- **Docstrings**: Concise, focus on purpose and key parameters
- **Comments**: Explain why, not what
- **README**: Maintain current v2 status and working system confirmation
- **CLAUDE.md**: Keep updated with v2 architecture and development constraints

## Frontend Conventions (Tauri/React)
- **Components**: Functional components with hooks
- **Styling**: CSS modules with glass morphism effects
- **State Management**: React state for UI, WebSocket for data
- **Build System**: Vite for development, Tauri for native packaging