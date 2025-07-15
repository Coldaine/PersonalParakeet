# PersonalParakeet Design Document

## Architecture Overview

PersonalParakeet follows a modular, event-driven architecture optimized for real-time speech recognition with minimal latency.

### Core Components

1. **Audio Capture Module**
   - Uses sounddevice for cross-platform audio
   - Non-blocking callback-based capture
   - Ring buffer for audio chunks
   - Automatic device selection

2. **Transcription Engine**
   - Direct NeMo model integration
   - GPU-accelerated inference
   - Batch processing optimization
   - Thread-safe model access

3. **LocalAgreement Buffer**
   - Novel text stabilization algorithm
   - Prevents unwanted rewrites
   - Configurable agreement thresholds
   - Token-based comparison

4. **Output Manager**
   - Keyboard simulation via pynput
   - Application-agnostic output
   - Special character handling
   - Proper spacing and punctuation

5. **Configuration System**
   - YAML-based configuration
   - Runtime hot-reloading
   - Profile management
   - Validation and defaults

## Configuration System Design

### Static Configuration
```yaml
# config.yaml structure
audio:
  sample_rate: 16000
  chunk_duration: 1.0
  channels: 1

model:
  name: "stt_en_fastconformer_transducer_large"
  device: "cuda"
  
local_agreement:
  threshold: 0.8
  max_buffer_size: 100
  
profiles:
  default:
    # Default settings
  coding:
    # Code-optimized settings
  writing:
    # Document-optimized settings
```

### Dynamic Configuration Extension

#### DynamicTuner Class Design
```python
class DynamicTuner:
    """Monitors system performance and adjusts configuration dynamically."""
    
    def __init__(self, config_manager, metrics_store):
        self.config = config_manager
        self.metrics = metrics_store
        self.learning_rate = 0.1
        self.adjustment_interval = 30  # seconds
        
    def monitor_and_adjust(self):
        """Main tuning loop - runs in background thread."""
        # Collect performance metrics
        metrics = self.metrics.get_recent_window()
        
        # Analyze patterns
        adjustments = self.analyze_performance(metrics)
        
        # Apply gradual adjustments
        self.apply_adjustments(adjustments)
        
    def analyze_performance(self, metrics):
        """Determine needed adjustments based on metrics."""
        adjustments = {}
        
        # Rewrite frequency analysis
        if metrics.rewrite_rate > 0.3:  # Too many rewrites
            adjustments['agreement_threshold'] = +0.05
        elif metrics.rewrite_rate < 0.1:  # Too conservative
            adjustments['agreement_threshold'] = -0.05
            
        # Latency analysis
        if metrics.avg_latency > 500:  # Too slow
            adjustments['chunk_duration'] = -0.1
        elif metrics.avg_latency < 200:  # Room for improvement
            adjustments['chunk_duration'] = +0.1
            
        # Speech pattern analysis
        if metrics.pause_variance > threshold:
            adjustments['vad_sensitivity'] = self.calculate_vad_adjustment()
            
        return adjustments
```

#### ApplicationDetector Class Design
```python
class ApplicationDetector:
    """Detects active application and switches profiles automatically."""
    
    def __init__(self, profile_manager):
        self.profiles = profile_manager
        self.app_mappings = {
            'code.exe': 'coding',
            'devenv.exe': 'coding',
            'winword.exe': 'writing',
            'chrome.exe': 'browsing',
            'slack.exe': 'messaging'
        }
        
    def get_active_application(self):
        """Get currently focused application."""
        import win32gui
        import win32process
        
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        # Get process name from PID
        return self.get_process_name(pid)
        
    def auto_switch_profile(self):
        """Switch profile based on active application."""
        app = self.get_active_application()
        
        if app in self.app_mappings:
            profile = self.app_mappings[app]
            self.profiles.switch_to(profile)
            
    def register_custom_mapping(self, app_name, profile):
        """Allow users to define custom app-profile mappings."""
        self.app_mappings[app_name] = profile
        self.save_mappings()
```

