# PersonalParakeet v3 - System Architecture Flow Diagrams

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "PersonalParakeet v3 Single Process"
        subgraph "Main Thread [Rust EGUI UI]"
            A[Rust EGUI Application Entry] --> B[Window Configuration]
            B --> C[Dictation View UI]
            C --> D[User Controls]
            D --> E[Real-time Updates]
        end
        
        subgraph "Audio Producer Thread"
            F[Audio Engine] --> G[Microphone Callback]
            G --> H[Audio Queue]
            H --> I[VAD Processing]
            I --> J[Voice Activity Detection]
        end
        
        subgraph "STT Consumer Thread"
            K[STT Processor] --> L[Audio Queue]
            L --> M[NeMo Parakeet Model]
            M --> N[Speech Recognition]
            N --> O[Raw Transcription]
        end
        
        subgraph "Processing Components"
            P[Clarity Engine] --> Q[Text Corrections]
            R[Thought Linker] --> S[Context Analysis]
            T[Injection Manager] --> U[Text Injection]
        end
    end
    
    F --> H
    H --> L
    O --> P
    P --> Q
    Q --> R
    R --> S
    S --> T
    T --> U
    U --> E
    
    style A fill:#e1f5fe
    style F fill:#f3e5f5
    style K fill:#e8f5e8
    style P fill:#fff3e0
    style R fill:#fce4ec
    style T fill:#f1f8e9
```

## 2. Audio Processing Pipeline

```mermaid
graph TD
    A[Microphone Input] --> B[Audio Engine Init]
    B --> C[Device Detection]
    C --> D[Stream Configuration]
    D --> E[sounddevice Callback]
    E --> F[Audio Chunk Capture]
    F --> G[Audio Queue Check]
    
    G -->|Queue Not Full| H[Add to Queue]
    G -->|Queue Full| I[Log Warning<br/>Drop Chunk]
    
    H --> J[VAD Engine]
    J --> K[RMS Energy Calculation]
    K --> L[Voice Activity Check]
    
    L -->|Speech Detected| M[Speech Start Event]
    L -->|Silence Detected| N[Silence Timer]
    
    N -->|Pause < Threshold| O[Continue Monitoring]
    N -->|Pause ≥ Threshold| P[Pause Detected Event]
    
    M --> Q[STT Consumer]
    P --> Q
    
    Q --> R[Audio Chunk Retrieval]
    R --> S[STT Processor]
    S --> T[NeMo Model Inference]
    T --> U[Raw Transcription]
    U --> V[Text Output]
    
    style I fill:#ffebee
    style P fill:#fff3e0
    style T fill:#e8f5e8
```

## 3. Text Processing and Correction Flow

```mermaid
graph TD
    A[Raw STT Output] --> B[Clarity Engine]
    B --> C[Rule-Based Corrections]
    
    subgraph "Correction Rules"
        D[Jargon Corrections] --> E[Technical Terms]
        F[Homophone Corrections] --> G[Context-Aware]
        H[Punctuation Handling] --> I[Sentence Structure]
    end
    
    C --> D
    C --> F
    C --> H
    
    E --> J[Apply Corrections]
    G --> J
    I --> J
    
    J --> K[Corrected Text]
    K --> L[Thought Linker]
    
    subgraph "Thought Linking Analysis"
        M[Semantic Similarity] --> N[Text Continuity]
        O[Cursor Movement] --> P[Context Switch]
        Q[Window Change] --> R[Application Focus]
        S[User Actions] --> T[Input Events]
    end
    
    L --> M
    L --> O
    L --> Q
    L --> S
    
    N --> U[Linking Decision]
    P --> U
    R --> U
    T --> U
    
    U --> V[Injection Context]
    V --> W[Injection Manager]
    
    style B fill:#e3f2fd
    style L fill:#f3e5f5
    style W fill:#e8f5e8
```

## 4. Text Injection Workflow

```mermaid
graph TD
    A[Corrected Text] --> B[Injection Manager]
    B --> C[Application Detection]
    
    C --> D[Active Application Analysis]
    D --> E[Application Type Classification]
    
    E --> F{Application Type}
    
    F -->|Modern GUI App| G[UI Automation Strategy]
    F -->|Legacy App| H[Keyboard Strategy]
    F -->|Web Browser| I[Clipboard Strategy]
    F -->|Terminal/Console| J[Direct Input Strategy]
    
    G --> K[Element Identification]
    H --> L[Key Sequence Generation]
    I --> M[Copy-Paste Operations]
    J --> N[Terminal Commands]
    
    K --> O[Injection Attempt]
    L --> O
    M --> O
    N --> O
    
    O --> P{Success?}
    
    P -->|Yes| Q[Performance Metrics]
    P -->|No| R[Fallback Strategy]
    
    Q --> S[Update Success Rate]
    R --> T[Try Alternative Method]
    
    T --> O
    
    S --> U[Text Injected]
    U --> V[User Continues Dictation]
    
    style O fill:#fff3e0
    style P fill:#fce4ec
    style Q fill:#e8f5e8
