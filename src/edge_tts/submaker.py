"""
SubMaker package for the Edge TTS project.

SubMaker is a package that makes the process of creating subtitles with
information provided by the service easier.
"""

import math
import re
from typing import Callable, List, Tuple, Union
from xml.sax.saxutils import escape, unescape


def formatter(
    sub_line_count: int, start_time: float, end_time: float, subdata: str
) -> str:
    """
    formatter returns the timecode and the text of the subtitle.
    """
    return (
        f"{sub_line_count}\n"
        f"{mktimestamp(start_time)} --> {mktimestamp(end_time)}\n"
        f"{escape(subdata)}\n\n"
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
    return f"{hour:02d}:{minute:02d}:{seconds:06.3f}".replace(".", ",")


def _spinoff_sentence(sentence: str) -> Tuple[str, str, int]:
    """
    _spinoff_sentence returns the sentence, the last word of the sentence,
    and the number of times the last word appears in the sentence.

    Args:
        sentence (str): The sentence to be processed.

    Returns:
        Tuple[str, str, int]: The sentence, the last word of the sentence,
        and the number of times the last word appears in the sentence.
    """
    if not isinstance(sentence, str):
        raise TypeError("sentence must be a string")
    last_word = sentence[-1]
    last_word_num = sentence.count(last_word)
    return (sentence, last_word, last_word_num)


def process_text(
    text: str,
    *,
    pattern_chi: str = r"[：“”‘’──{}【】·《》〈〉，、；。？！]",
    spinoff_sentence: Callable[[str], Tuple[str, str, int]] = _spinoff_sentence,
) -> List[Tuple[str, str, int]]:
    """
    process_text returns the three-dimensional list of the text to be passed
    to SubMaker's generate_subs method.

    Args:
        text (str): The text to be processed.
        pattern_chi (str): The pattern of Chinese characters.
        spinoff_sentence (function): The function used to process the sentence.

    Returns:
        List[Tuple[str, str, int]]: The three-dimensional list of the text.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not isinstance(pattern_chi, str):
        raise TypeError("pattern_chi must be a string")
    if not callable(spinoff_sentence):
        raise TypeError("spinoff_sentence must be a function")
    sentences = re.split(pattern_chi, text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    three_dimensional_list = []
    for sentence in sentences:
        three_dimensional_list.append(spinoff_sentence(sentence))
    return three_dimensional_list


class SubMaker:
    """
    SubMaker class
    """

    def __init__(self) -> None:
        """
        SubMaker constructor.
        """
        self.offset: List[Tuple[float, float]] = []
        self.subs: List[str] = []

    def create_sub(self, timestamp: Tuple[float, float], text: str) -> None:
        """
        create_sub creates a subtitle with the given timestamp and text
        and adds it to the list of subtitles, this should be called
        when receiving the wordboundary event from the service.

        Args:
            timestamp (tuple): The offset and duration of the subtitle.
            text (str): The text of the subtitle.

        Returns:
            None
        """
        self.offset.append((timestamp[0], timestamp[0] + timestamp[1]))
        self.subs.append(text)

    def generate_subs(self, text: Union[str, List[Tuple[str, str, int]]]) -> str:
        """
        generate_subs generates the complete subtitle file.

        Args:
            text: If the type is List[Tuple[str, str, int]], it is the three-dimensional
                list of the text already processed. If the type is str, the text will
                be processed automatically by process_text with the default parameters.
                It should not use data from WordBoundary events, but the text that was
                used to generate the audio.

        Returns:
            str: The complete subtitle file.
        """
        if len(self.subs) != len(self.offset):
            raise ValueError("subs and offset are not of the same length")

        if isinstance(text, str):
            text = process_text(text)
        elif isinstance(text, list):
            for sentence, last_word, last_word_num in text:
                if not isinstance(sentence, str):
                    raise TypeError("sentence (first element) must be a string")
                if not isinstance(last_word, str):
                    raise TypeError("last_word (second element) must be a string")
                if not isinstance(last_word_num, int):
                    raise TypeError("last_word_num (third element) must be an integer")
        else:
            raise TypeError("text must be a string or a list")

        data = ""
        sub_state_count = 0
        sub_state_start = -1.0
        sub_state_subs = ""
        sub_line_count = 0
        for idx, (offset, subs) in enumerate(zip(self.offset, self.subs)):
            start_time, end_time = offset
            subs = unescape(subs)

            # wordboundary is guaranteed not to contain whitespace
            sub_state_subs += subs

            if sub_state_start == -1.0:
                sub_state_start = start_time
            sub_state_count += 1

            sentence, last_word, last_word_num = text[sub_line_count]
            if (
                sub_state_subs.count(last_word) == last_word_num
                or idx == len(self.offset) - 1
            ):
                sub_line_count += 1
                subs = sentence
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

                data += formatter(
                    sub_line_count=sub_line_count,
                    start_time=sub_state_start,
                    end_time=end_time,
                    subdata="".join(split_subs),
                )
                sub_state_count = 0
                sub_state_start = -1
                sub_state_subs = ""
        return data
