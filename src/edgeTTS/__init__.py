#!/usr/bin/env python3
import sys
import json
import uuid
import signal
import argparse
import asyncio
import ssl
import websockets
import logging
import httpx
from email.utils import formatdate
from xml.sax.saxutils import escape

ssl_context = ssl.create_default_context()
trustedClientToken = '6A5AA1D4EAFF4E9FB37E23D68491D6F4'
wssUrl = 'wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?TrustedClientToken=' + trustedClientToken
voiceList = 'https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=' + trustedClientToken

def connectId():
    return str(uuid.uuid4()).replace("-", "")

def removeIncompatibleControlChars(s):
    output = []
    for char in s:
        char_code = ord(char)
        if (char_code >= 0 and char_code <= 8) or (char_code >= 11 and char_code <= 12) \
                or (char_code >= 14 and char_code <= 31):
            output += [ ' ' ]
        else:
            output += [ char ]
    return "".join(output)

def list_voices():
    with httpx.Client(http2=True, headers={
            'Authority': 'speech.platform.bing.com',
            'Host': 'speech.platform.bing.com',
            'Sec-CH-UA': "\" Not;A Brand\";v=\"99\", \"Microsoft Edge\";v=\"91\", \"Chromium\";v=\"91\"",
            'Sec-CH-UA-Mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Language': 'en-US,en;q=0.9'
    }) as url:
        logging.debug("Loading json from %s" % voiceList)
        data = json.loads(url.get(voiceList).content)
        logging.debug("JSON Loaded")
    return data

def mkssmlmsg(text="", voice="en-US-AriaNeural", pitchString="+0Hz", rateString="+0%", volumeString="+0%", customspeak=False):
    message='X-RequestId:'+connectId()+'\r\nContent-Type:application/ssml+xml\r\n'
    message+='X-Timestamp:'+formatdate()+'Z\r\nPath:ssml\r\n\r\n'
    if customspeak:
        message+=text
    else:
        message+="<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
        message+="<voice  name='" + voice + "'>" + "<prosody pitch='" + pitchString + "' rate ='" + rateString + "' volume='" + volumeString + "'>" + text + '</prosody></voice></speak>'
    return message

def bool_to_lower_str(x): return 'true' if x else 'false'
async def run_tts(msg, sentenceBoundary=False, wordBoundary=False, codec="audio-24khz-48kbitrate-mono-mp3"):
    sentenceBoundary = bool_to_lower_str(sentenceBoundary)
    wordBoundary = bool_to_lower_str(wordBoundary)
    # yes, the connectid() in websockets.connect is different
    async with websockets.connect(
        wssUrl + "&ConnectionId=" + connectId(),
        ssl=ssl_context,
        compression="deflate",
        extra_headers={
            "Pragma": "no-cache",
            "Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41",
            "Cache-Control": "no-cache"
        }
    ) as ws:
        message='X-Timestamp:'+formatdate()+'\r\nContent-Type:application/json; charset=utf-8\r\nPath:speech.config\r\n\r\n'
        message+='{"context":{"synthesis":{"audio":{"metadataoptions":{"sentenceBoundaryEnabled":"'+sentenceBoundary+'","wordBoundaryEnabled":"'+wordBoundary+'"},"outputFormat":"' + codec + '"}}}}\r\n'
        await ws.send(message)
        await ws.send(msg)
        download = False
        async for recv in ws:
            if type(recv) is str:
                if 'turn.start' in recv:
                    download = True
                elif 'turn.end' in recv:
                    download = False
                    await ws.close()
                # TODO: add some sort of captioning based on audio:metadata. It's just JSON with offset.
                # WordBoundary is the only thing supported. SentenceBoundary does nothing.
                #elif 'audio.metadata' in recv:
                #    print("".join(recv.split('Path:audio.metadata\r\n\r\n')[1:]), file=sys.stderr)
            elif type(recv) is bytes:
                if download:
                    yield b"".join(recv.split(b'Path:audio\r\n')[1:])

