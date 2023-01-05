#!/usr/bin/env python3

"""
Playback TTS with subtitles using edge-tts and mpv.
"""

import subprocess
import sys
import tempfile
from shutil import which


def _main() -> None:
    depcheck_failed = False
    if not which("mpv"):
        print("mpv is not installed.", file=sys.stderr)
        depcheck_failed = True
    if not which("edge-tts"):
        print("edge-tts is not installed.", file=sys.stderr)
        depcheck_failed = True
    if depcheck_failed:
        print("Please install the missing dependencies.", file=sys.stderr)
        sys.exit(1)

    with tempfile.NamedTemporaryFile(
        suffix=".mp3", delete=False
    ) as media, tempfile.NamedTemporaryFile(suffix=".vtt", delete=False) as subtitle:
        media.close()
        subtitle.close()

        print(f"Media file: {media.name}")
        print(f"Subtitle file: {subtitle.name}\n")
        with subprocess.Popen(
            [
                "edge-tts",
                f"--write-media={media.name}",
                f"--write-subtitles={subtitle.name}",
            ]
            + sys.argv[1:]
        ) as process:
            process.communicate()

        with subprocess.Popen(
            [
                "mpv",
                f"--sub-file={subtitle.name}",
                media.name,
            ]
        ) as process:
            process.communicate()


if __name__ == "__main__":
    _main()
