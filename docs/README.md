# Enhanced Edge-TTS Documentation

Welcome to the Enhanced Edge-TTS documentation! This directory contains comprehensive documentation for the advanced AI-powered TTS features.

## 📚 Documentation Structure

### 🚀 Getting Started
- **[ENHANCED_FEATURES.md](ENHANCED_FEATURES.md)** - Complete feature documentation with examples
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference guide for developers
- **[API_REFERENCE.md](API_REFERENCE.md)** - Detailed API documentation

### 📖 What's Included

#### 🧠 AI-Powered Features
- **Content Analysis**: Automatic content type detection (News, Story, Technical, etc.)
- **Emotion Detection**: AI-powered emotion recognition (Happy, Sad, Excited, etc.)
- **Sentiment Analysis**: Positive/Negative sentiment scoring
- **Language Detection**: Automatic language identification
- **Voice Recommendation**: AI selects optimal voice based on content

#### 🎭 Advanced Text Processing
- **Pause Effects**: `[pause:short]`, `[pause:medium]`, `[pause:long]`, `[pause:extra_long]`
- **Emotion Effects**: `[emotion:happy]`, `[emotion:sad]`, `[emotion:excited]`, etc.
- **Sound Effects**: `[laugh]`, `[sigh]`, `[whisper]`, `[shout]`
- **Voice Parameters**: `[speed:+50%]`, `[pitch:+100Hz]`, `[volume:+20%]`

#### 📊 Enterprise Features
- **Batch Processing**: Handle thousands of TTS tasks
- **Concurrent Processing**: Multiple tasks simultaneously
- **Database Integration**: SQLite for task tracking
- **Progress Monitoring**: Real-time status updates
- **Error Handling**: Automatic retry and recovery

#### ⚡ Real-time Features
- **WebRTC Integration**: Live audio streaming
- **Real-time TTS**: Generate audio for live applications
- **Audio Streaming**: Stream audio data directly

## 🎯 Quick Start

### Installation
```bash
pip install edge-tts

# Optional: For full ML capabilities
pip install scikit-learn pandas numpy transformers torch
```

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
```

## 🎭 Text Effects Examples

### Pause Effects
```python
text = "Welcome [pause:medium] to our show!"
# Result: "Welcome <break time="1s"/> to our show!"
```

### Emotion Effects
```python
text = "I'm so [emotion:excited] thrilled about this!"
# Result: Voice changes to excited, parameters optimized
```

### Combined Effects
```python
text = "Breaking news [pause:short] [emotion:surprised] [volume:+10%]!"
# Result: Multiple effects combined for rich audio
```

## 📊 Batch Processing Examples

### Simple Batch
```python
texts = ["Text 1", "Text 2", "Text 3"]
results = await edge_tts.batch_speak(texts, output_prefix="batch")
```

### Advanced Batch
```python
processor = edge_tts.BatchProcessor(max_concurrent=5)
results = await processor.process_batch(texts, voices, "output")
```

## 🧠 Content Analysis Examples

### Automatic Analysis
```python
analyzer = edge_tts.ContentAnalyzer()
analysis = analyzer.analyze_content("Breaking news: Major breakthrough!")

print(f"Content type: {analysis.content_type.value}")  # news
print(f"Emotion: {analysis.emotion.value}")           # excited
print(f"Sentiment: {analysis.sentiment_score}")       # 0.85
print(f"Language: {analysis.language}")               # en
print(f"Recommended voice: {analysis.recommended_voice}")  # en-US-AriaNeural
```

## 🎯 Use Cases

### 1. Podcast Production
```python
script = "Welcome [pause:medium] to our [emotion:excited] show!"
result = await edge_tts.speak_intelligently(script, "podcast.mp3")
```

### 2. Educational Content
```python
lesson = "Today we'll learn [speed:-20%] about photosynthesis [pause:short]"
enhanced = edge_tts.EnhancedCommunicate(lesson)
await enhanced.save("lesson.mp3")
```

### 3. News Broadcasting
```python
news = "Breaking news [pause:short] [emotion:surprised] [volume:+10%]!"
result = await edge_tts.speak_intelligently(news, "news.mp3")
```

### 4. Interactive Applications
```python
dialogue = """
Character A: Hello [emotion:happy]! How are you?
Character B: I'm great [laugh]! Thanks for asking.
"""
enhanced = edge_tts.EnhancedCommunicate(dialogue)
await enhanced.save("dialogue.mp3")
```

## 🔧 Advanced Configuration

### Custom Voice Parameters
```python
enhanced = edge_tts.EnhancedCommunicate("Custom text")
params = enhanced.get_voice_parameters()
print(f"Rate: {params['rate']}")
print(f"Volume: {params['volume']}")
print(f"Pitch: {params['pitch']}")
```

### Error Handling
```python
try:
    result = await edge_tts.speak_intelligently(text, "output.mp3")
except Exception as e:
    # Fallback to basic TTS
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save("output.mp3")
```

## 📈 Performance Tips

### Memory Management
```python
# Process in chunks for large datasets
chunk_size = 10
for i in range(0, len(texts), chunk_size):
    chunk = texts[i:i + chunk_size]
    results = await edge_tts.batch_speak(chunk, f"chunk_{i//chunk_size}")
```

### Caching
```python
# Cache repeated content
cache_key = hashlib.md5(text.encode()).hexdigest()
if os.path.exists(f"cache/{cache_key}.mp3"):
    return f"cache/{cache_key}.mp3"
```

## 🚨 Troubleshooting

### Common Issues
1. **403 Error**: Update edge-tts to latest version
2. **ML Dependencies**: Install scikit-learn, transformers
3. **Memory Issues**: Use chunked processing
4. **Voice Selection**: Check content analysis results

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

enhanced = edge_tts.EnhancedCommunicate("Debug text")
print(f"Analysis: {enhanced.get_analysis()}")
print(f"Effects: {enhanced.get_effects()}")
print(f"Parameters: {enhanced.get_voice_parameters()}")
```

## 🎉 Complete Example

```python
import edge_tts
import asyncio

async def main():
    # Professional podcast with effects
    script = """
    Welcome to Tech Talk [pause:medium] with your host [emotion:excited] Sarah!
    Today we're discussing [emotion:surprised] artificial intelligence [pause:short]
    and its impact on [emotion:calm] our daily lives.
    """
    
    # Generate with AI voice selection
    result = await edge_tts.speak_intelligently(script, "podcast.mp3")
    
    print(f"Voice used: {result['voice_used']}")
    print(f"Content type: {result['analysis'].content_type.value}")
    print(f"Emotion: {result['analysis'].emotion.value}")
    print(f"Parameters: {result['parameters']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📞 Support

- **Documentation**: This directory contains all documentation
- **Examples**: See [examples/](../examples/) for working examples
- **Issues**: GitHub Issues for bug reports
- **Community**: GitHub Discussions for questions

## 🤝 Contributing

Contributions are welcome! Please see the main repository for contribution guidelines.

## 📄 License

This project is licensed under the same terms as the original Edge-TTS library.

---

**Happy TTS Generation! 🎉**

For the latest updates and examples, visit the [main repository](https://github.com/rany2/edge-tts).
