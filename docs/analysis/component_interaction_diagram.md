# PersonalParakeet v3 - Component Interaction Analysis

## Component Relationship Matrix

| Component | Depends On | Communicates With | Data Flow | Event Flow |
|-----------|------------|-------------------|-----------|------------|
| **Main Application** | Flet, Config | All Components | Configuration, Events | Lifecycle Events |
| **Audio Engine** | Config, VAD Engine | STT Processor, UI | Audio Data, Status | Audio Events, Status Updates |
| **STT Processor** | Audio Engine, NeMo | Clarity Engine, UI | Transcription Text | Processing Events |
| **Clarity Engine** | STT Processor | Thought Linker, UI | Corrected Text | Correction Events |
| **VAD Engine** | Audio Engine | Audio Engine | Audio Frames | Voice Activity Events |
| **Injection Manager** | Clarity Engine, Config | Target Applications | Corrected Text | Injection Events |
| **Thought Linker** | Clarity Engine, Detectors | Injection Manager, UI | Context Decisions | Context Events |
| **UI Framework** | All Components | User | Display Data | User Events |
| **Configuration** | All Components | All Components | Settings | Configuration Events |

---

## Detailed Component Interactions

### 1. Main Application Component

```mermaid
graph TB
    subgraph "Main Application [main.py]"
        A[PersonalParakeetV3] --> B[Initialize Components]
        B --> C[Configure Window]
        C --> D[Start Audio Engine]
        D --> E[Initialize UI]
        E --> F[Start Event Loop]
        
        F --> G[Handle Window Events]
        G --> H[Handle User Input]
        H --> I[Manage Component Lifecycle]
        I --> J[Emergency Cleanup]
    end
    
    subgraph "Dependencies"
        K[Flet Framework] --> A
        L[V3Config] --> A
        M[Logging System] --> A
    end
    
    subgraph "Interactions"
        A --> N[Audio Engine]
        A --> O[UI Framework]
        A --> P[Configuration]
        A --> Q[Injection Manager]
        A --> R[Thought Linker]
    end
    
    style A fill:#e1f5fe
    style K fill:#f3e5f5
    style L fill:#e8f5e8
```

**Key Interactions**:
- **Initialization**: Sequential component startup with dependency validation
- **Event Handling**: Centralized event routing and user input processing
- **Lifecycle Management**: Component startup, shutdown, and error recovery
- **Configuration**: Central configuration management and distribution

### 2. Audio Engine Component

```mermaid
graph TD
    subgraph "Audio Engine [audio_engine.py]"
        A[AudioEngine] --> B[Initialize STT Processor]
        A --> C[Initialize Clarity Engine]
        A --> D[Initialize VAD Engine]
        
        D --> E[Audio Callback]
        E --> F[Audio Queue]
        F --> G[STT Processing]
        G --> H[Text Correction]
        H --> I[UI Updates]
    end
    
    subgraph "Dependencies"
        J[V3Config] --> A
        K[STT Processor] --> A
        L[Clarity Engine] --> A
        M[VAD Engine] --> A
        N[sounddevice] --> A
    end
    
    subgraph "Interactions"
        A --> O[Microphone Device]
        A --> P[UI Framework]
        A --> Q[STT Processor]
        A --> R[VAD Engine]
        A --> S[Clarity Engine]
    end
    
    style A fill:#e3f2fd
    style J fill:#f3e5f5
    style K fill:#e8f5e8
```

**Key Interactions**:
- **Audio Capture**: Real-time microphone input with device management
- **Queue Management**: Thread-safe audio chunk queuing and retrieval
- **VAD Processing**: Voice activity detection with pause detection
- **STT Integration**: Asynchronous speech-to-text processing
- **UI Communication**: Real-time transcription updates via callbacks

### 3. STT Processor Component

```mermaid
graph TD
    subgraph "STT Processor [stt_processor.py]"
        A[STTProcessor] --> B[Initialize NeMo Model]
        B --> C[Load Model Weights]
        C --> D[Configure Device]
        D --> E[Transcribe Audio]
        E --> F[Return Text]
    end
    
    subgraph "Dependencies"
        G[V3Config] --> A
        H[NeMo Toolkit] --> A
        I[PyTorch] --> A
        J[CUDA] --> A
    end
    
    subgraph "Interactions"
        A --> K[Audio Engine]
        A --> L[Clarity Engine]
        A --> M[Configuration]
        A --> N[GPU Memory]
    end
    
    style A fill:#e8f5e8
    style G fill:#f3e5f5
    style H fill:#fff3e0
```

