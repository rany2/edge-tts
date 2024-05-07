#!/usr/bin/env python3

"""
Example of dynamic voice selection using VoicesManager.
"""

import asyncio
import random

import edge_tts
from edge_tts import VoicesManager

TEXT = "Hoy es un buen día."
OUTPUT_FILE = "spanish.mp3"


async def amain() -> None:
    """Main function"""
    voices = await VoicesManager.create()
    voice = voices.find(Gender="Male", Language="es")
    # Also supports Locales
    # voice = voices.find(Gender="Female", Locale="es-AR")

    communicate = edge_tts.Communicate(TEXT, random.choice(voice)["Name"])
    await communicate.save(OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.run(amain())
