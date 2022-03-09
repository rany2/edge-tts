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

    $ edge-tts --text "Hello, world!" --write-media hello.mp3

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

    $ edge-tts --voice ar-EG-SalmaNeural --text "مرحبا كيف حالك؟" --write-media hello_in_arabic.mp3

### Custom SSML

It is possible to send Microsoft's text-to-speech servers a custom SSML document which would allow greater customization of the speech. 

Information about the SSML format can be found here on Microsoft's own website: https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/speech-synthesis-markup

As a short example, if you want to apply the following SSML document and play it back using `edge-tts`.

```
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
    <voice name="en-US-AriaNeural">
        <mstts:express-as style="cheerful">
            That'd be just amazing!
        </mstts:express-as>
    </voice>
</speak>
```

It would be easiest to do the following:

1. Create a file called `custom_ssml.xml` with the above content.
2. Run the following command:

       $ edge-tts --custom-ssml --file custom_ssml.xml --write-media amazing.mp3

3. Voila!

### Changing pitch, rate, volume, etc.

It is possible to make minor changes to the generated speech without resorting to custom SSML. However, you must note that you couldn't use the `--custom-ssml` option with the `--pitch`, `--rate`, `--volume`, etc. options.

    $ edge-tts --pitch=-10Hz --text "Hello, world!" --write-media hello_with_pitch_down.mp3
    $ edge-tts --rate=0.5 --text "Hello, world!" --write-media hello_with_rate_halved.mp3
    $ edge-tts --volume=50 --text "Hello, world!" --write-media hello_with_volume_halved.mp3

Keep in mind that the `--pitch`, `--rate`, `--volume`, etc. options are applied to the entire SSML document.

In addition, it is required to use `--pitch=-10Hz` instead of `--pitch -10Hz` otherwise the `-10Hz` would be interpreted as just another argument.

### Note on the `edge-playback` command

`edge-playback` is just a wrapper around `edge-tts` that plays back the generated speech. It takes the same arguments as the `edge-tts` option.

## Python module

It is possible to use the `edge-tts` module directly from Python. The `examples` directory contains a few examples of how to use it.
