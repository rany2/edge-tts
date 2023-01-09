"""
__init__ for edge_tts
"""

from . import exceptions
from .communicate import Communicate
from .list_voices import VoicesManager, list_voices
from .submaker import SubMaker
from .version import __version__

__all__ = [
    "Communicate",
    "SubMaker",
    "VoicesManager",
    "exceptions",
    "list_voices",
]
