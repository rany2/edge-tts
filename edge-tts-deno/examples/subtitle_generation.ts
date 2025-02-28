/**
 * 字幕生成示例
 * 展示不同格式的字幕生成功能
 */
import {
  WebSocketClient,
  SubtitleFormat,
  type TTSChunk,
} from "../mod.ts";

// 准备长文本进行转换
const text = `
这是一个演示字幕生成功能的示例。
我们将生成三种不同格式的字幕：
1. SRT格式 - 最常用的字幕格式
2. WebVTT格式 - 网页视频字幕标准
3. 纯文本格式 - 仅包含文本内容
让我们看看每种格式的效果。
`.trim();

// 创建三个不同格式的客户端实例
const formats = [
  { format: SubtitleFormat.SRT, filename: "output.srt" },
  { format: SubtitleFormat.VTT, filename: "output.vtt" },
  { format: SubtitleFormat.TEXT, filename: "output.txt" },
];

/**
 * 清除当前行
 */
function clearLine() {
  // 将光标移到行首并清除该行
  Deno.stdout.writeSync(new TextEncoder().encode("\r\x1b[K"));
}

/**
 * 显示进度
 */
function showProgress(text: string) {
  clearLine();
  Deno.stdout.writeSync(new TextEncoder().encode(`处理中: ${text}`));
}

async function generateSubtitles() {
  console.log("开始生成字幕...");

  for (const { format, filename } of formats) {
    console.log(`\n生成 ${format} 格式字幕...`);

    const client = new WebSocketClient(
      text,
      "zh-CN-XiaoxiaoNeural",
      "+0%",
      "+0%",
      "+0Hz",
      {
        subtitle: {
          format,
          wordsPerCue: 10,
          minDuration: 1000,
          maxDuration: 5000,
          timeOffset: 0,
        },
      }
    );

    try {
      // 处理音频和字幕
      const audioChunks: Uint8Array[] = [];
      for await (const chunk of client.stream()) {
        if (chunk.type === "audio") {
          audioChunks.push(chunk.data);
        } else if (chunk.type === "WordBoundary") {
          // 显示生成进度
          showProgress(chunk.text);
        }
      }

      // 清除进度显示
      clearLine();

      // 获取字幕内容
      const subtitles = client.getSubtitles();
      await Deno.writeTextFile(filename, subtitles);
      console.log(`字幕已保存至 ${filename}`);

      // 仅为第一个格式保存音频
      if (format === SubtitleFormat.SRT) {
        const audio = new Uint8Array(
          audioChunks.reduce((acc, chunk) => acc + chunk.length, 0)
        );
        let offset = 0;
        for (const chunk of audioChunks) {
          audio.set(chunk, offset);
          offset += chunk.length;
        }
        await Deno.writeFile("output.mp3", audio);
        console.log("音频已保存至 output.mp3");
      }
    } catch (error) {
      console.error(`生成${format}格式字幕时出错:`, error);
    }
  }

  console.log("\n所有字幕生成完成！");
  console.log("生成的文件:");
  console.log("- output.srt (SRT格式字幕)");
  console.log("- output.vtt (WebVTT格式字幕)");
  console.log("- output.txt (纯文本格式)");
  console.log("- output.mp3 (音频文件)");
}

// 运行示例
if (import.meta.main) {
  generateSubtitles().catch(console.error);
}