PersonalParakeet - Comprehensive Requirements

## BREAKTHROUGH STATUS: CORE SYSTEM PROVEN WORKING ✅

**Validated Functionality (July 2025):**
- ✅ Windows audio capture working (sounddevice)
- ✅ NVIDIA Parakeet transcription working (NeMo direct integration)  
- ✅ LocalAgreement buffering working (committed vs pending text)
- ✅ Real-time processing (2-3 iterations/second)
- ✅ F4 hotkey toggle working
- ✅ Text stabilization preventing rewrites

**Proven Log Output:**
```
🔊 Processing audio chunk (level: 0.386)
🎯 Raw transcription: 'well'
✅ Committed: '' | ⏳ Pending: 'well'

🔊 Processing audio chunk (level: 0.475)  
🎯 Raw transcription: 'oh shit this is actually'
✅ Committed: '' | ⏳ Pending: 'oh shit this is actually'

🔊 Processing audio chunk (level: 0.353)
🎯 Raw transcription: 'fucking working'
✅ Committed: 'well' | ⏳ Pending: 'working'
```

## Introduction
PersonalParakeet is a real-time speech-to-text dictation system that solves the "rewriting delay" problem common in existing dictation software. The core innovation is LocalAgreement buffering, which prevents jarring text rewrites by only committing text that has achieved sufficient stability across multiple transcription updates. 

**ARCHITECTURE UPDATE**: The system uses direct NeMo integration rather than FastAPI service, providing simpler deployment and proven functionality. The core components (audio capture, Parakeet transcription, LocalAgreement buffering) are validated and working.
Core Requirements
Requirement 1: Audio Capture and Device Management
User Story: As a user, I want to capture audio from my microphone with intelligent device detection, so that I can dictate speech reliably across different hardware configurations.
Acceptance Criteria

WHEN the system starts THEN it SHALL detect and list available audio input devices by name and capabilities
WHEN I start dictation THEN the system SHALL capture audio at 44.1kHz/16-bit and downsample to 16kHz mono for optimal ASR processing
WHEN audio is being captured THEN the system SHALL process audio chunks in real-time with less than 100ms buffer latency
WHEN multiple devices are available THEN the system SHALL allow device selection by partial name matching (e.g., "Blue Yeti", "Microphone")
IF no microphone is available THEN the system SHALL display an error message and gracefully exit
WHEN I stop dictation THEN the system SHALL cleanly release audio resources without hanging
WHEN Windows audio permissions are denied THEN the system SHALL provide clear guidance on enabling microphone access

Requirement 2: GPU-Accelerated Speech Recognition
User Story: As a user, I want my speech transcribed using state-of-the-art AI models with GPU acceleration, so that I get the highest accuracy (6.05% WER target) with optimal performance.
Acceptance Criteria

WHEN speech audio is captured THEN the system SHALL transcribe it using NVIDIA Parakeet as primary engine
WHEN RTX 5090 is available THEN the system SHALL use it for primary transcription processing
WHEN multiple GPUs are available THEN the system SHALL allocate Parakeet to GPU 0 and reserve GPU 1 for LLM processing
IF GPU is not available THEN the system SHALL fallback to faster-whisper on CPU with graceful degradation
WHEN transcription completes THEN the system SHALL return text with confidence scores for LocalAgreement evaluation
WHEN GPU memory is insufficient THEN the system SHALL adapt batch sizes and model precision (FP16) to prevent OOM errors
WHEN transcription fails THEN the system SHALL log the error, attempt recovery, and continue processing

Requirement 3: LocalAgreement Buffering (Core Innovation)
User Story: As a user, I want LocalAgreement buffering to prevent text rewrites, so that I don't experience jarring changes to previously displayed text like in SpeechPulse.
Acceptance Criteria

WHEN new transcription results arrive THEN the system SHALL track prefix agreements across consecutive updates
WHEN a text prefix appears identically in 2 consecutive transcription updates THEN the system SHALL commit that prefix as stable
WHEN text is committed THEN the system SHALL never rewrite, modify, or delete that committed text
WHEN text is pending THEN the system SHALL display it visually distinct from committed text (e.g., brackets, dim color)
WHEN silence is detected for >2 seconds THEN the system SHALL automatically commit all pending text
WHEN prefix agreement threshold is configurable THEN users SHALL be able to tune sensitivity (1-5 range)
WHEN utterances exceed 10 seconds THEN the system SHALL process them in overlapping chunks while maintaining agreement tracking

