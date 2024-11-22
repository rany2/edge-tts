"""Custom types for edge-tts."""

# pylint: disable=too-few-public-methods

from typing import List

from typing_extensions import Literal, NotRequired, TypedDict


class TTSChunk(TypedDict):
    """TTS chunk data."""

    type: Literal["audio", "WordBoundary"]
    data: NotRequired[bytes]  # only for audio
    duration: NotRequired[float]  # only for WordBoundary
    offset: NotRequired[float]  # only for WordBoundary
    text: NotRequired[str]  # only for WordBoundary


class VoiceTag(TypedDict):
    """VoiceTag data."""

    ContentCategories: List[
        Literal[
            "Cartoon",
            "Conversation",
            "Copilot",
            "Dialect",
            "General",
            "News",
            "Novel",
            "Sports",
        ]
    ]
    VoicePersonalities: List[
        Literal[
            "Approachable",
            "Authentic",
            "Authority",
            "Bright",
            "Caring",
            "Casual",
            "Cheerful",
            "Clear",
            "Comfort",
            "Confident",
            "Considerate",
            "Conversational",
            "Cute",
            "Expressive",
            "Friendly",
            "Honest",
            "Humorous",
            "Lively",
            "Passion",
            "Pleasant",
            "Positive",
            "Professional",
            "Rational",
            "Reliable",
            "Sincere",
            "Sunshine",
            "Warm",
        ]
    ]


class Voice(TypedDict):
    """Voice data."""

    Name: str
    ShortName: str
    Gender: Literal["Female", "Male"]
    Locale: str
    SuggestedCodec: Literal["audio-24khz-48kbitrate-mono-mp3"]
    FriendlyName: str
    Status: Literal["GA"]
    VoiceTag: VoiceTag


class VoiceManagerVoice(Voice):
    """Voice data for VoiceManager."""

    Language: str
