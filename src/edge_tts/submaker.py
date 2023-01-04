"""
SubMaker package for the Edge TTS project.

SubMaker is a package that makes the process of creating subtitles with
information provided by the service easier.
"""

import math
from typing import List, Tuple
from xml.sax.saxutils import escape, unescape


def formatter(offset1: float, offset2: float, subdata: str) -> str:
    """
    formatter returns the timecode and the text of the subtitle.
    """
    return (
        f"{mktimestamp(offset1)} --> {mktimestamp(offset2)}\r\n"
        f"{escape(subdata)}\r\n\r\n"
    )


def mktimestamp(time_unit: float) -> str:
    """
    mktimestamp returns the timecode of the subtitle.

    The timecode is in the format of 00:00:00.000.

    Returns:
        str: The timecode of the subtitle.
    """
    hour = math.floor(time_unit / 10**7 / 3600)
    minute = math.floor((time_unit / 10**7 / 60) % 60)
    seconds = (time_unit / 10**7) % 60
    return f"{hour:02d}:{minute:02d}:{seconds:06.3f}"


class SubMaker:
    """
    SubMaker class
    """

    def __init__(self, overlapping: int = 1) -> None:
        """
        SubMaker constructor.

        Args:
            overlapping (int): The amount of time in seconds that the
                               subtitles should overlap.
        """
        self.offset: List[Tuple[float, float]] = []
        self.subs: List[str] = []
        self.overlapping: int = overlapping * (10**7)

    def create_sub(self, timestamp: Tuple[float, float], text: str) -> None:
        """
        create_sub creates a subtitle with the given timestamp and text
        and adds it to the list of subtitles

        Args:
            timestamp (tuple): The offset and duration of the subtitle.
            text (str): The text of the subtitle.

        Returns:
            None
        """
        self.offset.append((timestamp[0], timestamp[0] + timestamp[1]))
        self.subs.append(text)

    def generate_subs(self) -> str:
        """
        generate_subs generates the complete subtitle file.

        Returns:
            str: The complete subtitle file.
        """
        if len(self.subs) == len(self.offset):
            data = "WEBVTT\r\n\r\n"
            for offset, subs in zip(self.offset, self.subs):
                subs = unescape(subs)
                split_subs: List[str] = [
                    subs[i : i + 79] for i in range(0, len(subs), 79)
                ]

                for i in range(len(split_subs) - 1):
                    sub = split_subs[i]
                    split_at_word = True
                    if sub[-1] == " ":
                        split_subs[i] = sub[:-1]
                        split_at_word = False

                    if sub[0] == " ":
                        split_subs[i] = sub[1:]
                        split_at_word = False

                    if split_at_word:
                        split_subs[i] += "-"

                subs = "\r\n".join(split_subs)

                data += formatter(offset[0], offset[1] + self.overlapping, subs)
            return data
        return ""
