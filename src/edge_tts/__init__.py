"""edge-tts allows you to use Microsoft Edge's online text-to-speech service without
needing Windows or the Edge browser."""

from . import exceptions
from .communicate import Communicate
from .version import __version__, __version_info__
from .voices import VoicesManager, list_voices
import sys
# Conditionally import the correct SubMaker based on the presence of `--word-by-word`
if '--word-by-word' in sys.argv:
    from .submaker_word_by_word import SubMaker  # Import SubMaker for word-by-word processing
else:
    from .submaker_sentence import SubMaker  # Import SubMaker for sentence-based processing

__all__ = [
    "Communicate",
    "SubMaker",
    "exceptions",
    "__version__",
    "__version_info__",
    "VoicesManager",
    "list_voices",
]
