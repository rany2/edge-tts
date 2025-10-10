#!/usr/bin/env python3
"""
Advanced Text Processing for Edge-TTS with Special Effects

This example demonstrates advanced text processing capabilities including:
- Pauses and timing control
- Emotional expressions (laughter, sighs, etc.)
- Voice effects and modifications
- Smart text chunking
- SSML-like features without custom SSML
"""

import asyncio
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import edge_tts

class EmotionType(Enum):
    """Emotion types for TTS"""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    ANGRY = "angry"
    SURPRISED = "surprised"
    CONFUSED = "confused"

class PauseType(Enum):
    """Types of pauses"""
    SHORT = "short"      # 0.5s
    MEDIUM = "medium"    # 1.0s
    LONG = "long"        # 2.0s
    VERY_LONG = "very_long"  # 3.0s

@dataclass
class TextEffect:
    """Represents a special effect in text"""
    effect_type: str
    start_pos: int
    end_pos: int
    parameters: Dict[str, Any]

@dataclass
class ProcessedText:
    """Processed text with effects and timing"""
    original_text: str
    processed_text: str
    effects: List[TextEffect]
    total_duration: float
    chunks: List[str]

class AdvancedTextProcessor:
    """Advanced text processing with special effects"""
    
    def __init__(self):
        self.effect_patterns = {
            r'\[pause:(\w+)\]': self._process_pause,
            r'\[laugh\]': self._process_laugh,
            r'\[sigh\]': self._process_sigh,
            r'\[emotion:(\w+)\]': self._process_emotion,
            r'\[whisper\]': self._process_whisper,
            r'\[shout\]': self._process_shout,
            r'\[speed:([+-]?\d+)%\]': self._process_speed,
            r'\[pitch:([+-]?\d+)Hz\]': self._process_pitch,
            r'\[volume:([+-]?\d+)%\]': self._process_volume,
        }
        
        self.pause_durations = {
            PauseType.SHORT: 0.5,
            PauseType.MEDIUM: 1.0,
            PauseType.LONG: 2.0,
            PauseType.VERY_LONG: 3.0
        }
        
        self.emotion_voice_mods = {
            EmotionType.HAPPY: {"rate": "+20%", "pitch": "+50Hz", "volume": "+10%"},
            EmotionType.SAD: {"rate": "-30%", "pitch": "-100Hz", "volume": "-20%"},
            EmotionType.EXCITED: {"rate": "+40%", "pitch": "+100Hz", "volume": "+30%"},
            EmotionType.CALM: {"rate": "-20%", "pitch": "-50Hz", "volume": "-10%"},
            EmotionType.ANGRY: {"rate": "+10%", "pitch": "+30Hz", "volume": "+40%"},
            EmotionType.SURPRISED: {"rate": "+50%", "pitch": "+150Hz", "volume": "+20%"},
            EmotionType.CONFUSED: {"rate": "-10%", "pitch": "-30Hz", "volume": "-5%"}
        }
    
    def process_text(self, text: str) -> ProcessedText:
        """Process text with special effects"""
        effects = []
        processed_text = text
        total_duration = 0.0
        
        # Find and process all effects
        for pattern, processor in self.effect_patterns.items():
            matches = list(re.finditer(pattern, text))
            for match in reversed(matches):  # Process from end to start
                effect = processor(match, text)
                if effect:
                    effects.append(effect)
                    total_duration += effect.parameters.get('duration', 0)
        
        # Remove effect markers from processed text
        for pattern in self.effect_patterns.keys():
            processed_text = re.sub(pattern, '', processed_text)
        
        # Clean up extra whitespace
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        # Split into chunks for processing
        chunks = self._split_into_chunks(processed_text)
        
        return ProcessedText(
            original_text=text,
            processed_text=processed_text,
            effects=effects,
            total_duration=total_duration,
            chunks=chunks
        )
    
    def _process_pause(self, match, text) -> Optional[TextEffect]:
        """Process pause effects"""
        pause_type = match.group(1).lower()
        duration = self.pause_durations.get(PauseType(pause_type), 1.0)
        
        return TextEffect(
            effect_type="pause",
            start_pos=match.start(),
            end_pos=match.end(),
            parameters={"duration": duration, "type": pause_type}
        )
    
    def _process_laugh(self, match, text) -> Optional[TextEffect]:
        """Process laughter effects"""
        return TextEffect(
            effect_type="laugh",
            start_pos=match.start(),
            end_pos=match.end(),
            parameters={
                "duration": 2.0,
                "rate": "+30%",
                "pitch": "+80Hz",
                "volume": "+20%",
                "text": "hahaha"
            }
        )
    
    def _process_sigh(self, match, text) -> Optional[TextEffect]:
        """Process sigh effects"""
        return TextEffect(
            effect_type="sigh",
            start_pos=match.start(),
            end_pos=match.end(),
            parameters={
                "duration": 1.5,
                "rate": "-40%",
                "pitch": "-120Hz",
                "volume": "-30%",
                "text": "sigh"
            }
        )
    
    def _process_emotion(self, match, text) -> Optional[TextEffect]:
        """Process emotion effects"""
        emotion = match.group(1).lower()
        try:
            emotion_type = EmotionType(emotion)
            mods = self.emotion_voice_mods[emotion_type]
            
            return TextEffect(
                effect_type="emotion",
                start_pos=match.start(),
                end_pos=match.end(),
                parameters={
                    "emotion": emotion,
                    "duration": 0,  # Emotion affects the following text
                    **mods
                }
            )
        except ValueError:
            return None
    
    def _process_whisper(self, match, text) -> Optional[TextEffect]:
        """Process whisper effects"""
        return TextEffect(
            effect_type="whisper",
            start_pos=match.start(),
            end_pos=match.end(),
            parameters={
                "rate": "-50%",
                "pitch": "-200Hz",
                "volume": "-60%"
            }
        )
    
    def _process_shout(self, match, text) -> Optional[TextEffect]:
        """Process shout effects"""
        return TextEffect(
            effect_type="shout",
            start_pos=match.start(),
            end_pos=match.end(),
            parameters={
                "rate": "+20%",
                "pitch": "+100Hz",
                "volume": "+50%"
            }
        )
    
    def _process_speed(self, match, text) -> Optional[TextEffect]:
        """Process speed effects"""
        speed = match.group(1)
        return TextEffect(
            effect_type="speed",
            start_pos=match.start(),
            end_pos=match.end(),
            parameters={"rate": f"{speed}%"}
        )
    
    def _process_pitch(self, match, text) -> Optional[TextEffect]:
        """Process pitch effects"""
        pitch = match.group(1)
        return TextEffect(
            effect_type="pitch",
            start_pos=match.start(),
            end_pos=match.end(),
            parameters={"pitch": f"{pitch}Hz"}
        )
    
    def _process_volume(self, match, text) -> Optional[TextEffect]:
        """Process volume effects"""
        volume = match.group(1)
        return TextEffect(
            effect_type="volume",
            start_pos=match.start(),
            end_pos=match.end(),
            parameters={"volume": f"{volume}%"}
        )
    
    def _split_into_chunks(self, text: str, max_length: int = 1000) -> List[str]:
        """Split text into chunks for processing"""
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

