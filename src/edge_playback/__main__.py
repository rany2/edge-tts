"""Main entrypoint for the edge-playback package."""

import argparse
import os
import subprocess
import sys
import tempfile
from shutil import which
from typing import List, Optional, Tuple

from .util import pr_err


def _parse_args() -> Tuple[bool, List[str]]:
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
    return use_mpv, tts_args


def _check_deps(use_mpv: bool) -> None:
    depcheck_failed = False
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


def _create_temp_files(
    use_mpv: bool, mp3_fname: Optional[str], srt_fname: Optional[str], debug: bool
) -> Tuple[str, Optional[str]]:
    media = subtitle = None
    if not mp3_fname:
        media = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        media.close()
        mp3_fname = media.name
        if debug:
            print(f"Media file: {mp3_fname}")

    if not srt_fname and use_mpv:
        subtitle = tempfile.NamedTemporaryFile(suffix=".srt", delete=False)
        subtitle.close()
        srt_fname = subtitle.name

    if debug and srt_fname:
        print(f"Subtitle file: {srt_fname}\n")

    return mp3_fname, srt_fname


def _run_edge_tts(
    mp3_fname: str, srt_fname: Optional[str], tts_args: List[str]
) -> None:
    edge_tts_cmd = ["edge-tts", f"--write-media={mp3_fname}"]
    if srt_fname:
        edge_tts_cmd.append(f"--write-subtitles={srt_fname}")
    edge_tts_cmd = edge_tts_cmd + tts_args
    with subprocess.Popen(edge_tts_cmd) as process:
        process.communicate()


def _play_media(use_mpv: bool, mp3_fname: str, srt_fname: Optional[str]) -> None:
    if sys.platform == "win32" and not use_mpv:
        # pylint: disable-next=import-outside-toplevel
        from .win32_playback import play_mp3_win32

        play_mp3_win32(mp3_fname)
        return

    mpv_cmd = [
        "mpv",
        "--msg-level=all=error,statusline=status",
    ]
    if srt_fname:
        mpv_cmd.append(f"--sub-file={srt_fname}")
    mpv_cmd.append(mp3_fname)
    with subprocess.Popen(mpv_cmd) as process:
        process.communicate()


def _cleanup(mp3_fname: Optional[str], srt_fname: Optional[str], keep: bool) -> None:
    if keep and mp3_fname is not None:
        print(f"\nKeeping temporary files: {mp3_fname}", end="")
        if srt_fname:
            print(f" and {srt_fname}", end="")
        print()
        return

    if mp3_fname is not None and os.path.exists(mp3_fname):
        os.unlink(mp3_fname)
    if srt_fname is not None and os.path.exists(srt_fname):
        os.unlink(srt_fname)


def _main() -> None:
    use_mpv, tts_args = _parse_args()
    _check_deps(use_mpv)

    debug = os.environ.get("EDGE_PLAYBACK_DEBUG") is not None
    keep = os.environ.get("EDGE_PLAYBACK_KEEP_TEMP") is not None
    mp3_fname = os.environ.get("EDGE_PLAYBACK_MP3_FILE")
    srt_fname = os.environ.get("EDGE_PLAYBACK_SRT_FILE")

    try:
        mp3_fname, srt_fname = _create_temp_files(use_mpv, mp3_fname, srt_fname, debug)
        _run_edge_tts(mp3_fname, srt_fname, tts_args)
        _play_media(use_mpv, mp3_fname, srt_fname)
    finally:
        _cleanup(mp3_fname, srt_fname, keep)


if __name__ == "__main__":
    _main()
