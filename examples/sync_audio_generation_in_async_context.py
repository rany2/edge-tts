#!/usr/bin/env python3

"""
This example shows that sync version of save function also works when run from 
a sync function called itself from an async function.
The simple implementation of save_sync() with only asyncio.run would fail in this scenario, 
that's why ThreadPoolExecutor is used in implementation.

"""

import asyncio

import edge_tts

TEXT = "Hello World!"
VOICE = "en-GB-SoniaNeural"
OUTPUT_FILE = "test.mp3"


def sync_main() -> None:
    """Main function"""
    communicate = edge_tts.Communicate(TEXT, VOICE)
    communicate.save_sync(OUTPUT_FILE)


async def amain() -> None:
    """Main function"""
    sync_main()


if __name__ == "__main__":
    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        loop.run_until_complete(amain())
    finally:
        loop.close()
