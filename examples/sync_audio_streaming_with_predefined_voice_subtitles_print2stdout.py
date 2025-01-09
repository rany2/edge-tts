#!/usr/bin/env python3

"""Sync variant of the async .stream() method to
get audio chunks and feed them to SubMaker to
generate subtitles"""
import sys

import edge_tts

TEXT = """君不见，黄河之水天上来，奔流到海不复回。
君不见，高堂明镜悲白发，朝如青丝暮成雪。
人生得意须尽欢，莫使金樽空对月。
天生我材必有用，千金散尽还复来。
烹羊宰牛且为乐，会须一饮三百杯。
岑夫子，丹丘生，将进酒，杯莫停。
与君歌一曲，请君为我倾耳听。
钟鼓馔玉不足贵，但愿长醉不复醒。
古来圣贤皆寂寞，惟有饮者留其名。
陈王昔时宴平乐，斗酒十千恣欢谑。
主人何为言少钱，径须沽取对君酌。
五花马，千金裘，呼儿将出换美酒，与尔同销万古愁。"""
VOICE = "zh-CN-YunjianNeural"


def main() -> None:
    """Main function"""
    communicate = edge_tts.Communicate(TEXT, VOICE, boundary="SentenceBoundary")
    submaker = edge_tts.SubMaker()
    stdout = sys.stdout
    audio_bytes = []
    for chunk in communicate.stream_sync():
        if chunk["type"] == "audio":
            audio_bytes.append(chunk["data"])
        elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
            submaker.feed(chunk)

    stdout.write(f"audio file length: {len(audio_bytes)}")
    stdout.write(submaker.get_srt())

if __name__ == "__main__":
    main()
