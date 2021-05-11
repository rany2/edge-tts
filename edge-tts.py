#!/usr/bin/env python3
import sys
import json
import uuid
import signal
import argparse
import urllib.request
import websocket # pip install websocket-client
from email.utils import formatdate
from xml.sax.saxutils import quoteattr as escape
try:
	import thread
except ImportError:
	import _thread as thread

trustedClientToken = '6A5AA1D4EAFF4E9FB37E23D68491D6F4'
voiceList = 'https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=' + trustedClientToken
wsUrl = 'wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?TrustedClientToken=' + trustedClientToken

def debug(msg, fd=sys.stderr):
	if DEBUG:
		print(msg, file=fd)

def terminator(signo, stack_frame):
	sys.exit()
signal.signal(signal.SIGINT, terminator)
signal.signal(signal.SIGTERM, terminator)

def removeIncompatibleControlChars(text):
	return text.replace(chr(9), " ").replace(chr(13), " ").replace(chr(32), " ")

def connectId():
	return str(uuid.uuid4()).replace("-", "")

def on_message(ws, m):
	m = m.encode() if type(m) is str else m
	debug("Received %s" % m)
	if b'turn.end' in m:
		ws.close()
	elif b'Path:audio\r\n' in m:
		sys.stdout.buffer.write(m.split(b'Path:audio\r\n')[1])
	"""
	elif b'"Type": "WordBoundary",\n' in m:
		print(m, file=sys.stderr)
	"""

def on_open(ws):
	def run(*args):
		message='X-Timestamp:'+formatdate()+'\r\nContent-Type:application/json; charset=utf-8\r\nPath:speech.config\r\n\r\n'
		message+='{"context":{"synthesis":{"audio":{"metadataoptions":{"sentenceBoundaryEnabled":"'+sentenceBoundaryEnabled+'","wordBoundaryEnabled":"'+wordBoundaryEnabled+'"},"outputFormat":"' + codec + '"}}}}\r\n'
		ws.send(message)
		debug("Sent %s" % message)
		message='X-RequestId:'+connectId()+'\r\nContent-Type:application/ssml+xml\r\n'
		message+='X-Timestamp:'+formatdate()+'Z\r\nPath:ssml\r\n\r\n'
		message+="<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
		message+="<voice  name='" + voice + "'>" + "<prosody pitch='" + pitchString + "' rate ='" + rateString + "' volume='" + volumeString + "'>" + escape(text) + '</prosody></voice></speak>'
		ws.send(message)
		debug("Sent %s" % message)
	thread.start_new_thread(run, ())

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

def run_tts():
	ws = websocket.WebSocketApp(wsUrl,
		on_open = on_open,
		on_message = on_message)
	ws.run_forever()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Microsoft Edge's Online TTS Reader")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-t', '--text', help='what TTS will say')
	group.add_argument('-f', '--file', help='same as --text but read from file')
	parser.add_argument('-v', '--voice', help='voice for TTS. Default: en-US-AriaNeural', default='en-US-AriaNeural')
	parser.add_argument('-c', '--codec', help="codec format. Default: audio-24khz-48kbitrate-mono-mp3. Another choice is webm-24khz-16bit-mono-opus", default='audio-24khz-48kbitrate-mono-mp3')
	group.add_argument('-l', '--list-voices', help="lists available voices. Edge's list is incomplete so check https://bit.ly/2SFq1d3", action='store_true')
	parser.add_argument('-p', '--pitch', help="set TTS pitch. Default +0Hz, For more info check https://bit.ly/3eAE5Nx", default="+0Hz")
	parser.add_argument('-r', '--rate', help="set TTS rate. Default +0%%. For more info check https://bit.ly/3eAE5Nx", default="+0%")
	parser.add_argument('-V', '--volume', help="set TTS volume. Default +0%%. For more info check https://bit.ly/3eAE5Nx", default="+0%")
	parser.add_argument('-s', '--enable-sentence-boundary', help="enable sentence boundary (not implemented but set)", action='store_true')
	parser.add_argument('-w', '--disable-word-boundary', help="disable word boundary (not implemented but set)", action='store_false')
	parser.add_argument('-S', '--dont-split-sentences', help="sends entire text as is (careful because limit is unknown)", action='store_true')
	parser.add_argument('-D', '--debug', help="some debugging", action='store_true')
	args = parser.parse_args()
	DEBUG = args.debug

	if (args.text or args.file) is not None:
		if args.file is not None:
			with open(args.file, 'r') as file:
				args.text = file.read()
		codec = args.codec
		voice = args.voice
		pitchString = args.pitch
		rateString = args.rate
		volumeString = args.volume
		sentenceBoundaryEnabled = 'true' if args.enable_sentence_boundary else 'false'
		wordBoundaryEnabled = 'true' if args.disable_word_boundary else 'false'
		if not args.dont_split_sentences:
			try:
				from nltk.tokenize import sent_tokenize
				debug("Was able to load nltk module")
			except Exception as e:
				print("You need nltk for sentence splitting.", file=sys.stderr)
				print("If you can't install it you could use the --dont-split-sentences flag.", file=sys.stderr)
				debug("Exception was %s %s" % (e.message, e.args))
				sys.exit(1)
			debug("Starting!")
			for text in sent_tokenize(removeIncompatibleControlChars(args.text)):
				debug(text)
				run_tts()
		else:
			debug("Split sentences disabled, sending text without splitting of any kind")
			text = removeIncompatibleControlChars(args.text)
			run_tts()
	elif args.list_voices:
		list_voices()