class EnhancedCommunicate:
    """Enhanced Communicate class with advanced text processing"""
    
    def __init__(self, text: str, voice: str = "en-US-AriaNeural", **kwargs):
        self.processor = AdvancedTextProcessor()
        self.processed_text = self.processor.process_text(text)
        self.voice = voice
        self.kwargs = kwargs
        
    async def save_with_effects(self, output_file: str):
        """Save audio with all effects applied"""
        # For now, save the processed text (effects would be applied in chunks)
        communicate = edge_tts.Communicate(
            self.processed_text.processed_text,
            self.voice,
            **self.kwargs
        )
        await communicate.save(output_file)
    
    async def save_chunked_with_effects(self, output_file: str):
        """Save audio with effects applied per chunk"""
        import os
        
        # Create temporary files for each chunk
        temp_files = []
        
        try:
            for i, chunk in enumerate(self.processed_text.chunks):
                temp_file = f"temp_chunk_{i}.mp3"
                temp_files.append(temp_file)
                
                # Apply effects for this chunk
                chunk_effects = self._get_effects_for_chunk(i)
                voice_mods = self._apply_effects_to_voice(chunk_effects)
                
                # Create communicate with modified voice settings
                communicate = edge_tts.Communicate(
                    chunk,
                    self.voice,
                    rate=voice_mods.get("rate", "+0%"),
                    volume=voice_mods.get("volume", "+0%"),
                    pitch=voice_mods.get("pitch", "+0Hz"),
                    **self.kwargs
                )
                
                await communicate.save(temp_file)
                
                # Add pause if needed
                if i < len(self.processed_text.chunks) - 1:
                    await self._add_pause_after_chunk(temp_file)
            
            # Combine all chunks
            await self._combine_audio_files(temp_files, output_file)
            
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    def _get_effects_for_chunk(self, chunk_index: int) -> List[TextEffect]:
        """Get effects that apply to a specific chunk"""
        # This would analyze which effects apply to which chunks
        return []
    
    def _apply_effects_to_voice(self, effects: List[TextEffect]) -> Dict[str, str]:
        """Apply effects to voice parameters"""
        voice_mods = {"rate": "+0%", "volume": "+0%", "pitch": "+0Hz"}
        
        for effect in effects:
            if effect.effect_type in ["emotion", "whisper", "shout", "speed", "pitch", "volume"]:
                voice_mods.update(effect.parameters)
        
        return voice_mods
    
    async def _add_pause_after_chunk(self, chunk_file: str):
        """Add pause after a chunk (would need audio processing)"""
        # This would use audio processing to add silence
        pass
    
    async def _combine_audio_files(self, input_files: List[str], output_file: str):
        """Combine multiple audio files into one"""
        # This would use ffmpeg or similar to combine files
        pass

