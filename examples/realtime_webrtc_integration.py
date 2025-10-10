#!/usr/bin/env python3
"""
Real-time TTS with WebRTC integration for live calls and streaming.

This example demonstrates how to integrate edge-tts with WebRTC for
real-time voice applications like live calls, AI assistants, etc.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Callable, Optional
import edge_tts
from dataclasses import dataclass
from enum import Enum

# WebRTC integration imports (would need aiortc or similar)
try:
    from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, AudioStreamTrack
    from aiortc.contrib.signaling import TcpSocketSignaling
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    print("WebRTC libraries not available. Install with: pip install aiortc")

# Audio processing imports
try:
    import pyaudio
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Audio processing libraries not available. Install with: pip install pyaudio numpy")

@dataclass
class RealtimeConfig:
    """Configuration for real-time TTS"""
    voice: str = "en-US-AriaNeural"
    sample_rate: int = 24000
    channels: int = 1
    chunk_size: int = 1024
    buffer_size: int = 4096
    latency_ms: int = 50  # Target latency in milliseconds

class AudioStreamTrack(AudioStreamTrack):
    """Custom audio stream track for real-time TTS"""
    
    def __init__(self, tts_generator: AsyncGenerator[bytes, None]):
        super().__init__()
        self.tts_generator = tts_generator
        self.audio_buffer = asyncio.Queue(maxsize=100)
        self.is_running = False
        
    async def start(self):
        """Start the audio stream"""
        self.is_running = True
        asyncio.create_task(self._buffer_audio())
    
    async def stop(self):
        """Stop the audio stream"""
        self.is_running = False
    
    async def _buffer_audio(self):
        """Buffer audio chunks from TTS generator"""
        try:
            async for chunk in self.tts_generator:
                if not self.is_running:
                    break
                await self.audio_buffer.put(chunk)
        except Exception as e:
            logging.error(f"Error buffering audio: {e}")
    
    async def recv(self):
        """Receive audio frame for WebRTC"""
        if self.audio_buffer.empty():
            # Return silence if no audio available
            return self._create_silence_frame()
        
        audio_data = await self.audio_buffer.get()
        return self._create_audio_frame(audio_data)
    
    def _create_silence_frame(self):
        """Create a silence frame"""
        # Implementation would create silence frame
        pass
    
    def _create_audio_frame(self, audio_data: bytes):
        """Create audio frame from TTS data"""
        # Implementation would convert TTS audio to WebRTC frame
        pass

class RealtimeTTS:
    """Real-time TTS with WebRTC integration"""
    
    def __init__(self, config: RealtimeConfig):
        self.config = config
        self.audio_track = None
        self.peer_connection = None
        
    async def initialize_webrtc(self, signaling_server: str = "localhost:8080"):
        """Initialize WebRTC connection"""
        if not WEBRTC_AVAILABLE:
            raise RuntimeError("WebRTC libraries not available")
        
        self.peer_connection = RTCPeerConnection()
        signaling = TcpSocketSignaling(signaling_server)
        
        # Set up audio track
        tts_generator = self._create_tts_generator("")
        self.audio_track = AudioStreamTrack(tts_generator)
        self.peer_connection.addTrack(self.audio_track)
        
        return signaling
    
    async def _create_tts_generator(self, text: str) -> AsyncGenerator[bytes, None]:
        """Create TTS audio generator"""
        communicate = edge_tts.Communicate(text, self.config.voice)
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
    
    async def speak_realtime(self, text: str):
        """Speak text in real-time with minimal latency"""
        # Create new TTS generator for this text
        tts_generator = self._create_tts_generator(text)
        
        # Update the audio track's generator
        if self.audio_track:
            self.audio_track.tts_generator = tts_generator
            await self.audio_track.start()
    
    async def stream_to_speakers(self, text: str):
        """Stream TTS directly to system speakers"""
        if not AUDIO_AVAILABLE:
            raise RuntimeError("Audio libraries not available")
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=self.config.channels,
            rate=self.config.sample_rate,
            output=True,
            frames_per_buffer=self.config.chunk_size
        )
        
        try:
            communicate = edge_tts.Communicate(text, self.config.voice)
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    # Convert and play audio chunk
                    audio_data = self._convert_audio_chunk(chunk["data"])
                    stream.write(audio_data)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
    
    def _convert_audio_chunk(self, audio_data: bytes) -> bytes:
        """Convert TTS audio chunk to playable format"""
        # Implementation would handle audio format conversion
        return audio_data

class LiveCallTTS:
    """TTS for live call applications"""
    
    def __init__(self, config: RealtimeConfig):
        self.config = config
        self.realtime_tts = RealtimeTTS(config)
        self.is_speaking = False
        self.speech_queue = asyncio.Queue()
        
    async def start_call_session(self):
        """Start a live call session"""
        # Initialize WebRTC
        signaling = await self.realtime_tts.initialize_webrtc()
        
        # Start speech processing loop
        asyncio.create_task(self._process_speech_queue())
        
        return signaling
    
    async def queue_speech(self, text: str, priority: int = 0):
        """Queue text for speech with priority"""
        await self.speech_queue.put((priority, text))
    
    async def interrupt_and_speak(self, text: str):
        """Interrupt current speech and speak new text"""
        # Clear current queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        # Queue high-priority speech
        await self.speech_queue.put((999, text))
    
    async def _process_speech_queue(self):
        """Process speech queue in priority order"""
        while True:
            try:
                priority, text = await self.speech_queue.get()
                await self.realtime_tts.speak_realtime(text)
                self.speech_queue.task_done()
            except Exception as e:
                logging.error(f"Error processing speech: {e}")

# Example usage for different scenarios
async def example_live_call():
    """Example: Live call with AI assistant"""
    config = RealtimeConfig(
        voice="en-US-AriaNeural",
        latency_ms=30  # Ultra-low latency for calls
    )
    
    call_tts = LiveCallTTS(config)
    signaling = await call_tts.start_call_session()
    
    # Simulate live call interactions
    await call_tts.queue_speech("Hello! How can I help you today?")
    await asyncio.sleep(2)
    await call_tts.queue_speech("I understand you need assistance with your account.")
    
    # Handle interruption
    await call_tts.interrupt_and_speak("Actually, let me check that for you right now.")

async def example_streaming_platform():
    """Example: Live streaming platform with TTS"""
    config = RealtimeConfig(
        voice="en-US-GuyNeural",  # More energetic voice
        latency_ms=100  # Slightly higher latency acceptable
    )
    
    realtime_tts = RealtimeTTS(config)
    
    # Stream to speakers for live streaming
    await realtime_tts.stream_to_speakers(
        "Welcome to our live stream! Today we'll be discussing AI and TTS technology."
    )

async def example_ai_assistant():
    """Example: AI assistant with real-time responses"""
    config = RealtimeConfig(
        voice="en-US-JennyNeural",
        latency_ms=50
    )
    
    assistant = LiveCallTTS(config)
    await assistant.start_call_session()
    
    # Simulate AI responses
    responses = [
        "I can help you with that.",
        "Let me search for the information you need.",
        "Based on my analysis, here's what I found...",
        "Is there anything else you'd like to know?"
    ]
    
    for response in responses:
        await assistant.queue_speech(response)
        await asyncio.sleep(1)  # Simulate processing time

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Real-time TTS with WebRTC Integration Examples")
    print("=" * 50)
    
    # Run examples
    asyncio.run(example_live_call())
    asyncio.run(example_streaming_platform())
    asyncio.run(example_ai_assistant())
