import { WebSocketClient } from "../src/core/websocket_client.ts";

/**
 * 简单的TTS示例
 * 将文本转换为语音并保存为MP3文件
 */
async function main() {
  const text = "您好，这是一个测试。Hello, this is a test.";
  const outputFile = "output.mp3";

  console.log("创建TTS客户端...");
  const client = new WebSocketClient(
    text,
    "zh-CN-XiaoxiaoNeural", // 使用中文语音
    "+0%", // 默认语速
    "+0%", // 默认音量
    "+0Hz", // 默认音调
  );

  console.log("开始语音合成...");
  const audioChunks: Uint8Array[] = [];
  let wordCount = 0;

  try {
    for await (const chunk of client.stream()) {
      if (chunk.type === "audio") {
        audioChunks.push(chunk.data);
      } else if (chunk.type === "WordBoundary") {
        wordCount++;
        console.log(`处理单词: ${chunk.text}`);
      }
    }

    // 合并所有音频块并保存
    const finalAudio = new Uint8Array(
      audioChunks.reduce((acc, chunk) => acc + chunk.length, 0),
    );
    let offset = 0;
    for (const chunk of audioChunks) {
      finalAudio.set(chunk, offset);
      offset += chunk.length;
    }

    await Deno.writeFile(outputFile, finalAudio);
    console.log(`完成！已处理 ${wordCount} 个单词，音频已保存到 ${outputFile}`);
  } catch (error) {
    console.error("发生错误:", error);
  }
}

if (import.meta.main) {
  main();
}