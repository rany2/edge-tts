"""
Communicate package.
"""

import json
import re
import ssl
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
import certifi

from edge_tts.exceptions import (
    NoAudioReceived,
    UnexpectedResponse,
    UnknownResponse,
    WebSocketError,
)

from .constants import WSS_URL


def get_headers_and_data(data: Union[str, bytes]) -> Tuple[Dict[bytes, bytes], bytes]:
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
    for line in data[: data.find(b"\r\n\r\n")].split(b"\r\n"):
        key, value = line.split(b":", 1)
        headers[key] = value

    return headers, data[data.find(b"\r\n\r\n") + 4 :]


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


def split_text_by_byte_length(
    text: Union[str, bytes], byte_length: int
) -> Generator[bytes, None, None]:
    """
    Splits a string into a list of strings of a given byte length
    while attempting to keep words together. This function assumes
    text will be inside of an XML tag.

    Args:
        text (str or bytes): The string to be split.
        byte_length (int): The maximum byte length of each string in the list.

    Yield:
        bytes: The next string in the list.
    """
    if isinstance(text, str):
        text = text.encode("utf-8")
    if not isinstance(text, bytes):
        raise TypeError("text must be str or bytes")

    if byte_length <= 0:
        raise ValueError("byte_length must be greater than 0")

    while len(text) > byte_length:
        # Find the last space in the string
        split_at = text.rfind(b" ", 0, byte_length)

        # If no space found, split_at is byte_length
        split_at = split_at if split_at != -1 else byte_length

        # Verify all & are terminated with a ;
        while b"&" in text[:split_at]:
            ampersand_index = text.rindex(b"&", 0, split_at)
            if text.find(b";", ampersand_index, split_at) != -1:
                break

            split_at = ampersand_index - 1
            if split_at < 0:
                raise ValueError("Maximum byte length is too small or invalid text")
            if split_at == 0:
                break

        # Append the string to the list
        new_text = text[:split_at].strip()
        if new_text:
            yield new_text
        if split_at == 0:
            split_at = 1
        text = text[split_at:]

    new_text = text.strip()
    if new_text:
        yield new_text


def mkssml(
    text: Union[str, bytes], voice: str, rate: str, volume: str, pitch: str
) -> str:
    """
    Creates a SSML string from the given parameters.

    Returns:
        str: The SSML string.
    """
    if isinstance(text, bytes):
        text = text.decode("utf-8")

    ssml = (
        "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
        f"<voice name='{voice}'><prosody pitch='{pitch}' rate='{rate}' volume='{volume}'>"
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


def calc_max_mesg_size(voice: str, rate: str, volume: str, pitch: str) -> int:
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
                mkssml("", voice, rate, volume, pitch),
            )
        )
        + 50  # margin of error
    )
    return websocket_max_size - overhead_per_message


