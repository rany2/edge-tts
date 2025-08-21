"""This module contains functions to list all available voices and a class to find the
correct voice based on their attributes."""

import json
import ssl
from typing import List, Optional

import aiohttp
import certifi
from typing_extensions import Unpack

from .constants import SEC_MS_GEC_VERSION, VOICE_HEADERS, VOICE_LIST
from .drm import DRM
from .typing import Voice, VoicesManagerFind, VoicesManagerVoice


async def __list_voices(
    session: aiohttp.ClientSession, ssl_ctx: ssl.SSLContext, proxy: Optional[str]
) -> List[Voice]:
    """
    Private function that makes the request to the voice list URL and parses the
    JSON response. This function is used by list_voices() and makes it easier to
    handle client response errors related to clock skew.

    Args:
        session (aiohttp.ClientSession): The aiohttp session to use for the request.
        ssl_ctx (ssl.SSLContext): The SSL context to use for the request.
        proxy (Optional[str]): The proxy to use for the request.

    Returns:
        List[Voice]: A list of voices and their attributes.
    """
    async with session.get(
        f"{VOICE_LIST}&Sec-MS-GEC={DRM.generate_sec_ms_gec()}"
        f"&Sec-MS-GEC-Version={SEC_MS_GEC_VERSION}",
        headers=VOICE_HEADERS,
        proxy=proxy,
        ssl=ssl_ctx,
        raise_for_status=True,
    ) as url:
        data: List[Voice] = json.loads(await url.text())

    for voice in data:
        # Remove leading and trailing whitespace from categories and personalities.
        # This has only happened in one case with the zh-CN-YunjianNeural voice
        # where there was a leading space in one of the categories.

        if "ContentCategories" in voice["VoiceTag"]:
            voice["VoiceTag"]["ContentCategories"] = [
                category.strip()  # type: ignore
                for category in voice["VoiceTag"]["ContentCategories"]
            ]

        voice["VoiceTag"]["VoicePersonalities"] = [
            personality.strip()  # type: ignore
            for personality in voice["VoiceTag"]["VoicePersonalities"]
        ]

        # if not exist key FriendlyName in voice create add value LocalName
        if "FriendlyName" not in voice:
            voice["FriendlyName"] = voice["LocalName"]
    return data


async def list_voices(
    *, connector: Optional[aiohttp.BaseConnector] = None, proxy: Optional[str] = None
) -> List[Voice]:
    """
    List all available voices and their attributes.

    This pulls data from the URL used by Microsoft Edge to return a list of
    all available voices.

    Args:
        connector (Optional[aiohttp.BaseConnector]): The connector to use for the request.
        proxy (Optional[str]): The proxy to use for the request.

    Returns:
        List[Voice]: A list of voices and their attributes.
    """
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
        try:
            data = await __list_voices(session, ssl_ctx, proxy)
        except aiohttp.ClientResponseError as e:
            if e.status != 403:
                raise

            DRM.handle_client_response_error(e)
            data = await __list_voices(session, ssl_ctx, proxy)
    return data


class VoicesManager:
    """
    A class to find the correct voice based on their attributes.
    """

    def __init__(self) -> None:
        self.voices: List[VoicesManagerVoice] = []
        self.called_create: bool = False

    @classmethod
    async def create(
        cls, custom_voices: Optional[List[Voice]] = None
    ) -> "VoicesManager":
        """
        Creates a VoicesManager object and populates it with all available voices.
        """
        self = VoicesManager()
        voices = await list_voices() if custom_voices is None else custom_voices
        self.voices = [
            {**voice, "Language": voice["Locale"].split("-")[0]} for voice in voices
        ]
        self.called_create = True
        return self

    def find(self, **kwargs: Unpack[VoicesManagerFind]) -> List[VoicesManagerVoice]:
        """
        Finds all matching voices based on the provided attributes.
        """
        if not self.called_create:
            raise RuntimeError(
                "VoicesManager.find() called before VoicesManager.create()"
            )

        matching_voices = [
            voice for voice in self.voices if kwargs.items() <= voice.items()
        ]
        return matching_voices
