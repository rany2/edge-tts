"""Terminal progress bar for the command line interface.

This module knows nothing about TTS. It is fed the source text up front, then
told which parts of it have been spoken, how far the audio timeline those parts
describe reaches, and how many audio bytes have actually arrived.

Progress is measured in audio, not in text. The service sends its boundary
metadata far ahead of the audio it describes -- in a measured run the text
cursor reached 67% after 0.6 seconds while only 7 of the eventual 382 seconds
of audio had arrived -- so the text cursor is useless as a progress bar on its
own. What it is good for is a ratio: the audio timeline covered by the metadata
received so far, divided by the fraction of the text that metadata covers,
extrapolates to the total length of the audio. In that same run the estimate
settled within 1% of the true total after 0.6 seconds of a 3.9 second job.
"""

import shutil
import sys
import time
from typing import Callable, Optional, TextIO

from .constants import MP3_BITRATE_BPS, TICKS_PER_SECOND

FULL_BLOCK = "█"
# Index i holds the glyph filling i/8 of a cell; index 0 is blank.
PARTIAL_BLOCKS = " ▏▎▍▌▋▊▉"

# Keep a usable bar even in a very narrow terminal.
MIN_BAR_WIDTH = 3
DEFAULT_WIDTH = 80


def format_time(seconds: float) -> str:
    """
    Formats a duration as MM:SS, or H:MM:SS once it reaches an hour.

    Args:
        seconds (float): The duration in seconds. Truncated, not rounded, so
                         the displayed time never runs ahead of the real one.

    Returns:
        str: The formatted duration.
    """
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_bytes(num_bytes: int) -> str:
    """
    Formats a byte count as a short human readable string.

    Args:
        num_bytes (int): The number of bytes.

    Returns:
        str: The byte count in KB below one megabyte, otherwise in MB.
    """
    if num_bytes < 1024 * 1024:
        return f"{num_bytes // 1024}KB"
    return f"{num_bytes / 1024 / 1024:.1f}MB"


def render_bar(fraction: float, width: int) -> str:
    """
    Renders the bar body for the given fill fraction.

    Args:
        fraction (float): The fill fraction, between 0 and 1.
        width (int): The width of the bar in characters.

    Returns:
        str: The bar body, always exactly `width` characters long.
    """
    filled = fraction * width
    whole = int(filled)
    if whole >= width:
        return FULL_BLOCK * width
    partial = PARTIAL_BLOCKS[min(len(PARTIAL_BLOCKS) - 1, int((filled - whole) * 8))]
    return FULL_BLOCK * whole + partial + " " * (width - whole - 1)


