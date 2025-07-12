# Project Structure

```
parakeet-dictation/
├── audio_handler.py      # Audio capture + dual VAD (Silero + WebRTC)
├── transcriber.py        # Parakeet streaming transcription with buffer
├── text_output.py        # Smart text injection (paste/type/terminal)
├── llm_refiner.py        # Ollama LLM integration for text refinement
├── dictation.py          # Main application with hotkeys and UI
├── requirements.txt      # Python dependencies
├── test_components.py    # Component tests (DO NOT RUN automatically)
├── README.md            # Project documentation
└── .serena/             # Serena project configuration
    └── project.yml
```

## Module Responsibilities

### audio_handler.py
- Continuous audio capture at 16kHz
- Dual VAD processing (Silero + WebRTC)
- Speech chunk detection and queuing
- Auto-detect best audio device

### transcriber.py
- NVIDIA Parakeet model loading and inference
- Streaming buffer management (3 seconds max)
- Context preservation for accuracy
- Text stability tracking

### text_output.py
- Application detection (editors, browsers, terminals)
- Smart injection method selection
- Clipboard preservation
- Natural typing simulation

### llm_refiner.py
- Ollama API integration
- Context-aware text refinement
- GPU device selection (cuda:1)
- Type-specific prompts (general, code, email)

### dictation.py
- Main event loop
- Hotkey management
- Component orchestration
- Real-time statistics display