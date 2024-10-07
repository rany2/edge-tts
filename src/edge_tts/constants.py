"""
Constants for the Edge TTS project.
"""

TRUSTED_CLIENT_TOKEN = "6A5AA1D4EAFF4E9FB37E23D68491D6F4"
BASE_URL = "https://speech.platform.bing.com/consumer/speech/synthesize"

WSS_URL = f"wss://{BASE_URL}/readaloud/edge/v1?TrustedClientToken={TRUSTED_CLIENT_TOKEN}"
VOICE_LIST = f"{BASE_URL}/readaloud/voices/list?trustedclienttoken={TRUSTED_CLIENT_TOKEN}"
