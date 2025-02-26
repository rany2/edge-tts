"""Main entrypoint for the edge-playback package."""

import argparse
import os
import subprocess
import sys
import tempfile
from shutil import which

from .util import pr_err


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

    use_mpv = sys.platform != "win32" or args.mpv

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

        if not srt_fname and use_mpv:
            subtitle = tempfile.NamedTemporaryFile(suffix=".srt", delete=False)
            subtitle.close()
            srt_fname = subtitle.name

        print(f"Media file: {mp3_fname}")
        print(f"Subtitle file: {srt_fname}\n")

        edge_tts_cmd = ["edge-tts", f"--write-media={mp3_fname}"]
        if srt_fname:
            edge_tts_cmd.append(f"--write-subtitles={srt_fname}")
        edge_tts_cmd = edge_tts_cmd + tts_args
        with subprocess.Popen(edge_tts_cmd) as process:
            process.communicate()

        if sys.platform == "win32" and not use_mpv:
            # pylint: disable-next=import-outside-toplevel
            from .win32_playback import play_mp3_win32

            play_mp3_win32(mp3_fname)
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
