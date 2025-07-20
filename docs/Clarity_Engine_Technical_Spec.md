# Clarity Engine Technical Specification

## Purpose
The Clarity Engine is a lightweight, real-time text correction system that fixes common STT errors including homophones, technical jargon, and contextual mistakes. It operates with sub-150ms latency to maintain fluid dictation.

## Model Selection Criteria

### Requirements
- **Size**: < 4GB RAM when loaded
- **Latency**: < 150ms per correction
- **Offline**: Must work without internet
- **Context**: Handle at least 512 tokens
- **Fine-tunable**: Ability to adapt to user vocabulary

### Candidate Models

| Model | Size | Latency (RTX 5090) | Pros | Cons |
|-------|------|-------------------|------|------|
| **Phi-3-mini** | 3.8B params | ~80ms | Microsoft support, good context | Larger size |
| **Gemma-2B** | 2B params | ~50ms | Google quality, very fast | Limited context |
| **Qwen2.5-1.5B** | 1.5B params | ~40ms | Excellent size/performance | Newer, less tested |
| **Custom DistilBERT** | 66M params | ~20ms | Tiny, trainable | Limited capability |

### Recommended: Qwen2.5-1.5B
- Optimal balance of speed and capability
- Specifically trained on text correction tasks
- Excellent performance on RTX 5090

## Architecture Design

```python
class ClarityEngine:
    def __init__(self, model_name="qwen2.5-1.5b"):
        self.model = self._load_model(model_name)
        self.correction_cache = LRUCache(maxsize=1000)
        self.user_dictionary = UserDictionary()
        self.context_buffer = deque(maxlen=5)  # Last 5 utterances
        
    def correct(self, raw_text: str) -> str:
        # Check cache first
        if raw_text in self.correction_cache:
            return self.correction_cache[raw_text]
            
        # Build context
        context = self._build_context()
        
        # Run correction
        corrected = self._run_inference(raw_text, context)
        
        # Apply user dictionary
        corrected = self.user_dictionary.apply(corrected)
        
        # Cache result
        self.correction_cache[raw_text] = corrected
        
        return corrected
```

## Correction Pipeline

### Stage 1: Homophone Resolution
```python
COMMON_HOMOPHONES = {
    "there their they're": lambda context: detect_possessive(context),
    "to too two": lambda context: detect_number_vs_direction(context),
    "your you're": lambda context: detect_contraction(context),
}
```

### Stage 2: Technical Term Correction
```python
TECH_CORRECTIONS = {
    "pie torch": "PyTorch",
    "kuda": "CUDA",
    "jason": "JSON",
    "get hub": "GitHub",
}
```

### Stage 3: Context-Aware Fixes
Using the LLM for intelligent corrections:

```python
PROMPT_TEMPLATE = """
Fix any transcription errors in the following text.
Context: {context}
Raw: {raw_text}
Corrected:"""
```

## Performance Optimization

### 1. Model Quantization
```python
# Use INT8 quantization for 4x speedup
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained("qwen2.5-1.5b")
quantized_model = torch.quantization.quantize_dynamic(
    model, 
    {torch.nn.Linear}, 
    dtype=torch.qint8
)
```

### 2. Batching Strategy
```python
class BatchedClarityEngine:
    def __init__(self, batch_size=4, max_wait_ms=50):
        self.batch_queue = asyncio.Queue()
        self.batch_size = batch_size
        self.max_wait = max_wait_ms / 1000
        
    async def correct_batch(self):
        batch = []
        deadline = time.time() + self.max_wait
        
        while len(batch) < self.batch_size and time.time() < deadline:
            try:
                timeout = deadline - time.time()
                item = await asyncio.wait_for(
                    self.batch_queue.get(), 
                    timeout=timeout
                )
                batch.append(item)
            except asyncio.TimeoutError:
                break
                
        if batch:
            results = self.model.generate(batch)
            # Return results to callers
```

### 3. GPU Memory Management
```python
# Use memory-mapped model loading
model = AutoModel.from_pretrained(
    "qwen2.5-1.5b",
    device_map="auto",
    max_memory={0: "2GB"},  # Limit GPU memory
    offload_folder="./offload"
)
```

## User Dictionary System

### Learning Pipeline
```python
class UserDictionary:
    def __init__(self):
        self.corrections = {}  # user corrections
        self.frequency = Counter()  # term frequency
        self.context_map = {}  # term -> common contexts
        
    def learn_correction(self, original: str, corrected: str, context: str):
        # User manually corrected 'original' to 'corrected'
        self.corrections[original.lower()] = corrected
        self.frequency[corrected] += 1
        
        # Store context for better future predictions
        if corrected not in self.context_map:
            self.context_map[corrected] = []
        self.context_map[corrected].append(context)
        
    def apply(self, text: str) -> str:
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in self.corrections:
                words[i] = self.corrections[word.lower()]
        return " ".join(words)
```

### Persistence
```json
{
    "user_corrections": {
        "kuda": "CUDA",
        "perakit": "Parakeet",
        "workshop": "WorkShop"  
    },
    "learned_patterns": [
        {
            "pattern": "pie torch",
            "replacement": "PyTorch",
            "confidence": 0.95
        }
    ]
}
```

## Integration with Workshop Box

### Real-time Correction Display
```python
class WorkshopBox:
    def display_correction(self, original: str, corrected: str):
        # Show strikethrough for replaced text
        # Pulse animation for new corrections
        # Different color for high-confidence vs low-confidence
        
        if self._is_significant_change(original, corrected):
            self.show_correction_animation(original, corrected)
        else:
            self.update_text_smooth(corrected)
```

### Confidence Scoring
```python
def calculate_correction_confidence(original: str, corrected: str, model_logits):
    # High confidence: Bold display
    # Medium confidence: Normal display  
    # Low confidence: Italic with question mark
    
    if model_logits.max() > 0.9:
        return "high"
    elif model_logits.max() > 0.7:
        return "medium"
    else:
        return "low"
```

## Performance Benchmarks

### Target Metrics (RTX 5090)
- First token latency: < 50ms
- Full correction (20 words): < 150ms
- Memory usage: < 2GB VRAM, < 4GB RAM
- Throughput: > 100 corrections/second

### Fallback Strategy
If Clarity Engine is too slow:
1. Disable for words < 5 characters
2. Cache aggressively (LRU with 10k entries)
3. Use rule-based corrections only
4. Offer "Fast Mode" without LLM

## Future Enhancements

### Phase 1 (MVP)
- Basic homophone correction
- Common technical terms
- Simple caching

### Phase 2 
- User dictionary learning
- Context awareness
- Confidence scoring

### Phase 3
- Domain-specific models (medical, legal, technical)
- Multi-language support
- Voice profile adaptation

This specification ensures the Clarity Engine enhances the dictation experience without introducing perceptible latency.