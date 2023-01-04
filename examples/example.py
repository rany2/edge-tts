#!/usr/bin/env python3
"""
Example Python script that shows how to use edge-tts as a module
"""

import asyncio
import edge_tts

async def main():
    """
    Main function
    """
    TEXT = "Hello World!"
    VOICE = "en-GB-SoniaNeural"
    OUTPUT_FILE = "test.mp3"

    communicate = edge_tts.Communicate()
    with open(OUTPUT_FILE, "wb") as f:
        async for i in communicate.run(TEXT, voice=VOICE):
            if i[2] is not None:
                f.write(i[2])

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())