# Based on https://github.com/pndurette/gTTS/blob/6d9309f05b3ad26ca356654732f3b5b9c3bec538/gtts/utils.py#L13-L54
# Modified to measure based on bytes rather than number of characters
def _minimize(the_string, delim, max_size):
    # Make sure we are measuring based on bytes
    the_string = the_string.encode('utf-8') if type(the_string) is str else the_string

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

async def _main():
    parser = argparse.ArgumentParser(description="Microsoft Edge's Online TTS Reader")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--text', help='what TTS will say')
    group.add_argument('-f', '--file', help='same as --text but read from file')
    parser.add_argument(
        "-L",
        "--log-level",
        default=logging.CRITICAL,
        type=lambda x: getattr(logging, x),
        help="configure the logging level (currently only DEBUG supported)"
    )
    parser.add_argument('-z', '--custom-ssml', help='treat text as ssml to send. For more info check https://bit.ly/3fIq13S', action='store_true')
    parser.add_argument('-v', '--voice', help='voice for TTS. Default: en-US-AriaNeural', default='en-US-AriaNeural')
    parser.add_argument('-c', '--codec', help="codec format. Default: audio-24khz-48kbitrate-mono-mp3. Another choice is webm-24khz-16bit-mono-opus. For more info check https://bit.ly/2T33h6S", default='audio-24khz-48kbitrate-mono-mp3')
    group.add_argument('-l', '--list-voices', help="lists available voices. Edge's list is incomplete so check https://bit.ly/2SFq1d3", action='store_true')
    parser.add_argument('-p', '--pitch', help="set TTS pitch. Default +0Hz, For more info check https://bit.ly/3eAE5Nx", default="+0Hz")
    parser.add_argument('-r', '--rate', help="set TTS rate. Default +0%%. For more info check https://bit.ly/3eAE5Nx", default="+0%")
    parser.add_argument('-V', '--volume', help="set TTS volume. Default +0%%. For more info check https://bit.ly/3eAE5Nx", default="+0%")
    parser.add_argument('-s', '--enable-sentence-boundary', help="enable sentence boundary (not implemented but settable)", action='store_true')
    parser.add_argument('-w', '--enable-word-boundary', help="enable word boundary (not implemented but settable)", action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)
    if (args.text or args.file) is not None:
        if args.file is not None:
            # we need to use sys.stdin.read() because some devices
            # like Windows and Termux don't have a /dev/stdin.
            if args.file == "/dev/stdin":
                logging.debug("stdin detected, reading natively from stdin")
                args.text = sys.stdin.read()
            else:
                logging.debug("reading from %s" % args.file)
                with open(args.file, 'r') as file:
                    args.text = file.read()
        if args.custom_ssml:
            async for i in run_tts(mkssmlmsg(text=args.text, customspeak=True), args.enable_sentence_boundary, args.enable_word_boundary, args.codec):
                sys.stdout.buffer.write(i)
        else:
            overhead = len(mkssmlmsg('', args.voice, args.pitch, args.rate, args.volume).encode('utf-8'))
            wsmax = 65536 - overhead
            for text in _minimize(escape(removeIncompatibleControlChars(args.text)), b" ", wsmax):
                async for i in run_tts(mkssmlmsg(text.decode('utf-8'), args.voice, args.pitch, args.rate, args.volume), args.enable_sentence_boundary, args.enable_word_boundary, args.codec):
                    sys.stdout.buffer.write(i)
    elif args.list_voices:
        seperator = False
        for voice in list_voices():
            if seperator: print()
            for key in voice.keys():
                logging.debug("Processing key %s" % key)
                if key in ["Name", "SuggestedCodec", "FriendlyName", "Status"]:
                    logging.debug("Key %s skipped" % key)
                    continue
                print("%s: %s" % ("Name" if key == "ShortName" else key, voice[key]))
            seperator = True

def terminator(signo, stack_frame): sys.exit()
def main():
    signal.signal(signal.SIGINT, terminator)
    signal.signal(signal.SIGTERM, terminator)
    asyncio.run(_main())

if __name__ == "__main__":
    main()