**Key Interactions**:
- **Model Loading**: Dynamic model loading from local or remote sources
- **Device Management**: GPU/CPU device selection and optimization
- **Audio Processing**: Synchronous transcription with memory management
- **Error Handling**: CUDA OOM errors and model loading failures
- **Performance**: Float16 optimization for GPU memory efficiency

### 4. Clarity Engine Component

```mermaid
graph TD
    subgraph "Clarity Engine [clarity_engine.py]"
        A[ClarityEngine] --> B[Initialize Correction Rules]
        B --> C[Start Worker Thread]
        C --> D[Process Text Corrections]
        D --> E[Apply Context-Aware Rules]
        E --> F[Return Corrected Text]
    end
    
    subgraph "Dependencies"
        G[V3Config] --> A
        H[Correction Rules] --> A
        I[Context Buffer] --> A
    end
    
    subgraph "Interactions"
        A --> J[STT Processor]
        A --> K[Thought Linker]
        A --> L[UI Framework]
        A --> M[Configuration]
    end
    
    style A fill:#fff3e0
    style G fill:#f3e5f5
    style H fill:#fce4ec
```

**Key Interactions**:
- **Rule Processing**: Jargon and homophone correction with context awareness
- **Async Processing**: Non-blocking corrections with worker thread
- **Context Management**: Maintaining conversation context for better corrections
- **Performance**: Target <50ms processing time for real-time feedback
- **Callback System**: Event-driven correction results

### 5. VAD Engine Component

```mermaid
graph TD
    subgraph "VAD Engine [vad_engine.py]"
        A[VAD Engine] --> B[Initialize Parameters]
        B --> C[Process Audio Frame]
        C --> D[Calculate RMS Energy]
        D --> E[Detect Voice Activity]
        E --> F[Generate Events]
    end
    
    subgraph "Dependencies"
        G[Audio Parameters] --> A
        H[Threshold Settings] --> A
    end
    
    subgraph "Interactions"
        A --> I[Audio Engine]
        A --> J[UI Framework]
        A --> K[Configuration]
    end
    
    style A fill:#f3e5f5
    style G fill:#e1f5fe
    style H fill:#e8f5e8
```

**Key Interactions**:
- **Frame Processing**: Real-time audio frame analysis
- **Event Generation**: Voice start/end and pause detection events
- **Callback System**: Event-driven notifications to other components
- **Parameter Configuration**: Dynamic threshold adjustment
- **State Management**: Maintaining voice activity state

### 6. Injection Manager Component

```mermaid
graph TD
    subgraph "Injection Manager [injection_manager_enhanced.py]"
        A[EnhancedInjectionManager] --> B[Initialize Strategies]
        B --> C[Detect Application Type]
        C --> D[Select Injection Strategy]
        D --> E[Execute Injection]
        E --> F[Track Performance]
        F --> G[Handle Failures]
    end
    
    subgraph "Dependencies"
        H[V3Config] --> A
        I[Application Detector] --> A
        J[UI Automation Tools] --> A
        K[Keyboard Tools] --> A
    end
    
    subgraph "Interactions"
        A --> L[Clarity Engine]
        A --> M[Target Applications]
        A --> N[UI Framework]
        A --> O[Configuration]
        A --> P[Performance Monitor]
    end
    
    style A fill:#f1f8e9
    style H fill:#f3e5f5
    style I fill:#e8f5e8
```

**Key Interactions**:
- **Strategy Selection**: Dynamic strategy selection based on application type
- **Performance Tracking**: Success rate and latency monitoring
- **Fallback Mechanisms**: Automatic strategy switching on failure
- **Application Detection**: Real-time application identification
- **Error Recovery**: Comprehensive error handling and retry logic

### 7. Thought Linker Component

```mermaid
graph TD
    subgraph "Thought Linker [thought_linker.py]"
        A[ThoughtLinker] --> B[Initialize Detectors]
        B --> C[Analyze Context]
        C --> D[Collect Signals]
        D --> E[Make Decision]
        E --> F[Generate Output]
    end
    
    subgraph "Dependencies"
        G[V3Config] --> A
        H[Window Detector] --> A
        I[Cursor Detector] --> A
        J[Similarity Engine] --> A
    end
    
    subgraph "Interactions"
        A --> K[Clarity Engine]
        A --> L[Injection Manager]
        A --> M[UI Framework]
        A --> N[User Input]
    end
    
    style A fill:#fce4ec
    style G fill:#f3e5f5
    style H fill:#e8f5e8
```

**Key Interactions**:
- **Context Analysis**: Multi-signal context analysis for intelligent linking
- **Signal Collection**: Window changes, cursor movement, user actions
- **Decision Making**: Sophisticated algorithm for thought linking decisions
- **Event Generation**: Context-aware linking decisions
- **Configuration**: Dynamic parameter adjustment

### 8. UI Framework Component

