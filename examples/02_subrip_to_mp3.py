#!/usr/bin/env python3

import asyncio
import os
import shutil
import subprocess
import sys
import tempfile

import edge_tts

if shutil.which("ffmpeg") is None:
    print("ffmpeg is not installed")
    exit(1)


def parse_srt(srt_file):
    with open(srt_file, "r", encoding="utf-8") as f:
        data = f.read().strip().split("\n\n")
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

        input_files = []
        input_files_start = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            for i in srt_data:
                print(f"Processing {i[0]}...")

                fname = os.path.join(temp_dir, f"{i[0]}.mp3")
                input_files.append(fname)

                duration = i[1].replace(",", ".")
                duration = duration.split("-->")

                start = duration[0].split(":")
                start = int(start[0]) * 3600 + int(start[1]) * 60 + float(start[2])
                input_files_start[fname] = start

                end = duration[1].split(":")
                end = int(end[0]) * 3600 + int(end[1]) * 60 + float(end[2])

                duration = end - start
                with open(fname, "wb") as f:
                    async for j in communicate.run(
                        i[2], codec="audio-24khz-48kbitrate-mono-mp3", voice=voice_name
                    ):
                        if j[2] is not None:
                            f.write(j[2])

                    temporary_file = tempfile.NamedTemporaryFile(
                        suffix=".mp3", delete=False
                    )
                    try:
                        ensure_audio_length(fname, temporary_file.name, duration)
                    finally:
                        shutil.move(temporary_file.name, fname)

            ffmpeg_opts = []
            for i in range(len(input_files)):
                ffmpeg_opts.append("-i")
                ffmpeg_opts.append(input_files[i])

            filter_complex = ""
            for i in range(len(input_files)):
                filter_complex += (
                    f"aevalsrc=0:d={input_files_start[input_files[i]]}[s{i+1}];"
                )
                filter_complex += f"[s{i+1}][{i+1}:a]concat=n=2:v=0:a=1[ac{i+1}];"

            filter_complex += f"[0:a]"
            for i in range(len(input_files)):
                filter_complex += f"[ac{i+1}]"
            filter_complex += f"amix={len(input_files)+1}[aout]"

            ffmpeg_opts.append("-filter_complex")
            ffmpeg_opts.append(filter_complex)
            ffmpeg_opts.append("-map")
            ffmpeg_opts.append("[aout]")

            temporary_file2 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            try:
                print("Concatenating...")
                subprocess.call(
                    ["ffmpeg", "-y", "-i", mother_temp_file.name]
                    + ffmpeg_opts
                    + [temporary_file2.name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            finally:
                shutil.move(temporary_file2.name, mother_temp_file.name)
    finally:
        shutil.move(mother_temp_file.name, out_file)
    print("Done")


def main():
    srt_file = sys.argv[1]
    voice_name = sys.argv[2]
    srt_data = parse_srt(srt_file)
    out_file = sys.argv[3]
    asyncio.get_event_loop().run_until_complete(_main(srt_data, voice_name, out_file))


if __name__ == "__main__":
    main()
