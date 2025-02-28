/**
 * 高级流式TTS示例
 * 展示重连机制和字幕生成功能
 */
import {
  WebSocketClient,
  type TTSChunk,
  SubtitleFormat,
} from "../mod.ts";

// 配置WebSocket客户端
const client = new WebSocketClient(
  "你好，这是一个带有自动重连和字幕生成功能的示例。" +
  "我们将演示如何处理流式数据，并生成不同格式的字幕。",
  "zh-CN-XiaoxiaoNeural",
  "+0%",  // 语速
  "+0%",  // 音量
  "+0Hz", // 音调
  {
    // 重连配置
    reconnect: {
      maxRetries: 3,
      initialDelay: 1000,
      maxDelay: 5000,
      backoffFactor: 2,
    },
    // 字幕配置
    subtitle: {
      format: SubtitleFormat.SRT,
      wordsPerCue: 5,
      minDuration: 1000,
      maxDuration: 5000,
      timeOffset: 0,
    },
    // 连接配置
    connectTimeout: 5000,
    receiveTimeout: 30000,
  }
);

// 收集音频数据
const audioChunks: Uint8Array[] = [];

console.log("开始流式转换...");

// 处理流式数据
try {
  for await (const chunk of client.stream()) {
    if (chunk.type === "audio") {
      // 处理音频数据
      audioChunks.push(chunk.data);
    } else if (chunk.type === "WordBoundary") {
      // 显示实时转录进度
      console.log(`转录进度: ${chunk.text}`);
    }
  }

  // 合并音频数据
  const totalLength = audioChunks.reduce((acc, chunk) => acc + chunk.length, 0);
  const mergedAudio = new Uint8Array(totalLength);
  let offset = 0;
  for (const chunk of audioChunks) {
    mergedAudio.set(chunk, offset);
    offset += chunk.length;
  }

  // 保存音频文件
  await Deno.writeFile("output.mp3", mergedAudio);
  console.log("音频文件已保存为 output.mp3");

  // 获取并保存字幕
  const subtitles = client.getSubtitles();
  await Deno.writeTextFile("output.srt", subtitles);
  console.log("字幕文件已保存为 output.srt");

} catch (error) {
  if (error instanceof Error) {
    console.error("转换过程中出现错误:", error.message);
  } else {
    console.error("发生未知错误");
  }
} finally {
  console.log("转换完成");
}