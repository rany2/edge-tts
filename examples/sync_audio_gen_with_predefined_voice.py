#!/usr/bin/env python3

"""Sync variant of the example for generating audio with a predefined voice"""


import edge_tts

TEXT = "Hello World!"
VOICE = "en-GB-SoniaNeural"
OUTPUT_FILE = "test.mp3"


def main() -> None:
    """Main function"""
    communicate = edge_tts.Communicate(TEXT, VOICE)
    communicate.save_sync(OUTPUT_FILE)


if __name__ == "__main__":
    main()
