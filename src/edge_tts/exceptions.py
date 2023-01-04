class UnknownResponse(Exception):
    """Raised when an unknown response is received from the server."""


class UnexpectedResponse(Exception):
    """Raised when an unexpected response is received from the server.

    This hasn't happened yet, but it's possible that the server will
    change its response format in the future."""


class NoAudioReceived(Exception):
    """Raised when no audio is received from the server."""
