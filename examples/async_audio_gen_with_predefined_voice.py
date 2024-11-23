#!/usr/bin/env python3

"""Simple example to generate audio with preset voice using async/await"""

import asyncio

import edge_tts

TEXT = "Hello World!"
VOICE = "en-GB-SoniaNeural"
OUTPUT_FILE = "test.mp3"


async def amain() -> None:
    """Main function"""
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.run(amain())
