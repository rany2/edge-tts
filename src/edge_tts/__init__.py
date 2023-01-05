"""
__init__ for edge_tts
"""

from .communicate import Communicate
from .list_voices import VoicesManager, list_voices
from .submaker import SubMaker

__all__ = ["Communicate", "VoicesManager", "list_voices", "SubMaker"]
__version__ = "6.0.5"