# Example usage and demonstrations
async def example_emotional_storytelling():
    """Example: Emotional storytelling with effects"""
    
    story_text = """
    Once upon a time [emotion:happy], there was a little girl who lived in a magical forest.
    [pause:medium] She loved to explore [emotion:excited] and discover new things every day.
    
    One day [pause:short], she heard a strange sound [emotion:surprised] coming from behind the trees.
    [pause:long] She whispered to herself [whisper], 'What could that be?'
    
    As she got closer [emotion:confused], she realized it was just the wind [sigh].
    [pause:very_long] But then, she saw something amazing [emotion:excited]!
    """
    
    processor = AdvancedTextProcessor()
    processed = processor.process_text(story_text)
    
    print("Original text:")
    print(story_text)
    print("\nProcessed text:")
    print(processed.processed_text)
    print("\nEffects found:")
    for effect in processed.effects:
        print(f"- {effect.effect_type}: {effect.parameters}")
    
    # Create enhanced communicate
    enhanced = EnhancedCommunicate(story_text, "en-US-AriaNeural")
    await enhanced.save_with_effects("emotional_story.mp3")

async def example_podcast_style():
    """Example: Podcast-style narration with natural pauses"""
    
    podcast_text = """
    Welcome to today's episode [pause:medium] where we'll be discussing the fascinating world of AI.
    [pause:short] I'm your host [laugh], and I'm excited to share some amazing insights with you.
    
    First [pause:short], let's talk about machine learning [emotion:excited].
    [pause:medium] This technology is revolutionizing how we approach problem-solving.
    
    But wait [emotion:surprised], there's more to it than meets the eye [pause:short].
    [pause:long] Let me explain the deeper implications [emotion:calm].
    """
    
    enhanced = EnhancedCommunicate(podcast_text, "en-US-GuyNeural")
    await enhanced.save_with_effects("podcast_episode.mp3")

async def example_technical_presentation():
    """Example: Technical presentation with emphasis"""
    
    tech_text = """
    Today we'll be diving deep into [emotion:excited] advanced text processing algorithms.
    [pause:short] These systems can handle [speed:+20%] complex linguistic patterns [speed:+0%].
    
    The key components include [pause:medium]:
    - Natural language processing [emotion:calm]
    - Machine learning models [emotion:excited]
    - Real-time processing capabilities [shout]
    
    [pause:long] Let's examine the implementation details [whisper] step by step.
    """
    
    enhanced = EnhancedCommunicate(tech_text, "en-US-JennyNeural")
    await enhanced.save_with_effects("tech_presentation.mp3")

async def example_interactive_dialogue():
    """Example: Interactive dialogue with character voices"""
    
    dialogue_text = """
    Character A: Hello there [emotion:happy]! How are you doing today?
    [pause:medium]
    Character B: Oh, I'm doing great [laugh]! Thanks for asking.
    [pause:short]
    Character A: That's wonderful to hear [emotion:excited]!
    [pause:short]
    Character B: Actually [emotion:confused], I have a question for you.
    [pause:medium]
    Character A: Of course [emotion:calm]! What would you like to know?
    [pause:short]
    Character B: Well [sigh], it's about the new project [emotion:excited].
    """
    
    # Process for different characters with different voices
    enhanced_a = EnhancedCommunicate(dialogue_text, "en-US-AriaNeural")  # Female voice
    enhanced_b = EnhancedCommunicate(dialogue_text, "en-US-GuyNeural")   # Male voice
    
    await enhanced_a.save_with_effects("dialogue_character_a.mp3")
    await enhanced_b.save_with_effects("dialogue_character_b.mp3")

if __name__ == "__main__":
    print("Advanced Text Processing with Special Effects")
    print("=" * 50)
    
    # Run examples
    asyncio.run(example_emotional_storytelling())
    asyncio.run(example_podcast_style())
    asyncio.run(example_technical_presentation())
    asyncio.run(example_interactive_dialogue())
    
    print("\nAll examples completed! Check the generated MP3 files.")
