#!/usr/bin/env python3
"""
Enhanced Library Usage Examples

This demonstrates how to use the enhanced edge-tts library with built-in advanced features.
"""

import asyncio
import edge_tts

async def example_basic_enhanced_usage():
    """Example: Basic enhanced TTS usage"""
    print("=== Basic Enhanced TTS Usage ===")
    
    # Simple intelligent TTS
    text = "Welcome to our exciting new podcast episode!"
    result = await edge_tts.speak_intelligently(text, "enhanced_basic.mp3")
    
    print(f"Text: {text}")
    print(f"Content Type: {result['analysis'].content_type.value}")
    print(f"Emotion: {result['analysis'].emotion.value}")
    print(f"Voice Used: {result['voice_used']}")
    print(f"Parameters: {result['parameters']}")

async def example_advanced_text_processing():
    """Example: Advanced text processing with effects"""
    print("\n=== Advanced Text Processing ===")
    
    # Text with effects
    text_with_effects = """
    Welcome to our podcast! [pause:medium] 
    Today we have [emotion:excited] amazing news [pause:short]
    that will [emotion:surprised] completely change everything!
    """
    
    # Use EnhancedCommunicate directly
    enhanced = edge_tts.EnhancedCommunicate(text_with_effects)
    await enhanced.save("enhanced_effects.mp3")
    
    print(f"Original Text: {text_with_effects}")
    print(f"Processed Text: {enhanced.processed_text}")
    print(f"Effects Found: {len(enhanced.effects)}")
    for effect in enhanced.effects:
        print(f"  - {effect.effect_type}: {effect.parameters}")

async def example_batch_processing():
    """Example: Batch processing with intelligent voice selection"""
    print("\n=== Batch Processing ===")
    
    texts = [
        "Breaking news: Scientists discover new planet!",
        "Once upon a time in a magical forest...",
        "The algorithm uses machine learning techniques.",
        "Hey there! How's it going today?",
        "Our quarterly revenue increased by 15%."
    ]
    
    # Batch process with intelligent voice selection
    results = await edge_tts.batch_speak(texts, output_prefix="enhanced_batch")
    
    print(f"Processed {len(results)} texts:")
    for i, result in enumerate(results):
        if result['success']:
            print(f"  {i+1}. {result['text'][:50]}...")
            print(f"     Voice: {result['voice_used']}")
            print(f"     Content Type: {result['analysis'].content_type.value}")
        else:
            print(f"  {i+1}. ERROR: {result.get('error', 'Unknown error')}")

async def example_emotion_aware_tts():
    """Example: Emotion-aware TTS"""
    print("\n=== Emotion-Aware TTS ===")
    
    emotional_texts = [
        "I'm absolutely thrilled about this amazing opportunity!",
        "This is such a sad and heartbreaking situation.",
        "I'm feeling calm and peaceful today.",
        "This makes me so angry and frustrated!",
        "Wow, that's completely unexpected and surprising!"
    ]
    
    for i, text in enumerate(emotional_texts):
        result = await edge_tts.speak_intelligently(text, f"emotion_enhanced_{i+1}.mp3")
        
        print(f"Text {i+1}: {text}")
        print(f"  Detected Emotion: {result['analysis'].emotion.value}")
        print(f"  Voice Parameters: {result['parameters']}")
        print(f"  Recommended Voice: {result['voice_used']}")
        print()

async def example_content_type_adaptation():
    """Example: Content type-based voice adaptation"""
    print("\n=== Content Type Adaptation ===")
    
    content_samples = [
        ("Breaking news: Major breakthrough in AI research", "News"),
        ("Once upon a time, in a magical forest far away", "Story"),
        ("The algorithm uses machine learning techniques", "Technical"),
        ("Today we'll learn about photosynthesis", "Educational"),
        ("That was hilarious! I can't stop laughing", "Entertainment")
    ]
    
    for text, expected_type in content_samples:
        result = await edge_tts.speak_intelligently(text, f"content_{expected_type.lower()}.mp3")
        
        print(f"Text: {text}")
        print(f"Expected: {expected_type}")
        print(f"Detected: {result['analysis'].content_type.value}")
        print(f"Voice: {result['voice_used']}")
        print(f"Confidence: {result['analysis'].confidence}")
        print()

async def example_voice_parameter_optimization():
    """Example: Voice parameter optimization"""
    print("\n=== Voice Parameter Optimization ===")
    
    # Same text, different contexts
    base_text = "This is important information that you need to know."
    
    contexts = [
        "urgent_news",
        "calm_story", 
        "technical_explanation",
        "entertainment_show"
    ]
    
    for context in contexts:
        # Simulate different contexts by modifying text
        if context == "urgent_news":
            text = f"URGENT: {base_text}"
        elif context == "calm_story":
            text = f"Once upon a time, {base_text.lower()}"
        elif context == "technical_explanation":
            text = f"From a technical perspective, {base_text.lower()}"
        else:
            text = f"Hey everyone! {base_text}"
        
        result = await edge_tts.speak_intelligently(text, f"context_{context}.mp3")
        
        print(f"Context: {context}")
        print(f"Text: {text}")
        print(f"Voice: {result['voice_used']}")
        print(f"Rate: {result['parameters']['rate']}")
        print(f"Volume: {result['parameters']['volume']}")
        print(f"Pitch: {result['parameters']['pitch']}")
        print()

if __name__ == "__main__":
    print("Enhanced Edge-TTS Library Usage Examples")
    print("=" * 50)
    
    # Run examples
    asyncio.run(example_basic_enhanced_usage())
    asyncio.run(example_advanced_text_processing())
    asyncio.run(example_batch_processing())
    asyncio.run(example_emotion_aware_tts())
    asyncio.run(example_content_type_adaptation())
    asyncio.run(example_voice_parameter_optimization())
    
    print("\nAll enhanced library examples completed!")
    print("\nGenerated files:")
    print("- enhanced_basic.mp3")
    print("- enhanced_effects.mp3") 
    print("- enhanced_batch_*.mp3")
    print("- emotion_enhanced_*.mp3")
    print("- content_*.mp3")
    print("- context_*.mp3")
