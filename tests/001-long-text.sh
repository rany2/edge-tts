#!/usr/bin/env bash

# test if prompt file exists
if ! [[ -f "tests/001-long-text.txt" ]]
then
    echo "File not found!"
    exit 1
fi

# spawn
for i in {a..z}
do
    edge-tts -f tests/001-long-text.txt --write-media "tests/001-long-text_${i}.mp3" --write-subtitles "tests/001-long-text_${i}.srt" &
done
wait

# set return code to 0
ret=0

# compare files to make sure all are the same
for i in {b..z}
do
    cmp tests/001-long-text_a.mp3 "tests/001-long-text_${i}.mp3" || ret=1
    cmp tests/001-long-text_a.srt "tests/001-long-text_${i}.srt" || ret=1
done

# clean up
rm tests/001-long-text_*.mp3 tests/001-long-text_*.srt

# exit with return code
exit "${ret}"
