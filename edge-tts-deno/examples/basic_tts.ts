/**
 * 基础TTS示例
 * 展示最简单的文本转语音用法
 */
import { WebSocketClient } from "../src/core/websocket_client.ts";

async function main() {
  // 创建TTS客户端
  const client = new WebSocketClient(
    "你好，这是一个基础的TTS示例。",
    "zh-CN-XiaoxiaoNeural"  // 使用中文女声
  );

  // 接收音频数据并保存
  const audioChunks: Uint8Array[] = [];
  console.log("开始转换...");

  try {
    for await (const chunk of client.stream()) {
      if (chunk.type === "audio") {
        audioChunks.push(chunk.data);
      } else if (chunk.type === "WordBoundary") {
        console.log(`处理词语: ${chunk.text}`);
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

    // 保存为MP3文件
    await Deno.writeFile("basic_output.mp3", finalAudio);
    console.log("转换完成！音频已保存为 basic_output.mp3");
  } catch (error) {
    console.error("发生错误:", error);
  }
}

if (import.meta.main) {
  main();
}