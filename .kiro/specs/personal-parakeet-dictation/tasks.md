# Implementation Plan

## Overview
PersonalParakeet has a **PROVEN WORKING CORE SYSTEM** ✅. The main components (audio capture, Parakeet transcription, LocalAgreement buffering, F4 hotkey) are functional. This implementation plan focuses on fixing the remaining issues and enhancing the working system.

## Current Status Summary
- ✅ **Audio capture working** - Windows sounddevice integration functional
- ✅ **Parakeet transcription working** - NVIDIA model processing speech in real-time  
- ✅ **LocalAgreement buffering working** - Text stabilization preventing rewrites
- ✅ **F4 hotkey working** - Toggle functionality operational
- ❌ **Text output needs fixing** - Callback errors preventing actual text injection

## Priority Tasks (Fix Current Issues)

- [x] 1. Clean up workspace and consolidate working code






  - Remove experimental and duplicate files (dictation_minimal.py, test_*.py, etc.)
  - Keep only essential working files (dictation_simple_fixed.py, ESSENTIAL_LocalAgreement_Code.py)
  - Archive or delete package_complete_documents folder (outdated documentation)

  - Clean up any other loose files not needed for current implementation
  - _Note: All files are preserved in git history if needed later_

- [ ] 2. Fix text output callback system




  - Debug keyboard.write() callback errors in SimpleDictation.output_text()
  - Ensure proper threading for text injection (main thread vs processing thread)
  - Test text output in multiple applications (Notepad, browser, VS Code)
  - _Requirements: 4.1, 4.6_
  - _Files: dictation_simple_fixed.py line 45-48_

- [ ] 2. Enhance error handling and robustness
  - Add proper exception handling for audio callback errors
  - Implement graceful degradation when text injection fails
  - Add fallback text display when keyboard output doesn't work
  - _Requirements: 12.1, 12.4, 12.5_
  - _Files: dictation_simple_fixed.py process_audio_loop()_


- [ ] 3. Polish the working system

  - Add device selection capability to SimpleDictation
  - Implement proper cleanup on shutdown (Ctrl+C handling)
  - Add configuration options for agreement threshold and chunk duration
  - _Requirements: 1.4, 9.1, 3.6_

## Enhancement Tasks (Build on Working System)

- [ ] 4. Implement intelligent text injection strategies
  - [ ] 4.1 Create application detection system
    - Detect active window and process name
    - Classify applications (EDITOR, BROWSER, TERMINAL, UNKNOWN)
    - Implement application-specific injection strategies
    - _Requirements: 4.2, 4.3, 4.4_

  - [ ] 4.2 Add injection strategy selection
    - Use clipboard paste for code editors (faster)
    - Use keyboard typing for browsers (more compatible)
    - Implement fallback overlay for unknown applications
    - _Requirements: 4.5, 4.7_

- [ ] 5. Add advanced Voice Activity Detection
  - [ ] 5.1 Create dual VAD system (Silero + WebRTC)
    - Implement SileroVAD integration for neural speech detection
    - Add WebRTCVAD for traditional energy-based detection
    - Create VADResult data structure with confidence scores
    - _Requirements: 7.1, 7.8_

  - [ ] 5.2 Implement VAD configuration and adaptation
    - Add configurable sensitivity thresholds (0.1-0.9 range)
    - Implement automatic noise floor adaptation
    - Create pre-roll and post-roll buffer configuration (0.5s/1.0s defaults)
    - _Requirements: 7.2, 7.3, 7.5, 7.6_

  - [ ] 5.3 Integrate VAD with audio processing pipeline
    - Add speech boundary detection for utterance processing
    - Implement low-power monitoring mode for silence periods
    - Create streaming chunk processing for long utterances (>15 seconds)
    - _Requirements: 7.4, 7.7, 7.9_

- [ ] 6. Implement dual GPU optimization
  - [ ] 6.1 Create GPU detection and allocation system
    - Detect available NVIDIA GPUs with memory information
    - Implement RTX 5090 + RTX 3090 allocation strategy
    - Add GPU memory monitoring and pressure handling
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ] 6.2 Add GPU resource management
    - Allocate Parakeet to primary GPU (RTX 5090)
    - Reserve secondary GPU for future LLM processing
    - Implement automatic fallback for single GPU systems
    - _Requirements: 6.4, 6.5, 6.6_

