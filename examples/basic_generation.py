#!/usr/bin/env python3

"""
Basic example of edge_tts usage.
"""

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
    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        loop.run_until_complete(amain())
    finally:
        loop.close()
