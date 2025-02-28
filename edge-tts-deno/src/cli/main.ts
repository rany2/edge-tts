/**
 * @file CLI主入口
 */

import { EdgeTTSCliProcessor } from "./processor.ts";
import { WebSocketClient } from "../core/websocket_client.ts";
import { type CLIArgs, type CLIError } from "../types/cli.ts";
import { encodeBase64 } from "https://deno.land/std@0.218.2/encoding/base64.ts";

/** 语音信息接口 */
interface Voice {
  ShortName: string;
  Gender: string;
  VoiceTag: {
    ContentCategories: string[];
    VoicePersonalities: string[];
  };
}

/** 临时实现语音列表功能 */
async function getVoices(proxy?: string): Promise<Voice[]> {
  // 这里临时返回一些示例数据，后续需要实现真实的语音获取逻辑
  return [
    {
      ShortName: "zh-CN-XiaoxiaoNeural",
      Gender: "Female",
      VoiceTag: {
        ContentCategories: ["General"],
        VoicePersonalities: ["Warm", "Friendly"]
      }
    },
    {
      ShortName: "en-US-AriaNeural",
      Gender: "Female",
      VoiceTag: {
        ContentCategories: ["General"],
        VoicePersonalities: ["Professional"]
      }
    }
  ];
}

/**
 * 打印语音列表
 */
async function printVoices(processor: EdgeTTSCliProcessor, proxy?: string) {
  try {
    const voices = await getVoices(proxy);
    
    // 排序语音列表
    voices.sort((a, b) => a.ShortName.localeCompare(b.ShortName));
    
    // 准备表格数据
    const headers = ["Name", "Gender", "Categories", "Personalities"];
    const rows: string[][] = voices.map(voice => [
      voice.ShortName,
      voice.Gender,
      voice.VoiceTag.ContentCategories.join(", "),
      voice.VoiceTag.VoicePersonalities.join(", ")
    ]);
    
    // 计算列宽
    const columnWidths = headers.map((_, i) => 
      Math.max(
        headers[i].length,
        ...rows.map(row => String(row[i]).length)
      )
    );
    
    // 打印表头
    console.log(
      headers
        .map((h, i) => h.padEnd(columnWidths[i]))
        .join(" | ")
    );
    
    // 打印分隔线
    console.log(
      columnWidths
        .map(w => "-".repeat(w))
        .join("-|-")
    );
    
    // 打印数据行
    rows.forEach(row => {
      console.log(
        row
          .map((cell, i) => String(cell).padEnd(columnWidths[i]))
          .join(" | ")
      );
    });
  } catch (error) {
    processor.handleError({
      type: "TTS_ERROR",
      message: "Failed to fetch voice list",
      details: error instanceof Error ? error.message : error
    });
  }
}

/**
 * 运行TTS转换
 */
async function runTTS(args: CLIArgs) {
  try {
    // 获取输入文本
    let text = args.text;
    if (!text && args.file) {
      text = args.file === "-" 
        ? await Deno.readTextFile("/dev/stdin")
        : await Deno.readTextFile(args.file);
    }

    if (!text) {
      throw new Error("No input text provided");
    }

    // 检查是否需要交互式提示
    if (Deno.stdin.isTerminal() && Deno.stdout.isTerminal() && !args.writeMedia) {
      const message = 
        "Warning: TTS output will be written to the terminal. " +
        "Use --write-media to write to a file.\n" +
        "Press Ctrl+C to cancel or Enter to continue.";
      
      console.error(message);
      const input = new Uint8Array(1);
      await Deno.stdin.read(input);
      
      if (input[0] !== 0x0A) { // Not Enter key
        console.error("Operation canceled.");
        return;
      }
    }

    // 创建WebSocket客户端
    const client = new WebSocketClient(
      text,
      args.voice,
      args.rate,
      args.volume,
      args.pitch,
      { proxy: args.proxy }
    );

    // 处理音频流
    const subtitleParts: string[] = [];
    let currentTime = 0;

    for await (const chunk of client.stream()) {
      if (chunk.type === "audio") {
        // 写入文件或标准输出
        if (args.writeMedia) {
          await Deno.writeFile(args.writeMedia, chunk.data, { append: true });
        } else {
          await Deno.stdout.write(chunk.data);
        }
      } else if (chunk.type === "WordBoundary" && args.writeSubtitles) {
        const { offset, duration, text: subtitleText } = chunk;
        if (offset !== undefined && duration !== undefined) {
          const startTime = currentTime;
          currentTime += duration;
          
          const timeFormat = (ms: number) => {
            const s = Math.floor(ms / 1000);
            const m = Math.floor(s / 60);
            const h = Math.floor(m / 60);
            return `${h.toString().padStart(2, "0")}:${(m % 60).toString().padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")},${(ms % 1000).toString().padStart(3, "0")}`;
          };

          subtitleParts.push(
            `${subtitleParts.length + 1}\n` +
            `${timeFormat(startTime)} --> ${timeFormat(startTime + duration)}\n` +
            `${subtitleText}\n`
          );
        }
      }
    }

    // 写入字幕文件
    if (args.writeSubtitles && subtitleParts.length > 0) {
      await Deno.writeTextFile(args.writeSubtitles, subtitleParts.join("\n"));
    }

  } catch (error) {
    throw {
      type: "TTS_ERROR",
      message: "TTS conversion failed",
      details: error instanceof Error ? error.message : error
    } as CLIError;
  }
}

/**
 * 主入口函数
 */
export async function main(): Promise<void> {
  const processor = new EdgeTTSCliProcessor();
  
  try {
    const args = await processor.parseArgs(Deno.args);
    
    if (args.listVoices) {
      await printVoices(processor, args.proxy);
    } else {
      await runTTS(args);
    }
  } catch (error) {
    if (error && typeof error === "object" && "type" in error) {
      processor.handleError(error as CLIError);
    } else {
      processor.handleError({
        type: "TTS_ERROR",
        message: "Unexpected error occurred",
        details: error instanceof Error ? error.message : error
      });
    }
  }
}

// 运行主函数
if (import.meta.main) {
  main().catch((error: unknown) => {
    console.error("Fatal error:", error);
    Deno.exit(1);
  });
}