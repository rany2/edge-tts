"""Main entrypoint for the edge-playback package."""

import argparse
import ctypes
import os
import platform
import subprocess
import sys
import tempfile
from shutil import which


def pr_err(msg: str) -> None:
    """Print to stderr."""
    print(msg, file=sys.stderr)


def _main() -> None:
    depcheck_failed = False

    parser = argparse.ArgumentParser(
        prog="edge-playback",
        description="Speak text using Microsoft Edge's online text-to-speech API",
        epilog="See `edge-tts` for additional arguments",
    )
    parser.add_argument(
        "--mpv",
        action="store_true",
        help="Use mpv to play audio. By default, false on Windows and true on all other platforms",
    )
    args, tts_args = parser.parse_known_args()

    use_mpv = platform.system() != "Windows" or args.mpv

    deps = ["edge-tts"]
    if use_mpv:
        deps.append("mpv")

    for dep in deps:
        if not which(dep):
            pr_err(f"{dep} is not installed.")
            depcheck_failed = True

    if depcheck_failed:
        pr_err("Please install the missing dependencies.")
        sys.exit(1)

    keep = os.environ.get("EDGE_PLAYBACK_KEEP_TEMP") is not None
    mp3_fname = os.environ.get("EDGE_PLAYBACK_MP3_FILE")
    srt_fname = os.environ.get("EDGE_PLAYBACK_SRT_FILE")
    media, subtitle = None, None
    try:
        if not mp3_fname:
            media = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            media.close()
            mp3_fname = media.name

        if not srt_fname:
            subtitle = tempfile.NamedTemporaryFile(suffix=".srt", delete=False)
            subtitle.close()
            srt_fname = subtitle.name

        print(f"Media file: {mp3_fname}")
        print(f"Subtitle file: {srt_fname}\n")
        with subprocess.Popen(
            [
                "edge-tts",
                f"--write-media={mp3_fname}",
                f"--write-subtitles={srt_fname}",
            ]
            + tts_args
        ) as process:
            process.communicate()

        if platform.system() == "Windows" and not use_mpv:

            def mci_send(msg: str) -> None:
                result = ctypes.windll.winmm.mciSendStringW(msg, 0, 0, 0)
                if result != 0:
                    print(f"Error {result} in mciSendString {msg}")

            mci_send("Close All")
            mci_send(f'Open "{mp3_fname}" Type MPEGVideo Alias theMP3')
            mci_send("Play theMP3 Wait")
            mci_send("Close theMP3")
        else:
            with subprocess.Popen(
                [
                    "mpv",
                    f"--sub-file={srt_fname}",
                    mp3_fname,
                ]
            ) as process:
                process.communicate()
    finally:
        if keep:
            print(f"\nKeeping temporary files: {mp3_fname} and {srt_fname}")
        else:
            if mp3_fname is not None and os.path.exists(mp3_fname):
                os.unlink(mp3_fname)
            if srt_fname is not None and os.path.exists(srt_fname):
                os.unlink(srt_fname)


if __name__ == "__main__":
    _main()
