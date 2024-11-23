"""SubMaker module is used to generate subtitles from WordBoundary events."""

from typing import List

import srt  # type: ignore

from .typing import TTSChunk


class SubMaker:
    """
    SubMaker is used to generate subtitles from WordBoundary messages.
    """

    def __init__(self) -> None:
        self.cues: List[srt.Subtitle] = []  # type: ignore

    def feed(self, msg: TTSChunk) -> None:
        """
        Feed a WordBoundary message to the SubMaker object.

        Args:
            msg (dict): The WordBoundary message.

        Returns:
            None
        """
        if msg["type"] != "WordBoundary":
            raise ValueError("Invalid message type, expected 'WordBoundary'")

        self.cues.append(
            srt.Subtitle(
                index=len(self.cues) + 1,
                start=srt.timedelta(microseconds=msg["offset"] / 10),
                end=srt.timedelta(microseconds=(msg["offset"] + msg["duration"]) / 10),
                content=msg["text"],
            )
        )

    def get_srt(self) -> str:
        """
        Get the SRT formatted subtitles from the SubMaker object.

        Returns:
            str: The SRT formatted subtitles.
        """
        return srt.compose(self.cues)  # type: ignore

    def __str__(self) -> str:
        return self.get_srt()
