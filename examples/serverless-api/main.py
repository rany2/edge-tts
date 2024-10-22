
import edge_tts

async def run(text: str, voice: str = "en-GB-SoniaNeural"): 

    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()
    audio_data = bytearray()
    subtitles = ""

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    subtitles = submaker.generate_subs()
    return {
        "audio_data": audio_data.decode("latin-1"),
        "subtitles": subtitles
    }