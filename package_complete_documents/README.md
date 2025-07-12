# Advanced Parakeet Dictation System

Feature-complete dictation system with GPU acceleration, dual VAD, LLM refinement, and smart text injection.

## Features Implemented

- **Dual VAD** (Silero + WebRTC) for accurate speech detection
- **Streaming transcription** with context and stability tracking
- **Smart text injection** based on active application
- **LLM refinement** with context awareness
- **GPU distribution** (Parakeet on GPU 0, Ollama on GPU 1)
- **Real-time statistics overlay**
- **Multiple hotkeys** for feature control
- **WebSocket server mode** for custom integrations

## Quick Start

```bash
pip install -r requirements.txt
python dictation.py
```

### WebSocket Server Mode

To enable WebSocket streaming for external applications:

```bash
python dictation.py --server
```

This starts a WebSocket server on `ws://localhost:8765` that streams transcriptions in real-time.

## Hotkeys

- **F4**: Toggle dictation ON/OFF
- **F5**: Toggle LLM refinement
- **F6**: Toggle overlay display
- **Ctrl+Alt+Q**: Quit

## Architecture

### Audio Processing (`audio_handler.py`)
- 16kHz audio capture with low latency
- Dual VAD processing for robust speech detection
- Automatic device selection with USB preference
- Buffered speech chunks with silence detection

### Transcription (`transcriber.py`)
- NVIDIA Parakeet TDT 0.6B model
- Streaming buffer with 3-second maximum
- Context preservation for improved accuracy
- Word stability tracking for reliable output

### Text Output (`text_output.py`)
- Smart injection based on active application:
  - **Code editors**: Fast clipboard paste
  - **Browsers**: Quick typing
  - **Terminals**: Special paste handling
- Application detection with pattern matching
- Clipboard preservation

### LLM Refinement (`llm_refiner.py`)
- Ollama integration for text improvement
- Context-aware refinement (general, code, email)
- GPU device selection (defaults to cuda:1)
- Maintains conversation context

### Main Application (`dictation.py`)
- Orchestrates all components
- Real-time statistics display
- Hotkey management
- Optional WebSocket server
- Async processing for performance

## Requirements

### Hardware
- CUDA-capable GPU (preferably 2 for optimal performance)
- Microphone with good quality

### Software
- Python 3.8+
- CUDA toolkit
- Ollama (for LLM refinement)
- Windows/Linux/macOS

## WebSocket API

When running with `--server`, the system exposes a WebSocket endpoint that streams JSON messages:

```json
{
  "type": "transcription",
  "text": "transcribed text",
  "timestamp": 1234567890.123,
  "refined": true
}
```

### Example WebSocket Client

```python
import asyncio
import websockets
import json

async def client():
    async with websockets.connect("ws://localhost:8765") as websocket:
        async for message in websocket:
            data = json.loads(message)
            print(f"Transcription: {data['text']}")

asyncio.run(client())
```

## Performance Tips

1. **GPU Memory**: Monitor with `nvidia-smi` to ensure models fit
2. **Audio Device**: USB microphones typically provide better quality
3. **LLM Performance**: Disable with F5 if experiencing delays
4. **Buffer Size**: Adjust in `transcriber.py` if needed

## Troubleshooting

### No Audio Input
- Check device permissions
- Verify microphone is connected
- Look for device in audio handler initialization

### GPU Out of Memory
- Close other GPU applications
- Use CPU fallback (automatic)
- Reduce model precision if needed

### LLM Connection Failed
- Ensure Ollama is running (`ollama serve`)
- Check port 11434 is available
- Verify model is pulled (`ollama pull llama2:7b`)

## Development

### Testing
Tests are in `test_components.py`. Run only when explicitly needed:
```bash
pytest test_components.py
```

### Adding Features
1. Follow existing code patterns
2. Maintain separation of concerns
3. Update README for new features
4. Test thoroughly before deployment

## License

This is a prototype implementation for demonstration purposes.