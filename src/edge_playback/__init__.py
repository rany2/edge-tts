"""The edge_playback package wraps the functionality of mpv and edge-tts to generate
text-to-speech (TTS) using edge-tts and then plays back the generated audio using mpv.
"""

from .__main__ import _main

__all__ = ["_main"]