Requirement 4: Platform-Aware Intelligent Text Injection
User Story: As a user, I want transcribed text to appear intelligently in my active application with platform-optimized injection methods, so that I can dictate efficiently into any program with optimal speed and compatibility across Windows and Linux.
Acceptance Criteria

WHEN new text is committed THEN the system SHALL detect the current platform (Windows/Linux) and use platform-specific injection methods
WHEN running on Windows THEN the system SHALL use:
  - UI Automation API for smart text injection as primary method (most reliable)
  - Direct text pattern insertion for elements supporting IUIAutomationTextPattern
  - keyboard.write() for simple text injection as secondary method
  - Win32 API SendInput for complex scenarios requiring precise control
  - Clipboard automation with Ctrl+V simulation for editors
  - WinRT accessibility APIs for UWP applications
WHEN running on Linux with KDE Plasma THEN the system SHALL use:
  - XTEST extension via python-xlib for X11 sessions (primary method)
  - xdotool for simple text injection with --clearmodifiers flag
  - D-Bus integration for KDE-specific applications (Konsole, Kate)
  - Clipboard with xclip for code editors when appropriate
WHEN running on Linux with GNOME THEN the system SHALL use:
  - AT-SPI accessibility framework for Wayland compatibility
  - XTEST for X11 sessions as fallback
  - IBus input method framework for complex text
WHEN the active application is detected THEN the system SHALL optimize injection method:
  - Code editors (VS Code, Kate, Sublime): Clipboard paste for speed
  - Browsers (Chrome, Firefox): Character-by-character typing for compatibility
  - Terminals (Konsole, GNOME Terminal): Direct injection via app-specific APIs
  - Unknown applications: Conservative character typing
WHEN platform detection occurs THEN the system SHALL cache platform information to avoid repeated checks
IF text injection fails THEN the system SHALL:
  - Attempt alternative injection methods in order of compatibility
  - Display text in fallback overlay as last resort
  - Log failure details for debugging
WHEN text is injected THEN the system SHALL track injection state to prevent duplication
WHEN application context changes THEN the system SHALL adapt injection method dynamically

Requirement 5: Multi-Modal Hotkey Controls
User Story: As a user, I want comprehensive hotkey controls for all system functions, so that I can control dictation and enhancement without interrupting my workflow.
Acceptance Criteria

WHEN I press F4 THEN the system SHALL toggle dictation on/off with immediate audio feedback
WHEN I press F5 THEN the system SHALL trigger LLM refinement of the last transcribed text
WHEN I press F1+F4 THEN the system SHALL trigger context-aware LLM enhancement with application awareness
WHEN I press Ctrl+Alt+Q THEN the system SHALL gracefully quit the application with resource cleanup
WHEN dictation starts THEN the system SHALL provide visual and optional audio feedback within 50ms
WHEN dictation stops THEN the system SHALL commit pending text and provide stop confirmation
WHEN hotkeys conflict with other applications THEN the system SHALL provide alternative key binding configuration

Requirement 6: Dual GPU Windows Optimization
User Story: As a user, I want the system to optimally utilize my Windows RTX 5090 + RTX 3090 setup, so that I get maximum performance with intelligent resource allocation.
Acceptance Criteria

WHEN the system starts on Windows THEN it SHALL detect and enumerate available NVIDIA GPUs with memory information
WHEN RTX 5090 and RTX 3090 are both available THEN the system SHALL allocate Parakeet to RTX 5090 and Ollama/LLM to RTX 3090
WHEN only one GPU is available THEN the system SHALL share resources between Parakeet and LLM processing with memory monitoring
WHEN CUDA is not available THEN the system SHALL fallback to CPU processing with performance warnings
WHEN GPU memory utilization exceeds 90% THEN the system SHALL reduce batch sizes and log memory pressure warnings
WHEN running on Windows THEN the system SHALL properly handle Windows audio APIs, keyboard injection, and window detection
WHEN system performance degrades THEN the system SHALL provide diagnostic information about GPU utilization and bottlenecks

Requirement 7: Advanced Voice Activity Detection
User Story: As a user, I want sophisticated voice activity detection to minimize false transcriptions and optimize processing, so that the system only processes actual speech efficiently.
Acceptance Criteria

