#!/usr/bin/env python3

"""Unit tests for edge_tts.progress. Requires no network access.

Run from the repository root:

    python tests/002-progress.py
"""

import io
import os
import sys
from typing import Tuple

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
)

from edge_tts.progress import (  # noqa: E402
    ProgressBar,
    format_bytes,
    format_time,
    render_bar,
)


class FakeClock:
    """Manually advanced clock, so tests never depend on wall time."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        """Move the clock forward."""
        self.now += seconds


def audio_bytes_for(seconds: float) -> int:
    """Bytes of 48 kbps CBR MP3 holding the given number of seconds."""
    return int(seconds * 48000 / 8)


def ticks(seconds: float) -> int:
    """The given number of seconds as 100-nanosecond metadata ticks."""
    return int(seconds * 10_000_000)


def make_bar(
    text: str, width: int = 40, min_interval: float = 0.1
) -> Tuple[ProgressBar, io.StringIO, FakeClock]:
    """Build a ProgressBar writing to a StringIO with a fake clock."""
    stream = io.StringIO()
    clock = FakeClock()
    bar = ProgressBar(
        text,
        stream=stream,
        width=width,
        min_interval=min_interval,
        time_fn=clock,
    )
    return bar, stream, clock


def test_format_time() -> None:
    """Durations render as MM:SS, or H:MM:SS past an hour."""
    assert format_time(0) == "00:00"
    assert format_time(5) == "00:05"
    assert format_time(65) == "01:05"
    assert format_time(599) == "09:59"
    assert format_time(3600) == "1:00:00"
    assert format_time(3725) == "1:02:05"
    # Fractional seconds truncate rather than round up past the total.
    assert format_time(65.9) == "01:05"


def test_format_bytes() -> None:
    """Byte counts render in KB below a megabyte, in MB above it."""
    assert format_bytes(0) == "0KB"
    assert format_bytes(1024) == "1KB"
    assert format_bytes(1024 * 512) == "512KB"
    assert format_bytes(1024 * 1024) == "1.0MB"
    assert format_bytes(int(1024 * 1024 * 2.1)) == "2.1MB"


def test_render_bar_is_always_exactly_width() -> None:
    """Whatever the fill, the body occupies the full width."""
    for fraction in (0.0, 0.01, 0.333, 0.5, 0.999, 1.0):
        for width in (3, 10, 37):
            assert len(render_bar(fraction, width)) == width, (fraction, width)
    assert render_bar(1.0, 5) == "█████"
    assert render_bar(0.0, 5) == "     "
    assert render_bar(0.5, 4) == "██  "


# --- text cursor: the ratio used to extrapolate the total audio length ---


def test_text_fraction_tracks_spoken_text() -> None:
    """The cursor follows the boundary metadata through the source text."""
    text = "Hello world. Foo bar."
    bar, _, _ = make_bar(text)
    assert bar.text_fraction == 0.0

    bar.advance("Hello world.")
    assert bar.text_fraction == 12 / len(text)

    bar.advance("Foo bar.")
    assert bar.text_fraction == 1.0


def test_advance_ignores_unmatched_text() -> None:
    """Metadata that does not appear in the source must not move the cursor."""
    bar, _, _ = make_bar("Hello world.")
    bar.advance("Hello")
    before = bar.text_fraction
    bar.advance("not in the source text")
    assert bar.text_fraction == before
    bar.advance("")
    assert bar.text_fraction == before


def test_cursor_moves_forward_through_repeats() -> None:
    """A repeated word must match the next occurrence, not an earlier one."""
    text = "a b a b"
    bar, _, _ = make_bar(text)
    bar.advance("a")
    assert bar.text_fraction == 1 / 7
    bar.advance("b")
    assert bar.text_fraction == 3 / 7
    bar.advance("a")  # must find the SECOND "a", at index 4
    assert bar.text_fraction == 5 / 7


def test_text_fraction_never_exceeds_one() -> None:
    """Repeated metadata cannot push the cursor past the end."""
    bar, _, _ = make_bar("abc")
    bar.advance("abc")
    bar.advance("abc")
    assert bar.text_fraction == 1.0


# --- progress: received audio over the extrapolated total ---


def test_fraction_is_unknown_before_any_metadata() -> None:
    """Audio alone says nothing about the total, so progress stays at zero."""
    bar, stream, clock = make_bar("x" * 100)
    bar.add_audio_bytes(audio_bytes_for(10))
    assert bar.fraction == 0.0
    clock.advance(1)
    bar.render()
    out = stream.getvalue()
    assert "  0%" in out, repr(out)
    assert "--:--" in out, repr(out)


def test_fraction_extrapolates_total_from_metadata() -> None:
    """100s of audio timeline covering half the text implies a 200s total."""
    bar, _, _ = make_bar("x" * 100)
    bar.advance("x" * 50)
    bar.set_audio_timeline(ticks(100))
    bar.add_audio_bytes(audio_bytes_for(50))
    assert bar.fraction == 0.25
    bar.add_audio_bytes(audio_bytes_for(50))
    assert bar.fraction == 0.5


def test_fraction_is_exact_once_metadata_covers_all_text() -> None:
    """With the whole text spoken, the timeline IS the total; no extrapolation."""
    bar, _, _ = make_bar("x" * 100)
    bar.advance("x" * 100)
    bar.set_audio_timeline(ticks(300))
    bar.add_audio_bytes(audio_bytes_for(150))
    assert bar.fraction == 0.5


def test_fraction_never_goes_backwards() -> None:
    """A total that turns out larger must hold the bar, not rewind it."""
    bar, _, _ = make_bar("x" * 100)
    bar.advance("x" * 80)
    bar.set_audio_timeline(ticks(80))  # extrapolated total: 100s
    bar.add_audio_bytes(audio_bytes_for(50))
    assert bar.fraction == 0.5

    # Later text turns out much longer than extrapolated: total becomes 200s,
    # which would drop the raw ratio to 0.25.
    bar.advance("x" * 20)
    bar.set_audio_timeline(ticks(200))
    assert bar.fraction == 0.5


def test_fraction_never_exceeds_one() -> None:
    """More audio than the estimate predicted still reads as 100%."""
    bar, _, _ = make_bar("x" * 100)
    bar.advance("x" * 100)
    bar.set_audio_timeline(ticks(100))
    bar.add_audio_bytes(audio_bytes_for(500))
    assert bar.fraction == 1.0


def test_empty_text_does_not_divide_by_zero() -> None:
    """An empty input must not crash the bar."""
    bar, stream, _ = make_bar("")
    assert bar.fraction == 0.0
    bar.render()
    assert "0%" in stream.getvalue()
    bar.finish()
    assert "100%" in stream.getvalue()


# --- rendering ---


def test_render_line_format() -> None:
    """Exact layout assertion at a known width, fill, size and time."""
    bar, stream, clock = make_bar("x" * 100, width=40)
    bar.advance("x" * 50)
    bar.set_audio_timeline(ticks(100))  # extrapolated total: 200s
    bar.add_audio_bytes(audio_bytes_for(100))  # 600000 bytes == 585KB
    clock.advance(65)
    bar.render()

    # 40 columns: " 50%|" (5) + bar (15) + "| 585KB  01:05<01:05" (20)
    expected = " 50%|" + "█" * 7 + "▌" + " " * 7 + "| 585KB  01:05<01:05"
    assert len(expected) == 40, len(expected)
    assert stream.getvalue() == "\r" + expected, repr(stream.getvalue())


def test_render_is_throttled() -> None:
    """Redraws respect min_interval so a byte-per-chunk loop cannot spam."""
    bar, stream, clock = make_bar("x" * 100, min_interval=0.1)
    bar.render()
    first = stream.getvalue()
    assert first != ""

    clock.advance(0.05)
    bar.render()
    assert stream.getvalue() == first, "render within min_interval must be skipped"

    clock.advance(0.06)
    bar.render()
    assert stream.getvalue() != first, "render after min_interval must be written"


def test_narrow_terminal_still_renders() -> None:
    """A tiny terminal must not produce a negative-width bar or crash."""
    bar, stream, clock = make_bar("x" * 100, width=10)
    bar.advance("x" * 50)
    bar.set_audio_timeline(ticks(100))
    bar.add_audio_bytes(audio_bytes_for(100))
    clock.advance(1)
    bar.render()
    out = stream.getvalue().lstrip("\r")
    assert out.startswith(" 50%|")
    assert "|" in out[5:]


def test_audio_bytes_accumulate() -> None:
    """Audio byte counts from separate chunks must add up."""
    bar, stream, clock = make_bar("x" * 100, width=60)
    bar.add_audio_bytes(1024 * 600)
    bar.add_audio_bytes(1024 * 600)  # 1228800 bytes == 1.17MB
    clock.advance(1)
    bar.render()
    assert "1.2MB" in stream.getvalue(), repr(stream.getvalue())


# --- ending the line ---


def test_finish_forces_full_bar_and_newline() -> None:
    """A completed run reads 100%, even though the cursor stops short."""
    bar, stream, clock = make_bar("x" * 100, width=40)
    bar.advance("x" * 10)
    bar.render()
    clock.advance(0.01)  # within min_interval: finish must ignore throttling
    bar.finish()

    out = stream.getvalue()
    assert out.endswith("\n")
    last = out.rsplit("\r", 1)[-1].rstrip("\n")
    assert last.startswith("100%|"), repr(last)
    assert "█" * 15 in last, repr(last)
    assert "<00:00" in last, repr(last)


def test_finish_without_prior_render_still_prints() -> None:
    """A run short enough to never redraw still gets a summary line."""
    bar, stream, _ = make_bar("x" * 100)
    bar.finish()
    assert "100%" in stream.getvalue()


def test_finish_is_idempotent() -> None:
    """Finishing twice must not print the line twice."""
    bar, stream, _ = make_bar("x" * 100)
    bar.finish()
    once = stream.getvalue()
    bar.finish()
    assert stream.getvalue() == once


def test_close_ends_line_without_claiming_completion() -> None:
    """On failure the bar must not be filled in to 100%."""
    bar, stream, clock = make_bar("x" * 100, width=40)
    bar.advance("x" * 50)
    bar.set_audio_timeline(ticks(100))  # extrapolated total: 200s
    bar.add_audio_bytes(audio_bytes_for(20))
    bar.render()
    clock.advance(1)
    bar.close()

    out = stream.getvalue()
    assert out.endswith("\n")
    assert "100%" not in out, repr(out)
    assert " 10%|" in out, repr(out)


def test_close_without_prior_render_writes_nothing() -> None:
    """Nothing was drawn, so there is no line to terminate."""
    bar, stream, _ = make_bar("x" * 100)
    bar.close()
    assert stream.getvalue() == ""


def test_close_after_finish_adds_no_extra_output() -> None:
    """close() in a finally block after a successful run is a no-op."""
    bar, stream, _ = make_bar("x" * 100)
    bar.finish()
    once = stream.getvalue()
    bar.close()
    assert stream.getvalue() == once


def test_finish_after_close_is_suppressed() -> None:
    """Once the line is closed, nothing more may be drawn on it."""
    bar, stream, _ = make_bar("x" * 100)
    bar.render()
    bar.close()
    once = stream.getvalue()
    bar.finish()
    assert stream.getvalue() == once
    assert "100%" not in stream.getvalue()


def main() -> None:
    """Run every test_* function in this module."""
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"\n{len(tests)} passed")


if __name__ == "__main__":
    main()
