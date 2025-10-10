"""
__init__ for edge_tts
"""

from . import exceptions
from .communicate import Communicate
from .list_voices import VoicesManager, list_voices
from .submaker import SubMaker
from .version import __version__

# Enhanced features
try:
    from .enhanced import (
        EnhancedCommunicate,
        ContentAnalyzer,
        AdvancedTextProcessor,
        BatchProcessor,
        speak_intelligently,
        batch_speak,
        ContentType,
        EmotionType,
        PauseType,
        VoiceProfile,
        MLAnalysis,
        TextEffect
    )
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

__all__ = [
    "Communicate",
    "SubMaker",
    "VoicesManager",
    "exceptions",
    "list_voices",
]

if ENHANCED_AVAILABLE:
    __all__.extend([
        "EnhancedCommunicate",
        "ContentAnalyzer", 
        "AdvancedTextProcessor",
        "BatchProcessor",
        "speak_intelligently",
        "batch_speak",
        "ContentType",
        "EmotionType",
        "PauseType",
        "VoiceProfile",
        "MLAnalysis",
        "TextEffect"
    ])
