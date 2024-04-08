#!/usr/bin/env python3

"""
Streaming TTS example with subtitles.

This example is similar to the example basic_audio_streaming.py, but it shows
WordBoundary events to create subtitles using SubMaker.
"""

import asyncio

import edge_tts

TEXT = "Hello World!"
VOICE = "en-GB-SoniaNeural"
OUTPUT_FILE = "test.mp3"
WEBVTT_FILE = "test.vtt"


async def amain() -> None:
    """Main function"""
    communicate = edge_tts.Communicate(TEXT, VOICE)
    submaker = edge_tts.SubMaker()
    with open(OUTPUT_FILE, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    with open(WEBVTT_FILE, "w", encoding="utf-8") as file:
        file.write(submaker.generate_subs())


if __name__ == "__main__":
    asyncio.run(amain())
