"""
list_voices package for edge_tts.
"""

import json
import ssl
from typing import Any, Dict, List, Optional

import aiohttp
import certifi

from .constants import VOICE_HEADERS, VOICE_LIST
from .drm import generate_sec_ms_gec_token, generate_sec_ms_gec_version


async def list_voices(*, proxy: Optional[str] = None) -> Any:
    """
    List all available voices and their attributes.

    This pulls data from the URL used by Microsoft Edge to return a list of
    all available voices.

    Returns:
        dict: A dictionary of voice attributes.
    """
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(
            f"{VOICE_LIST}&Sec-MS-GEC={generate_sec_ms_gec_token()}"
            f"&Sec-MS-GEC-Version={generate_sec_ms_gec_version()}",
            headers=VOICE_HEADERS,
            proxy=proxy,
            ssl=ssl_ctx,
        ) as url:
            data = json.loads(await url.text())
    return data


class VoicesManager:
    """
    A class to find the correct voice based on their attributes.
    """

    def __init__(self) -> None:
        self.voices: List[Dict[str, Any]] = []
        self.called_create: bool = False

    @classmethod
    async def create(
        cls: Any, custom_voices: Optional[List[Dict[str, Any]]] = None
    ) -> Any:
        """
        Creates a VoicesManager object and populates it with all available voices.
        """
        self = VoicesManager()
        self.voices = await list_voices() if custom_voices is None else custom_voices
        self.voices = [
            {**voice, **{"Language": voice["Locale"].split("-")[0]}}
            for voice in self.voices
        ]
        self.called_create = True
        return self

    def find(self, **kwargs: Any) -> List[Dict[str, Any]]:
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
