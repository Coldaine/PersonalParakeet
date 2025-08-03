# PersonalParakeet 🦜

**Real-time dictation with a transparent floating UI, AI-powered corrections, and a unique "LocalAgreement" buffering system to prevent text rewrites.**

PersonalParakeet v3 is a complete rewrite with a single-process architecture using Flet.

## Core Features & Requirements

-   **LocalAgreement Buffering**: The core innovation that prevents jarring text rewrites by only committing text that is stable across multiple transcription updates.
-   **High-Performance STT**: GPU-accelerated speech recognition using NVIDIA Parakeet, with a target accuracy of 6.05% WER.
-   **Floating UI**: A transparent, draggable dictation window that floats above other applications.
-   **Clarity Engine**: Real-time, rule-based text corrections for homophones and technical jargon.
-   **Smart Text Injection**: Multi-strategy, platform-aware text input that adapts to the active application.
-   **Advanced VAD**: Dual VAD system (Silero + WebRTC) for robust and accurate speech detection.
-   **Configuration Profiles**: Pre-tuned profiles (e.g., "Fast Conversation", "Accurate Document") that can be switched at runtime.

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

## Documentation

-   [**QUICKSTART.md**](docs/QUICKSTART.md) - Installation and first run.
-   [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) - Technical design decisions.
-   [**DEVELOPMENT.md**](docs/DEVELOPMENT.md) - Contributing and API reference.
-   [**STATUS.md**](docs/STATUS.md) - Current project status and roadmap.

## System Requirements

-   Python 3.11+
-   NVIDIA GPU (recommended) or CPU mode.
-   8GB RAM minimum.

## License

MIT License - See LICENSE file for details.
