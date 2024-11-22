"""Custom exceptions for the edge-tts package."""


class EdgeTTSException(Exception):
    """Base exception for the edge-tts package."""


class UnknownResponse(EdgeTTSException):
    """Raised when an unknown response is received from the server."""


class UnexpectedResponse(EdgeTTSException):
    """Raised when an unexpected response is received from the server.

    This hasn't happened yet, but it's possible that the server will
    change its response format in the future."""


class NoAudioReceived(EdgeTTSException):
    """Raised when no audio is received from the server."""


class WebSocketError(EdgeTTSException):
    """Raised when a WebSocket error occurs."""


class SkewAdjustmentError(EdgeTTSException):
    """Raised when an error occurs while adjusting the clock skew."""
