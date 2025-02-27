"""Utility functions for edge-playback"""

import sys


def pr_err(msg: str) -> None:
    """Print to stderr."""
    print(msg, file=sys.stderr)
