"""Communicate with the service. Only the Communicate class should be used by
end-users. The other classes and functions are for internal use only."""

import asyncio
import concurrent.futures
import json
import ssl
import time
import uuid
from contextlib import nullcontext
from io import TextIOWrapper
from queue import Queue
from typing import (
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

from .constants import DEFAULT_VOICE, SEC_MS_GEC_VERSION, WSS_HEADERS, WSS_URL
from .data_classes import TTSConfig
from .drm import DRM
from .exceptions import (
    NoAudioReceived,
    UnexpectedResponse,
    UnknownResponse,
    WebSocketError,
)
from .typing import CommunicateState, TTSChunk


def get_headers_and_data(
    data: bytes, header_length: int
) -> Tuple[Dict[bytes, bytes], bytes]:
    """
    Returns the headers and data from the given data.

    Args:
        data (bytes): The data to be parsed.
        header_length (int): The length of the header.

    Returns:
        tuple: The headers and data to be used in the request.
    """
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")

    headers = {}
    for line in data[:header_length].split(b"\r\n"):
        key, value = line.split(b":", 1)
        headers[key] = value

    return headers, data[header_length + 2 :]


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


def _find_last_newline_or_space_within_limit(text: bytes, limit: int) -> int:
    """
    Finds the index of the rightmost preferred split character (newline or space)
    within the initial `limit` bytes of the text.

    This helps find a natural word or sentence boundary for splitting, prioritizing
    newlines over spaces.

    Args:
        text (bytes): The byte string to search within.
        limit (int): The maximum index (exclusive) to search up to.

    Returns:
        int: The index of the last found newline or space within the limit,
             or -1 if neither is found in that range.
    """
    # Prioritize finding a newline character
    split_at = text.rfind(b"\n", 0, limit)
    # If no newline is found, search for a space
    if split_at < 0:
        split_at = text.rfind(b" ", 0, limit)
    return split_at


def _find_safe_utf8_split_point(text_segment: bytes) -> int:
    """
    Finds the rightmost possible byte index such that the
    segment `text_segment[:index]` is a valid UTF-8 sequence.

    This prevents splitting in the middle of a multi-byte UTF-8 character.

    Args:
        text_segment (bytes): The byte segment being considered for splitting.

    Returns:
        int: The index of the safe split point. Returns 0 if no valid split
             point is found (e.g., if the first byte is part of a multi-byte
             sequence longer than the limit allows).
    """
    split_at = len(text_segment)
    while split_at > 0:
        try:
            text_segment[:split_at].decode("utf-8")
            # Found the largest valid UTF-8 sequence
            return split_at
        except UnicodeDecodeError:
            # The byte at split_at-1 is part of an incomplete multi-byte char, try earlier
            split_at -= 1

    return split_at


def _adjust_split_point_for_xml_entity(text: bytes, split_at: int) -> int:
    """
    Adjusts a proposed split point backward to prevent splitting inside an XML entity.

    For example, if `text` is `b"this &amp; that"` and `split_at` falls between
    `&` and `;`, this function moves `split_at` to the index before `&`.

    Args:
        text (bytes): The text segment being considered.
        split_at (int): The proposed split point index, determined by whitespace
                        or UTF-8 safety.

    Returns:
        int: The adjusted split point index. It will be moved to the '&'
             if an unterminated entity is detected right before the original `split_at`.
             Otherwise, the original `split_at` is returned.
    """
    while split_at > 0 and b"&" in text[:split_at]:
        ampersand_index = text.rindex(b"&", 0, split_at)
        # Check if a semicolon exists between the ampersand and the split point
        if text.find(b";", ampersand_index, split_at) != -1:
            # Found a terminated entity (like &amp;), safe to break at original split_at
            break

        # Ampersand is not terminated before split_at, move split_at to it
        split_at = ampersand_index

    return split_at


def split_text_by_byte_length(
    text: Union[str, bytes], byte_length: int
) -> Generator[bytes, None, None]:
    """
    Splits text into chunks, each not exceeding a maximum byte length.

    This function prioritizes splitting at natural boundaries (newlines, spaces)
    while ensuring that:
    1. No chunk exceeds `byte_length` bytes.
    2. Chunks do not end with an incomplete UTF-8 multi-byte character.
    3. Chunks do not split XML entities (like `&amp;`) in the middle.

    Args:
        text (str or bytes): The input text. If str, it's encoded to UTF-8.
        byte_length (int): The maximum allowed byte length for any yielded chunk.
                           Must be positive.

    Yields:
        bytes: Text chunks (UTF-8 encoded, stripped of leading/trailing whitespace)
               that conform to the byte length and integrity constraints.

    Raises:
        TypeError: If `text` is not str or bytes.
        ValueError: If `byte_length` is not positive, or if a split point
                    cannot be determined (e.g., due to extremely small byte_length
                    relative to character/entity sizes).
    """
    if isinstance(text, str):
        text = text.encode("utf-8")
    if not isinstance(text, bytes):
        raise TypeError("text must be str or bytes")

    if byte_length <= 0:
        raise ValueError("byte_length must be greater than 0")

    while len(text) > byte_length:
        # Find the initial split point based on whitespace or UTF-8 boundary
        split_at = _find_last_newline_or_space_within_limit(text, byte_length)

        if split_at < 0:
            ## No newline or space found, so we need to find a safe UTF-8 split point
            split_at = _find_safe_utf8_split_point(text)

        # Adjust the split point to avoid cutting in the middle of an xml entity, such as '&amp;'
        split_at = _adjust_split_point_for_xml_entity(text, split_at)

        if split_at < 0:
            # This should not happen if byte_length is reasonable,
            # but guards against edge cases.
            raise ValueError(
                "Maximum byte length is too small or invalid text structure near '&' or invalid UTF-8"
            )

        # Yield the chunk
        chunk = text[:split_at].strip()
        if chunk:
            yield chunk

        # Prepare for the next iteration
        # If split_at became 0 after adjustment, advance by 1 to avoid infinite loop
        text = text[split_at if split_at > 0 else 1 :]

    # Yield the remaining part
    remaining_chunk = text.strip()
    if remaining_chunk:
        yield remaining_chunk


def mkssml(tc: TTSConfig, escaped_text: Union[str, bytes]) -> str:
    """
    Creates a SSML string from the given parameters.

    Args:
        tc (TTSConfig): The TTS configuration.
        escaped_text (str or bytes): The escaped text. If bytes, it must be UTF-8 encoded.

    Returns:
        str: The SSML string.
    """
    if isinstance(escaped_text, bytes):
        escaped_text = escaped_text.decode("utf-8")

    return (
        "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
        f"<voice name='{tc.voice}'>"
        f"<prosody pitch='{tc.pitch}' rate='{tc.rate}' volume='{tc.volume}'>"
        f"{escaped_text}"
        "</prosody>"
        "</voice>"
        "</speak>"
    )


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


def calc_max_mesg_size(tts_config: TTSConfig) -> int:
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
                mkssml(tts_config, ""),
            )
        )
        + 50  # margin of error
    )
    return websocket_max_size - overhead_per_message


