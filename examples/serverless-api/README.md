# Serverless Edge TTS API

This project demonstrates how to run Edge TTS as a serverless API using [Cerebrium](https://www.cerebrium.ai)

## Overview

The `main.py` file contains a function `run` that takes a text input and an optional voice parameter to generate audio and subtitles using Edge TTS. This example specifically streams the output.

## Installation

1. pip install cerebrium
2. cerebrium login
3. Make sure you are in the serverless-api folder and run ```cerebrium deploy```

## Usage

Once deployed, you should be able to make a curl request similar to the below. You can find this url on your Cerebrium dashboard.
```
curl --location 'https://api.cortex.cerebrium.ai/v4/p-xxxxxx/serverless-api/run' \
--header 'Authorization: Bearer <AUTH_TOKEN>' \
--header 'Content-Type: application/json' \
--data '{"text": "Tell me something"}'
```

The `run` function takes two parameters:

- `text` (str): The text to be converted to speech
- `voice` (str, optional): The voice to use for TTS (default: "en-GB-SoniaNeural")

It returns a dictionary containing:

- `audio_data`: The generated audio as a base64-encoded string
- `subtitles`: The generated subtitles in WebVTT format
