#!/bin/sh
{ [ -e "edge-tts.py" ] && [ -e "easy-playback.sh" ]; } || { echo "Script needs to be run on root of the repo" >&2; exit 1; }
[ -z "$1" ] && { echo "You need to specify the install path." >&2; exit 1; }
mkdir -p -- "$1" 2>/dev/null
rm -f -- "$1/edge-tts" "$1/easy-playback"
cp -f -- edge-tts.py "$1/edge-tts"
cp -f -- easy-playback.sh "$1/edge-playback"
chmod +x -- "$1/edge-tts" "$1/edge-playback"
exit 0
