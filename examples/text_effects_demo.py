#!/usr/bin/env python3
"""
Text Effects Demo for Enhanced Edge-TTS

This demonstrates all available text effects in the enhanced library.
"""

import asyncio
import edge_tts

async def demo_all_text_effects():
    """Demonstrate all available text effects"""
    print("=== Text Effects Demo ===")
    print("Available text effects in the enhanced edge-tts library:\n")
    
    # 1. Pause Effects
    print("1. 🕐 PAUSE EFFECTS:")
    pause_examples = [
        "Welcome to our show [pause:short] today we have exciting news!",
        "This is important [pause:medium] so listen carefully.",
        "And now [pause:long] for the main event!",
        "The moment you've been waiting for [pause:extra_long] is here!"
    ]
    
    for i, text in enumerate(pause_examples):
        print(f"   Example {i+1}: {text}")
        # Create enhanced TTS
        enhanced = edge_tts.EnhancedCommunicate(text)
        print(f"   Processed: {enhanced.processed_text}")
        print(f"   Effects: {len(enhanced.effects)} found")
        print()
    
    # 2. Emotion Effects
    print("2. 😊 EMOTION EFFECTS:")
    emotion_examples = [
        "I'm so [emotion:happy] excited about this!",
        "This makes me [emotion:sad] feel really down.",
        "I'm [emotion:excited] absolutely thrilled!",
        "I feel [emotion:calm] peaceful and relaxed.",
        "This is [emotion:angry] so frustrating!",
        "Wow, that's [emotion:surprised] completely unexpected!",
        "I'm feeling [emotion:neutral] okay about this."
    ]
    
    for i, text in enumerate(emotion_examples):
        print(f"   Example {i+1}: {text}")
        enhanced = edge_tts.EnhancedCommunicate(text)
        print(f"   Voice: {enhanced.voice}")
        print(f"   Parameters: {enhanced.voice_params}")
        print()
    
    # 3. Sound Effects
    print("3. 🔊 SOUND EFFECTS:")
    sound_examples = [
        "That was hilarious [laugh] I can't stop laughing!",
        "I'm so tired [sigh] of this situation.",
        "Let me tell you a secret [whisper] this is confidential.",
        "I'm so excited [shout] about this announcement!"
    ]
    
    for i, text in enumerate(sound_examples):
        print(f"   Example {i+1}: {text}")
        enhanced = edge_tts.EnhancedCommunicate(text)
        print(f"   Effects: {[e.effect_type for e in enhanced.effects]}")
        print()
    
    # 4. Voice Parameter Effects
    print("4. 🎛️ VOICE PARAMETER EFFECTS:")
    parameter_examples = [
        "This is urgent [speed:+50%] so listen quickly!",
        "Let me explain slowly [speed:-30%] so you understand.",
        "High pitch announcement [pitch:+100Hz] for everyone!",
        "Low and serious [pitch:-50Hz] discussion.",
        "Loud and clear [volume:+20%] for the back row!",
        "Quiet conversation [volume:-15%] between friends."
    ]
    
    for i, text in enumerate(parameter_examples):
        print(f"   Example {i+1}: {text}")
        enhanced = edge_tts.EnhancedCommunicate(text)
        print(f"   Effects: {[e.effect_type for e in enhanced.effects]}")
        print()
    
    # 5. Combined Effects
    print("5. 🎭 COMBINED EFFECTS:")
    combined_examples = [
        "Welcome [pause:medium] to our [emotion:excited] amazing [laugh] podcast!",
        "Breaking news [pause:short] [emotion:surprised] [volume:+10%] just in!",
        "Once upon a time [pause:long] in a [emotion:calm] magical forest [whisper] far away.",
        "Technical explanation [speed:-20%] [pitch:-30Hz] [emotion:neutral] coming up."
    ]
    
    for i, text in enumerate(combined_examples):
        print(f"   Example {i+1}: {text}")
        enhanced = edge_tts.EnhancedCommunicate(text)
        print(f"   Processed: {enhanced.processed_text}")
        print(f"   Effects: {len(enhanced.effects)} found")
        for effect in enhanced.effects:
            print(f"     - {effect.effect_type}: {effect.parameters}")
        print()

