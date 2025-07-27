# PersonalParakeet 🦜

**Real-time dictation with transparent floating UI and AI-powered corrections**

PersonalParakeet v3 - Complete rewrite with single-process architecture using Flet.

## Quick Start

```bash
# Clone and install
git clone <repository>
cd PersonalParakeet/v3-flet
poetry install --with ml

# Run
poetry run python main.py
```

See [**QUICKSTART.md**](docs/QUICKSTART.md) for detailed setup instructions.

## Key Features

- 🎯 **Floating UI** - Transparent, draggable dictation window
- 🎤 **Real-time STT** - NVIDIA Parakeet-TDT 1.1B model
- ✨ **Clarity Engine** - Automatic text corrections
- 🔄 **Smart Injection** - Multi-strategy text input
- 🖥️ **Cross-platform** - Windows/Linux support

## Documentation

- [**QUICKSTART.md**](docs/QUICKSTART.md) - Installation and first run
- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) - Technical design decisions
- [**DEVELOPMENT.md**](docs/DEVELOPMENT.md) - Contributing and API reference
- [**STATUS.md**](docs/STATUS.md) - Current progress (20% complete)

## Project Status

**v3.0.0-alpha** - Core functionality working, integration in progress.

| Component | Status | Description |
|-----------|---------|-------------|
| Architecture | ✅ Complete | Single-process Flet design |
| Audio/STT | ✅ Complete | Real-time transcription |
| UI | ✅ Complete | Floating transparent window |
| Text Injection | 🚧 Testing | Multi-strategy system |
| Integration | 🚧 In Progress | End-to-end validation |

## Requirements

- Python 3.11+
- NVIDIA GPU (recommended) or CPU mode
- 8GB RAM minimum

## License

MIT License - See LICENSE file for details.