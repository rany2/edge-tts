#!/usr/bin/env python3
import sys
import json
import uuid
import argparse
import urllib.request
import websocket # pip install websocket-client
from xml.sax.saxutils import quoteattr as escape
try:
	import thread
except ImportError:
	import _thread as thread

trustedClientToken = '6A5AA1D4EAFF4E9FB37E23D68491D6F4'
voiceList = 'https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=' + trustedClientToken
wsUrl = 'wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?TrustedClientToken=' + trustedClientToken

def connectId():
	return str(uuid.uuid4()).replace("-", "")

def on_message(ws, m):
	m = m.encode() if type(m) is str else m
	if b'turn.end' in m:
		ws.close()
	elif b'Path:audio\r\n' in m:
		sys.stdout.buffer.write(m.split(b'Path:audio\r\n')[1])

def on_open(ws):
	# TODO: add X-Timestamp header with value being javascript Date().toString() in US locale
	def run(*args):
		message='Content-Type:application/json; charset=utf-8\r\n\r\nPath:speech.config\r\n\r\n{"context":{"synthesis":{"audio":{"metadataoptions":'
		message+='{"sentenceBoundaryEnabled":"'+sentenceBoundaryEnabled+'","wordBoundaryEnabled":"'+wordBoundaryEnabled+'"},"outputFormat":"' + codec + '"}}}}\r\n'
		ws.send(message)
		message='X-RequestId:'+connectId()+'\r\nContent-Type:application/ssml+xml\r\nPath:ssml\r\n\r\n'
		message+="<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
		message+="<voice  name='" + voice + "'>" + "<prosody pitch='" + pitchString + "' rate ='" + rateString + "' volume='" + volumeString + "'>" + escape(text) + '</prosody></voice></speak>'
		ws.send(message)
	thread.start_new_thread(run, ())

def list_voices():
	with urllib.request.urlopen(voiceList) as url:
		data = json.loads(url.read().decode())
		for voice in data:
			print()
			for key in voice.keys():
				if key == "Name" or key == "SuggestedCodec" \
				or key == "FriendlyName" or key == "Status":
					continue
				print("%s: %s" % (key, voice[key]))

def run_tts():
	#websocket.enableTrace(1)
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
	parser.add_argument('-c', '--codec', help="codec format. Default: audio-24khz-48kbitrate-mono-mp3. webm-24khz-16bit-mono-opus doesn't work", default='audio-24khz-48kbitrate-mono-mp3')
	group.add_argument('-l', '--list-voices', help="lists available voices. Edge's list is incomplete so check https://bit.ly/2SFq1d3", action='store_true')
	parser.add_argument('-p', '--pitch', help="set TTS pitch. Default +0Hz", default="+0Hz")
	parser.add_argument('-r', '--rate', help="set TTS rate. Default +0%%", default="+0%")
	parser.add_argument('-V', '--volume', help="set TTS volume. Default +0%%", default="+0%")
	parser.add_argument('-s', '--enable-sentence-boundary', help="enable sentence boundary", action='store_true')
	parser.add_argument('-w', '--disable-word-boundary', help="disable word boundary", action='store_false')
	args = parser.parse_args()

	if args.text is not None or args.file is not None:
		if args.file is not None:
			with open(args.file, 'r') as file:
				args.text = file.read()
		codec = args.codec
		voice = args.voice
		pitchString = args.pitch
		rateString = args.rate
		volumeString = args.volume
		sentenceBoundaryEnabled = 'True' if args.enable_sentence_boundary else 'False'
		wordBoundaryEnabled = 'True' if args.disable_word_boundary else 'False'
		text = args.text.replace(chr(9), " ").replace(chr(13), " ").replace(chr(32), " ")
		run_tts()
	elif args.list_voices is True:
		list_voices()