async def demo_effect_processing():
    """Demonstrate how effects are processed"""
    print("=== Effect Processing Demo ===")
    
    # Complex text with multiple effects
    complex_text = """
    Welcome to our podcast! [pause:medium]
    Today we have [emotion:excited] amazing news [laugh] that will [emotion:surprised] 
    completely change everything [pause:short] in the world of technology!
    
    But first [speed:-20%] let me explain [pitch:-30Hz] the technical details [volume:+10%]
    in a [emotion:calm] peaceful and [whisper] quiet manner.
    """
    
    print("Original Text:")
    print(complex_text)
    print()
    
    # Process with enhanced TTS
    enhanced = edge_tts.EnhancedCommunicate(complex_text)
    
    print("Processed Text (SSML-ready):")
    print(enhanced.processed_text)
    print()
    
    print("Effects Found:")
    for i, effect in enumerate(enhanced.effects):
        print(f"  {i+1}. {effect.effect_type}: {effect.parameters}")
        print(f"     Position: {effect.start_pos}-{effect.end_pos}")
    print()
    
    print("Voice Analysis:")
    analysis = enhanced.get_analysis()
    print(f"  Content Type: {analysis.content_type.value}")
    print(f"  Emotion: {analysis.emotion.value}")
    print(f"  Sentiment: {analysis.sentiment_score:.2f}")
    print(f"  Language: {analysis.language}")
    print(f"  Complexity: {analysis.complexity_score:.2f}")
    print(f"  Formality: {analysis.formality_score:.2f}")
    print()
    
    print("Voice Parameters:")
    params = enhanced.get_voice_parameters()
    print(f"  Rate: {params['rate']}")
    print(f"  Volume: {params['volume']}")
    print(f"  Pitch: {params['pitch']}")

async def demo_effect_categories():
    """Demonstrate different categories of effects"""
    print("=== Effect Categories Demo ===")
    
    categories = {
        "Timing Effects": [
            "[pause:short] - 0.5 second pause",
            "[pause:medium] - 1 second pause", 
            "[pause:long] - 2 second pause",
            "[pause:extra_long] - 3 second pause"
        ],
        "Emotion Effects": [
            "[emotion:happy] - Happy voice",
            "[emotion:sad] - Sad voice",
            "[emotion:excited] - Excited voice",
            "[emotion:calm] - Calm voice",
            "[emotion:angry] - Angry voice",
            "[emotion:surprised] - Surprised voice",
            "[emotion:neutral] - Neutral voice"
        ],
        "Sound Effects": [
            "[laugh] - Laughter sound",
            "[sigh] - Sigh sound",
            "[whisper] - Whisper voice",
            "[shout] - Shout voice"
        ],
        "Voice Parameters": [
            "[speed:+50%] - 50% faster",
            "[speed:-30%] - 30% slower",
            "[pitch:+100Hz] - Higher pitch",
            "[pitch:-50Hz] - Lower pitch",
            "[volume:+20%] - Louder",
            "[volume:-15%] - Quieter"
        ]
    }
    
    for category, effects in categories.items():
        print(f"\n{category}:")
        for effect in effects:
            print(f"  • {effect}")

if __name__ == "__main__":
    print("Enhanced Edge-TTS Text Effects Demo")
    print("=" * 50)
    
    # Run demos
    asyncio.run(demo_all_text_effects())
    asyncio.run(demo_effect_processing())
    asyncio.run(demo_effect_categories())
    
    print("\n" + "=" * 50)
    print("🎉 All text effects demonstrated!")
    print("\nTo use these effects in your code:")
    print("```python")
    print("import edge_tts")
    print("")
    print("# Simple usage")
    print("result = await edge_tts.speak_intelligently(")
    print("    'Welcome [pause:medium] to our [emotion:excited] show!',")
    print("    'output.mp3'")
    print(")")
    print("")
    print("# Advanced usage")
    print("enhanced = edge_tts.EnhancedCommunicate(")
    print("    'Hello [laugh] [speed:+20%] world!'")
    print(")")
    print("await enhanced.save('output.mp3')")
    print("```")
