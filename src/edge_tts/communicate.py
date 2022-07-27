"""
Communicate package.
"""


import json
import time
import uuid
from xml.sax.saxutils import escape

import aiohttp

from .constants import WSS_URL


def get_headers_and_data(data):
    """
    Returns the headers and data from the given data.

    Args:
        data (str or bytes): The data to be parsed.

    Returns:
        tuple: The headers and data to be used in the request.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    headers = {}
    for line in data.split(b"\r\n\r\n")[0].split(b"\r\n"):
        line_split = line.split(b":")
        key, value = line_split[0], b":".join(line_split[1:])
        if value.startswith(b" "):
            value = value[1:]
        headers[key.decode("utf-8")] = value.decode("utf-8")

    return headers, b"\r\n\r\n".join(data.split(b"\r\n\r\n")[1:])


def remove_incompatible_characters(string):
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

    string = list(string)

    for idx, char in enumerate(string):
        code = ord(char)
        if (0 <= code <= 8) or (11 <= code <= 12) or (14 <= code <= 31):
            string[idx] = " "

    return "".join(string)


def connect_id():
    """
    Returns a UUID without dashes.

    Args:
        None

    Returns:
        str: A UUID without dashes.
    """
    return str(uuid.uuid4()).replace("-", "")


def iter_bytes(my_bytes):
    """
    Iterates over bytes object

    Args:
        my_bytes: Bytes object to iterate over

    Yields:
        the individual bytes
    """
    for i in range(len(my_bytes)):
        yield my_bytes[i : i + 1]


def split_text_by_byte_length(text, byte_length):
    """
    Splits a string into a list of strings of a given byte length
    while attempting to keep words together.

    Args:
        text (byte): The string to be split.
        byte_length (int): The byte length of each string in the list.

    Returns:
        list: A list of strings of the given byte length.
    """
    if isinstance(text, str):
        text = text.encode("utf-8")

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


def mkssml(text, voice, pitch, rate, volume):
    """
    Creates a SSML string from the given parameters.

    Args:
        text (str): The text to be spoken.
        voice (str): The voice to be used.
        pitch (str): The pitch to be used.
        rate (str): The rate to be used.
        volume (str): The volume to be used.

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


def date_to_string():
    """
    Return Javascript-style date string.

    Args:
        None

    Returns:
        str: Javascript-style date string.
    """
    # %Z is not what we want, but it's the only way to get the timezone
    # without having to use a library. We'll just use UTC and hope for the best.
    # For example, right now %Z would return EEST when we need it to return
    # Eastern European Summer Time.
    #
    # return time.strftime("%a %b %d %Y %H:%M:%S GMT%z (%Z)")
    return time.strftime(
        "%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)", time.gmtime()
    )