```

## 5. Component Interaction and Data Flow

```mermaid
graph LR
    subgraph "UI Layer"
        A[Rust EGUI Main Thread] --> B[Dictation View]
        B --> C[Status Indicators]
        B --> D[Control Buttons]
        B --> E[Text Display]
    end
    
    subgraph "Audio Layer"
        F[Audio Engine] --> G[Microphone]
        G --> H[Audio Stream]
        H --> I[Audio Buffer]
    end
    
    subgraph "Processing Layer"
        J[STT Processor] --> K[NeMo Model]
        K --> L[Inference Engine]
        L --> M[Transcription Output]
        
        N[Clarity Engine] --> O[Correction Rules]
        O --> P[Text Processing]
        
        Q[VAD Engine] --> R[Voice Detection]
        R --> S[Activity States]
    end
    
    subgraph "Injection Layer"
        T[Injection Manager] --> U[Strategy Selection]
        U --> V[Injection Execution]
        V --> W[Target Application]
    end
    
    subgraph "Configuration Layer"
        X[Config Manager] --> Y[Profile Settings]
        Y --> Z[Runtime Parameters]
    end
    
    I --> F
    F --> J
    M --> N
    P --> Q
    S --> F
    P --> T
    Z --> F
    Z --> J
    Z --> N
    Z --> Q
    Z --> T
    
    M --> E
    P --> E
    V --> W
    
    style A fill:#e1f5fe
    style F fill:#f3e5f5
    style J fill:#e8f5e8
    style N fill:#fff3e0
    style T fill:#f1f8e9
    style X fill:#fce4ec
```

## 6. Error Handling and Recovery Flow

```mermaid
graph TD
    A[System Start] --> B[Component Initialization]
    B --> C{All Components OK?}
    
    C -->|Yes| D[Normal Operation]
    C -->|No| E[Error Recovery]
    
    D --> F[Audio Processing]
    F --> G[STT Inference]
    G --> H[Text Correction]
    H --> I[Text Injection]
    
    I --> J{Injection Success?}
    J -->|Yes| K[Continue Operation]
    J -->|No| L[Retry Logic]
    
    L --> M{Max Retries?}
    M -->|No| N[Try Alternative Strategy]
    M -->|Yes| O[Log Error]
    
    N --> I
    O --> P[User Notification]
    
    subgraph "Error Recovery Paths"
        E --> Q[STT Model Error]
        E --> R[Audio Device Error]
        E --> S[Injection Strategy Error]
        E --> T[Memory Error]
    end
    
    Q --> U[Fallback to Mock STT]
    R --> V[Reinitialize Audio Device]
    S --> W[Switch Injection Strategy]
    T --> X[Clear GPU Memory]
    
    U --> D
    V --> D
    W --> D
    X --> D
    
    style C fill:#ffebee
    style J fill:#fff3e0
    style M fill:#ffebee
    style E fill:#fce4ec
    style P fill:#fff8e1
```

## 7. Configuration and Profile Management

```mermaid
graph TD
    A[Application Start] --> B[Load Configuration]
    B --> C[Default Profile]
    
    C --> D[Profile Manager]
    D --> E[Available Profiles]
    
    E --> F{Profile Selection}
    
    F -->|Fast Conversation| G[Low Latency Settings]
    F -->|Balanced| H[Default Settings]
    F -->|Accurate Document| I[High Accuracy Settings]
    F -->|Low Latency| J[Minimal Delay Settings]
    
    G --> K[Apply Configuration]
    H --> K
    I --> K
    J --> K
    
    K --> L[Update Component Settings]
    
    subgraph "Component Configuration"
        M[Audio Engine] --> N[Sample Rate/Buffer]
        O[STT Processor] --> P[Model/Device]
        Q[VAD Engine] --> R[Thresholds]
        S[Clarity Engine] --> T[Correction Rules]
        U[Injection Manager] --> V[Strategies]
    end
    
    L --> M
    L --> O
    L --> Q
    L --> S
    L --> U
    
    M --> X[System Ready]
    O --> X
    Q --> X
    S --> X
    U --> X
    
    X --> Y[Runtime Profile Switching]
    
    Y --> Z[User Request]
    Z --> AA[Validate New Profile]
    AA --> BB{Profile Valid?}
    BB -->|Yes| CC[Apply Changes]
    BB -->|No| DD[Show Error]
    
    CC --> EE[Update Components]
    EE --> FF[Confirm Switch]
    
    style F fill:#e3f2fd
    style BB fill:#fff3e0
    style Y fill:#f3e5f5
