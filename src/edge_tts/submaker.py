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

        new_cues: List[srt.Subtitle] = []  # type: ignore
        current_cue: srt.Subtitle = self.cues[0]  # type: ignore
        for cue in self.cues[1:]:
            if len(current_cue.content.split()) < words:
                current_cue = srt.Subtitle(
                    index=current_cue.index,
                    start=current_cue.start,
                    end=cue.end,
                    content=current_cue.content + " " + cue.content,
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
        return srt.compose(self.cues)  # type: ignore

    def __str__(self) -> str:
        return self.get_srt()
