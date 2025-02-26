"""Utility functions for the command line interface."""

import sys


def pr_err(msg: str) -> None:
    """Print to stderr."""
    print(msg, file=sys.stderr)
