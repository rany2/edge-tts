"""
Main package.
"""


import argparse
import asyncio
import sys
from io import BufferedWriter
from typing import Any

from edge_tts import Communicate, SubMaker, list_voices


async def _print_voices(*, proxy: str) -> None:
    """Print all available voices."""
    for idx, voice in enumerate(await list_voices(proxy=proxy)):
        if idx != 0:
            print()

        for key in voice.keys():
            if key in (
                "SuggestedCodec",
                "FriendlyName",
                "Status",
                "VoiceTag",
                "Name",
                "Locale",
            ):
                continue
            pretty_key_name = key if key != "ShortName" else "Name"
            print(f"{pretty_key_name}: {voice[key]}")


async def _run_tts(args: Any) -> None:
    """Run TTS after parsing arguments from command line."""
    tts = Communicate(
        args.text,
        args.voice,
        proxy=args.proxy,
        rate=args.rate,
        volume=args.volume,
    )
    try:
        media_file = None
        if args.write_media:
            media_file = open(args.write_media, "wb")

        subs = SubMaker(args.overlapping)
        async for data in tts.stream():
            if data["type"] == "audio":
                if isinstance(media_file, BufferedWriter):
                    media_file.write(data["data"])
                else:
                    sys.stdout.buffer.write(data["data"])
            elif data["type"] == "WordBoundary":
                subs.create_sub((data["offset"], data["duration"]), data["text"])

        if not args.write_subtitles:
            sys.stderr.write(subs.generate_subs())
        else:
            with open(args.write_subtitles, "w", encoding="utf-8") as file:
                file.write(subs.generate_subs())
    finally:
        if media_file is not None:
            media_file.close()


async def _async_main() -> None:
    parser = argparse.ArgumentParser(description="Microsoft Edge TTS")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--text", help="what TTS will say")
    group.add_argument("-f", "--file", help="same as --text but read from file")
    parser.add_argument(
        "-v",
        "--voice",
        help="voice for TTS. " "Default: en-US-AriaNeural",
        default="en-US-AriaNeural",
    )
    group.add_argument(
        "-l",
        "--list-voices",
        help="lists available voices",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--pitch",
        help="set TTS pitch. Default +0Hz, For more info check https://bit.ly/3eAE5Nx",
        default="+0Hz",
    )
    parser.add_argument(
        "-r",
        "--rate",
        help="set TTS rate. Default +0%%. For more info check https://bit.ly/3eAE5Nx",
        default="+0%",
    )
    parser.add_argument(
        "-V",
        "--volume",
        help="set TTS volume. Default +0%%. For more info check https://bit.ly/3eAE5Nx",
        default="+0%",
    )
    parser.add_argument(
        "-O",
        "--overlapping",
        help="overlapping subtitles in seconds",
        default=1,
        type=float,
    )
    parser.add_argument(
        "--write-media", help="send media output to file instead of stdout"
    )
    parser.add_argument(
        "--write-subtitles",
        help="send subtitle output to provided file instead of stderr",
    )
    parser.add_argument("--proxy", help="use a proxy for TTS and voice list.")
    args = parser.parse_args()

    if args.list_voices:
        await _print_voices(proxy=args.proxy)
        sys.exit(0)

    if args.text is not None or args.file is not None:
        if args.file is not None:
            # we need to use sys.stdin.read() because some devices
            # like Windows and Termux don't have a /dev/stdin.
            if args.file == "/dev/stdin":
                # logger.debug("stdin detected, reading natively from stdin")
                args.text = sys.stdin.read()
            else:
                # logger.debug("reading from %s" % args.file)
                with open(args.file, "r", encoding="utf-8") as file:
                    args.text = file.read()

        await _run_tts(args)


def main() -> None:
    """Run the main function using asyncio."""
    asyncio.get_event_loop().run_until_complete(_async_main())


if __name__ == "__main__":
    main()