def ssml_headers_plus_data(request_id, timestamp, ssml):
    """
    Returns the headers and data to be used in the request.

    Args:
        request_id (str): The request ID.
        timestamp (str): The timestamp.
        ssml (str): The SSML string.

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


class Communicate:
    """
    Class for communicating with the service.
    """

    def __init__(self):
        """
        Initializes the Communicate class.
        """
        self.date = date_to_string()

    async def run(
        self,
        messages,
        boundary_type=0,
        codec="audio-24khz-48kbitrate-mono-mp3",
        voice="Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)",
        pitch="+0Hz",
        rate="+0%",
        volume="+0%",
        proxy=None,
    ):
        """
        Runs the Communicate class.

        Args:
            messages (str or list): A list of SSML strings or a single text.
            boundery_type (int): The type of boundary to use. 0 for none, 1 for word_boundary, 2 for sentence_boundary.
            codec (str): The codec to use.
            voice (str): The voice to use.
            pitch (str): The pitch to use.
            rate (str): The rate to use.
            volume (str): The volume to use.

        Yields:
            tuple: The subtitle offset, subtitle, and audio data.
        """

        word_boundary = False

        if boundary_type > 0:
            word_boundary = True
        if boundary_type > 1:
            raise ValueError(
                "Invalid boundary type. SentenceBoundary is no longer supported."
            )

        word_boundary = str(word_boundary).lower()

        websocket_max_size = 2**16
        overhead_per_message = (
            len(
                ssml_headers_plus_data(
                    connect_id(), self.date, mkssml("", voice, pitch, rate, volume)
                )
            )
            + 50
        )  # margin of error
        messages = split_text_by_byte_length(
            escape(remove_incompatible_characters(messages)),
            websocket_max_size - overhead_per_message,
        )

        # Variables for the loop
        download = False
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.ws_connect(
                f"{WSS_URL}&ConnectionId={connect_id()}",
                compress=15,
                autoclose=True,
                autoping=True,
                proxy=proxy,
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
                for message in messages:
                    # Each message needs to have the proper date
                    self.date = date_to_string()

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
                    request = (
                        f"X-Timestamp:{self.date}\r\n"
                        "Content-Type:application/json; charset=utf-8\r\n"
                        "Path:speech.config\r\n\r\n"
                        '{"context":{"synthesis":{"audio":{"metadataoptions":{'
                        f'"sentenceBoundaryEnabled":false,'
                        f'"wordBoundaryEnabled":{word_boundary}}},"outputFormat":"{codec}"'
                        "}}}}\r\n"
                    )
                    # Send the request to the service.
                    await websocket.send_str(request)
                    # Send the message itself.
                    await websocket.send_str(
                        ssml_headers_plus_data(
                            connect_id(),
                            self.date,
                            mkssml(message, voice, pitch, rate, volume),
                        )
                    )

                    # Begin listening for the response.
                    async for received in websocket:
                        if received.type == aiohttp.WSMsgType.TEXT:
                            parameters, data = get_headers_and_data(received.data)
                            if (
                                "Path" in parameters
                                and parameters["Path"] == "turn.start"
                            ):
                                download = True
                            elif (
                                "Path" in parameters
                                and parameters["Path"] == "turn.end"
                            ):
                                download = False
                                break
                            elif (
                                "Path" in parameters
                                and parameters["Path"] == "audio.metadata"
                            ):
                                metadata = json.loads(data)
                                metadata_type = metadata["Metadata"][0]["Type"]
                                metadata_offset = metadata["Metadata"][0]["Data"][
                                    "Offset"
                                ]
                                if metadata_type == "WordBoundary":
                                    metadata_duration = metadata["Metadata"][0]["Data"][
                                        "Duration"
                                    ]
                                    metadata_text = metadata["Metadata"][0]["Data"]["text"][
                                        "Text"
                                    ]
                                    yield (
                                        [
                                            metadata_offset,
                                            metadata_duration,
                                        ],
                                        metadata_text,
                                        None,
                                    )
                                elif metadata_type == "SentenceBoundary":
                                    raise NotImplementedError(
                                        "SentenceBoundary is not supported due to being broken."
                                    )
                                elif metadata_type == "SessionEnd":
                                    continue
                                else:
                                    raise NotImplementedError(
                                        f"Unknown metadata type: {metadata_type}"
                                    )
                            elif (
                                "Path" in parameters
                                and parameters["Path"] == "response"
                            ):
                                # TODO: implement this:
                                """
                                X-RequestId:xxxxxxxxxxxxxxxxxxxxxxxxx
                                Content-Type:application/json; charset=utf-8
                                Path:response

                                {"context":{"serviceTag":"yyyyyyyyyyyyyyyyyyy"},"audio":{"type":"inline","streamId":"zzzzzzzzzzzzzzzzz"}}
                                """
                                pass
                            else:
                                raise ValueError(
                                    "The response from the service is not recognized.\n"
                                    + received.data
                                )
                        elif received.type == aiohttp.WSMsgType.BINARY:
                            if download:
                                yield (
                                    None,
                                    None,
                                    b"Path:audio\r\n".join(
                                        received.data.split(b"Path:audio\r\n")[1:]
                                    ),
                                )
                            else:
                                raise ValueError(
                                    "The service sent a binary message, but we are not expecting one."
                                )
                await websocket.close()
