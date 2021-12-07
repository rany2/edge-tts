"""
Constants for the edgeTTS package.
"""

TRUSTED_CLIENT_TOKEN = "6A5AA1D4EAFF4E9FB37E23D68491D6F4"
WSS_URL = (
    "wss://speech.platform.bing.com/consumer/speech/synthesize/"
    + "readaloud/edge/v1?TrustedClientToken="
    + TRUSTED_CLIENT_TOKEN
)
VOICE_LIST = (
    "https://speech.platform.bing.com/consumer/speech/synthesize/"
    + "readaloud/voices/list?trustedclienttoken="
    + TRUSTED_CLIENT_TOKEN
)
