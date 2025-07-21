# PersonalParakeet v3 - Flet Single-Process Architecture

## Overview

PersonalParakeet v3 represents a complete architectural redesign from v2, eliminating the problematic dual-process WebSocket architecture in favor of a clean, single-process Flet application.

## Key Changes from v2

### ✅ What's Fixed
- **Single Process**: No more WebSocket servers or process management
- **Direct Communication**: Components communicate via direct function calls
- **Modern UI**: Flet provides native-quality UI with Python-only codebase
- **Simplified Dependencies**: No Node.js, Rust, or Tauri required
- **Producer-Consumer**: Clean audio pipeline with proper threading

### ✅ What's Preserved
- **Core STT**: Parakeet-TDT-1.1B model integration
- **Clarity Engine**: Real-time text corrections with <50ms latency
- **VAD Engine**: Voice activity detection with pause triggers
- **Configuration**: Type-safe dataclass-based config system
- **Glass Morphism UI**: Beautiful transparent floating window

### 🚧 What's Planned
- **Command Mode**: Voice command recognition system
- **Thought Linking**: Intelligent text flow decisions
- **Text Injection**: Direct injection to active applications

## Quick Start

```bash
# Install dependencies
pip install -r requirements-v3.txt

# Run PersonalParakeet v3
python main.py
```

## Architecture

```
PersonalParakeet v3 Architecture
├── main.py                    # Flet app entry point
├── audio_engine.py            # Producer-consumer audio pipeline
├── config.py                  # Dataclass-based configuration
├── core/
│   ├── stt_processor.py       # Parakeet STT integration
│   ├── clarity_engine.py      # Real-time text corrections
│   ├── vad_engine.py          # Voice activity detection
│   └── thought_linker.py      # Thought linking (placeholder)
├── ui/
│   ├── dictation_view.py      # Main UI component
│   ├── components.py          # Reusable UI widgets
│   └── theme.py               # Material Design theme
└── requirements-v3.txt        # Python-only dependencies
```

## Components

### AudioEngine
- **Producer-Consumer Pipeline**: Clean separation of audio capture and processing
- **Direct Callbacks**: No WebSocket messages, direct UI updates
- **Thread Safety**: Proper async/thread communication patterns
- **Error Handling**: Robust error recovery and logging

### Core Components
- **STTProcessor**: Extracted Parakeet integration with CUDA optimization
- **ClarityEngine**: Direct port of working v2 text correction system
- **VADEngine**: Voice activity detection with customizable thresholds
- **ThoughtLinker**: Placeholder for future intelligent text flow

### UI Components
- **DictationView**: Main floating transparent window
- **Components**: Reusable widgets (StatusIndicator, ControlPanel, etc.)
- **Theme**: Consistent Material Design styling with glass morphism

### Configuration
- **V3Config**: Type-safe dataclass configuration
- **Backward Compatibility**: Loads existing config.json files
- **Runtime Updates**: Live configuration changes without restart

## Features

### Working Features ✅
- **Real-time Transcription**: Live STT with Parakeet model
- **Text Corrections**: Rule-based corrections for technical terms
- **Voice Activity Detection**: Automatic pause detection and text commit
- **Glass Morphism UI**: Modern transparent floating interface
- **Configuration Management**: Persistent settings with type safety

### Planned Features 🚧
- **Text Injection**: Direct text insertion to active applications
- **Command Mode**: Voice command recognition and execution
- **Thought Linking**: Intelligent text flow and punctuation
- **Application Detection**: Context-aware behavior per application
- **Keyboard Shortcuts**: Global hotkeys for control

## Performance Targets

- **STT Latency**: <500ms audio-to-text
- **Correction Latency**: <50ms rule-based corrections
- **UI Updates**: <100ms transcription display
- **Memory Usage**: <2GB with Parakeet model loaded
- **GPU Usage**: Efficient CUDA memory management

## Development

### Running in Development
```bash
# Development mode (web browser)
python main.py

# Native app mode (requires flet app)
# Modify main.py: ft.app(target=main, view=ft.FLET_APP)
```

### Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests (when implemented)
pytest tests/
```

### Building
```bash
# Build executable
pip install pyinstaller
pyinstaller --onefile main.py
```

## Compatibility

- **Python**: 3.8+ (tested on 3.11)
- **Operating System**: Windows 10/11 primary, Linux/macOS potential
- **Hardware**: NVIDIA GPU required for Parakeet model
- **CUDA**: 11.8+ recommended for RTX 5090 compatibility

## Migration from v2

1. **Stop v2 system**: Ensure no WebSocket servers running
2. **Install v3 dependencies**: `pip install -r requirements-v3.txt`
3. **Copy configuration**: Existing config.json files are compatible
4. **Run v3**: `python main.py`

## Known Limitations

- **Text Injection**: Not yet implemented (logs to console)
- **Window Dragging**: Basic dragging may not work in web browser mode
- **Command Mode**: Placeholder implementation only
- **Packaging**: Executable building not tested

## Future Roadmap

1. **Text Injection System**: Direct keyboard simulation or clipboard integration
2. **Command Mode Implementation**: Voice command parsing and execution
3. **Thought Linking**: AI-powered text flow decisions
4. **Native Packaging**: Standalone executables for distribution
5. **Cross-Platform**: Full Linux and macOS support

---

PersonalParakeet v3 represents the stable, maintainable foundation for future development. The single-process architecture eliminates the complexity that plagued v2 while preserving all working functionality.