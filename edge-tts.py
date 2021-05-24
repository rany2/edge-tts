#!/usr/bin/env python3
import sys
import json
import uuid
import signal
import argparse
import urllib.request
import asyncio
import ssl
import websockets
import unicodedata
from email.utils import formatdate
from xml.sax.saxutils import escape

ssl_context = ssl.create_default_context()
trustedClientToken = '6A5AA1D4EAFF4E9FB37E23D68491D6F4'
wssUrl = 'wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?TrustedClientToken=' + trustedClientToken
voiceList = 'https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=' + trustedClientToken

def debug(msg, fd=sys.stderr):
    if DEBUG: print(msg, file=fd)
def terminator(signo, stack_frame): sys.exit()
signal.signal(signal.SIGINT, terminator)
signal.signal(signal.SIGTERM, terminator)
def connectId(): return str(uuid.uuid4()).replace("-", "")
def removeIncompatibleControlChars(s):
    output = []
    for ch in s:
        # We consider that these control characters are whitespace
        if ch in ['\t','\n','\r']:
            pass
        else:
            abr = unicodedata.category(ch)
            if abr.startswith("C"): continue
        output += [ ch ]
    return "".join(output)

def list_voices():
    with urllib.request.urlopen(voiceList) as url:
        debug("Loading json from %s" % voiceList)
        data = json.loads(url.read().decode())
        debug("JSON Loaded")
        for voice in data:
            print()
            for key in voice.keys():
                debug("Processing key %s" % key)
                if key in ["Name", "SuggestedCodec", "FriendlyName", "Status"]:
                    debug("Key %s skipped" % key)
                    continue
                print("%s: %s" % ("Name" if key == "ShortName" else key, voice[key]))
    print()

def mkssmlmsg(text="", customspeak=False):
    message='X-RequestId:'+connectId()+'\r\nContent-Type:application/ssml+xml\r\n'
    message+='X-Timestamp:'+formatdate()+'Z\r\nPath:ssml\r\n\r\n'
    if customspeak:
        message+=text
    else:
        message+="<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
        message+="<voice  name='" + voice + "'>" + "<prosody pitch='" + pitchString + "' rate ='" + rateString + "' volume='" + volumeString + "'>" + text + '</prosody></voice></speak>'
    return message

async def run_tts(msg):
    debug("Doing %s!" % msg)
    async with websockets.connect(wssUrl, ssl=ssl_context) as ws:
        message='X-Timestamp:'+formatdate()+'\r\nContent-Type:application/json; charset=utf-8\r\nPath:speech.config\r\n\r\n'
        message+='{"context":{"synthesis":{"audio":{"metadataoptions":{"sentenceBoundaryEnabled":"'+sentenceBoundaryEnabled+'","wordBoundaryEnabled":"'+wordBoundaryEnabled+'"},"outputFormat":"' + codec + '"}}}}\r\n'
        await ws.send(message)
        debug("> %s" % message)
        await ws.send(msg)
        debug("> %s" % msg)
        while True:
            recv = await ws.recv()
            recv = recv.encode() if type(recv) is not bytes else recv
            debug("< %s" % recv)
            if b'turn.end' in recv:
                break
            elif b'Path:audio\r\n' in recv:
                sys.stdout.buffer.write(recv.split(b'Path:audio\r\n')[1])

