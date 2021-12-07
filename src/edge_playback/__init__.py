#!/usr/bin/env python3

"""
Playback TTS with subtitles using edge-tts and mpv.
"""

import subprocess
import sys
import tempfile
from shutil import which


def main():
    """
    Main function.
    """
    if which("mpv") and which("edge-tts"):
        with tempfile.NamedTemporaryFile() as media:
            with tempfile.NamedTemporaryFile() as subtitle:
                print()
                print(f"Media file      {media.name}")
                print(f"Subtitle file   {subtitle.name}\n")
                with subprocess.Popen(
                    [
                        "edge-tts",
                        "-w",
                        "--write-media",
                        media.name,
                        "--write-subtitles",
                        subtitle.name,
                    ]
                    + sys.argv[1:]
                ) as process:
                    process.communicate()

                with subprocess.Popen(
                    [
                        "mpv",
                        "--keep-open=yes",
                        f"--sub-file={subtitle.name}",
                        media.name,
                    ]
                ) as process:
                    process.communicate()
    else:
        print("This script requires mpv and edge-tts.")


if __name__ == "__main__":
    main()
