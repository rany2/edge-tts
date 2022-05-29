#!/usr/bin/env python3

"""
Playback TTS with subtitles using edge-tts and mpv.
"""

import os
import subprocess
import sys
import tempfile
from shutil import which


def main():
    """
    Main function.
    """
    if which("mpv") and which("edge-tts"):
        media = tempfile.NamedTemporaryFile(delete=False)
        subtitle = tempfile.NamedTemporaryFile(delete=False)
        try:
            media.close()
            subtitle.close()

            print()
            print(f"Media file: {media.name}")
            print(f"Subtitle file: {subtitle.name}\n")
            with subprocess.Popen(
                [
                    "edge-tts",
                    "--boundary-type=1",
                    f"--write-media={media.name}",
                    f"--write-subtitles={subtitle.name}",
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
        finally:
            os.unlink(media.name)
            os.unlink(subtitle.name)
    else:
        print("This script requires mpv and edge-tts.")


if __name__ == "__main__":
    main()
