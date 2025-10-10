# Enhanced Edge-TTS Quick Reference

## 🚀 Quick Start

```python
import edge_tts

# Simple AI-powered TTS
result = await edge_tts.speak_intelligently("Hello world!", "output.mp3")

# Advanced control
enhanced = edge_tts.EnhancedCommunicate("Text with [pause:medium] effects!")
await enhanced.save("output.mp3")
```

## 🎭 Text Effects

### Pause Effects
```python
"[pause:short]"     # 0.5s pause
"[pause:medium]"    # 1s pause
"[pause:long]"      # 2s pause
"[pause:extra_long]" # 3s pause
```

### Emotion Effects
```python
"[emotion:happy]"     # Happy voice
"[emotion:sad]"       # Sad voice
"[emotion:excited]"   # Excited voice
"[emotion:calm]"      # Calm voice
"[emotion:angry]"     # Angry voice
"[emotion:surprised]" # Surprised voice
"[emotion:neutral]"   # Neutral voice
```

### Sound Effects
```python
"[laugh]"    # Laughter
"[sigh]"     # Sigh
"[whisper]"  # Whisper
"[shout]"    # Shout
```

### Voice Parameters
```python
"[speed:+50%]"   # 50% faster
"[speed:-30%]"   # 30% slower
"[pitch:+100Hz]" # Higher pitch
"[pitch:-50Hz]"  # Lower pitch
"[volume:+20%]"  # Louder
"[volume:-15%]"  # Quieter
```

## 📊 Batch Processing

```python
# Simple batch processing
texts = ["Text 1", "Text 2", "Text 3"]
results = await edge_tts.batch_speak(texts, output_prefix="batch")

# Advanced batch processing
processor = edge_tts.BatchProcessor(max_concurrent=5)
results = await processor.process_batch(texts, voices, "output")
```

## 🧠 Content Analysis

```python
# Analyze content
analyzer = edge_tts.ContentAnalyzer()
analysis = analyzer.analyze_content("Breaking news!")

print(f"Type: {analysis.content_type.value}")      # news
print(f"Emotion: {analysis.emotion.value}")        # excited
print(f"Voice: {analysis.recommended_voice}")     # en-US-AriaNeural
```

## 🎵 Voice Profiles

```python
# Access voice characteristics
profile = edge_tts.VoiceProfile(
    voice_name='Aria',
    gender='Female',
    characteristics={'warm': 0.8, 'professional': 0.9}
)
```

## ⚡ Real-time Features

```python
# WebRTC integration
class RealtimeTTS:
    async def speak_live(self, text: str):
        enhanced = edge_tts.EnhancedCommunicate(text)
        # Stream audio data
        return audio_data
```

## 🎯 Common Use Cases

### Podcast Production
```python
script = "Welcome [pause:medium] to our [emotion:excited] show!"
result = await edge_tts.speak_intelligently(script, "podcast.mp3")
```

### Educational Content
```python
lesson = "Today we'll learn [speed:-20%] about photosynthesis [pause:short]"
enhanced = edge_tts.EnhancedCommunicate(lesson)
await enhanced.save("lesson.mp3")
```

### News Broadcasting
```python
news = "Breaking news [pause:short] [emotion:surprised] [volume:+10%]!"
result = await edge_tts.speak_intelligently(news, "news.mp3")
```

### Interactive Dialogue
```python
dialogue = """
Character A: Hello [emotion:happy]! How are you?
Character B: I'm great [laugh]! Thanks for asking.
"""
enhanced = edge_tts.EnhancedCommunicate(dialogue)
await enhanced.save("dialogue.mp3")
```

## 🔧 Advanced Features

### Custom Voice Parameters
```python
enhanced = edge_tts.EnhancedCommunicate("Custom text")
params = enhanced.get_voice_parameters()
print(f"Rate: {params['rate']}")
print(f"Volume: {params['volume']}")
print(f"Pitch: {params['pitch']}")
```

### Effect Processing
```python
enhanced = edge_tts.EnhancedCommunicate("Text with [pause:medium] effects!")
print(f"Effects: {len(enhanced.effects)}")
for effect in enhanced.effects:
    print(f"- {effect.effect_type}: {effect.parameters}")
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

## 📚 API Reference

### Core Classes
- `EnhancedCommunicate`: Main enhanced TTS class
- `ContentAnalyzer`: ML-powered content analysis
- `AdvancedTextProcessor`: Text effects processing
- `BatchProcessor`: Enterprise batch processing
- `VoiceProfile`: Voice characteristics

### Convenience Functions
- `speak_intelligently()`: Simple AI-powered TTS
- `batch_speak()`: Batch processing with AI

### Enums
- `ContentType`: News, Story, Technical, Educational, etc.
- `EmotionType`: Happy, Sad, Excited, Calm, etc.
- `PauseType`: Short, Medium, Long, Extra Long

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

# Enhanced TTS with debug info
enhanced = edge_tts.EnhancedCommunicate("Debug text")
print(f"Analysis: {enhanced.get_analysis()}")
print(f"Effects: {enhanced.get_effects()}")
print(f"Parameters: {enhanced.get_voice_parameters()}")
```

## 🎯 Best Practices

1. **Use AI Voice Selection**: Let the library choose optimal voices
2. **Combine Effects**: Mix multiple effects for rich audio
3. **Batch Processing**: Use for large-scale applications
4. **Error Handling**: Always implement fallbacks
5. **Performance**: Use caching and chunked processing
6. **Testing**: Test with different content types and emotions

## 📞 Support

- **Documentation**: [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md)
- **Examples**: [examples/](examples/)
- **Issues**: GitHub Issues
- **Community**: GitHub Discussions

---

**Happy TTS Generation! 🎉**
