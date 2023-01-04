#!/usr/bin/env python3

"""
Basic example of edge_tts usage.
"""

import asyncio

import edge_tts


async def main() -> None:
    TEXT = "Hello World!"
    VOICE = "en-GB-SoniaNeural"
    OUTPUT_FILE = "test.mp3"

    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