WHEN audio is captured THEN the system SHALL use dual VAD (Silero + WebRTC) for robust speech detection
WHEN speech is detected by either VAD THEN the system SHALL begin buffering audio with configurable pre-roll (0.5s default)
WHEN silence is detected after speech THEN the system SHALL process the complete utterance with post-roll buffer (1.0s default)
WHEN no speech is detected for >5 seconds THEN the system SHALL enter low-power monitoring mode
WHEN VAD sensitivity is configurable THEN users SHALL be able to adjust thresholds for different environments (0.1-0.9 range)
WHEN background noise is detected THEN the system SHALL adapt VAD sensitivity automatically based on noise floor
WHEN speech utterances exceed 15 seconds THEN the system SHALL process them in streaming chunks with overlap
WHEN VAD confidence scores are available THEN the system SHALL provide both Silero and WebRTC confidence values
WHEN VAD results disagree THEN the system SHALL use configurable logic to resolve conflicts (default: either detects speech)

Requirement 8: LLM Integration and Post-Processing
User Story: As a user, I want AI-powered text refinement and correction, so that my transcribed text is grammatically correct and contextually appropriate.
Acceptance Criteria

WHEN F5 is pressed THEN the system SHALL send the last transcribed text to configured LLM for refinement
WHEN multiple LLM providers are configured THEN the system SHALL support Ollama (local), OpenAI, and Google Gemini
WHEN Ollama is used THEN the system SHALL use local models (llama3, etc.) on dedicated GPU for privacy
WHEN LLM refinement completes THEN the system SHALL replace the original text with enhanced version
WHEN LLM processing fails THEN the system SHALL fallback gracefully and retain original transcription
WHEN context-aware enhancement is triggered THEN the system SHALL include application type and surrounding text context
WHEN LLM responses are streaming THEN the system SHALL provide real-time feedback during processing

Requirement 9: Configuration and Customization
User Story: As a user, I want comprehensive configuration options, so that I can customize the system for my specific hardware, preferences, and use cases.
Acceptance Criteria

WHEN the system starts THEN it SHALL load configuration from TOML file with sensible defaults
WHEN configuration is missing THEN the system SHALL create default configuration and guide user through setup
WHEN I modify configuration THEN the system SHALL validate settings and apply changes without restart where possible
WHEN audio devices change THEN the system SHALL allow device selection by name pattern matching
WHEN hotkeys conflict THEN the system SHALL provide alternative key binding configuration
WHEN LLM providers are configured THEN the system SHALL validate API keys and model availability
WHEN configuration is invalid THEN the system SHALL provide clear error messages and correction guidance

Requirement 10: Transparent Status Interface
User Story: As a user, I want unobtrusive real-time feedback about system status, so that I know when it's listening, processing, or encountering issues without disrupting my workflow.
Acceptance Criteria

WHEN dictation is active THEN the system SHALL display a transparent overlay widget with minimal screen footprint
WHEN speech is being processed THEN the system SHALL show processing status with progress indication
WHEN text is committed vs pending THEN the system SHALL visually distinguish status with color coding
WHEN errors occur THEN the system SHALL display clear error messages with suggested resolutions
WHEN the system is ready for input THEN the system SHALL indicate readiness with subtle visual cues
WHEN LLM processing is active THEN the system SHALL show enhancement status separately from transcription
WHEN overlay interface is not desired THEN the system SHALL support system tray operation as alternative

Requirement 11: Performance and Reliability
User Story: As a user, I want consistent performance and reliability, so that the system works dependably during extended dictation sessions.
Acceptance Criteria

WHEN processing audio THEN the system SHALL maintain end-to-end latency between 150-700ms as acceptable for dictation
WHEN running continuously THEN the system SHALL manage memory usage to prevent leaks during extended sessions
WHEN errors occur THEN the system SHALL log detailed diagnostic information for troubleshooting
WHEN system resources are low THEN the system SHALL adapt processing parameters to maintain functionality
WHEN transcription accuracy degrades THEN the system SHALL provide feedback about potential causes (noise, hardware, etc.)
WHEN network connectivity is lost THEN cloud LLM features SHALL degrade gracefully to local processing
WHEN the system crashes THEN it SHALL provide crash reports and automatic recovery options

Requirement 12: Comprehensive Error Handling and Recovery
User Story: As a user, I want robust error handling and automatic recovery, so that the system continues working reliably even when encountering hardware or software issues.
Acceptance Criteria