class ProgressBar:
    """
    A single line, in place progress bar for a TTS run.

    Fed by `advance`, `set_audio_timeline` and `add_audio_bytes`; drawn by
    `render`; ended by `finish` on success or `close` on failure.
    """

    # pylint: disable=too-many-arguments,too-many-instance-attributes
    def __init__(
        self,
        text: str,
        stream: Optional[TextIO] = None,
        width: Optional[int] = None,
        min_interval: float = 0.1,
        time_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        self._text = text
        self._stream: TextIO = stream if stream is not None else sys.stderr
        if width is None:
            width = shutil.get_terminal_size((DEFAULT_WIDTH, 24)).columns - 1
        self._width = width
        self._min_interval = min_interval
        self._time_fn = time_fn

        self._cursor = 0
        self._audio_bytes = 0
        self._timeline_ticks = 0
        self._start = time_fn()
        self._last_render: Optional[float] = None
        self._fraction = 0.0
        self._complete = False
        self._finished = False

    @property
    def text_fraction(self) -> float:
        """The fraction of the source text spoken so far, between 0 and 1."""
        if not self._text:
            return 0.0
        return min(1.0, self._cursor / len(self._text))

    @property
    def fraction(self) -> float:
        """
        The fraction of the audio received so far, between 0 and 1.

        Zero until the first boundary event arrives, since until then there is
        nothing to estimate the total length from. Never decreases: when the
        remaining text turns out to speak for longer than extrapolated, the bar
        holds rather than rewinding.
        """
        if self._complete:
            return 1.0
        estimated_total = self._estimated_total_seconds()
        if estimated_total > 0:
            self._fraction = max(
                self._fraction, min(1.0, self._received_seconds() / estimated_total)
            )
        return self._fraction

    def _received_seconds(self) -> float:
        """Seconds of audio received, by exact CBR byte arithmetic."""
        return self._audio_bytes * 8 / MP3_BITRATE_BPS

    def _estimated_total_seconds(self) -> float:
        """
        Estimated length of the complete audio, or 0 if not yet knowable.

        The metadata received so far describes the audio up to
        `_timeline_ticks` and covers `text_fraction` of the text, so the whole
        text extrapolates to `timeline / text_fraction`. Once the metadata
        covers all of the text this stops being an extrapolation and becomes
        the exact total.
        """
        text_fraction = self.text_fraction
        if text_fraction <= 0 or self._timeline_ticks <= 0:
            return 0.0
        return self._timeline_ticks / TICKS_PER_SECOND / text_fraction

    def advance(self, spoken_text: str) -> None:
        """
        Moves the cursor past the given piece of spoken text.

        The piece is searched for from the current cursor onwards, so repeated
        words advance to their next occurrence and the cursor never moves
        backwards. Text that cannot be found is ignored.

        Args:
            spoken_text (str): The text from a boundary event.

        Returns:
            None
        """
        if not spoken_text:
            return
        found = self._text.find(spoken_text, self._cursor)
        if found >= 0:
            self._cursor = found + len(spoken_text)

    def set_audio_timeline(self, ticks: int) -> None:
        """
        Records how far into the audio the metadata received so far reaches.

        Args:
            ticks (int): The end of the latest boundary event on the audio
                         timeline, in 100-nanosecond ticks; that is, its
                         offset plus its duration.

        Returns:
            None
        """
        self._timeline_ticks = max(self._timeline_ticks, ticks)

    def add_audio_bytes(self, num_bytes: int) -> None:
        """
        Adds to the count of audio bytes received.

        Args:
            num_bytes (int): The number of bytes in the latest audio chunk.

        Returns:
            None
        """
        self._audio_bytes += num_bytes

    def render(self) -> None:
        """
        Redraws the bar in place, at most once per `min_interval` seconds.

        Returns:
            None
        """
        now = self._time_fn()
        if (
            self._last_render is not None
            and now - self._last_render < self._min_interval
        ):
            return
        self._last_render = now
        self._write(self._line())

    def finish(self) -> None:
        """
        Fills the bar to 100%, ends the line and stops further drawing.

        The estimated total is never exactly right, so a completed run is
        declared complete rather than left a percent short.

        Returns:
            None
        """
        if self._finished:
            return
        self._finished = True
        self._complete = True
        self._write(self._line(), end="\n")

    def close(self) -> None:
        """
        Ends the line without claiming the run completed.

        Used when the run is abandoned, so a failed run is not left showing a
        bar filled in to 100%.

        Returns:
            None
        """
        if self._finished:
            return
        self._finished = True
        if self._last_render is not None:
            self._stream.write("\n")
            self._stream.flush()

    def _line(self) -> str:
        fraction = self.fraction
        elapsed = self._time_fn() - self._start
        eta = format_time(elapsed / fraction - elapsed) if fraction > 0 else "--:--"
        prefix = f"{int(fraction * 100):3d}%|"
        suffix = f"| {format_bytes(self._audio_bytes)}  {format_time(elapsed)}<{eta}"
        bar_width = max(MIN_BAR_WIDTH, self._width - len(prefix) - len(suffix))
        return prefix + render_bar(fraction, bar_width) + suffix

    def _write(self, line: str, end: str = "") -> None:
        self._stream.write("\r" + line.ljust(self._width) + end)
        self._stream.flush()
