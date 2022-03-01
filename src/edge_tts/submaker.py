"""
SubMaker package for the Edge TTS project.

SubMaker is a package that makes the process of creating subtitles with
information provided by the service easier.
"""

import math


def formatter(offset1, offset2, subdata):
    """
    formatter returns the timecode and the text of the subtitle.
    """
    return (
        f"{mktimestamp(offset1)} --> {mktimestamp(offset2)}\r\n"
        f"{subdata}\r\n\r\n"
    )


def mktimestamp(time_unit):
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

    def __init__(self, overlapping=5):
        """
        SubMaker constructor.

        Args:
            overlapping (int): The amount of time in seconds that the
                               subtitles should overlap.
        """
        self.subs_and_offset = []
        self.broken_offset = []
        self.overlapping = overlapping * (10**7)

    def create_sub(self, timestamp, text):
        """
        create_sub creates a subtitle with the given timestamp and text
        and adds it to the list of subtitles

        Args:
            timestamp (tuple): The offset and duration of the subtitle.
            text (str): The text of the subtitle.

        Returns:
            None
        """
        timestamp[1] += timestamp[0]

        if len(self.subs_and_offset) >= 2:
            if self.subs_and_offset[-2][-1] >= timestamp[1] + sum(self.broken_offset):
                self.broken_offset.append(self.subs_and_offset[-2][1])
            timestamp[0] += sum(self.broken_offset)
            timestamp[1] += sum(self.broken_offset)

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
            for offset, subs in zip(
                self.subs_and_offset[::2], self.subs_and_offset[1::2]
            ):
                subs = [subs[i : i + 79] for i in range(0, len(subs), 79)]

                for i in range(len(subs) - 1):
                    sub = subs[i]
                    split_at_word = True
                    if sub[-1] == " ":
                        subs[i] = sub[:-1]
                        split_at_word = False

                    if sub[0] == " ":
                        subs[i] = sub[1:]
                        split_at_word = False

                    if split_at_word:
                        subs[i] += "-"

                subs = "\r\n".join(subs)

                data += formatter(offset[0], offset[1] + self.overlapping, subs)
            return data
        return ""