WHEN audio device errors occur THEN the system SHALL attempt automatic device switching with user notification
WHEN GPU memory errors occur THEN the system SHALL reduce batch sizes and switch to FP16 precision automatically
WHEN model loading fails THEN the system SHALL retry with progress indication and provide CPU fallback options
WHEN text injection fails THEN the system SHALL queue text and retry with alternative strategies
WHEN callback registration fails THEN the system SHALL verify permissions and provide troubleshooting guidance
WHEN CUDA errors occur THEN the system SHALL check GPU availability and provide clear error messages
WHEN system resources are exhausted THEN the system SHALL adapt processing parameters and notify user
WHEN configuration is corrupted THEN the system SHALL restore defaults and guide user through reconfiguration
WHEN the system crashes THEN it SHALL generate crash reports and attempt automatic recovery on restart

Requirement 13: Testing and Quality Assurance
User Story: As a developer, I want comprehensive testing coverage, so that the system is reliable and maintainable across different environments and use cases.
Acceptance Criteria

WHEN unit tests are run THEN they SHALL cover LocalAgreement algorithm, audio processing, and model integration
WHEN integration tests are run THEN they SHALL test end-to-end audio-to-text pipeline with real hardware
WHEN performance tests are run THEN they SHALL measure latency, accuracy, and resource usage under load
WHEN error scenario tests are run THEN they SHALL validate recovery mechanisms for all error categories
WHEN compatibility tests are run THEN they SHALL verify functionality across different Windows versions and hardware
WHEN regression tests are run THEN they SHALL ensure new changes don't break existing functionality
WHEN the test suite runs THEN it SHALL complete within 5 minutes for rapid development feedback
WHEN tests fail THEN they SHALL provide clear diagnostic information for debugging

Requirement 14: Cross-Platform Foundation
User Story: As a user, I want the system architecture to support future cross-platform expansion, so that core functionality can be extended to other operating systems.
Acceptance Criteria

WHEN implementing core features THEN the system SHALL use cross-platform libraries where possible
WHEN handling platform-specific features THEN the system SHALL abstract them through platform adapters
WHEN audio processing is implemented THEN it SHALL support both Windows DirectSound and cross-platform alternatives
WHEN keyboard injection is implemented THEN it SHALL provide Windows-optimized paths with cross-platform fallbacks
WHEN window detection is implemented THEN it SHALL support Windows-specific APIs with extensible architecture
WHEN file paths are handled THEN the system SHALL use cross-platform path handling
WHEN building executables THEN the system SHALL support Windows packaging with future platform extension capability

Performance Targets

Transcription Accuracy: 6.05% Word Error Rate (Parakeet target)
End-to-End Latency: 150-700ms (capture to text injection)
Hotkey Response: <50ms (F4 toggle response time)
LocalAgreement Threshold: 2 consecutive agreements (configurable 1-5)
Memory Usage: <4GB total system footprint
GPU Utilization: 70-90% efficient utilization without OOM
VAD Latency: <30ms for speech detection
LLM Enhancement: <5 seconds for typical refinement requests

Technical Architecture Notes

Primary STT: NVIDIA Parakeet 0.6B model on RTX 5090
Fallback STT: faster-whisper large-v3 on CPU
VAD: Dual system (Silero + WebRTC) for robustness
LLM: Ollama (local) primary, OpenAI/Gemini as alternatives
Audio: 44.1kHz capture → 16kHz processing pipeline
Configuration: TOML-based with live reload capabilities
UI: Transparent overlay with system tray fallback
Deployment: Single executable with embedded dependencies

## Configuration System Requirements

### Requirement 15: Advanced Configuration System
**User Story**: As a user, I want a flexible configuration system with pre-defined profiles, so that I can easily switch between different usage scenarios and fine-tune the system for my specific needs.

#### Acceptance Criteria

WHEN the system loads configuration THEN it SHALL support the following configurable parameters with specified ranges:
- Agreement threshold: 1-5 (number of consecutive agreements required before committing text)
- Chunk duration: 0.3-2.0 seconds (audio processing chunk size)
- Max pending words: 5-30 (maximum words held in pending buffer)
- Word timeout: 2.0-7.0 seconds (time before forcing pending words to commit)
- Position tolerance: 1-3 (word position flexibility for agreement matching)
- Audio level threshold: 0.001-0.1 (minimum audio level to process)

