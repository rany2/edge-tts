"""Functions to play audio on Windows using native win32 APIs"""

import sys

from .util import pr_err


def play_mp3_win32(mp3_fname: str) -> None:
    """Play mp3 file with given path using win32 API"""

    if sys.platform != "win32":
        raise NotImplementedError("Function only available on Windows")

    # pylint: disable-next=import-outside-toplevel
    from ctypes import create_unicode_buffer, windll, wintypes  # type: ignore

    _get_short_path_name_w = windll.kernel32.GetShortPathNameW
    _get_short_path_name_w.argtypes = [
        wintypes.LPCWSTR,
        wintypes.LPWSTR,
        wintypes.DWORD,
    ]
    _get_short_path_name_w.restype = wintypes.DWORD

    def get_short_path_name(long_name: str) -> str:
        """
        Gets the DOS-safe short path name of a given long path.
        http://stackoverflow.com/a/23598461/200291
        """
        output_buf_size = 0
        while True:
            output_buf = create_unicode_buffer(output_buf_size)
            needed = _get_short_path_name_w(long_name, output_buf, output_buf_size)
            if output_buf_size >= needed:
                return output_buf.value
            output_buf_size = needed

    mci_send_string_w = windll.winmm.mciSendStringW

    def mci_send(msg: str) -> None:
        """Send MCI command string"""
        result = mci_send_string_w(msg, 0, 0, 0)
        if result != 0:
            pr_err(f"Error {result} in mciSendString {msg}. Exiting.")
            sys.exit(1)

    mp3_shortname = get_short_path_name(mp3_fname)

    mci_send("Close All")
    mci_send(f'Open "{mp3_shortname}" Type MPEGVideo Alias theMP3')
    mci_send("Play theMP3 Wait")
    mci_send("Close theMP3")