```

## 8. Memory and Resource Management

```mermaid
graph TD
    A[System Resources] --> B[Memory Allocation]
    B --> C[GPU Memory]
    B --> D[CPU Memory]
    B --> E[Audio Buffers]
    
    C --> F[NeMo Model Loading]
    F --> G[Model Weights]
    G --> H[Inference Cache]
    
    D --> I[Audio Processing]
    I --> J[Audio Queue]
    J --> K[Chunk Storage]
    
    E --> L[VAD Processing]
    L --> M[Feature Extraction]
    M --> N[Real-time Analysis]
    
    subgraph "Resource Monitoring"
        O[GPU Usage] --> P[CUDA Memory Tracking]
        Q[CPU Usage] --> R[Thread Management]
        S[Memory Usage] --> T[Buffer Management]
        U[Audio Latency] --> V[Performance Metrics]
    end
    
    P --> W{Resource Alert?}
    R --> W
    T --> W
    V --> W
    
    W -->|Normal| X[Continue Operation]
    W -->|High| Y[Optimization Actions]
    
    Y --> Z[Clear GPU Cache]
    Y --> AA[Reduce Audio Buffer]
    Y --> BB[Throttle Processing]
    
    Z --> X
    AA --> X
    BB --> X
    
    style F fill:#e8f5e8
    style J fill:#fff3e0
    style W fill:#fce4ec
    style Y fill:#ffebee
```

## 9. Thread Synchronization and Communication

```mermaid
graph TD
    subgraph "Main Thread [Rust EGUI UI]"
        A[Event Loop] --> B[UI Updates]
        B --> C[User Input Handling]
        C --> D[Window Management]
    end
    
    subgraph "Audio Thread"
        E[Audio Callback] --> F[Queue Producer]
        F --> G[Audio Queue]
        G --> H[Thread-Safe Put]
    end
    
    subgraph "STT Thread"
        I[Consumer Loop] --> J[Queue Consumer]
        J --> K[Thread-Safe Get]
        K --> L[STT Processing]
        L --> M[Transcription Result]
    end
    
    subgraph "Communication Mechanisms"
        N[asyncio.run_coroutine_threadsafe] --> O[UI Update Request]
        P[Callback Registration] --> Q[Event Notification]
        R[Shared State] --> S[Configuration Updates]
    end
    
    M --> O
    O --> B
    H --> G
    K --> G
    
    Q --> E
    Q --> I
    S --> F
    S --> J
    
    style G fill:#e1f5fe
    style O fill:#f3e5f5
    style N fill:#e8f5e8
    style R fill:#fff3e0
```

## 10. Deployment and Installation Flow

```mermaid
graph TD
    A[User Download] --> B[Environment Check]
    B --> C[Python Version Check]
    C --> D[Python 3.11+?]
    
    D -->|No| E[Show Error]
    D -->|Yes| F[GPU Detection]
    
    F --> G[CUDA Available?]
    G -->|Yes| H[GPU Mode Setup]
    G -->|No| I[CPU Mode Setup]
    
    H --> J[Install ML Dependencies]
    I --> J
    
    J --> K[Create Conda Environment]
    K --> L[Install Poetry Dependencies]
    L --> M[Download Models]
    M --> N[Configuration Setup]
    N --> O[Desktop Shortcut]
    O --> P[Application Ready]
    
    subgraph "Dependency Installation"
        Q[NeMo Toolkit] --> R[PyTorch]
        R --> S[Torch Audio]
        S --> T[Sound Libraries]
        T --> U[Rust EGUI Framework]
    end
    
    subgraph "Model Downloads"
        V[Parakeet Model] --> W[Model Weights]
        X[VAD Models] --> Y[Silero Model]
        Z[Configuration Files] --> AA[Default Profiles]
    end
    
    J --> Q
    J --> X
    N --> Z
    
    style E fill:#ffebee
    style H fill:#e8f5e8
    style I fill:#fff3e0
    style P fill:#e1f5fe
```

These diagrams provide a comprehensive view of the PersonalParakeet v3 system architecture, showing data flow, component interactions, error handling, and deployment processes. Each diagram uses color coding to distinguish different types of components and processes.
