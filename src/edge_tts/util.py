"""
Main package.
"""


import argparse
import asyncio
import sys

from edge_tts import Communicate, SubMaker, list_voices


async def _list_voices():
    """
    List available voices.
    """
    for idx, voice in enumerate(await list_voices()):
        if idx != 0:
            print()

        for key in voice.keys():
            if key in ["SuggestedCodec", "FriendlyName", "Status"]:
                continue
            # print ("%s: %s" % ("Name" if key == "ShortName" else key, voice[key]))
            print(f"{key}: {voice[key]}")


async def _tts(args):
    tts = Communicate()
    subs = SubMaker(args.overlapping)
    if args.write_media:
        media_file = open(args.write_media, "wb")  # pylint: disable=consider-using-with
    async for i in tts.run(
        args.text,
        args.boundary_type,
        args.codec,
        args.voice,
        args.pitch,
        args.rate,
        args.volume,
        customspeak=args.custom_ssml,
    ):
        if i[2] is not None:
            if not args.write_media:
                sys.stdout.buffer.write(i[2])
            else:
                media_file.write(i[2])
        elif i[0] is not None and i[1] is not None:
            subs.create_sub(i[0], i[1])
    if args.write_media:
        media_file.close()
    if not args.write_subtitles:
        sys.stderr.write(subs.generate_subs())
    else:
        with open(args.write_subtitles, "w", encoding="utf-8") as file:
            file.write(subs.generate_subs())


async def _main():
    parser = argparse.ArgumentParser(description="Microsoft Edge TTS")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--text", help="what TTS will say")
    group.add_argument("-f", "--file", help="same as --text but read from file")
    parser.add_argument(
        "-z",
        "--custom-ssml",
        help="treat text as ssml to send. For more info check https://bit.ly/3fIq13S",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--voice",
        help="voice for TTS. "
        "Default: Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)",
        default="Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)",
    )
    parser.add_argument(
        "-c",
        "--codec",
        help="codec format. Default: audio-24khz-48kbitrate-mono-mp3. "
        "Another choice is webm-24khz-16bit-mono-opus. "
        "For more info check https://bit.ly/2T33h6S",
        default="audio-24khz-48kbitrate-mono-mp3",
    )
    group.add_argument(
        "-l",
        "--list-voices",
        help="lists available voices. "
        "Edge's list is incomplete so check https://bit.ly/2SFq1d3",
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
        default=5,
        type=float,
    )
    parser.add_argument(
        "-b",
        "--boundary-type",
        help="set boundary type for subtitles. Default 0 for none. Set 1 for word_boundary, 2 for sentence_boundary",
        default=0,
        type=int,
    )
    parser.add_argument(
        "--write-media", help="instead of stdout, send media output to provided file"
    )
    parser.add_argument(
        "--write-subtitles",
        help="instead of stderr, send subtitle output to provided file",
    )
    args = parser.parse_args()

    if args.list_voices:
        await _list_voices()
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

        await _tts(args)


def main():
    """
    Main function.
    """
    asyncio.run(_main())


if __name__ == "__main__":
    main()
