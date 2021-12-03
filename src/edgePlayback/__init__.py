#!/usr/bin/env python3

import subprocess
import sys
import tempfile
from shutil import which


def main():
    if which("mpv") and which("edge-tts"):
        with tempfile.NamedTemporaryFile() as media:
            with tempfile.NamedTemporaryFile() as subtitle:
                print()
                print("Media file      %s" % media.name)
                print("Subtitle file   %s\n" % subtitle.name)
                p = subprocess.Popen(
                    [
                        "edge-tts",
                        "-w",
                        "--write-media",
                        media.name,
                        "--write-subtitles",
                        subtitle.name,
                    ]
                    + sys.argv[1:]
                )
                p.communicate()
                p = subprocess.Popen(
                    [
                        "mpv",
                        "--keep-open=yes",
                        "--sub-file=" + subtitle.name,
                        media.name,
                    ]
                )
                p.communicate()
    else:
        print("This script requires mpv and edge-tts.")


if __name__ == "__main__":
    main()
