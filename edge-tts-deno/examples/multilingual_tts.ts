/**
 * 多语言TTS示例
 * 展示如何使用不同的语言和声音
 */
import { WebSocketClient } from "../src/core/websocket_client.ts";

// 定义不同的语言和对应的语音
const voices = [
  {
    text: "你好，这是中文示例。",
    voice: "zh-CN-XiaoxiaoNeural",
    lang: "中文"
  },
  {
    text: "Hello, this is an English example.",
    voice: "en-US-JennyNeural",
    lang: "英语"
  },
  {
    text: "こんにちは、これは日本語のサンプルです。",
    voice: "ja-JP-NanamiNeural",
    lang: "日语"
  },
  {
    text: "안녕하세요, 한국어 예제입니다.",
    voice: "ko-KR-SunHiNeural",
    lang: "韩语"
  }
];

async function synthesizeVoice(text: string, voice: string, lang: string): Promise<void> {
  console.log(`\n正在转换${lang}...`);
  
  const client = new WebSocketClient(
    text,
    voice,
    "+0%",  // 正常语速
    "+0%",  // 正常音量
    "+0Hz"  // 正常音调
  );

  const audioChunks: Uint8Array[] = [];

  try {
    for await (const chunk of client.stream()) {
      if (chunk.type === "audio") {
        audioChunks.push(chunk.data);
      } else if (chunk.type === "WordBoundary") {
        console.log(`处理文本: ${chunk.text}`);
      }
    }

    // 合并音频数据
    const finalAudio = new Uint8Array(
      audioChunks.reduce((acc, chunk) => acc + chunk.length, 0)
    );
    let offset = 0;
    for (const chunk of audioChunks) {
      finalAudio.set(chunk, offset);
      offset += chunk.length;
    }

    // 保存音频文件
    const filename = `multilingual_${lang}.mp3`;
    await Deno.writeFile(filename, finalAudio);
    console.log(`${lang}音频已保存为 ${filename}`);

  } catch (error) {
    console.error(`${lang}转换发生错误:`, error);
  }
}

async function main() {
  console.log("开始多语言转换示例...");
  
  // 按顺序处理每种语言
  for (const { text, voice, lang } of voices) {
    await synthesizeVoice(text, voice, lang);
  }

  console.log("\n所有语言转换完成！");
}

if (import.meta.main) {
  main();
}