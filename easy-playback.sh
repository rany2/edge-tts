#!/usr/bin/env bash

## To use this script you need to install edge-tts.py to a directory in your $PATH as executable
## and give it the name edge-tts. Alternatively you could just run the install script.
export LC_ALL=C

## We use a temporary file now instead of file descriptor because mpg123 doesn't
## let me seek back a file descriptor, only seek forward.
ttsmpeg=$(mktemp)

## Cleanup function to kill all processes and remove tmp file
quitfunc() {
	# shellcheck disable=SC2046
	kill -- $(jobs -p)
	rm -f -- "${ttsmpeg:?}"
}
trap 'quitfunc > /dev/null 2>&1' EXIT

## If stdin is $1 we shift 1 and save the stdin data to an stdin variable.
## We also add --file=/dev/stdin to params that edge-tts will get.
if [ "$1" == "stdin" ]
then
	stdin=$(cat)
	shift 1
	set -- "$@" '--file=/dev/stdin'
else
	stdin=""
fi
edge-tts "${@}" >"$ttsmpeg" <<<"$stdin" &
edgePID=$!

## Wait until temporary file has some data so mpg123 doesn't exit immediately
## because it thinks file is empty and won't have any data.
##
## kill -0 checks if PID is still running.
while kill -0 "$edgePID" 2>/dev/null && [ "$(wc -c < "$ttsmpeg")" == 0 ]
do
	sleep 0.1
done
mpg123 --quiet --control "$ttsmpeg"
