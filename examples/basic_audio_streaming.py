#!/usr/bin/env python3

"""
Basic audio streaming example.

This example shows how to stream the audio data from the TTS engine,
and how to get the WordBoundary events from the engine (which could
be ignored if not needed).

The example streaming_with_subtitles.py shows how to use the
WordBoundary events to create subtitles using SubMaker.
"""

import asyncio

import edge_tts

TEXT = "Hello World!"
VOICE = "en-GB-SoniaNeural"
OUTPUT_FILE = "test.mp3"


async def _main() -> None:
    communicate = edge_tts.Communicate(TEXT, VOICE)
    with open(OUTPUT_FILE, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                print(f"WordBoundary: {chunk}")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(_main())
