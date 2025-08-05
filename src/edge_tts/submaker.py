"""SubMaker module is used to generate subtitles from WordBoundary and SentenceBoundary events."""

from datetime import timedelta
from typing import List, Optional

from .srt_composer import Subtitle, compose
from .typing import TTSChunk


class SubMaker:
    """
    SubMaker is used to generate subtitles from WordBoundary and SentenceBoundary messages.
    """

    def __init__(self) -> None:
        self.cues: List[Subtitle] = []
        self.type: Optional[str] = None

    def feed(self, msg: TTSChunk) -> None:
        """
        Feed a WordBoundary or SentenceBoundary message to the SubMaker object.

        Args:
            msg (dict): The WordBoundary or SentenceBoundary message.

        Returns:
            None
        """
        if msg["type"] not in ("WordBoundary", "SentenceBoundary"):
            raise ValueError(
                "Invalid message type, expected 'WordBoundary' or 'SentenceBoundary'."
            )

        if self.type is None:
            self.type = msg["type"]
        elif self.type != msg["type"]:
            raise ValueError(
                f"Expected message type '{self.type}', but got '{msg['type']}'."
            )

        self.cues.append(
            Subtitle(
                index=len(self.cues) + 1,
                start=timedelta(microseconds=msg["offset"] / 10),
                end=timedelta(microseconds=(msg["offset"] + msg["duration"]) / 10),
                content=msg["text"],
            )
        )

    def get_srt(self) -> str:
        """
        Get the SRT formatted subtitles from the SubMaker object.

        Returns:
            str: The SRT formatted subtitles.
        """
        return compose(self.cues)

    def __str__(self) -> str:
        return self.get_srt()
