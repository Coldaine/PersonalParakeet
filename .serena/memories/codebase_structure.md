# PersonalParakeet Codebase Structure

## Root Directory Organization
```
PersonalParakeet/
├── src/personalparakeet/           # Main application code
├── tests/                          # Test suites (unit, integration, hardware)
├── docs/                          # Documentation
├── scripts/                       # Utility scripts
├── test_reports/                  # Test execution reports
├── pyproject.toml                 # Poetry configuration
├── environment.yml                # Conda environment
├── requirements-torch.txt         # PyTorch dependencies
├── requirements-ml.txt            # ML dependencies
└── CLAUDE.md                      # AI assistant instructions
```

## Source Code Structure
```
src/personalparakeet/
├── __main__.py                    # Entry point
├── main.py                       # Application bootstrap (PersonalParakeetV3)
├── config.py                     # Dataclass configuration system
├── audio_engine.py              # Audio processing orchestrator
├── core/                        # Business logic components
│   ├── stt_processor.py         # Speech-to-text processing
│   ├── stt_factory.py          # STT model factory
│   ├── clarity_engine.py       # Text correction engine
│   ├── text_injector.py        # Text input strategies
│   ├── vad_engine.py           # Voice activity detection
│   ├── thought_linker.py       # Thought linking logic
│   └── injection_manager*.py   # Text injection management
├── ui/                         # UI components (now using Rust + egui)
└── utils/                      # Utility modules
    └── dependency_validation.py
```

## Test Structure
```
tests/
├── unit/                       # Unit tests (isolated components)
├── integration/                # End-to-end integration tests
├── hardware/                   # Hardware validation tests
├── benchmarks/                 # Performance benchmarks
├── fixtures/                   # Test data and audio samples
└── core/                      # Test infrastructure
    ├── base_hardware_test.py   # Hardware test base class
    ├── test_reporter.py        # Test result reporting
    └── resource_monitor.py     # Resource usage monitoring
```

## Documentation Structure
```
docs/
├── QUICKSTART.md              # Installation guide
├── ARCHITECTURE.md            # Design decisions
├── DEVELOPMENT.md             # API reference and contributing
├── STATUS.md                 # Progress tracking
├── TESTING_*.md              # Testing framework docs
└── instructions/             # Additional guides
```

## Key Entry Points
- **Main Application**: `src/personalparakeet/main.py:PersonalParakeetV3`
- **CLI Entry**: `src/personalparakeet/__main__.py`
- **Configuration**: `src/personalparakeet/config.py:V3Config`
- **Audio Processing**: `src/personalparakeet/audio_engine.py:AudioEngine`
- **UI**: Rust + egui via `personalparakeet_ui.GuiController`

## Threading Architecture
- **Main Thread**: Flet UI event loop
- **Audio Thread**: sounddevice callback (producer)
- **STT Thread**: Speech recognition processing (consumer)
- **Communication**: queue.Queue + asyncio.run_coroutine_threadsafe()
