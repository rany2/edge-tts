"""
SubMaker package for the Edge TTS project.

SubMaker is a package that makes the process of creating subtitles with
information provided by the service easier.
"""

import math
from xml.sax.saxutils import escape


def formatter(offset1, offset2, subdata):
    """
    formatter returns the timecode and the text of the subtitle.
    """
    return (
        f"{mktimestamp(offset1)} --> {mktimestamp(offset2)}\r\n"
        f"{escape(subdata)}\r\n\r\n"
    )


def mktimestamp(time_unit):
    """
    mktimestamp returns the timecode of the subtitle.

    The timecode is in the format of 00:00:00.000.

    Returns:
        str: The timecode of the subtitle.
    """
    hour = math.floor(time_unit / 10 ** 7 / 3600)
    minute = math.floor((time_unit / 10 ** 7 / 60) % 60)
    seconds = (time_unit / 10 ** 7) % 60
    return f"{hour:02d}:{minute:02d}:{seconds:06.3f}"


class SubMaker:
    """
    SubMaker class
    """

    def __init__(self, overlapping=5):
        """
        SubMaker constructor.

        Args:
            overlapping (int): The amount of time in seconds that the
                               subtitles should overlap.
        """
        self.subs_and_offset = []
        self.broken_offset = []
        self.overlapping = overlapping * (10 ** 7)

    def create_sub(self, timestamp, text):
        """
        create_sub creates a subtitle with the given timestamp and text
        and adds it to the list of subtitles

        Args:
            timestamp (int): The timestamp of the subtitle.
            text (str): The text of the subtitle.

        Returns:
            None
        """
        if len(self.subs_and_offset) >= 2:
            if self.subs_and_offset[-2] >= timestamp + sum(self.broken_offset):
                self.broken_offset.append(self.subs_and_offset[-2])
            timestamp = timestamp + sum(self.broken_offset)

        self.subs_and_offset.append(timestamp)
        self.subs_and_offset.append(text)

    def generate_subs(self):
        """
        generate_subs generates the complete subtitle file.

        Returns:
            str: The complete subtitle file.
        """
        if len(self.subs_and_offset) >= 2:
            data = "WEBVTT\r\n\r\n"
            old_time_stamp = None
            old_sub_data = None
            for offset, subs in zip(
                self.subs_and_offset[::2], self.subs_and_offset[1::2]
            ):
                if old_time_stamp is not None and old_sub_data is not None:
                    data += formatter(
                        old_time_stamp, offset + self.overlapping, old_sub_data
                    )
                old_time_stamp = offset
                old_sub_data = subs
            data += formatter(
                old_time_stamp, old_time_stamp + ((10 ** 7) * 10), old_sub_data
            )
            return data
        return ""