class Communicate:
    """
    Class for communicating with the service.
    """

    @staticmethod
    def validate_string_param(param_name: str, param_value: str, pattern: str) -> str:
        """
        Validates the given string parameter based on type and pattern.

        Args:
            param_name (str): The name of the parameter.
            param_value (str): The value of the parameter.
            pattern (str): The pattern to validate the parameter against.

        Returns:
            str: The validated parameter.
        """
        if not isinstance(param_value, str):
            raise TypeError(f"{param_name} must be str")
        if re.match(pattern, param_value) is None:
            raise ValueError(f"Invalid {param_name} '{param_value}'.")
        return param_value

    def __init__(
        self,
        text: str,
        voice: str = "Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)",
        *,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
        proxy: Optional[str] = None,
        receive_timeout: int = 5,
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
        # - fil-PH-AngeloNeural
        # Always send the first variant as that is what Microsoft Edge does.
        if not isinstance(voice, str):
            raise TypeError("voice must be str")
        self.voice: str = voice
        match = re.match(r"^([a-z]{2,})-([A-Z]{2,})-(.+Neural)$", voice)
        if match is not None:
            lang = match.group(1)
            region = match.group(2)
            name = match.group(3)
            if name.find("-") != -1:
                region = region + "-" + name[: name.find("-")]
                name = name[name.find("-") + 1 :]
            self.voice = (
                "Microsoft Server Speech Text to Speech Voice"
                + f" ({lang}-{region}, {name})"
            )

        self.voice = self.validate_string_param(
            "voice",
            self.voice,
            r"^Microsoft Server Speech Text to Speech Voice \(.+,.+\)$",
        )
        self.rate = self.validate_string_param("rate", rate, r"^[+-]\d+%$")
        self.volume = self.validate_string_param("volume", volume, r"^[+-]\d+%$")
        self.pitch = self.validate_string_param("pitch", pitch, r"^[+-]\d+Hz$")

        if proxy is not None and not isinstance(proxy, str):
            raise TypeError("proxy must be str")
        self.proxy: Optional[str] = proxy

        if not isinstance(receive_timeout, int):
            raise TypeError("receive_timeout must be int")
        self.receive_timeout: int = receive_timeout

    async def stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Streams audio and metadata from the service."""

        async def send_command_request() -> None:
            """Sends the request to the service."""

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
                f"X-Timestamp:{date_to_string()}\r\n"
                "Content-Type:application/json; charset=utf-8\r\n"
                "Path:speech.config\r\n\r\n"
                '{"context":{"synthesis":{"audio":{"metadataoptions":{'
                '"sentenceBoundaryEnabled":false,"wordBoundaryEnabled":true},'
                '"outputFormat":"audio-24khz-48kbitrate-mono-mp3"'
                "}}}}\r\n"
            )

        async def send_ssml_request() -> bool:
            """Sends the SSML request to the service."""

            # Get the next string from the generator.
            text = next(texts, None)

            # If there are no more strings, return False.
            if text is None:
                return False

            # Send the request to the service and return True.
            await websocket.send_str(
                ssml_headers_plus_data(
                    connect_id(),
                    date_to_string(),
                    mkssml(text, self.voice, self.rate, self.volume, self.pitch),
                )
            )
            return True

        def parse_metadata():
            for meta_obj in json.loads(data)["Metadata"]:
                meta_type = meta_obj["Type"]
                if meta_type == "WordBoundary":
                    current_offset = meta_obj["Data"]["Offset"] + offset_compensation
                    current_duration = meta_obj["Data"]["Duration"]
                    return {
                        "type": meta_type,
                        "offset": current_offset,
                        "duration": current_duration,
                        "text": meta_obj["Data"]["text"]["Text"],
                    }
                elif meta_type in ("SessionEnd",):
                    continue
                else:
                    raise UnknownResponse(f"Unknown metadata type: {meta_type}")

        # Split the text into multiple strings if it is too long for the service.
        texts = split_text_by_byte_length(
            escape(remove_incompatible_characters(self.text)),
            calc_max_mesg_size(self.voice, self.rate, self.volume, self.pitch),
        )

        # Keep track of last duration + offset to calculate the offset
        # upon word split.
        last_duration_offset = 0

        # Current offset compensations.
        offset_compensation = 0

        # Create a new connection to the service.
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession(
            trust_env=True,
        ) as session, session.ws_connect(
            f"{WSS_URL}&ConnectionId={connect_id()}",
            compress=15,
            proxy=self.proxy,
            receive_timeout=self.receive_timeout,
            headers={
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41",
            },
            ssl=ssl_ctx,
        ) as websocket:
            # audio_was_received indicates whether we have received audio data
            # from the websocket. This is so we can raise an exception if we
            # don't receive any audio data.
            audio_was_received = False

            # Send the request to the service.
            await send_command_request()

            # Send the SSML request to the service.
            await send_ssml_request()

            async for received in websocket:
                if received.type == aiohttp.WSMsgType.TEXT:
                    parameters, data = get_headers_and_data(received.data)
                    path = parameters.get(b"Path")
                    if path == b"audio.metadata":
                        # Parse the metadata and yield it.
                        parsed_metadata = parse_metadata()
                        yield parsed_metadata

                        # Update the last duration offset for use by the next SSML request.
                        last_duration_offset = (
                            parsed_metadata["offset"] + parsed_metadata["duration"]
                        )
                    elif path == b"turn.end":
                        # Update the offset compensation for the next SSML request.
                        offset_compensation = last_duration_offset

                        # Use average padding typically added by the service
                        # to the end of the audio data. This seems to work pretty
                        # well for now, but we might ultimately need to use a
                        # more sophisticated method like using ffmpeg to get
                        # the actual duration of the audio data.
                        offset_compensation += 8_750_000

                        # Send the next SSML request to the service.
                        if not await send_ssml_request():
                            break
                    elif path in (b"response", b"turn.start"):
                        pass
                    else:
                        raise UnknownResponse(
                            "The response from the service is not recognized.\n"
                            + received.data
                        )
                elif received.type == aiohttp.WSMsgType.BINARY:
                    if len(received.data) < 2:
                        raise UnexpectedResponse(
                            "We received a binary message, but it is missing the header length."
                        )

                    header_length = int.from_bytes(received.data[:2], "big")
                    if len(received.data) < header_length + 2:
                        raise UnexpectedResponse(
                            "We received a binary message, but it is missing the audio data."
                        )

                    audio_was_received = True
                    yield {
                        "type": "audio",
                        "data": received.data[header_length + 2 :],
                    }
                elif received.type == aiohttp.WSMsgType.ERROR:
                    raise WebSocketError(
                        received.data if received.data else "Unknown error"
                    )

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
        metadata: Union[TextIOWrapper, ContextManager[None]] = (
            open(metadata_fname, "w", encoding="utf-8")
            if metadata_fname is not None
            else nullcontext()
        )
        with metadata, open(audio_fname, "wb") as audio:
            async for message in self.stream():
                if message["type"] == "audio":
                    audio.write(message["data"])
                elif (
                    isinstance(metadata, TextIOWrapper)
                    and message["type"] == "WordBoundary"
                ):
                    json.dump(message, metadata)
                    metadata.write("\n")
