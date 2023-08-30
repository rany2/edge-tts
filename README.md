# edge-tts

`edge-tts` is a Python module that allows you to use Microsoft Edge's online text-to-speech service from within your Python code or using the provided `edge-tts` or `edge-playback` command.

## Installation

To install it, run the following command:

    $ pip install edge-tts

If you only want to use the `edge-tts` and `edge-playback` commands, it would be better to use pipx:

    $ pipx install edge-tts

## Usage

### Basic usage

If you want to use the `edge-tts` command, you can simply run it with the following command:

    $ edge-tts --text "Hello, world!" --write-media hello.mp3 --write-subtitles hello.vtt

If you wish to play it back immediately with subtitles, you could use the `edge-playback` command:

    $ edge-playback --text "Hello, world!"

Note the above requires the installation of the `mpv` command line player.

All `edge-tts` commands work in `edge-playback` as well.

### Changing the voice

If you want to change the language of the speech or more generally, the voice. 

You must first check the available voices with the `--list-voices` option:

    $ edge-tts --list-voices
    Name: Microsoft Server Speech Text to Speech Voice (af-ZA, AdriNeural)
    ShortName: af-ZA-AdriNeural
    Gender: Female
    Locale: af-ZA

    Name: Microsoft Server Speech Text to Speech Voice (am-ET, MekdesNeural)
    ShortName: am-ET-MekdesNeural
    Gender: Female
    Locale: am-ET

    Name: Microsoft Server Speech Text to Speech Voice (ar-EG, SalmaNeural)
    ShortName: ar-EG-SalmaNeural
    Gender: Female
    Locale: ar-EG

    Name: Microsoft Server Speech Text to Speech Voice (ar-SA, ZariyahNeural)
    ShortName: ar-SA-ZariyahNeural
    Gender: Female
    Locale: ar-SA

    ...

    $ edge-tts --voice ar-EG-SalmaNeural --text "مرحبا كيف حالك؟" --write-media hello_in_arabic.mp3 --write-subtitles hello_in_arabic.vtt

### Custom SSML

Support for custom SSML has been removed since 5.0.0 because Microsoft has taken the initiative to prevent it from working. You cannot use custom SSML anymore.

### Changing rate and volume

It is possible to make minor changes to the generated speech.

    $ edge-tts --rate=-50% --text "Hello, world!" --write-media hello_with_rate_halved.mp3 --write-subtitles hello_with_rate_halved.vtt
    $ edge-tts --volume=-50% --text "Hello, world!" --write-media hello_with_volume_halved.mp3 --write-subtitles hello_with_volume_halved.vtt

In addition, it is required to use `--rate=-50%` instead of `--rate -50%` (note the lack of an equal sign) otherwise the `-50%` would be interpreted as just another argument.

### Note on the `edge-playback` command

`edge-playback` is just a wrapper around `edge-tts` that plays back the generated speech. It takes the same arguments as the `edge-tts` option.

## Python module

It is possible to use the `edge-tts` module directly from Python. For a list of example applications:

* https://github.com/rany2/edge-tts/blob/master/examples/basic_generation.py
* https://github.com/rany2/edge-tts/blob/master/examples/dynamic_voice_selection.py
* https://github.com/rany2/edge-tts/blob/master/examples/basic_audio_streaming.py
* https://github.com/rany2/edge-tts/blob/master/examples/streaming_with_subtitles.py
* https://github.com/rany2/edge-tts/blob/master/src/edge_tts/util.py
* https://github.com/hasscc/hass-edge-tts/blob/main/custom_components/edge_tts/tts.py