WHEN a user selects a configuration profile THEN the system SHALL apply pre-tuned settings for that profile:
- Fast Conversation Mode: Optimized for quick responses in conversational settings
- Balanced Mode (default): Balanced accuracy and responsiveness for general use
- Accurate Document Mode: Maximizes accuracy for formal document dictation
- Low-Latency Mode: Minimizes delay for real-time applications

WHEN Fast Conversation Mode is selected THEN the system SHALL configure:
- Agreement threshold: 1 (commit text after single agreement)
- Chunk duration: 0.3s (short chunks for quick processing)
- Max pending words: 8 (limited buffer for fast output)
- Word timeout: 2.0s (quick timeout for responsiveness)
- Position tolerance: 3 (flexible matching for conversation flow)
- Audio level threshold: 0.005 (moderate sensitivity)

WHEN Balanced Mode is selected THEN the system SHALL configure:
- Agreement threshold: 2 (default stability requirement)
- Chunk duration: 1.0s (standard chunk size)
- Max pending words: 15 (moderate buffer size)
- Word timeout: 4.0s (balanced timeout)
- Position tolerance: 2 (standard matching flexibility)
- Audio level threshold: 0.01 (default sensitivity)

WHEN Accurate Document Mode is selected THEN the system SHALL configure:
- Agreement threshold: 3 (high stability requirement)
- Chunk duration: 2.0s (longer chunks for context)
- Max pending words: 30 (large buffer for accuracy)
- Word timeout: 7.0s (extended timeout for careful dictation)
- Position tolerance: 1 (strict position matching)
- Audio level threshold: 0.02 (reduced sensitivity to avoid false triggers)

WHEN Low-Latency Mode is selected THEN the system SHALL configure:
- Agreement threshold: 1 (immediate commitment)
- Chunk duration: 0.5s (balanced for low latency)
- Max pending words: 5 (minimal buffer)
- Word timeout: 2.5s (quick timeout)
- Position tolerance: 2 (moderate flexibility)
- Audio level threshold: 0.001 (high sensitivity for quick response)

WHEN configuration values are modified THEN the system SHALL validate them within allowed ranges and provide clear error messages for invalid values

WHEN switching between profiles THEN the system SHALL apply changes immediately without requiring restart

WHEN custom configuration is created THEN the system SHALL allow saving it as a new profile with a user-defined name

WHEN configuration changes are made THEN the system SHALL provide visual feedback showing the impact on accuracy vs responsiveness trade-offs

### Requirement 16: Dynamic Configuration Adaptation
**User Story**: As a user, I want the system to automatically adapt to my speech patterns and usage context, so that it continuously improves performance without manual configuration.

#### Acceptance Criteria

**Auto-tuning based on speech patterns:**
- WHEN the system detects my speaking pace THEN it SHALL automatically adjust chunk duration to match my natural rhythm
- WHEN the system detects my pause patterns THEN it SHALL optimize agreement thresholds for my speaking style
- WHEN the system learns my speech rhythm THEN it SHALL adapt to my natural flow and timing
- WHEN the system identifies optimal buffer sizes THEN it SHALL learn and apply user-specific settings

**Application-aware tuning:**
- WHEN the system detects the active application THEN it SHALL identify whether it's an editor, browser, or other application type
- WHEN Word, VS Code, or other applications are active THEN it SHALL auto-switch to appropriate configuration profiles
- WHEN different applications require different settings THEN it SHALL maintain separate optimized configurations for coding vs. document writing
- WHEN custom application profiles are needed THEN it SHALL provide an API for defining application-specific settings

**User preference learning:**
- WHEN I make manual corrections to transcribed text THEN the system SHALL track these patterns and learn from them
- WHEN I manually switch between configuration profiles THEN the system SHALL monitor this behavior and learn my preferences
- WHEN the system identifies user-specific patterns THEN it SHALL build optimization models tailored to my usage
- WHEN learned preferences are developed THEN the system SHALL store them persistently across sessions

**Performance monitoring and adjustment:**
- WHEN the system processes audio THEN it SHALL track real-time latency and maintain performance metrics
- WHEN transcription accuracy can be measured THEN it SHALL collect accuracy metrics and trend analysis
- WHEN text rewrites occur THEN it SHALL analyze rewrite frequency and automatically adjust thresholds
- WHEN performance metrics indicate issues THEN it SHALL automatically adjust thresholds based on measured performance
- WHEN performance degradation is detected THEN it SHALL provide alerts and suggested optimizations