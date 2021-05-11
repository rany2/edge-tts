#!/usr/bin/env bash
## To use this script you need to install
## edge-tts.py to a directory in your $PATH
## as executable and give it the name edge-tts
trap 'kill -- $(jobs -p) 2>/dev/null' EXIT
exec {fd}< <(edge-tts "${@}")
mpg123 -C "/dev/fd/$fd"
