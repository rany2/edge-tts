#!/usr/bin/env python3
# Example Python script that shows how to use edge-tts as a module
import asyncio
import tempfile
import edgeTTS
from playsound import playsound

async def main():
    communicate = edgeTTS.Communicate()
    ask = input("What do you want TTS to say? ")
    with tempfile.NamedTemporaryFile() as fp:
        async for i in communicate.run(ask):
            if i[2] is not None:
                fp.write(i[2])
        playsound(fp.name)

if __name__ == "__main__":
    asyncio.run(main())
