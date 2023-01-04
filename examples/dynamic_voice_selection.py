#!/usr/bin/env python3

"""
Example of dynamic voice selection using VoicesManager.
"""

import asyncio
import random

import edge_tts
from edge_tts import VoicesManager


async def main():
    voices = await VoicesManager.create()
    voice = voices.find(Gender="Male", Language="es")
    # Also supports Locales
    # voice = voices.find(Gender="Female", Locale="es-AR")
    VOICE = random.choice(voice)["ShortName"]
    TEXT = "Hoy es un buen día."
    OUTPUT_FILE = "spanish.mp3"

    communicate = edge_tts.Communicate(TEXT, VOICE)
    communicate.save(OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
