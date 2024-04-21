#!/usr/bin/env python3

"""
This example shows the sync version of stream function which also
works when run from a sync function called itself from an async function.
"""

import asyncio

import edge_tts

TEXT = "Hello World!"
VOICE = "en-GB-SoniaNeural"
OUTPUT_FILE = "test.mp3"


def main() -> None:
    """Main function to process audio and metadata synchronously."""
    communicate = edge_tts.Communicate(TEXT, VOICE)
    with open(OUTPUT_FILE, "wb") as file:
        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                print(f"WordBoundary: {chunk}")


async def amain() -> None:
    """ "
    Async main function to call sync main function

    This demonstrates that this works even when called from an async function.
    """
    main()


if __name__ == "__main__":
    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        loop.run_until_complete(amain())
    finally:
        loop.close()
