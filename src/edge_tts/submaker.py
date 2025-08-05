"""SubMaker module is used to generate subtitles from WordBoundary and SentenceBoundary events."""

from datetime import timedelta
from typing import List

from .srt_composer import Subtitle, compose
from .typing import TTSChunk


class SubMaker:
    """
    SubMaker is used to generate subtitles from WordBoundary and SentenceBoundary messages.
    """

    def __init__(self) -> None:
        self.cues: List[Subtitle] = []

    def feed(self, msg: TTSChunk) -> None:
        """
        Feed a WordBoundary or SentenceBoundary message to the SubMaker object.

        Args:
            msg (dict): The WordBoundary or SentenceBoundary message.

        Returns:
            None
        """
        if msg["type"] not in ("WordBoundary", "SentenceBoundary"):
            raise ValueError("Invalid message type, expected 'WordBoundary'")

        self.cues.append(
            Subtitle(
                index=len(self.cues) + 1,
                start=timedelta(microseconds=msg["offset"] / 10),
                end=timedelta(microseconds=(msg["offset"] + msg["duration"]) / 10),
                content=msg["text"],
            )
        )

    def merge_cues(self, words: int) -> None:
        """
        Merge cues to reduce the number of cues.

        Args:
            words (int): The number of words to merge.

        Returns:
            None
        """
        if words <= 0:
            raise ValueError("Invalid number of words to merge, expected > 0")

        if len(self.cues) == 0:
            return

        new_cues: List[Subtitle] = []
        current_cue: Subtitle = self.cues[0]
        for cue in self.cues[1:]:
            if len(current_cue.content.split()) < words:
                current_cue = Subtitle(
                    index=current_cue.index,
                    start=current_cue.start,
                    end=cue.end,
                    content=f"{current_cue.content} {cue.content}",
                )
            else:
                new_cues.append(current_cue)
                current_cue = cue
        new_cues.append(current_cue)
        self.cues = new_cues

    def get_srt(self) -> str:
        """
        Get the SRT formatted subtitles from the SubMaker object.

        Returns:
            str: The SRT formatted subtitles.
        """
        return compose(self.cues)

    def __str__(self) -> str:
        return self.get_srt()
