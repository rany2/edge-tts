#!/usr/bin/env python3
# Example Python script that shows how to use edge-tts as a module
import asyncio
import tempfile
import edgeTTS as e
from playsound import playsound

async def main():
	ask = input("What do you want TTS to say? ")
	overhead = len(e.mkssmlmsg('').encode('utf-8'))
	ask = e._minimize(e.escape(e.removeIncompatibleControlChars(ask)), b" ", 2**16 - overhead)
	with tempfile.NamedTemporaryFile() as fp:
		for part in ask:
			async for i in e.run_tts(e.mkssmlmsg(part.decode('utf-8'))):
				fp.write(i)
		playsound(fp.name)

if __name__ == "__main__":
	asyncio.run(main())