# From https://github.com/pndurette/gTTS/blob/6d9309f05b3ad26ca356654732f3b5b9c3bec538/gtts/utils.py#L13-L54
def _minimize(the_string, delim, max_size):
    """Recursively split a string in the largest chunks
    possible from the highest position of a delimiter all the way
    to a maximum size
    Args:
        the_string (string): The string to split.
        delim (string): The delimiter to split on.
        max_size (int): The maximum size of a chunk.
    Returns:
        list: the minimized string in tokens
    Every chunk size will be at minimum ``the_string[0:idx]`` where ``idx``
    is the highest index of ``delim`` found in ``the_string``; and at maximum
    ``the_string[0:max_size]`` if no ``delim`` was found in ``the_string``.
    In the latter case, the split will occur at ``the_string[max_size]``
    which can be any character. The function runs itself again on the rest of
    ``the_string`` (``the_string[idx:]``) until no chunk is larger than
    ``max_size``.
    """
    # Remove `delim` from start of `the_string`
    # i.e. prevent a recursive infinite loop on `the_string[0:0]`
    # if `the_string` starts with `delim` and is larger than `max_size`
    if the_string.startswith(delim):
        the_string = the_string[len(delim):]

    if len(the_string) > max_size:
        try:
            # Find the highest index of `delim` in `the_string[0:max_size]`
            # i.e. `the_string` will be cut in half on `delim` index
            idx = the_string.rindex(delim, 0, max_size)
        except ValueError:
            # `delim` not found in `the_string`, index becomes `max_size`
            # i.e. `the_string` will be cut in half arbitrarily on `max_size`
            idx = max_size
        # Call itself again for `the_string[idx:]`
        return [the_string[:idx]] + \
            _minimize(the_string[idx:], delim, max_size)
    else:
        return [the_string]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Microsoft Edge's Online TTS Reader")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--text', help='what TTS will say')
    group.add_argument('-f', '--file', help='same as --text but read from file')
    parser.add_argument('-z', '--custom-ssml', help='treat text as ssml to send. For more info check https://bit.ly/3fIq13S', action='store_true')
    parser.add_argument('-v', '--voice', help='voice for TTS. Default: en-US-AriaNeural', default='en-US-AriaNeural')
    parser.add_argument('-c', '--codec', help="codec format. Default: audio-24khz-48kbitrate-mono-mp3. Another choice is webm-24khz-16bit-mono-opus", default='audio-24khz-48kbitrate-mono-mp3')
    group.add_argument('-l', '--list-voices', help="lists available voices. Edge's list is incomplete so check https://bit.ly/2SFq1d3", action='store_true')
    parser.add_argument('-p', '--pitch', help="set TTS pitch. Default +0Hz, For more info check https://bit.ly/3eAE5Nx", default="+0Hz")
    parser.add_argument('-r', '--rate', help="set TTS rate. Default +0%%. For more info check https://bit.ly/3eAE5Nx", default="+0%")
    parser.add_argument('-V', '--volume', help="set TTS volume. Default +0%%. For more info check https://bit.ly/3eAE5Nx", default="+0%")
    parser.add_argument('-s', '--enable-sentence-boundary', help="enable sentence boundary (not implemented but set)", action='store_true')
    parser.add_argument('-w', '--enable-word-boundary', help="enable word boundary (not implemented but set)", action='store_true')
    parser.add_argument('-D', '--debug', help="some debugging", action='store_true')
    args = parser.parse_args()
    DEBUG = args.debug

    if (args.text or args.file) is not None:
        if args.file is not None:
            # we need to use sys.stdin.read() because some devices
            # like Windows and Termux don't have a /dev/stdin.
            if args.file == "/dev/stdin":
                debug("stdin detected, reading natively from stdin")
                args.text = sys.stdin.read()
            else:
                debug("reading from %s" % args.file)
                with open(args.file, 'r') as file:
                    args.text = file.read()
        codec = args.codec
        voice = args.voice
        pitchString = args.pitch
        rateString = args.rate
        volumeString = args.volume
        sentenceBoundaryEnabled = 'true' if args.enable_sentence_boundary else 'false'
        wordBoundaryEnabled = 'true' if args.enable_word_boundary else 'false'
        # https://hpbn.co/websocket/ says client must also send a masking key,
        # which adds an extra 4 bytes to the header, resulting in 6–14 bytes over overhead
        if args.custom_ssml:
            asyncio.get_event_loop().run_until_complete(run_tts(mkssmlmsg(text=args.text, customspeak=True)))
        else:
            overhead = len(mkssmlmsg()) + 14
            wsmax = 65536 - overhead
            for text in _minimize(escape(removeIncompatibleControlChars(args.text)), " ", wsmax):
                asyncio.get_event_loop().run_until_complete(run_tts(mkssmlmsg(text)))
    elif args.list_voices:
        list_voices()
