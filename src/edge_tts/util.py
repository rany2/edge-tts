"""Utility functions for the command line interface. Used by the main module."""

import argparse
import asyncio
import sys
from typing import Optional, TextIO

from tabulate import tabulate

from . import Communicate, SubMaker, list_voices
from .constants import DEFAULT_VOICE
from .data_classes import UtilArgs
from .progress import ProgressBar
from .version import __version__


async def _print_voices(*, proxy: Optional[str]) -> None:
    """Print all available voices."""
    voices = await list_voices(proxy=proxy)
    voices = sorted(voices, key=lambda voice: voice["ShortName"])
    headers = ["Name", "Gender", "ContentCategories", "VoicePersonalities"]
    table = [
        [
            voice["ShortName"],
            voice["Gender"],
            ", ".join(voice["VoiceTag"]["ContentCategories"]),
            ", ".join(voice["VoiceTag"]["VoicePersonalities"]),
        ]
        for voice in voices
    ]
    print(tabulate(table, headers))


def _should_show_progress(args: UtilArgs) -> bool:
    """
    Decides whether to draw a progress bar for this run.

    The bar is drawn on stderr, so anything else that wants stderr wins, and
    there is no point drawing it when stderr is not a terminal.

    Args:
        args (UtilArgs): The parsed command line arguments.

    Returns:
        bool: True if the progress bar should be drawn.
    """
    if args.no_progress:
        return False
    if args.write_subtitles == "-":
        return False
    return sys.stderr.isatty()


async def _run_tts(args: UtilArgs) -> None:
    """Run TTS after parsing arguments from command line."""

    try:
        if sys.stdin.isatty() and sys.stdout.isatty() and not args.write_media:
            print(
                "Warning: TTS output will be written to the terminal. "
                "Use --write-media to write to a file.\n"
                "Press Ctrl+C to cancel the operation. "
                "Press Enter to continue.",
                file=sys.stderr,
            )
            input()
    except KeyboardInterrupt:
        print("\nOperation canceled.", file=sys.stderr)
        return

    communicate = Communicate(
        args.text,
        args.voice,
        rate=args.rate,
        volume=args.volume,
        pitch=args.pitch,
        proxy=args.proxy,
    )
    submaker = SubMaker()
    progress = ProgressBar(args.text) if _should_show_progress(args) else None
    try:
        audio_file = (
            open(args.write_media, "wb")
            if args.write_media is not None and args.write_media != "-"
            else sys.stdout.buffer
        )
        sub_file: Optional[TextIO] = (
            open(args.write_subtitles, "w", encoding="utf-8")
            if args.write_subtitles is not None and args.write_subtitles != "-"
            else None
        )
        if sub_file is None and args.write_subtitles == "-":
            sub_file = sys.stderr

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
                if progress is not None:
                    progress.add_audio_bytes(len(chunk["data"]))
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)
                if progress is not None:
                    progress.advance(chunk["text"])
                    progress.set_audio_timeline(
                        int(chunk["offset"] + chunk["duration"])
                    )
            if progress is not None:
                progress.render()

        if progress is not None:
            progress.finish()

        if sub_file is not None:
            sub_file.write(submaker.get_srt())
    finally:
        # No-op if the run already completed; this is for the paths where it
        # did not, so a failed run does not leave a bar sitting at 99%.
        if progress is not None:
            progress.close()
        if audio_file is not sys.stdout.buffer:
            audio_file.close()
        if sub_file is not None and sub_file is not sys.stderr:
            sub_file.close()


async def amain() -> None:
    """Async main function"""
    parser = argparse.ArgumentParser(
        description="Text-to-speech using Microsoft Edge's online TTS service."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--text", help="what TTS will say")
    group.add_argument("-f", "--file", help="same as --text but read from file")
    parser.add_argument(
        "-v",
        "--voice",
        help=f"voice for TTS. Default: {DEFAULT_VOICE}",
        default=DEFAULT_VOICE,
    )
    group.add_argument(
        "-l",
        "--list-voices",
        help="lists available voices and exits",
        action="store_true",
    )
    parser.add_argument("--rate", help="set TTS rate. Default +0%%.", default="+0%")
    parser.add_argument("--volume", help="set TTS volume. Default +0%%.", default="+0%")
    parser.add_argument("--pitch", help="set TTS pitch. Default +0Hz.", default="+0Hz")
    parser.add_argument(
        "--write-media", help="send media output to file instead of stdout"
    )
    parser.add_argument(
        "--write-subtitles",
        help="send subtitle output to provided file instead of stderr",
    )
    parser.add_argument("--proxy", help="use a proxy for TTS and voice list.")
    parser.add_argument(
        "--no-progress",
        help="do not show the progress bar on stderr",
        action="store_true",
    )
    parser.add_argument(
        "--version", action="version", version=f"edge-tts {__version__}"
    )
    args = parser.parse_args(namespace=UtilArgs())

    if args.list_voices:
        await _print_voices(proxy=args.proxy)
        sys.exit(0)

    if args.file is not None:
        if args.file in ("-", "/dev/stdin"):
            args.text = sys.stdin.read()
        else:
            with open(args.file, encoding="utf-8") as file:
                args.text = file.read()

    if args.text is not None:
        await _run_tts(args)


def main() -> None:
    """Run the main function using asyncio."""
    asyncio.run(amain())


if __name__ == "__main__":
    main()
