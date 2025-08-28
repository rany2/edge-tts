"""Custom types for edge-tts."""

# pylint: disable=too-few-public-methods

from typing import List

from typing_extensions import Literal, NotRequired, TypedDict


class TTSChunk(TypedDict):
    """TTS chunk data."""

    type: Literal["audio", "WordBoundary", "SentenceBoundary"]
    data: NotRequired[bytes]  # only for audio
    duration: NotRequired[float]  # only for WordBoundary and SentenceBoundary
    offset: NotRequired[float]  # only for WordBoundary and SentenceBoundary
    text: NotRequired[str]  # only for WordBoundary and SentenceBoundary


class VoiceTag(TypedDict):
    """VoiceTag data."""

    ContentCategories: List[str]
    VoicePersonalities: List[str]


class Voice(TypedDict):
    """Voice data."""

    Name: str
    ShortName: str
    DisplayName: str
    LocalName: str
    LocaleName: str
    Locale: str
    Gender: Literal["Female", "Male"]
    WordsPerMinute: str
    Status: Literal["Deprecated", "GA", "Preview"]
    VoiceTag: VoiceTag

class VoicesManagerVoice(Voice):
    """Voice data for VoicesManager."""

    Language: str


class VoicesManagerFind(TypedDict):
    """Voice data for VoicesManager.find()."""

    Gender: NotRequired[Literal["Female", "Male"]]
    Locale: NotRequired[str]
    Language: NotRequired[str]


class CommunicateState(TypedDict):
    """Communicate state data."""

    partial_text: bytes
    offset_compensation: float
    last_duration_offset: float
    stream_was_called: bool
