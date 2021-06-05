#!/usr/bin/env python3

# Example Python script that shows how to use edge-tts as a module

import asyncio
import edgeTTS
import time
import tempfile
from playsound import playsound

async def main():
	ask = input("What do you want TTS to say? ")
	with tempfile.NamedTemporaryFile() as fp:
		async for i in edgeTTS.run_tts(edgeTTS.mkssmlmsg(ask)): # default Aria, audio-24khz-48kbitrate-mono-mp3, etc..
			fp.write(i)
		playsound(fp.name)

if __name__ == "__main__":
	asyncio.run(main())
