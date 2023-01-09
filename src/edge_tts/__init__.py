"""
__init__ for edge_tts
"""

from . import exceptions
from .communicate import Communicate
from .list_voices import VoicesManager, list_voices
from .submaker import SubMaker

__all__ = [
    "Communicate",
    "SubMaker",
    "VoicesManager",
    "exceptions",
    "list_voices",
]
__version__ = "6.1"
