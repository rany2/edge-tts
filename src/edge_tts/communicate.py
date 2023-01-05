"""
Communicate package.
"""


import json
import re
import time
import uuid
from contextlib import nullcontext
from io import TextIOWrapper
from typing import (
    Any,
    AsyncGenerator,
    ContextManager,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Union,
)
from xml.sax.saxutils import escape

import aiohttp

from edge_tts.exceptions import (
    NoAudioReceived,
    UnexpectedResponse,
    UnknownResponse,
    WebSocketError,
)

from .constants import WSS_URL


def get_headers_and_data(data: Union[str, bytes]) -> Tuple[Dict[str, str], bytes]:
    """
    Returns the headers and data from the given data.

    Args:
        data (str or bytes): The data to be parsed.

    Returns:
        tuple: The headers and data to be used in the request.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    if not isinstance(data, bytes):
        raise TypeError("data must be str or bytes")

    headers = {}
    for line in data.split(b"\r\n\r\n")[0].split(b"\r\n"):
        line_split = line.split(b":")
        key, value = line_split[0], b":".join(line_split[1:])
        if value.startswith(b" "):
            value = value[1:]
        headers[key.decode("utf-8")] = value.decode("utf-8")

    return headers, b"\r\n\r\n".join(data.split(b"\r\n\r\n")[1:])


def remove_incompatible_characters(string: Union[str, bytes]) -> str:
    """
    The service does not support a couple character ranges.
    Most important being the vertical tab character which is
    commonly present in OCR-ed PDFs. Not doing this will
    result in an error from the service.

    Args:
        string (str or bytes): The string to be cleaned.

    Returns:
        str: The cleaned string.
    """
    if isinstance(string, bytes):
        string = string.decode("utf-8")
    if not isinstance(string, str):
        raise TypeError("string must be str or bytes")

    chars: List[str] = list(string)

    for idx, char in enumerate(chars):
        code: int = ord(char)
        if (0 <= code <= 8) or (11 <= code <= 12) or (14 <= code <= 31):
            chars[idx] = " "

    return "".join(chars)


def connect_id() -> str:
    """
    Returns a UUID without dashes.

    Returns:
        str: A UUID without dashes.
    """
    return str(uuid.uuid4()).replace("-", "")


def iter_bytes(my_bytes: bytes) -> Generator[bytes, None, None]:
    """
    Iterates over bytes object

    Args:
        my_bytes: Bytes object to iterate over

    Yields:
        the individual bytes
    """
    for i in range(len(my_bytes)):
        yield my_bytes[i : i + 1]


def split_text_by_byte_length(text: Union[str, bytes], byte_length: int) -> List[bytes]:
    """
    Splits a string into a list of strings of a given byte length
    while attempting to keep words together.

    Args:
        text (str or bytes): The string to be split.
        byte_length (int): The maximum byte length of each string in the list.

    Returns:
        list: A list of bytes of the given byte length.
    """
    if isinstance(text, str):
        text = text.encode("utf-8")
    if not isinstance(text, bytes):
        raise TypeError("text must be str or bytes")

    words = []
    while len(text) > byte_length:
        # Find the last space in the string
        last_space = text.rfind(b" ", 0, byte_length)
        if last_space == -1:
            # No space found, just split at the byte length
            words.append(text[:byte_length])
            text = text[byte_length:]
        else:
            # Split at the last space
            words.append(text[:last_space])
            text = text[last_space:]
    words.append(text)

    # Remove empty strings from the list
    words = [word for word in words if word]
    # Return the list
    return words


def mkssml(text: Union[str, bytes], voice: str, rate: str, volume: str) -> str:
    """
    Creates a SSML string from the given parameters.

    Returns:
        str: The SSML string.
    """
    if isinstance(text, bytes):
        text = text.decode("utf-8")

    ssml = (
        "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
        f"<voice name='{voice}'><prosody pitch='+0Hz' rate='{rate}' volume='{volume}'>"
        f"{text}</prosody></voice></speak>"
    )
    return ssml


def date_to_string() -> str:
    """
    Return Javascript-style date string.

    Returns:
        str: Javascript-style date string.
    """
    # %Z is not what we want, but it's the only way to get the timezone
    # without having to use a library. We'll just use UTC and hope for the best.
    # For example, right now %Z would return EEST when we need it to return
    # Eastern European Summer Time.
    return time.strftime(
        "%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)", time.gmtime()
    )


def ssml_headers_plus_data(request_id: str, timestamp: str, ssml: str) -> str:
    """
    Returns the headers and data to be used in the request.

    Returns:
        str: The headers and data to be used in the request.
    """

    return (
        f"X-RequestId:{request_id}\r\n"
        "Content-Type:application/ssml+xml\r\n"
        f"X-Timestamp:{timestamp}Z\r\n"  # This is not a mistake, Microsoft Edge bug.
        "Path:ssml\r\n\r\n"
        f"{ssml}"
    )


def calc_max_mesg_size(voice: str, rate: str, volume: str) -> int:
    """Calculates the maximum message size for the given voice, rate, and volume.

    Returns:
        int: The maximum message size.
    """
    websocket_max_size: int = 2**16
    overhead_per_message: int = (
        len(
            ssml_headers_plus_data(
                connect_id(),
                date_to_string(),
                mkssml("", voice, rate, volume),
            )
        )
        + 50  # margin of error
    )
    return websocket_max_size - overhead_per_message


class Communicate:
    """
    Class for communicating with the service.
    """

    def __init__(
        self,
        text: str,
        voice: str = "Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)",
        *,
        rate: str = "+0%",
        volume: str = "+0%",
        proxy: Optional[str] = None,
    ):
        """
        Initializes the Communicate class.

        Raises:
            ValueError: If the voice is not valid.
        """
        if not isinstance(text, str):
            raise TypeError("text must be str")
        self.text: str = text

        # Possible values for voice are:
        # - Microsoft Server Speech Text to Speech Voice (cy-GB, NiaNeural)
        # - cy-GB-NiaNeural
        # Always send the first variant as that is what Microsoft Edge does.
        if not isinstance(voice, str):
            raise TypeError("voice must be str")
        self.voice: str = voice
        match = re.match(r"^([a-z]{2})-([A-Z]{2})-(.+Neural)$", voice)
        if match is not None:
            self.voice = (
                "Microsoft Server Speech Text to Speech Voice"
                + f" ({match.group(1)}-{match.group(2)}, {match.group(3)})"
            )

        if (
            re.match(
                r"^Microsoft Server Speech Text to Speech Voice \(.+,.+\)$",
                self.voice,
            )
            is None
        ):
            raise ValueError(f"Invalid voice '{voice}'.")

        if not isinstance(rate, str):
            raise TypeError("rate must be str")
        if re.match(r"^[+-]\d+%$", rate) is None:
            raise ValueError(f"Invalid rate '{rate}'.")
        self.rate: str = rate

        if not isinstance(volume, str):
            raise TypeError("volume must be str")
        if re.match(r"^[+-]\d+%$", volume) is None:
            raise ValueError(f"Invalid volume '{volume}'.")
        self.volume: str = volume

        if proxy is not None and not isinstance(proxy, str):
            raise TypeError("proxy must be str")
        self.proxy: Optional[str] = proxy

    async def stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Streams audio and metadata from the service."""

        texts = split_text_by_byte_length(
            escape(remove_incompatible_characters(self.text)),
            calc_max_mesg_size(self.voice, self.rate, self.volume),
        )

        async with aiohttp.ClientSession(trust_env=True) as session, session.ws_connect(
            f"{WSS_URL}&ConnectionId={connect_id()}",
            compress=15,
            autoclose=True,
            autoping=True,
            proxy=self.proxy,
            headers={
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41",
            },
        ) as websocket:
            for text in texts:
                # download indicates whether we should be expecting audio data,
                # this is so what we avoid getting binary data from the websocket
                # and falsely thinking it's audio data.
                download_audio = False

                # audio_was_received indicates whether we have received audio data
                # from the websocket. This is so we can raise an exception if we
                # don't receive any audio data.
                audio_was_received = False

                # Each message needs to have the proper date.
                date = date_to_string()

                # Prepare the request to be sent to the service.
                #
                # Note sentenceBoundaryEnabled and wordBoundaryEnabled are actually supposed
                # to be booleans, but Edge Browser seems to send them as strings.
                #
                # This is a bug in Edge as Azure Cognitive Services actually sends them as
                # bool and not string. For now I will send them as bool unless it causes
                # any problems.
                #
                # Also pay close attention to double { } in request (escape for f-string).
                await websocket.send_str(
                    f"X-Timestamp:{date}\r\n"
                    "Content-Type:application/json; charset=utf-8\r\n"
                    "Path:speech.config\r\n\r\n"
                    '{"context":{"synthesis":{"audio":{"metadataoptions":{'
                    '"sentenceBoundaryEnabled":false,"wordBoundaryEnabled":true},'
                    '"outputFormat":"audio-24khz-48kbitrate-mono-mp3"'
                    "}}}}\r\n"
                )

                await websocket.send_str(
                    ssml_headers_plus_data(
                        connect_id(),
                        date,
                        mkssml(text, self.voice, self.rate, self.volume),
                    )
                )

                async for received in websocket:
                    if received.type == aiohttp.WSMsgType.TEXT:
                        parameters, data = get_headers_and_data(received.data)
                        if parameters.get("Path") == "turn.start":
                            download_audio = True
                        elif parameters.get("Path") == "turn.end":
                            download_audio = False
                            break  # End of audio data
                        elif parameters.get("Path") == "audio.metadata":
                            meta = json.loads(data)
                            for i in range(len(meta["Metadata"])):
                                meta_obj = meta["Metadata"][i]
                                meta_type = meta_obj["Type"]
                                if meta_type == "WordBoundary":
                                    yield {
                                        "type": meta_type,
                                        "offset": meta_obj["Data"]["Offset"],
                                        "duration": meta_obj["Data"]["Duration"],
                                        "text": meta_obj["Data"]["text"]["Text"],
                                    }
                                elif meta_type == "SessionEnd":
                                    continue
                                else:
                                    raise UnknownResponse(
                                        f"Unknown metadata type: {meta_type}"
                                    )
                        elif parameters.get("Path") == "response":
                            pass
                        else:
                            raise UnknownResponse(
                                "The response from the service is not recognized.\n"
                                + received.data
                            )
                    elif received.type == aiohttp.WSMsgType.BINARY:
                        if not download_audio:
                            raise UnexpectedResponse(
                                "We received a binary message, but we are not expecting one."
                            )

                        yield {
                            "type": "audio",
                            "data": b"Path:audio\r\n".join(
                                received.data.split(b"Path:audio\r\n")[1:]
                            ),
                        }
                        audio_was_received = True
                    elif received.type == aiohttp.WSMsgType.ERROR:
                        raise WebSocketError(received.data)

                if not audio_was_received:
                    raise NoAudioReceived(
                        "No audio was received. Please verify that your parameters are correct."
                    )

    async def save(
        self,
        audio_fname: Union[str, bytes],
        metadata_fname: Optional[Union[str, bytes]] = None,
    ) -> None:
        """
        Save the audio and metadata to the specified files.
        """
        written_audio: bool = False
        metadata: Union[TextIOWrapper, ContextManager[None]] = (
            open(metadata_fname, "w", encoding="utf-8")
            if metadata_fname is not None
            else nullcontext()
        )
        with metadata, open(audio_fname, "wb") as audio:
            async for message in self.stream():
                if message["type"] == "audio":
                    audio.write(message["data"])
                    written_audio = True
                elif (
                    isinstance(metadata, TextIOWrapper)
                    and message["type"] == "WordBoundary"
                ):
                    json.dump(message, metadata)
                    metadata.write("\n")

        if not written_audio:
            raise NoAudioReceived(
                "No audio was received from the service, so the file is empty."
            )
