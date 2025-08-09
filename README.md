# PersonalParakeet 🦜

**Real-time dictation with a transparent floating UI, AI-powered corrections, and intelligent text processing for seamless speech-to-text experiences.**

PersonalParakeet v3 is a complete rewrite with a single-process architecture using Rust+EGUI, designed for high-performance real-time dictation with GPU acceleration.

## Core Features & Requirements

-   **Intelligent Text Processing**: Prevents jarring text rewrites using pause-based text commitment and multi-second STT processing for more stable output.
-   **High-Performance STT**: GPU-accelerated speech recognition using NVIDIA Parakeet, with a target accuracy of 6.05% WER.
-   **Floating UI**: A transparent, draggable dictation window that floats above other applications.
-   **Clarity Engine**: Real-time, rule-based text corrections for homophones and technical jargon.
-   **Smart Text Injection**: Multi-strategy, platform-aware text input that adapts to the active application.
-   **Advanced VAD**: Dual VAD system (Silero + WebRTC) for robust and accurate speech detection.
-   **Configuration Profiles**: Pre-tuned profiles (e.g., "Fast Conversation", "Accurate Document") that can be switched at runtime.
-   **Voice Commands**: Hands-free control with "Hey Parakeet" activation pattern and customizable commands.
-   **Thought Linking**: Intelligent context management for better dictation flow and text continuity.

## Quick Start

```bash
# Clone repository
git clone <repo>
cd PersonalParakeet

# Setup (see SETUP.md for details)
conda create -n personalparakeet python=3.12
conda activate personalparakeet
poetry install
poetry run pip install -r requirements-torch.txt  # RTX 5090 support

# Run application
poetry run personalparakeet
# or
python -m personalparakeet
```

See [**QUICKSTART.md**](docs/QUICKSTART.md) for detailed setup instructions.

## Architecture

PersonalParakeet v3 uses a modern single-process architecture with:

- **Rust+EGUI Framework**: High-performance native UI with transparent floating window via PyO3 bridge
- **Audio Engine**: Real-time audio processing with VAD and STT integration
- **GPU Acceleration**: NVIDIA Parakeet for high-performance speech recognition
- **Text Processing**: Multi-stage pipeline with clarity corrections and intelligent injection
- **Platform Integration**: Cross-platform text injection with multiple fallback strategies

## Documentation

-   [**QUICKSTART.md**](docs/QUICKSTART.md) - Installation and first run.
-   [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) - Technical design decisions.
-   [**DEVELOPMENT.md**](docs/DEVELOPMENT.md) - Contributing and API reference.
-   [**STATUS.md**](docs/STATUS.md) - Current project status and roadmap.

## System Requirements

-   Python 3.11+
-   NVIDIA GPU (recommended) or CPU mode.
-   8GB RAM minimum.
-   Microphone access
-   Windows/Linux/macOS

## Key Features in Detail

### Speech Recognition
- **NVIDIA Parakeet**: State-of-the-art speech recognition with GPU acceleration
- **Multi-second Processing**: 4-second audio chunks for optimal accuracy vs. latency balance
- **Real-time Transcription**: Continuous speech-to-text with minimal delay

### Text Processing
- **Pause-based Commitment**: Text is committed when natural speech pauses are detected
- **Clarity Engine**: Automatic correction of homophones and technical terminology
- **Context Awareness**: Maintains context for more accurate corrections

### User Interface
- **Transparent Floating Window**: Non-intrusive dictation interface
- **Draggable & Resizable**: Position the dictation window where you need it
- **Real-time Feedback**: Visual and audio feedback for system status
- **Dark Theme**: Easy on the eyes for extended use

### Text Injection
- **Cross-platform**: Works on Windows, Linux, and macOS
- **Multiple Strategies**: Keyboard simulation, clipboard injection, and platform-specific methods
- **Application-aware**: Adapts injection strategy based on active application
- **Fallback Mechanisms**: Multiple injection methods ensure reliability

### Voice Commands
- **"Hey Parakeet" Activation**: Two-step voice command system to minimize false positives
- **Built-in Commands**: Text management, clarity control, and system commands
- **Extensible**: Easy to add custom voice commands
- **Confirmation System**: Destructive commands require user confirmation

## Performance

- **Target WER**: 6.05% Word Error Rate with NVIDIA Parakeet
- **Latency**: Sub-second transcription delay
- **Memory Usage**: Optimized for minimal footprint
- **CPU/GPU**: Automatically detects and uses optimal hardware

## Troubleshooting

See [**TROUBLESHOOTING.md**](docs/TROUBLESHOOTING.md) for common issues and solutions.

## Contributing

We welcome contributions! Please see [**DEVELOPMENT.md**](docs/DEVELOPMENT.md) for guidelines.

## License

MIT License - See LICENSE file for details.

## Support

For issues and questions:
- Check the [documentation](docs/)
- Search existing [GitHub issues](https://github.com/yourusername/PersonalParakeet/issues)
- Create a new issue if needed
