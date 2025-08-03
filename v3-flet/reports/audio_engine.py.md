# audio_engine.py Analysis Report

## Overview
Core audio processing engine implementing producer-consumer architecture for real-time audio capture, speech-to-text processing, and text correction.

## Purpose
- Manage audio input stream from microphone
- Process audio through STT (Speech-to-Text) engine
- Apply text corrections via Clarity Engine
- Detect voice activity and pauses
- Coordinate callbacks to UI layer

## Dependencies

### External Libraries
- `sounddevice` (as `sd`) - Audio input/output management
- `numpy` (as `np`) - Numerical operations on audio data
- `asyncio` - Asynchronous programming
- `logging` - Logging functionality
- `threading` - Background audio processing thread
- `queue` - Thread-safe audio buffer

### Internal Modules
- `core.stt_processor.STTProcessor` - Speech-to-text processing
- `core.clarity_engine.ClarityEngine` - Text correction and clarity improvements
- `core.vad_engine.VoiceActivityDetector` - Voice activity detection
- `config.V3Config` - Configuration management

## Class: AudioEngine

### Architecture Pattern
Producer-Consumer pattern with:
- **Producer**: Audio callback fills queue with audio chunks
- **Consumer**: Background thread processes audio from queue

### Key Attributes
- `config` - V3Config instance
- `event_loop` - Asyncio event loop for UI callbacks
- `audio_queue` - Thread-safe queue (max 50 chunks)
- `audio_stream` - SoundDevice input stream
- `audio_thread` - Background processing thread
- `stt_processor` - STT processing component
- `clarity_engine` - Text correction component
- `vad_engine` - Voice activity detector
- Callback functions for UI updates:
  - `on_raw_transcription`
  - `on_corrected_transcription`
  - `on_pause_detected`
  - `on_vad_status`
  - `on_error`

### Key Methods

#### Initialization & Lifecycle
1. `initialize()` - Async initialization of all components:
   - STT processor
   - Clarity Engine (with worker thread)
   - VAD Engine with pause detection callback

2. `start()` - Start audio capture and processing:
   - Launch background processing thread
   - Create and start audio input stream

3. `stop()` - Clean shutdown:
   - Stop audio stream
   - Join processing thread (2s timeout)
   - Clear audio queue

#### Audio Processing Pipeline
1. `_audio_callback()` - **Producer** (runs in audio thread):
   - Receives audio chunks from sounddevice
   - Converts to float32
   - Adds to queue (drops if full)

2. `_audio_processing_loop()` - **Consumer** (runs in background thread):
   - Gets audio from queue
   - Processes through VAD
   - Checks silence threshold
   - Runs STT processing
   - Handles transcription

3. `_process_stt_sync()` - Synchronous STT processing wrapper

4. `_handle_transcription()` - Process raw STT output:
   - Update current text
   - Trigger raw transcription callback
   - Apply Clarity Engine corrections if enabled
   - Create CorrectionResult object

#### Callback Management
- All callbacks use `asyncio.run_coroutine_threadsafe()` for thread-safe UI updates
- Supports both sync and async callbacks
- Error handling for failed callbacks

### Control Methods
- `set_clarity_enabled()` - Toggle clarity corrections
- `clear_current_text()` - Reset text and context
- `get_current_text()` - Get current transcription
- Callback setters for UI integration

## Design Patterns

### Producer-Consumer with Queue
- Decouples audio capture from processing
- Prevents blocking in audio callback
- Handles backpressure with queue size limit

### Callback Pattern
- Loose coupling with UI through callbacks
- Thread-safe async execution
- Graceful error handling

### State Management
- Tracks listening/running states
- Maintains current transcription text
- Clarity engine enable/disable state

## Potential Issues & Weaknesses

### Critical Issues
1. **Event loop handling**: Uses both `self.event_loop` and `asyncio.get_event_loop()` inconsistently
2. **Thread safety**: `current_text` accessed from multiple threads without synchronization
3. **Resource cleanup**: No cleanup for clarity_engine worker thread
4. **Queue overflow**: Drops audio chunks silently when queue full

### Design Concerns
1. **Mixed sync/async**: Complex callback handling for both sync and async functions
2. **CorrectionResult creation**: Creates class inline instead of proper data structure
3. **Hardcoded values**: Queue size (50), timeout values
4. **Error propagation**: Errors logged but not always propagated to UI

### Performance Issues
1. **Queue blocking**: 0.5s timeout in processing loop adds latency
2. **Multiple event loop lookups**: Could cache event loop reference
3. **Copy operations**: Audio chunk copied unnecessarily

### Robustness Issues
1. **No reconnection logic**: Audio stream failures not recoverable
2. **Limited error context**: Generic error messages
3. **No metrics/monitoring**: No performance tracking beyond warnings

## Integration Points
- **STTProcessor**: Synchronous transcription calls
- **ClarityEngine**: Async initialization, sync correction calls
- **VoiceActivityDetector**: Frame processing and pause detection
- **DictationView**: All UI callbacks

## Recommendations
1. **Thread safety**: Add locks for shared state (`current_text`)
2. **Event loop**: Store and reuse event loop reference consistently
3. **Queue management**: Implement adaptive queue sizing or flow control
4. **Error handling**: Add error recovery and retry logic
5. **Monitoring**: Add performance metrics and health checks
6. **Resource cleanup**: Ensure all threads/resources cleaned up properly
7. **Configuration**: Make queue size and timeouts configurable
8. **Data structures**: Define proper dataclasses instead of inline classes
9. **Testing**: Add unit tests for producer-consumer pipeline
10. **Documentation**: Add docstrings for all public methods