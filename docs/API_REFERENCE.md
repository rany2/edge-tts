# Enhanced Edge-TTS API Reference

## 📚 Table of Contents

- [Core Classes](#core-classes)
- [Convenience Functions](#convenience-functions)
- [Data Classes](#data-classes)
- [Enums](#enums)
- [Examples](#examples)

## 🏗️ Core Classes

### EnhancedCommunicate

The main enhanced TTS class with AI-powered features.

```python
class EnhancedCommunicate:
    def __init__(self, text: str, voice: str = None, **kwargs):
        """
        Initialize enhanced TTS with AI analysis.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (optional, AI will select if None)
            **kwargs: Additional parameters
        """
    
    async def save(self, output_file: str):
        """Save audio to file"""
    
    async def saveMore(self, audio_fname: Union[str, bytes, BytesIO, BinaryIO],
                      metadata_fname: Optional[Union[str, bytes, BytesIO, TextIO]] = None):
        """Save audio and metadata with advanced file handling"""
    
    def get_analysis(self) -> MLAnalysis:
        """Get content analysis results"""
    
    def get_effects(self) -> List[TextEffect]:
        """Get processed text effects"""
    
    def get_voice_parameters(self) -> Dict[str, str]:
        """Get calculated voice parameters"""
```

**Properties:**
- `original_text`: Original input text
- `processed_text`: Text after effect processing
- `voice`: Selected voice name
- `analysis`: Content analysis results
- `effects`: List of detected effects
- `voice_params`: Calculated voice parameters

### ContentAnalyzer

ML-powered content analysis for intelligent voice selection.

```python
class ContentAnalyzer:
    def __init__(self):
        """Initialize content analyzer with ML models"""
    
    def analyze_content(self, text: str) -> MLAnalysis:
        """
        Analyze content and return ML insights.
        
        Returns:
            MLAnalysis: Complete analysis including content type, emotion, sentiment, etc.
        """
    
    def _classify_content_type(self, text: str) -> ContentType:
        """Classify content type using ML"""
    
    def _classify_emotion(self, text: str) -> EmotionType:
        """Classify emotion using ML"""
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment score (-1 to 1)"""
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text"""
    
    def _analyze_complexity(self, text: str) -> float:
        """Analyze text complexity (0 to 1)"""
    
    def _analyze_formality(self, text: str) -> float:
        """Analyze formality level (0 to 1)"""
```

### AdvancedTextProcessor

Advanced text processing with effects and SSML generation.

```python
class AdvancedTextProcessor:
    def __init__(self):
        """Initialize text processor with effect patterns"""
    
    def process_text(self, text: str) -> Tuple[str, List[TextEffect]]:
        """
        Process text and extract effects.
        
        Returns:
            Tuple of processed text and list of effects
        """
    
    def _extract_parameters(self, match, effect_type: str) -> Dict[str, Any]:
        """Extract parameters from effect match"""
    
    def _get_pause_duration(self, pause_type: str) -> str:
        """Get SSML pause duration"""
```

### BatchProcessor

Enterprise-grade batch processing for large-scale TTS operations.

```python
class BatchProcessor:
    def __init__(self, max_concurrent: int = 5):
        """
        Initialize batch processor.
        
        Args:
            max_concurrent: Maximum concurrent tasks
        """
    
    async def process_batch(self, texts: List[str], voices: List[str] = None, 
                           output_prefix: str = "batch") -> List[Dict[str, Any]]:
        """
        Process multiple texts with intelligent voice selection.
        
        Args:
            texts: List of texts to process
            voices: List of voices (optional, AI will select if None)
            output_prefix: Prefix for output files
            
        Returns:
            List of processing results
        """
    
    async def _process_single(self, text: str, voice: str, output_file: str) -> Dict[str, Any]:
        """Process a single text"""
```

### TTSBatchProcessor

Advanced batch processing with database integration and monitoring.

```python
class TTSBatchProcessor:
    def __init__(self, config: BatchConfig):
        """Initialize batch processor with configuration"""
    
    async def add_task(self, task: TTSBatchTask):
        """Add a task to the processing queue"""
    
    async def add_batch_tasks(self, tasks: List[TTSBatchTask]):
        """Add multiple tasks to the processing queue"""
    
    async def start_processing(self):
        """Start the batch processing"""
    
    async def stop_processing(self):
        """Stop the batch processing"""
    
    def get_task_status(self, task_id: str) -> Optional[TTSBatchTask]:
        """Get task status by ID"""
    
    def get_batch_statistics(self) -> Dict[str, Any]:
        """Get batch processing statistics"""
```

## 🚀 Convenience Functions

### speak_intelligently

Simple AI-powered TTS with automatic voice selection.

```python
async def speak_intelligently(text: str, output_file: str = None, voice: str = None) -> Dict[str, Any]:
    """
    Speak text with intelligent voice selection.
    
    Args:
        text: Text to convert to speech
        output_file: Output file path (optional)
        voice: Voice to use (optional, AI will select if None)
        
    Returns:
        Dict containing analysis, voice used, parameters, and effects
    """
```

**Example:**
```python
result = await edge_tts.speak_intelligently("Hello world!", "output.mp3")
print(f"Voice: {result['voice_used']}")
print(f"Content type: {result['analysis'].content_type.value}")
```

### batch_speak

Batch process multiple texts with intelligent voice selection.

```python
async def batch_speak(texts: List[str], voices: List[str] = None, 
                     output_prefix: str = "batch") -> List[Dict[str, Any]]:
    """
    Batch process multiple texts.
    
    Args:
        texts: List of texts to process
        voices: List of voices (optional, AI will select if None)
        output_prefix: Prefix for output files
        
    Returns:
        List of processing results
    """
```

**Example:**
```python
texts = ["Text 1", "Text 2", "Text 3"]
results = await edge_tts.batch_speak(texts, output_prefix="batch")
```

## 📊 Data Classes

### MLAnalysis

Content analysis results from ML models.

```python
@dataclass
class MLAnalysis:
    content_type: ContentType
    emotion: EmotionType
    sentiment_score: float
    language: str
    complexity_score: float
    formality_score: float
    recommended_voice: str
    confidence: float
```

### VoiceProfile

Voice characteristics and suitability scores.

```python
@dataclass
class VoiceProfile:
    voice_name: str
    gender: str
    age_range: str
    language: str
    region: str
    characteristics: Dict[str, float]
    suitability_scores: Dict[str, float]
```

### TextEffect

Individual text effect with parameters and position.

```python
@dataclass
class TextEffect:
    effect_type: str
    parameters: Dict[str, Any]
    start_pos: int
    end_pos: int
```

### TTSBatchTask

Individual task in batch processing.

```python
@dataclass
class TTSBatchTask:
    task_id: str
    text: str
    voice: str
    output_file: str
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
```

### BatchConfig

Configuration for batch processing.

```python
@dataclass
class BatchConfig:
    max_concurrent_tasks: int = 5
    rate_limit_per_minute: int = 100
    retry_delay_seconds: int = 30
    max_retry_attempts: int = 3
    database_path: str = "tts_batch.db"
    output_directory: str = "batch_output"
    enable_progress_tracking: bool = True
    enable_notifications: bool = True
```

## 🎭 Enums

### ContentType

Content type classification.

```python
class ContentType(Enum):
    NEWS = "news"
    STORY = "story"
    TECHNICAL = "technical"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"
    SCIENTIFIC = "scientific"
    CONVERSATIONAL = "conversational"
```

### EmotionType

Emotion classification.

```python
class EmotionType(Enum):
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    ANGRY = "angry"
    SURPRISED = "surprised"
    NEUTRAL = "neutral"
```

### PauseType

Pause types for text processing.

```python
class PauseType(Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    EXTRA_LONG = "extra_long"
```

### TaskPriority

Task priority levels for batch processing.

```python
class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5
```

### TaskStatus

Task status states for batch processing.

```python
class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
```

## 🎯 Examples

### Basic Usage

```python
import edge_tts

# Simple AI-powered TTS
result = await edge_tts.speak_intelligently("Hello world!", "output.mp3")
print(f"Voice: {result['voice_used']}")
print(f"Content type: {result['analysis'].content_type.value}")
```

### Advanced Usage

```python
import edge_tts

# Full control with enhanced features
enhanced = edge_tts.EnhancedCommunicate(
    "Welcome [pause:medium] to our [emotion:excited] show!"
)
await enhanced.save("podcast.mp3")

# Access analysis and effects
analysis = enhanced.get_analysis()
effects = enhanced.get_effects()
params = enhanced.get_voice_parameters()

print(f"Content type: {analysis.content_type.value}")
print(f"Emotion: {analysis.emotion.value}")
print(f"Effects: {len(effects)}")
print(f"Parameters: {params}")
```

### Batch Processing

```python
import edge_tts

# Batch process multiple texts
texts = [
    "Breaking news: Scientists discover new planet!",
    "Once upon a time in a magical forest...",
    "The algorithm uses machine learning techniques."
]

results = await edge_tts.batch_speak(texts, output_prefix="batch")

for i, result in enumerate(results):
    if result['success']:
        print(f"Text {i+1}: {result['voice_used']}")
    else:
        print(f"Text {i+1}: ERROR - {result.get('error')}")
```

### Content Analysis

```python
import edge_tts

# Analyze content without generating audio
analyzer = edge_tts.ContentAnalyzer()
analysis = analyzer.analyze_content("Breaking news: Major breakthrough!")

print(f"Content type: {analysis.content_type.value}")
print(f"Emotion: {analysis.emotion.value}")
print(f"Sentiment: {analysis.sentiment_score}")
print(f"Language: {analysis.language}")
print(f"Complexity: {analysis.complexity_score}")
print(f"Formality: {analysis.formality_score}")
print(f"Recommended voice: {analysis.recommended_voice}")
```

### Text Effects

```python
import edge_tts

# Text with multiple effects
text = """
Welcome to our podcast [pause:medium]!
Today we have [emotion:excited] amazing news [laugh]
that will [emotion:surprised] completely change everything [pause:short]!
"""

enhanced = edge_tts.EnhancedCommunicate(text)
await enhanced.save("podcast.mp3")

# Access effect information
print(f"Original: {enhanced.original_text}")
print(f"Processed: {enhanced.processed_text}")
print(f"Effects: {len(enhanced.effects)}")

for effect in enhanced.effects:
    print(f"- {effect.effect_type}: {effect.parameters}")
```

### Enterprise Batch Processing

```python
import edge_tts

# Configure batch processing
config = edge_tts.BatchConfig(
    max_concurrent_tasks=10,
    rate_limit_per_minute=100,
    output_directory="enterprise_output"
)

processor = edge_tts.TTSBatchProcessor(config)

# Add progress callback
async def progress_callback(task):
    print(f"Progress: {task.task_id} - {task.status.value}")

processor.add_progress_callback(progress_callback)

# Create tasks
tasks = []
for i in range(100):
    task = edge_tts.TTSBatchTask(
        task_id=f"task_{i}",
        text=f"This is task number {i}",
        voice="en-US-AriaNeural",
        output_file=f"task_{i:04d}.mp3"
    )
    tasks.append(task)

# Add tasks and start processing
await processor.add_batch_tasks(tasks)
await processor.start_processing()
```

### Custom Voice Parameters

```python
import edge_tts

# Custom voice parameter calculation
class CustomVoiceCalculator:
    def calculate_parameters(self, analysis):
        if analysis.content_type == edge_tts.ContentType.NEWS:
            return {'rate': '+10%', 'volume': '+5%', 'pitch': '+0Hz'}
        elif analysis.content_type == edge_tts.ContentType.STORY:
            return {'rate': '-5%', 'volume': '+0%', 'pitch': '+10Hz'}
        else:
            return {'rate': '+0%', 'volume': '+0%', 'pitch': '+0Hz'}

# Use custom calculator
calculator = CustomVoiceCalculator()
enhanced = edge_tts.EnhancedCommunicate("Custom text")
enhanced._calculate_voice_parameters = calculator.calculate_parameters
```

### Error Handling

```python
import edge_tts
import logging

async def safe_tts_generation(text: str, output_file: str):
    """Safe TTS generation with error handling"""
    try:
        # Try enhanced TTS first
        result = await edge_tts.speak_intelligently(text, output_file)
        return result
    except Exception as e:
        logging.warning(f"Enhanced TTS failed: {e}")
        
        # Fallback to basic TTS
        try:
            communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
            await communicate.save(output_file)
            return {"voice_used": "en-US-AriaNeural", "fallback": True}
        except Exception as e2:
            logging.error(f"Basic TTS also failed: {e2}")
            raise

# Usage
try:
    result = await safe_tts_generation("Hello world!", "output.mp3")
    print(f"Success: {result['voice_used']}")
except Exception as e:
    print(f"TTS generation failed: {e}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Set cache directory
export EDGE_TTS_CACHE_DIR="/path/to/cache"

# Optional: Set log level
export EDGE_TTS_LOG_LEVEL="INFO"

# Optional: Set ML model cache
export TRANSFORMERS_CACHE="/path/to/transformers"
```

### Logging Configuration

```python
import logging

# Configure logging for enhanced features
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable debug mode for detailed information
logging.getLogger('edge_tts.enhanced').setLevel(logging.DEBUG)
```

## 🚨 Error Handling

### Common Exceptions

```python
try:
    result = await edge_tts.speak_intelligently(text, "output.mp3")
except edge_tts.exceptions.EdgeTTSException as e:
    print(f"Edge-TTS error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Fallback Strategies

```python
async def robust_tts(text: str, output_file: str):
    """Robust TTS with multiple fallback strategies"""
    strategies = [
        # Strategy 1: Enhanced TTS
        lambda: edge_tts.speak_intelligently(text, output_file),
        
        # Strategy 2: Basic TTS with AI voice
        lambda: edge_tts.Communicate(text, "en-US-AriaNeural").save(output_file),
        
        # Strategy 3: Basic TTS with default voice
        lambda: edge_tts.Communicate(text).save(output_file)
    ]
    
    for i, strategy in enumerate(strategies):
        try:
            result = await strategy()
            print(f"Strategy {i+1} succeeded")
            return result
        except Exception as e:
            print(f"Strategy {i+1} failed: {e}")
            continue
    
    raise Exception("All TTS strategies failed")
```

## 📈 Performance Tips

### Memory Management

```python
import gc

async def memory_efficient_batch(texts: list):
    """Memory-efficient batch processing"""
    processor = edge_tts.BatchProcessor(max_concurrent=3)
    
    # Process in chunks
    chunk_size = 10
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        results = await processor.process_batch(chunk, f"chunk_{i//chunk_size}")
        
        # Clean up memory
        gc.collect()
        
        yield results
```

### Caching

```python
import hashlib
import os

class CachedTTS:
    def __init__(self, cache_dir="tts_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    async def speak_with_cache(self, text: str, voice: str = None):
        """TTS with caching for repeated content"""
        cache_key = hashlib.md5(f"{text}_{voice}".encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.mp3")
        
        if os.path.exists(cache_file):
            return cache_file
        
        result = await edge_tts.speak_intelligently(text, cache_file, voice)
        return cache_file
```

## 🎉 Complete Example

```python
import edge_tts
import asyncio

async def main():
    """Complete example demonstrating all features"""
    
    # 1. Simple AI-powered TTS
    print("1. Simple AI-powered TTS")
    result = await edge_tts.speak_intelligently("Hello world!", "simple.mp3")
    print(f"Voice: {result['voice_used']}")
    print(f"Content type: {result['analysis'].content_type.value}")
    
    # 2. Advanced text processing
    print("\n2. Advanced text processing")
    enhanced = edge_tts.EnhancedCommunicate(
        "Welcome [pause:medium] to our [emotion:excited] show!"
    )
    await enhanced.save("advanced.mp3")
    print(f"Effects: {len(enhanced.effects)}")
    
    # 3. Batch processing
    print("\n3. Batch processing")
    texts = ["Text 1", "Text 2", "Text 3"]
    results = await edge_tts.batch_speak(texts, output_prefix="batch")
    print(f"Processed {len(results)} texts")
    
    # 4. Content analysis
    print("\n4. Content analysis")
    analyzer = edge_tts.ContentAnalyzer()
    analysis = analyzer.analyze_content("Breaking news!")
    print(f"Type: {analysis.content_type.value}")
    print(f"Emotion: {analysis.emotion.value}")
    
    print("\nAll examples completed!")

if __name__ == "__main__":
    asyncio.run(main())
```

---

**For more examples and detailed documentation, see:**
- [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) - Complete feature documentation
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference guide
- [examples/](examples/) - Working examples
