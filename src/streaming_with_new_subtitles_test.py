import asyncio
import edge_tts
from edge_tts.communicate import Communicate

TEXT = """Title: Exploring the Beauty of Mathematics

Mathematics, often regarded as the language of the universe, encompasses a myriad of concepts, from basic arithmetic to complex calculus. It's a discipline that transcends boundaries and delves into the depths of abstraction.

In mathematics, precision is paramount. Numbers dance across the page, guided by symbols such as +, -, ×, and ÷, each punctuation mark playing a crucial role in shaping equations and expressions. These symbols, like punctuation in language, clarify and organize mathematical ideas.

Consider the beauty of decimals, those subtle points that delineate fractions of wholes. They appear unassumingly yet hold profound significance in calculations. Whether it's 3.14, the beloved pi, or the golden ratio 1.618, decimals offer glimpses into the elegant patterns underlying the chaos of numbers.

But mathematics isn't just about numbers and symbols; it's about discovery and exploration. It's about unraveling the mysteries of the universe, from the microscopic world of quantum mechanics to the vast expanse of cosmology. Punctuation marks in mathematics, much like their linguistic counterparts, serve as signposts on this journey, guiding us through the intricate landscapes of mathematical thought.

So let us embrace the beauty of mathematics, where decimals and punctuation marks converge to form the tapestry of our understanding, illuminating the path to new insights and discoveries."""
# VOICE = "zh-CN-YunxiNeural"
OUTPUT_FILE = "test.mp3"
WEBVTT_FILE = "test.vtt"

async def amain() -> None:
    """Main function"""
    communicate = Communicate(TEXT,
                            #   rate="+50%",volume="+50%"
                              )
    submaker = edge_tts.SubMaker()
    with open(OUTPUT_FILE, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    with open(WEBVTT_FILE, "w", encoding="utf-8") as file:
        file.write(submaker.generate_subs_based_on_punc(TEXT))
        # file.write(submaker.generate_subs())


loop = asyncio.get_event_loop_policy().get_event_loop()
try:
    loop.run_until_complete(amain())
finally:
    loop.close()