#### UserPreferenceTracker Class Design
```python
class UserPreferenceTracker:
    """Learns from user behavior and corrections."""
    
    def __init__(self, storage_path):
        self.storage = storage_path
        self.correction_history = []
        self.profile_switches = []
        self.preference_model = self.load_or_create_model()
        
    def track_correction(self, original, corrected, context):
        """Record when user corrects output."""
        correction = {
            'timestamp': time.time(),
            'original': original,
            'corrected': corrected,
            'context': context,
            'active_profile': self.current_profile,
            'metrics': self.current_metrics
        }
        self.correction_history.append(correction)
        self.update_model(correction)
        
    def track_profile_switch(self, from_profile, to_profile, context):
        """Record manual profile switches."""
        switch = {
            'timestamp': time.time(),
            'from': from_profile,
            'to': to_profile,
            'app': context['active_app'],
            'metrics': context['current_metrics']
        }
        self.profile_switches.append(switch)
        
    def suggest_adjustments(self):
        """Suggest configuration changes based on learned patterns."""
        # Analyze correction patterns
        common_corrections = self.analyze_corrections()
        
        # Analyze profile switching patterns
        profile_patterns = self.analyze_profile_switches()
        
        # Generate suggestions
        suggestions = []
        
        if common_corrections['punctuation_errors'] > threshold:
            suggestions.append({
                'type': 'punctuation_model',
                'action': 'enable_enhanced_punctuation'
            })
            
        if profile_patterns['frequent_manual_switches']:
            suggestions.append({
                'type': 'auto_profile',
                'action': 'update_app_mappings',
                'data': profile_patterns['suggested_mappings']
            })
            
        return suggestions
```

#### PerformanceMonitor Class Design
```python
class PerformanceMonitor:
    """Tracks system performance metrics for optimization."""
    
    def __init__(self, metrics_store):
        self.store = metrics_store
        self.metrics_window = deque(maxlen=1000)
        self.alert_thresholds = {
            'latency': 1000,  # ms
            'accuracy': 0.7,   # minimum accuracy
            'gpu_usage': 90,   # percentage
            'memory': 4096     # MB
        }
        
    def record_transcription(self, audio_timestamp, text_timestamp, text, rewrites):
        """Record metrics for each transcription."""
        metric = {
            'timestamp': time.time(),
            'latency': (text_timestamp - audio_timestamp) * 1000,
            'text_length': len(text),
            'rewrite_count': rewrites,
            'gpu_usage': self.get_gpu_usage(),
            'memory_usage': self.get_memory_usage()
        }
        self.metrics_window.append(metric)
        self.check_alerts(metric)
        
    def get_optimization_suggestions(self):
        """Analyze metrics and suggest optimizations."""
        recent_metrics = list(self.metrics_window)[-100:]
        
        avg_latency = np.mean([m['latency'] for m in recent_metrics])
        rewrite_rate = np.mean([m['rewrite_count'] > 0 for m in recent_metrics])
        
        suggestions = []
        
        if avg_latency > 500:
            suggestions.append({
                'issue': 'high_latency',
                'suggestion': 'reduce_chunk_duration',
                'severity': 'medium'
            })
            
        if rewrite_rate > 0.4:
            suggestions.append({
                'issue': 'excessive_rewrites',
                'suggestion': 'increase_agreement_threshold',
                'severity': 'high'
            })
            
        return suggestions
        
    def export_metrics(self, filepath):
        """Export metrics for analysis."""
        import pandas as pd
        df = pd.DataFrame(list(self.metrics_window))
        df.to_csv(filepath, index=False)
```

### Integration Architecture

```
┌─────────────────────┐
│   Main Dictation    │
│      System         │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  ConfigurationMgr   │◄────┐
│  (Static + Dynamic) │     │
└──────────┬──────────┘     │
           │                │
    ┌──────┴──────┐         │
    │             │         │
┌───▼───┐    ┌───▼───┐     │
│Dynamic│    │ App   │     │
│ Tuner │    │Detect │     │
└───┬───┘    └───┬───┘     │
    │            │         │
    └────────────┴─────────┤
                           │
┌──────────────────────────▼─┐
│   Performance Monitor      │
│   & Preference Tracker     │
└────────────────────────────┘
```

## Data Flow

1. **Audio Input** → Audio Capture → Ring Buffer
2. **Ring Buffer** → Transcription Engine → Raw Text
3. **Raw Text** → LocalAgreement → Stabilized Text
4. **Stabilized Text** → Output Manager → Keyboard Events
5. **All Components** → Performance Monitor → Metrics
6. **Metrics** → Dynamic Tuner → Configuration Updates

## Threading Model

- **Main Thread**: UI and control logic
- **Audio Thread**: Audio capture callback
- **Transcription Thread**: Model inference
- **Output Thread**: Keyboard events
- **Monitor Thread**: Performance tracking
- **Tuner Thread**: Dynamic adjustments

## Error Handling Strategy

1. **Graceful Degradation**
   - Fall back to CPU if GPU fails
   - Use default audio device if preferred fails
   - Disable dynamic tuning if errors occur

2. **Recovery Mechanisms**
   - Automatic reconnection for audio devices
   - Model reloading on corruption
   - Configuration rollback on invalid changes

3. **User Notification**
   - System tray notifications for errors
   - Log file for debugging
   - Performance degradation warnings