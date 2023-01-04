"""
list_voices package for edge_tts.
"""

import json
from typing import Any, Optional

import aiohttp

from .constants import VOICE_LIST


async def list_voices(*, proxy: Optional[str] = None) -> Any:
    """
    List all available voices and their attributes.

    This pulls data from the URL used by Microsoft Edge to return a list of
    all available voices.

    Returns:
        dict: A dictionary of voice attributes.
    """
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(
            VOICE_LIST,
            headers={
                "Authority": "speech.platform.bing.com",
                "Sec-CH-UA": '" Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
                "Sec-CH-UA-Mobile": "?0",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41",
                "Accept": "*/*",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
            },
            proxy=proxy,
        ) as url:
            data = json.loads(await url.text())
    return data


class VoicesManager:
    """
    A class to find the correct voice based on their attributes.
    """

    @classmethod
    async def create(cls): # type: ignore
        """
        Creates a VoicesManager object and populates it with all available voices.
        """
        self = VoicesManager()
        self.voices = await list_voices()
        self.voices = [
            {**voice, **{"Language": voice["Locale"].split("-")[0]}}
            for voice in self.voices
        ]
        return self

    def find(self, **kwargs: Any) -> list[dict[str, Any]]:
        """
        Finds all matching voices based on the provided attributes.
        """

        matching_voices = [
            voice for voice in self.voices if kwargs.items() <= voice.items() # type: ignore
        ]
        return matching_voices