```mermaid
graph TD
    subgraph "UI Framework [dictation_view.py]"
        A[DictationView] --> B[Build UI Components]
        B --> C[Handle User Input]
        C --> D[Update Display]
        D --> E[Manage Window State]
        E --> F[Provide Feedback]
    end
    
    subgraph "Dependencies"
        G[Flet Framework] --> A
        H[Configuration] --> A
        I[Assets] --> A
    end
    
    subgraph "Interactions"
        A --> J[Audio Engine]
        A --> K[STT Processor]
        A --> L[Clarity Engine]
        A --> M[Injection Manager]
        A --> N[Thought Linker]
        A --> O[User]
    end
    
    style A fill:#e1f5fe
    style G fill:#f3e5f5
    style H fill:#e8f5e8
```

**Key Interactions**:
- **Real-time Updates**: Live transcription and correction display
- **User Input**: Mouse, keyboard, and voice command handling
- **Window Management**: Floating window positioning and transparency
- **Status Display**: System status and performance indicators
- **User Feedback**: Visual and audio feedback for system events

---

## Communication Patterns

### 1. Synchronous Communication
- **Configuration Loading**: Main → Components (sync)
- **Audio Processing**: Audio Engine → STT Processor (sync in thread)
- **Text Correction**: Clarity Engine → Rules (sync)

### 2. Asynchronous Communication
- **UI Updates**: All Components → UI (async via callbacks)
- **Audio Events**: Audio Engine → UI (async events)
- **Injection Events**: Injection Manager → UI (async callbacks)

### 3. Event-Driven Communication
- **Voice Activity**: VAD Engine → All Components (events)
- **User Actions**: UI → Components (events)
- **System Events**: Main → Components (lifecycle events)

### 4. Queue-Based Communication
- **Audio Data**: Audio Engine → STT Processor (queue.Queue)
- **Correction Requests**: UI → Clarity Engine (queue.Queue)

---

## Data Flow Analysis

### 1. Audio Data Flow
```
Microphone → Audio Engine → Audio Queue → STT Processor → 
Raw Transcription → Clarity Engine → Corrected Text → 
Thought Linker → Injection Manager → Target Application
```

### 2. Configuration Data Flow
```
Config File → Configuration Manager → All Components → 
Runtime Updates → Configuration Manager → Component Updates
```

### 3. Event Data Flow
```
User Input → UI Framework → Event Handler → 
Component Notification → Component Processing → 
UI Update → User Feedback
```

### 4. Error Data Flow
```
Component Error → Error Handler → Logging System → 
User Notification → Recovery Attempt → Status Update
```

---

## Performance Considerations

### 1. Latency Targets
- **Audio Capture**: <10ms
- **VAD Processing**: <5ms
- **STT Processing**: <150ms
- **Text Correction**: <50ms
- **Injection**: <100ms
- **UI Updates**: <16ms (60 FPS)

### 2. Throughput Requirements
- **Audio Chunks**: 100ms chunks (10 chunks/second)
- **Queue Capacity**: 50 chunks (5 seconds buffer)
- **Concurrent Processing**: Multiple threads for parallel operations

### 3. Memory Usage
- **STT Model**: 2-4GB GPU memory
- **Audio Buffers**: ~100MB
- **Context Storage**: ~10MB
- **UI Components**: ~50MB

---

## Error Handling Patterns

### 1. Component-Level Error Handling
- **Graceful Degradation**: Continue with reduced functionality
- **Error Recovery**: Automatic retry and fallback mechanisms
- **User Notification**: Clear error messages and status updates

### 2. System-Level Error Handling
- **Emergency Cleanup**: Resource cleanup on critical failures
- **State Recovery**: Restore stable state after errors
- **Logging**: Comprehensive error logging for debugging

### 3. User-Level Error Handling
- **Friendly Messages**: Technical error descriptions for users
- **Recovery Suggestions**: Actionable steps to resolve issues
- **Fallback Options**: Alternative methods when primary methods fail

---

## Scalability Considerations

### 1. Component Independence
- **Loose Coupling**: Components communicate through well-defined interfaces
- **State Management**: Each component manages its own state
- **Dependency Injection**: Easy to swap implementations

### 2. Resource Management
- **Memory Management**: Proper cleanup and garbage collection
- **Thread Management**: Optimal thread pool configuration
- **Connection Pooling**: Efficient resource reuse

### 3. Performance Optimization
- **Caching**: Intelligent caching for expensive operations
- **Lazy Loading**: Load resources only when needed
- **Parallel Processing**: Multi-threading for CPU-intensive tasks

This component interaction analysis provides a comprehensive view of how PersonalParakeet v3 components work together, their dependencies, communication patterns, and performance characteristics.