class Communicate:
    """
    Communicate with the service.
    """

    def __init__(
        self,
        text: str,
        voice: str = DEFAULT_VOICE,
        *,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
        connector: Optional[aiohttp.BaseConnector] = None,
        proxy: Optional[str] = None,
        connect_timeout: Optional[int] = 10,
        receive_timeout: Optional[int] = 60,
    ):
        # Validate TTS settings and store the TTSConfig object.
        self.tts_config = TTSConfig(voice, rate, volume, pitch)

        # Validate the text parameter.
        if not isinstance(text, str):
            raise TypeError("text must be str")

        # Split the text into multiple strings and store them.
        self.texts = split_text_by_byte_length(
            escape(remove_incompatible_characters(text)),
            calc_max_mesg_size(self.tts_config),
        )

        # Validate the proxy parameter.
        if proxy is not None and not isinstance(proxy, str):
            raise TypeError("proxy must be str")
        self.proxy: Optional[str] = proxy

        # Validate the timeout parameters.
        if not isinstance(connect_timeout, int):
            raise TypeError("connect_timeout must be int")
        if not isinstance(receive_timeout, int):
            raise TypeError("receive_timeout must be int")
        self.session_timeout = aiohttp.ClientTimeout(
            total=None,
            connect=None,
            sock_connect=connect_timeout,
            sock_read=receive_timeout,
        )

        # Validate the connector parameter.
        if connector is not None and not isinstance(connector, aiohttp.BaseConnector):
            raise TypeError("connector must be aiohttp.BaseConnector")
        self.connector: Optional[aiohttp.BaseConnector] = connector

        # Store current state of TTS.
        self.state: CommunicateState = {
            "partial_text": b"",
            "offset_compensation": 0,
            "last_duration_offset": 0,
            "stream_was_called": False,
        }

    def __parse_metadata(self, data: bytes) -> TTSChunk:
        for meta_obj in json.loads(data)["Metadata"]:
            meta_type = meta_obj["Type"]
            if meta_type == "WordBoundary":
                current_offset = (
                    meta_obj["Data"]["Offset"] + self.state["offset_compensation"]
                )
                current_duration = meta_obj["Data"]["Duration"]
                return {
                    "type": meta_type,
                    "offset": current_offset,
                    "duration": current_duration,
                    "text": meta_obj["Data"]["text"]["Text"],
                }
            if meta_type in ("SessionEnd",):
                continue
            raise UnknownResponse(f"Unknown metadata type: {meta_type}")
        raise UnexpectedResponse("No WordBoundary metadata found")

    async def __stream(self) -> AsyncGenerator[TTSChunk, None]:
        async def send_command_request() -> None:
            """Sends the command request to the service."""
            await websocket.send_str(
                f"X-Timestamp:{date_to_string()}\r\n"
                "Content-Type:application/json; charset=utf-8\r\n"
                "Path:speech.config\r\n\r\n"
                '{"context":{"synthesis":{"audio":{"metadataoptions":{'
                '"sentenceBoundaryEnabled":"false","wordBoundaryEnabled":"true"},'
                '"outputFormat":"audio-24khz-48kbitrate-mono-mp3"'
                "}}}}\r\n"
            )

        async def send_ssml_request() -> None:
            """Sends the SSML request to the service."""
            await websocket.send_str(
                ssml_headers_plus_data(
                    connect_id(),
                    date_to_string(),
                    mkssml(
                        self.tts_config,
                        self.state["partial_text"],
                    ),
                )
            )

        # audio_was_received indicates whether we have received audio data
        # from the websocket. This is so we can raise an exception if we
        # don't receive any audio data.
        audio_was_received = False

        # Create a new connection to the service.
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession(
            connector=self.connector,
            trust_env=True,
            timeout=self.session_timeout,
        ) as session, session.ws_connect(
            f"{WSS_URL}&Sec-MS-GEC={DRM.generate_sec_ms_gec()}"
            f"&Sec-MS-GEC-Version={SEC_MS_GEC_VERSION}"
            f"&ConnectionId={connect_id()}",
            compress=15,
            proxy=self.proxy,
            headers=WSS_HEADERS,
            ssl=ssl_ctx,
        ) as websocket:
            await send_command_request()

            await send_ssml_request()

            async for received in websocket:
                if received.type == aiohttp.WSMsgType.TEXT:
                    encoded_data: bytes = received.data.encode("utf-8")
                    parameters, data = get_headers_and_data(
                        encoded_data, encoded_data.find(b"\r\n\r\n")
                    )

                    path = parameters.get(b"Path", None)
                    if path == b"audio.metadata":
                        # Parse the metadata and yield it.
                        parsed_metadata = self.__parse_metadata(data)
                        yield parsed_metadata

                        # Update the last duration offset for use by the next SSML request.
                        self.state["last_duration_offset"] = (
                            parsed_metadata["offset"] + parsed_metadata["duration"]
                        )
                    elif path == b"turn.end":
                        # Update the offset compensation for the next SSML request.
                        self.state["offset_compensation"] = self.state[
                            "last_duration_offset"
                        ]

                        # Use average padding typically added by the service
                        # to the end of the audio data. This seems to work pretty
                        # well for now, but we might ultimately need to use a
                        # more sophisticated method like using ffmpeg to get
                        # the actual duration of the audio data.
                        self.state["offset_compensation"] += 8_750_000

                        # Exit the loop so we can send the next SSML request.
                        break
                    elif path not in (b"response", b"turn.start"):
                        raise UnknownResponse("Unknown path received")
                elif received.type == aiohttp.WSMsgType.BINARY:
                    # Message is too short to contain header length.
                    if len(received.data) < 2:
                        raise UnexpectedResponse(
                            "We received a binary message, but it is missing the header length."
                        )

                    # The first two bytes of the binary message contain the header length.
                    header_length = int.from_bytes(received.data[:2], "big")
                    if header_length > len(received.data):
                        raise UnexpectedResponse(
                            "The header length is greater than the length of the data."
                        )

                    # Parse the headers and data from the binary message.
                    parameters, data = get_headers_and_data(
                        received.data, header_length
                    )

                    # Check if the path is audio.
                    if parameters.get(b"Path") != b"audio":
                        raise UnexpectedResponse(
                            "Received binary message, but the path is not audio."
                        )

                    # At termination of the stream, the service sends a binary message
                    # with no Content-Type; this is expected. What is not expected is for
                    # an MPEG audio stream to be sent with no data.
                    content_type = parameters.get(b"Content-Type", None)
                    if content_type not in [b"audio/mpeg", None]:
                        raise UnexpectedResponse(
                            "Received binary message, but with an unexpected Content-Type."
                        )

                    # We only allow no Content-Type if there is no data.
                    if content_type is None:
                        if len(data) == 0:
                            continue

                        # If the data is not empty, then we need to raise an exception.
                        raise UnexpectedResponse(
                            "Received binary message with no Content-Type, but with data."
                        )

                    # If the data is empty now, then we need to raise an exception.
                    if len(data) == 0:
                        raise UnexpectedResponse(
                            "Received binary message, but it is missing the audio data."
                        )

                    # Yield the audio data.
                    audio_was_received = True
                    yield {"type": "audio", "data": data}
                elif received.type == aiohttp.WSMsgType.ERROR:
                    raise WebSocketError(
                        received.data if received.data else "Unknown error"
                    )

            if not audio_was_received:
                raise NoAudioReceived(
                    "No audio was received. Please verify that your parameters are correct."
                )

    async def stream(
        self,
    ) -> AsyncGenerator[TTSChunk, None]:
        """
        Streams audio and metadata from the service.

        Raises:
            NoAudioReceived: If no audio is received from the service.
            UnexpectedResponse: If the response from the service is unexpected.
            UnknownResponse: If the response from the service is unknown.
            WebSocketError: If there is an error with the websocket.
        """

        # Check if stream was called before.
        if self.state["stream_was_called"]:
            raise RuntimeError("stream can only be called once.")
        self.state["stream_was_called"] = True

        # Stream the audio and metadata from the service.
        for self.state["partial_text"] in self.texts:
            try:
                async for message in self.__stream():
                    yield message
            except aiohttp.ClientResponseError as e:
                if e.status != 403:
                    raise

                DRM.handle_client_response_error(e)
                async for message in self.__stream():
                    yield message

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

    def stream_sync(self) -> Generator[TTSChunk, None, None]:
        """Synchronous interface for async stream method"""

        def fetch_async_items(queue: Queue) -> None:  # type: ignore
            async def get_items() -> None:
                async for item in self.stream():
                    queue.put(item)
                queue.put(None)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(get_items())
            loop.close()

        queue: Queue = Queue()  # type: ignore

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(fetch_async_items, queue)

            while True:
                item = queue.get()
                if item is None:
                    break
                yield item

    def save_sync(
        self,
        audio_fname: Union[str, bytes],
        metadata_fname: Optional[Union[str, bytes]] = None,
    ) -> None:
        """Synchronous interface for async save method."""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run, self.save(audio_fname, metadata_fname)
            )
            future.result()