- [ ] 7. Add status display and user interface
  - [ ] 7.1 Create transparent overlay widget
    - Display dictation status (listening, processing, idle)
    - Show committed vs pending text with visual distinction
    - Add error messages and system notifications
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [ ] 7.2 Implement system tray integration
    - Add system tray icon with status indication
    - Create context menu for basic controls
    - Provide alternative to overlay for minimal UI preference
    - _Requirements: 10.7_

- [ ] 8. Add configuration and customization system
  - [ ] 8.1 Implement TOML configuration loading
    - Create configuration file structure with sensible defaults
    - Add audio device, model, and agreement threshold settings
    - Implement configuration validation and error reporting
    - _Requirements: 9.1, 9.2, 9.7_

  - [ ] 8.2 Add hotkey and device configuration
    - Allow custom hotkey bindings (alternative to F4)
    - Add audio device selection by name pattern
    - Implement VAD sensitivity and timing configuration
    - _Requirements: 9.4, 9.5_

- [ ] 9. Create comprehensive testing suite
  - [ ] 9.1 Add unit tests for LocalAgreement system
    - Test agreement tracking with various transcription patterns
    - Verify timeout handling and edge cases
    - Test performance with long transcription sessions
    - _Requirements: 13.1_
    - _Files: Test ESSENTIAL_LocalAgreement_Code.py_

  - [ ] 9.2 Create integration tests for audio pipeline
    - Test end-to-end audio capture → transcription → output flow
    - Verify error recovery mechanisms
    - Test performance under various load conditions
    - _Requirements: 13.2, 13.3_

  - [ ] 9.3 Add compatibility testing
    - Test across different Windows versions and hardware
    - Verify functionality with various audio devices
    - Test application compatibility for text injection
    - _Requirements: 13.5_

## Future Enhancement Tasks (Post-MVP)

- [ ] 13. Implement LLM integration system
  - [ ] 13.1 Create LLM provider abstraction
    - Implement Ollama integration for local LLM processing
    - Add OpenAI and Google Gemini provider support
    - Create LLM configuration and API key management
    - _Requirements: 8.2, 8.3_

  - [ ] 13.2 Implement F5 LLM refinement feature
    - Create text refinement pipeline with context awareness
    - Add streaming response handling with real-time feedback
    - Implement graceful fallback when LLM processing fails
    - _Requirements: 8.1, 8.4, 8.5_

  - [ ] 13.3 Add context-aware enhancement (F1+F4)
    - Implement application context detection for enhancement
    - Create surrounding text context extraction
    - Add application-specific enhancement prompts
    - _Requirements: 8.6, 5.3_

- [ ] 14. Advanced features and polish
  - [ ] 14.1 Implement multi-language support
    - Add language detection and model switching
    - Create language-specific configuration profiles
    - Implement Unicode text handling for international characters

  - [ ] 14.2 Create advanced UI features
    - Add customizable overlay positioning and transparency
    - Implement keyboard shortcuts for advanced functions
    - Create settings UI for configuration management

  - [ ] 14.3 Add productivity enhancements
    - Implement text templates and macros
    - Create dictation history and replay functionality
    - Add integration with popular productivity applications

## Implementation Notes

### Development Environment Setup
```bash
# Python 3.11 virtual environment
uv venv --python 3.11 .venv
.venv\Scripts\activate

# Core dependencies
pip install nemo-toolkit[asr] sounddevice numpy keyboard

# Testing dependencies  
pip install pytest pytest-asyncio pytest-mock

# Development dependencies
pip install black isort mypy
```

### Testing Strategy
- Unit tests should cover individual component functionality
- Integration tests should use real hardware when possible
- Performance tests should measure against target latencies (150-700ms)
- Error scenario tests should validate all recovery mechanisms

### Code Quality Standards
- Type hints required for all public interfaces
- Docstrings required for all classes and public methods
- Error handling required for all external dependencies
- Logging required for all significant operations

### Performance Targets
- End-to-end latency: 150-700ms (audio capture to text injection)
- Memory usage: <4GB total system footprint
- GPU utilization: 70-90% efficient utilization
- Hotkey response: <50ms for F4 toggle

This implementation plan prioritizes the proven working components first, then builds out the advanced features systematically. Each task is designed to be executable by a coding agent with clear objectives and requirements traceability.