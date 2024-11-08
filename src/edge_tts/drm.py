"""This module contains functions for generating the Sec-MS-GEC and Sec-MS-GEC-Version tokens."""

import datetime
import hashlib

from .constants import CHROMIUM_FULL_VERSION, TRUSTED_CLIENT_TOKEN


def generate_sec_ms_gec_token() -> str:
    """Generates the Sec-MS-GEC token value.

    See: https://github.com/rany2/edge-tts/issues/290#issuecomment-2464956570"""

    # Get the current time in Windows file time format (100ns intervals since 1601-01-01)
    ticks = int(
        (datetime.datetime.now(datetime.UTC).timestamp() + 11644473600) * 10000000
    )

    # Round down to the nearest 5 minutes (3,000,000,000 * 100ns = 5 minutes)
    ticks -= ticks % 3_000_000_000

    # Create the string to hash by concatenating the ticks and the trusted client token
    str_to_hash = f"{ticks}{TRUSTED_CLIENT_TOKEN}"

    # Compute the SHA256 hash
    hash_object = hashlib.sha256(str_to_hash.encode("ascii"))
    hex_dig = hash_object.hexdigest()

    # Return the hexadecimal representation of the hash
    return hex_dig.upper()


def generate_sec_ms_gec_version() -> str:
    """Generates the Sec-MS-GEC-Version token value."""
    return f"1-{CHROMIUM_FULL_VERSION}"
