/**
 * 高级TTS示例
 * 展示使用更多参数的TTS功能
 */
import { WebSocketClient } from "../src/core/websocket_client.ts";

async function main() {
  // 创建TTS客户端，使用更多参数
  const client = new WebSocketClient(
    "这是一个高级的TTS示例，我们可以调整语速和音量。",
    "zh-CN-XiaoxiaoNeural",  // 语音
    "+50%",                  // 语速 (+50% 更快)
    "+20%",                  // 音量 (+20% 更大)
    "+2Hz",                  // 音调 (略高)
  );

  // 接收音频数据和元数据
  const audioChunks: Uint8Array[] = [];
  const subtitles: Array<{
    text: string;
    offset: number;
    duration: number;
  }> = [];

  console.log("开始转换...");

  try {
    for await (const chunk of client.stream()) {
      if (chunk.type === "audio") {
        audioChunks.push(chunk.data);
      } else if (chunk.type === "WordBoundary") {
        console.log(`处理词语: ${chunk.text} (时间偏移: ${chunk.offset}ms, 持续时间: ${chunk.duration}ms)`);
        subtitles.push({
          text: chunk.text,
          offset: chunk.offset,
          duration: chunk.duration,
        });
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

    // 保存音频
    await Deno.writeFile("advanced_output.mp3", finalAudio);
    console.log("音频已保存为 advanced_output.mp3");

    // 保存字幕
    const subtitleContent = subtitles.map(sub => 
      `${sub.text}\t${sub.offset}\t${sub.duration}`
    ).join("\n");
    await Deno.writeTextFile("advanced_output.srt", subtitleContent);
    console.log("字幕已保存为 advanced_output.srt");

  } catch (error) {
    console.error("发生错误:", error);
  }
}

if (import.meta.main) {
  main();
}