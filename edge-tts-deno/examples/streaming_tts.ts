/**
 * 流式TTS示例
 * 展示如何实时处理音频流和字幕
 */
import { WebSocketClient } from "../src/core/websocket_client.ts";

async function main() {
  // 创建TTS客户端
  const client = new WebSocketClient(
    "这是一个流式处理的例子，我们会实时获取音频和字幕数据。每个词语都会立即显示出来。",
    "zh-CN-XiaoxiaoNeural",  // 语音
    "+0%",                   // 正常语速
    "+0%",                   // 正常音量
    "+0Hz"                   // 正常音调
  );

  // 创建输出文件流
  const audioFile = await Deno.open("streaming_output.mp3", {
    write: true,
    create: true,
  });

  console.log("开始流式转换...");
  let totalBytes = 0;
  let wordCount = 0;

  try {
    // 实时处理流数据
    for await (const chunk of client.stream()) {
      if (chunk.type === "audio") {
        // 立即写入音频数据
        await audioFile.write(chunk.data);
        totalBytes += chunk.data.length;
        console.log(`已处理 ${totalBytes} 字节的音频数据`);
      } else if (chunk.type === "WordBoundary") {
        wordCount++;
        // 实时显示处理进度
        console.log(`第 ${wordCount} 个词: ${chunk.text}`);
        console.log(`时间戳: ${chunk.offset}ms, 持续时间: ${chunk.duration}ms`);
      }
    }

    console.log("\n转换完成!");
    console.log(`总计处理了 ${totalBytes} 字节的音频数据`);
    console.log(`共处理了 ${wordCount} 个词`);
    console.log(`音频文件已保存为 streaming_output.mp3`);

  } catch (error) {
    console.error("发生错误:", error);
  } finally {
    // 关闭文件
    audioFile.close();
  }
}

if (import.meta.main) {
  main();
}