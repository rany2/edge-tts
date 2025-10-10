#!/usr/bin/env python3
"""
Enhanced Edge-TTS Features Demo

This demonstrates the key enhanced features with clear examples.
"""

import asyncio
import edge_tts

async def demo_basic_enhanced_features():
    """Demonstrate basic enhanced features"""
    print("=== Basic Enhanced Features Demo ===")
    
    # 1. Simple AI-powered TTS
    print("\n1. 🧠 AI-Powered Voice Selection:")
    text = "Welcome to our exciting new podcast episode!"
    result = await edge_tts.speak_intelligently(text, "demo_basic.mp3")
    
    print(f"   Text: {text}")
    print(f"   Voice: {result['voice_used']}")
    print(f"   Content Type: {result['analysis'].content_type.value}")
    print(f"   Emotion: {result['analysis'].emotion.value}")
    print(f"   Parameters: {result['parameters']}")

async def demo_text_effects():
    """Demonstrate text effects"""
    print("\n=== Text Effects Demo ===")
    
    # 2. Pause Effects
    print("\n2. 🕐 Pause Effects:")
    pause_text = "Welcome to our show [pause:medium] today we have exciting news!"
    enhanced = edge_tts.EnhancedCommunicate(pause_text)
    await enhanced.save("demo_pauses.mp3")
    
    print(f"   Original: {enhanced.original_text}")
    print(f"   Processed: {enhanced.processed_text}")
    print(f"   Effects: {len(enhanced.effects)} found")
    
    # 3. Emotion Effects
    print("\n3. 😊 Emotion Effects:")
    emotion_text = "I'm so [emotion:excited] thrilled about this amazing opportunity!"
    enhanced = edge_tts.EnhancedCommunicate(emotion_text)
    await enhanced.save("demo_emotions.mp3")
    
    print(f"   Text: {emotion_text}")
    print(f"   Voice: {enhanced.voice}")
    print(f"   Parameters: {enhanced.get_voice_parameters()}")
    
    # 4. Combined Effects
    print("\n4. 🎭 Combined Effects:")
    combined_text = "Breaking news [pause:short] [emotion:surprised] [volume:+10%] just in!"
    enhanced = edge_tts.EnhancedCommunicate(combined_text)
    await enhanced.save("demo_combined.mp3")
    
    print(f"   Text: {combined_text}")
    print(f"   Effects: {len(enhanced.effects)} found")
    for effect in enhanced.effects:
        print(f"     - {effect.effect_type}: {effect.parameters}")

async def demo_content_analysis():
    """Demonstrate content analysis"""
    print("\n=== Content Analysis Demo ===")
    
    # 5. Different Content Types
    print("\n5. 📊 Content Type Analysis:")
    content_samples = [
        "Breaking news: Scientists discover new planet!",
        "Once upon a time in a magical forest...",
        "The algorithm uses machine learning techniques.",
        "Hey there! How's it going today?",
        "Our quarterly revenue increased by 15%."
    ]
    
    analyzer = edge_tts.ContentAnalyzer()
    
    for i, text in enumerate(content_samples):
        analysis = analyzer.analyze_content(text)
        print(f"   Sample {i+1}: {text}")
        print(f"     Type: {analysis.content_type.value}")
        print(f"     Emotion: {analysis.emotion.value}")
        print(f"     Voice: {analysis.recommended_voice}")
        print(f"     Confidence: {analysis.confidence}")
        print()

async def demo_batch_processing():
    """Demonstrate batch processing"""
    print("\n=== Batch Processing Demo ===")
    
    # 6. Batch Processing
    print("\n6. 📊 Batch Processing:")
    texts = [
        "Welcome to our podcast episode one.",
        "Today we'll be discussing artificial intelligence.",
        "Machine learning is revolutionizing technology.",
        "Thank you for listening to our show."
    ]
    
    results = await edge_tts.batch_speak(texts, output_prefix="demo_batch")
    
    print(f"   Processed {len(results)} texts:")
    for i, result in enumerate(results):
        if result['success']:
            print(f"     {i+1}. Voice: {result['voice_used']}")
            print(f"        Type: {result['analysis'].content_type.value}")
        else:
            print(f"     {i+1}. ERROR: {result.get('error', 'Unknown error')}")

async def demo_advanced_usage():
    """Demonstrate advanced usage patterns"""
    print("\n=== Advanced Usage Demo ===")
    
    # 7. Professional Podcast
    print("\n7. 🎙️ Professional Podcast:")
    podcast_script = """
    Welcome to Tech Talk [pause:medium] with your host [emotion:excited] Sarah!
    Today we're discussing [emotion:surprised] artificial intelligence [pause:short]
    and its impact on [emotion:calm] our daily lives.
    """
    
    enhanced = edge_tts.EnhancedCommunicate(podcast_script)
    await enhanced.save("demo_podcast.mp3")
    
    print(f"   Script: {podcast_script.strip()}")
    print(f"   Voice: {enhanced.voice}")
    print(f"   Effects: {len(enhanced.effects)} found")
    print(f"   Parameters: {enhanced.get_voice_parameters()}")
    
    # 8. Educational Content
    print("\n8. 📚 Educational Content:")
    lesson_script = "Today we'll learn [speed:-20%] about photosynthesis [pause:short] step by step."
    
    enhanced = edge_tts.EnhancedCommunicate(lesson_script)
    await enhanced.save("demo_lesson.mp3")
    
    print(f"   Script: {lesson_script}")
    print(f"   Voice: {enhanced.voice}")
    print(f"   Parameters: {enhanced.get_voice_parameters()}")

async def demo_error_handling():
    """Demonstrate error handling"""
    print("\n=== Error Handling Demo ===")
    
    # 9. Safe TTS Generation
    print("\n9. 🚨 Error Handling:")
    
    async def safe_tts_generation(text: str, output_file: str):
        """Safe TTS generation with error handling"""
        try:
            result = await edge_tts.speak_intelligently(text, output_file)
            return result
        except Exception as e:
            print(f"     Enhanced TTS failed: {e}")
            try:
                # Fallback to basic TTS
                communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
                await communicate.save(output_file)
                return {"voice_used": "en-US-AriaNeural", "fallback": True}
            except Exception as e2:
                print(f"     Basic TTS also failed: {e2}")
                raise
    
    try:
        result = await safe_tts_generation("Hello world!", "demo_safe.mp3")
        print(f"   Success: {result['voice_used']}")
        if result.get('fallback'):
            print("   (Used fallback method)")
    except Exception as e:
        print(f"   All methods failed: {e}")

async def main():
    """Main demo function"""
    print("Enhanced Edge-TTS Features Demo")
    print("=" * 50)
    
    # Run all demos
    await demo_basic_enhanced_features()
    await demo_text_effects()
    await demo_content_analysis()
    await demo_batch_processing()
    await demo_advanced_usage()
    await demo_error_handling()
    
    print("\n" + "=" * 50)
    print("🎉 All enhanced features demonstrated!")
    print("\nGenerated files:")
    print("- demo_basic.mp3")
    print("- demo_pauses.mp3")
    print("- demo_emotions.mp3")
    print("- demo_combined.mp3")
    print("- demo_batch_*.mp3")
    print("- demo_podcast.mp3")
    print("- demo_lesson.mp3")
    print("- demo_safe.mp3")
    
    print("\nTo test the audio files:")
    print("ffplay demo_basic.mp3")
    print("ffplay demo_podcast.mp3")
    print("ffplay demo_lesson.mp3")

if __name__ == "__main__":
    asyncio.run(main())
