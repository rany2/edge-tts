#!/usr/bin/env python3
import sys
import json
import uuid
import argparse
import asyncio
import ssl
import websockets
import logging
import httpx
import time
import math
from xml.sax.saxutils import escape

# Default variables
ssl_context = ssl.create_default_context()
trustedClientToken = '6A5AA1D4EAFF4E9FB37E23D68491D6F4'
wssUrl = 'wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?TrustedClientToken=' + trustedClientToken
voiceList = 'https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=' + trustedClientToken

# Return date format in Microsoft Edge's broken way (Edge does it wrong because they
# append Z to a date with locale time zone). They probably just use Date().toString()
def formatdate():
    return time.strftime('%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)', time.gmtime())

# The connectID Edge sends to the service (just UUID without dashes)
def connectId():
    return str(uuid.uuid4()).replace("-", "")

# The service doesn't support a couple character ranges. Most bothering being
# \v because it is present in OCR-ed PDFs. Not doing this causes the whole
# connection with websockets server to crash.
def removeIncompatibleControlChars(s):
    logger = logging.getLogger("edgeTTS.removeIncompatibleControlChars")
    output = ""
    for char in s:
        char_code = ord(char)
        if (char_code >= 0 and char_code <= 8) or (char_code >= 11 and char_code <= 12) \
                or (char_code >= 14 and char_code <= 31):
            logger.debug("Forbidden character %s" % char.encode('utf-8'))
            output += ' '
        else:
            logger.debug("Allowed character %s" % char.encode('utf-8'))
            output += char
    logger.debug("Generated %s" % output.encode('utf-8'))
    return output

# Make WEBVTT formated timestamp based on TTS service's Offset value
def mktimestamp(ns):
    hour = math.floor(ns / 10000 / 1000 / 3600)
    minute = math.floor((ns / 10000 / 1000 / 60) % 60)
    seconds = math.floor((ns / 10000 / 1000) % 60)
    mili = float(str(math.modf((ns / 10000) - (1000 * seconds))[1])[:3])
    return "%.02d:%.02d:%.02d.%.03d" % (hour, minute, seconds, mili)

# Return loaded JSON data of list of Edge's voices
# NOTE: It's not the total list of available voices.
#       This is only what is presented in the UI.
def list_voices():
    logger = logging.getLogger("edgeTTS.list_voices")
    with httpx.Client(http2=True, headers={
            'Authority': 'speech.platform.bing.com',
            'Sec-CH-UA': "\" Not;A Brand\";v=\"99\", \"Microsoft Edge\";v=\"91\", \"Chromium\";v=\"91\"",
            'Sec-CH-UA-Mobile': '?0',
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41",
            'Accept': '*/*',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9'
    }) as url:
        logger.debug("Loading json from %s" % voiceList)
        data = json.loads(url.get(voiceList).content)
        logger.debug("JSON Loaded")
    return data

class SubMaker:
    def __init__(self, overlapping=5):
        self.subsAndOffset = {}
        self.overlapping = (overlapping * (10**7))

    def formatter(self, offset1, offset2, subdata):
        data = "%s --> %s\r\n" % (mktimestamp(offset1), mktimestamp(offset2))
        data += "%s\r\n\r\n" % escape(subdata)
        return data

    def createSub(self, timestamp, text):
        self.subsAndOffset.update({ timestamp: text })

    def generateSubs(self):
        oldTimeStamp = None
        oldSubData = None
        data = "WEBVTT\r\n\r\n"
        first = sorted(self.subsAndOffset.keys(), key=int)[0]
        try:
            second = sorted(self.subsAndOffset.keys(), key=int)[1]
            data += self.formatter(first, second + self.overlapping, self.subsAndOffset[first]) ## overlapping Subtitles
        except IndexError: # This means TTS said one word only.
            data += self.formatter(0, first + ((10**7) * 10), self.subsAndOffset[first])
        for sub in sorted(self.subsAndOffset.keys(), key=int)[1:]:
            if oldTimeStamp is not None and oldSubData is not None:
                data += self.formatter(oldTimeStamp, sub + self.overlapping, oldSubData) ## overlapping Subtitles
            oldTimeStamp = sub
            oldSubData = self.subsAndOffset[sub]
        if oldTimeStamp is not None and oldSubData is not None:
            data += self.formatter(oldTimeStamp, oldTimeStamp + ((10**7) * 10), oldSubData)
        return data

