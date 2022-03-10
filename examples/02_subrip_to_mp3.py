#!/usr/bin/env python3

import asyncio
import shutil
import subprocess
import sys
import tempfile

import edge_tts

if shutil.which("ffmpeg") is None:
    print("ffmpeg is not installed")
    exit(1)


def parse_srt(srt_file):
    with open(srt_file, "r") as f:
        data = f.read().split("\n\n")
    data = [i.strip() for i in data]
    data = [(*i.split("\n")[:2], " ".join(i.split("\n")[2:])) for i in data]
    data = sorted(data, key=lambda x: int(x[0]))
    return data


def ensure_audio_length(in_file, out_file, length):
    duration = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            in_file,
        ]
    ).decode("utf-8")
    duration = float(duration)
    atempo = duration / length
    if atempo < 0.5:
        atempo = 0.5
    elif atempo > 100:
        atempo = 100
    process = subprocess.call(
        [
            "ffmpeg",
            "-y",
            "-i",
            in_file,
            "-filter:a",
            f"atempo={atempo}",
            out_file,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if process != 0:
        raise Exception("ffmpeg failed")


async def _main(srt_data, voice_name, out_file):
    communicate = edge_tts.Communicate()

    max_duration = srt_data[-1][1].replace(",", ".").split("-->")[1]
    max_duration = max_duration.split(":")
    max_duration = (
        float(max_duration[0]) * 3600
        + float(max_duration[1]) * 60
        + float(max_duration[2])
    )
    mother_temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    try:
        subprocess.call(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=channel_layout=mono:sample_rate=48000",
                "-t",
                str(max_duration),
                mother_temp_file.name,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        for i in srt_data:
            duration = i[1].replace(",", ".")
            duration = duration.split("-->")

            start = duration[0].split(":")
            start = int(start[0]) * 3600 + int(start[1]) * 60 + float(start[2])

            end = duration[1].split(":")
            end = int(end[0]) * 3600 + int(end[1]) * 60 + float(end[2])

            duration = end - start
            with tempfile.NamedTemporaryFile(suffix=".mp3") as temporary_file:
                async for j in communicate.run(
                    i[2], codec="audio-24khz-48kbitrate-mono-mp3", voice=voice_name
                ):
                    if j[2] is not None:
                        temporary_file.write(j[2])

                temporary_file2 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                try:
                    ensure_audio_length(
                        temporary_file.name, temporary_file2.name, duration
                    )
                finally:
                    shutil.move(temporary_file2.name, temporary_file.name)

                temporary_file2 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                try:
                    subprocess.call(
                        [
                            "ffmpeg",
                            "-y",
                            "-i",
                            mother_temp_file.name,
                            "-i",
                            temporary_file.name,
                            "-filter_complex",
                            f"aevalsrc=0:d={start}[s1];[s1][1:a]concat=n=2:v=0:a=1[ac1];[0:a][ac1]amix=2[aout]",
                            "-map",
                            "[aout]",
                            temporary_file2.name,
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                finally:
                    shutil.move(temporary_file2.name, mother_temp_file.name)
    finally:
        shutil.move(mother_temp_file.name, out_file)


def main():
    srt_file = sys.argv[1]
    voice_name = sys.argv[2]
    srt_data = parse_srt(srt_file)
    out_file = sys.argv[3]
    asyncio.get_event_loop().run_until_complete(_main(srt_data, voice_name, out_file))


if __name__ == "__main__":
    main()
