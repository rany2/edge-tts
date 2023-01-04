import asyncio
import edge_tts
from edge_tts import VoicesManager
import random

async def main():
    """
    Main function
    """
    voices = await VoicesManager.create()
    voice = voices.find(Gender="Male", Language="es")  
    # Also supports Locales
    # voice = voices.find(Gender="Female", Locale="es-AR")
    VOICE = random.choice(voice)["ShortName"]
    TEXT = "Hoy es un buen día."
    OUTPUT_FILE = "spanish.mp3"

    communicate = edge_tts.Communicate()

    with open(OUTPUT_FILE, "wb") as f:
        async for i in communicate.run(TEXT, voice=VOICE):
            if i[2] is not None:
                f.write(i[2])

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
