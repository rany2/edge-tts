
"""
This module provides a serverless API for text-to-speech conversion using Edge TTS.

It includes functionality to generate audio and subtitles from input text,
utilizing the edge_tts library. The main function, `run`, is designed to be
used in a serverless environment, returning an asynchronous generator that
yields audio data and subtitles.

Dependencies:
    - edge_tts: For text-to-speech conversion
    - typing: For type hinting

Usage:
    The main entry point is the `run` function, which takes text input
    and an optional voice parameter to generate audio and subtitles.
"""

from typing import Dict
from typing import AsyncGenerator
import edge_tts

async def run(text: str, voice: str = "en-GB-SoniaNeural") -> AsyncGenerator[Dict[str, str], None]:
    """
        Asynchronously generates audio and subtitles for the given text using the specified voice.
        
        Args:
            text (str): The text to be converted to speech.
            voice (str): The voice model to use, defaults to "en-GB-SoniaNeural".
        
        Returns:
            AsyncGenerator[Dict[str, str], None]: A generator that yields dictionaries containing
    """
    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()
    audio_data = bytearray()
    subtitles = ""

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    subtitles = submaker.generate_subs()
    yield {
        "audio_data": audio_data.decode("latin-1"),
        "subtitles": subtitles
    }
