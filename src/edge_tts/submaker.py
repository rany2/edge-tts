"""SubMaker module is used to generate subtitles from WordBoundary events."""

from typing import List, Tuple

import srt  # type: ignore


class SubMaker:
    """
    SubMaker is used to generate subtitles from WordBoundary messages.
    """

    def __init__(self) -> None:
        self.cues: List[srt.Subtitle] = []  # type: ignore

    def add_cue(self, timestamp: Tuple[float, float], text: str) -> None:
        """
        Add a cue to the SubMaker object.

        Args:
            timestamp (tuple): The offset and duration of the subtitle.
            text (str): The text of the subtitle.

        Returns:
            None
        """
        self.cues.append(
            srt.Subtitle(
                index=len(self.cues) + 1,
                start=srt.timedelta(microseconds=timestamp[0] / 10),
                end=srt.timedelta(microseconds=sum(timestamp) / 10),
                content=text,
            )
        )

    def get_srt(self) -> str:
        """
        Get the SRT formatted subtitles from the SubMaker object.

        Returns:
            str: The SRT formatted subtitles.
        """
        return srt.compose(self.cues)  # type: ignore