class Communicate:
    def __init__(self):
        self.date = formatdate()

    def mkssmlmsg(self, text="", voice="", pitch="", rate="", volume="", customspeak=False):
        message='X-RequestId:'+connectId()+'\r\nContent-Type:application/ssml+xml\r\n'
        message+='X-Timestamp:'+self.date+'Z\r\nPath:ssml\r\n\r\n'
        if customspeak:
            message+=text
        else:
            message+="<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
            message+="<voice  name='" + voice + "'>" + "<prosody pitch='" + pitch + "' rate ='" + rate + "' volume='" + volume + "'>" + text + '</prosody></voice></speak>'
        return message

    async def run(self, msg, sentenceBoundary=False, wordBoundary=False, codec="audio-24khz-48kbitrate-mono-mp3", voice="Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)", pitch="+0Hz", rate="+0%", volume="+0%", customspeak=False):
        sentenceBoundary = str(sentenceBoundary).lower()
        wordBoundary = str(wordBoundary).lower()

        if not customspeak:
            wsmax = 2 ** 16
            overhead = len(self.mkssmlmsg("", voice, pitch, rate, volume, customspeak=False).encode('utf-8'))
            msgs = _minimize(escape(removeIncompatibleControlChars(msg)), b" ", wsmax - overhead)

        async with websockets.connect(
            wssUrl + "&ConnectionId=" + connectId(),
            ssl=ssl_context,
            compression="deflate",
            extra_headers={
                "Pragma": "no-cache",
                "Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41",
                "Cache-Control": "no-cache"
            }
        ) as ws:
            for msg in msgs:
                self.date = formatdate() # Each message needs to have its send date

                if not customspeak:
                    msg = self.mkssmlmsg(msg.decode('utf-8'), voice, pitch, rate, volume, customspeak=False)
                else:
                    msg = self.mkssmlmsg(msg, customspeak=True)

                message='X-Timestamp:'+self.date+'\r\nContent-Type:application/json; charset=utf-8\r\nPath:speech.config\r\n\r\n'
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
                            break
                        elif 'audio.metadata' in recv:
                            #print("".join(recv.split('Path:audio.metadata\r\n\r\n')[1:]), file=sys.stderr)
                            metadata = json.loads("".join(recv.split('Path:audio.metadata\r\n\r\n')[1:]))
                            text = metadata['Metadata'][0]['Data']['text']['Text']
                            offset = metadata['Metadata'][0]['Data']['Offset']
                            yield [ offset, text, None ]
                    elif type(recv) is bytes:
                        if download:
                            yield [ None, None, b"".join(recv.split(b'Path:audio\r\n')[1:]) ]

            await ws.close()

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
    parser.add_argument('-v', '--voice', help='voice for TTS. Default: Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)', default='Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)')
    parser.add_argument('-c', '--codec', help="codec format. Default: audio-24khz-48kbitrate-mono-mp3. Another choice is webm-24khz-16bit-mono-opus. For more info check https://bit.ly/2T33h6S", default='audio-24khz-48kbitrate-mono-mp3')
    group.add_argument('-l', '--list-voices', help="lists available voices. Edge's list is incomplete so check https://bit.ly/2SFq1d3", action='store_true')
    parser.add_argument('-p', '--pitch', help="set TTS pitch. Default +0Hz, For more info check https://bit.ly/3eAE5Nx", default="+0Hz")
    parser.add_argument('-r', '--rate', help="set TTS rate. Default +0%%. For more info check https://bit.ly/3eAE5Nx", default="+0%")
    parser.add_argument('-V', '--volume', help="set TTS volume. Default +0%%. For more info check https://bit.ly/3eAE5Nx", default="+0%")
    parser.add_argument('-s', '--enable-sentence-boundary', help="enable sentence boundary (not implemented but settable)", action='store_true')
    parser.add_argument('-w', '--enable-word-boundary', help="enable word boundary (not implemented but settable)", action='store_true')
    parser.add_argument('-O', '--overlapping', help="overlapping subtitles in seconds", default=5, type=float)
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)
    logger = logging.getLogger("edgeTTS._main")
    if args.text is not None or args.file is not None:
        if args.file is not None:
            # we need to use sys.stdin.read() because some devices
            # like Windows and Termux don't have a /dev/stdin.
            if args.file == "/dev/stdin":
                logger.debug("stdin detected, reading natively from stdin")
                args.text = sys.stdin.read()
            else:
                logger.debug("reading from %s" % args.file)
                with open(args.file, 'r') as file:
                    args.text = file.read()
        tts = Communicate()
        subs = SubMaker(args.overlapping)
        async for i in tts.run(args.text, args.enable_sentence_boundary, args.enable_word_boundary, args.codec, args.voice, args.pitch, args.rate, args.volume, customspeak=args.custom_ssml):
            if i[2] is not None:
                sys.stdout.buffer.write(i[2])
            elif i[0] is not None and i[1] is not None:
                subs.createSub(i[0], i[1])
        if not subs.subsAndOffset == {}:
            sys.stderr.write(subs.generateSubs())
    elif args.list_voices:
        seperator = False
        for voice in list_voices():
            if seperator: print()
            for key in voice.keys():
                logger.debug("Processing key %s" % key)
                if key in ["SuggestedCodec", "FriendlyName", "Status"]:
                    logger.debug("Key %s skipped" % key)
                    continue
                #print ("%s: %s" % ("Name" if key == "ShortName" else key, voice[key]))
                print ("%s: %s" % (key, voice[key]))
            seperator = True

def main():
    asyncio.run(_main())

if __name__ == "__main__":
    main()
