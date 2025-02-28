/**
 * @file CLI处理器实现
 */

import { parse } from "https://deno.land/std@0.218.2/flags/mod.ts";
import { exists } from "https://deno.land/std@0.218.2/fs/exists.ts";
import { join } from "https://deno.land/std@0.218.2/path/mod.ts";
import { 
  type CLIArgs, 
  type CLIProcessor,
  type InputSource,
  type OutputTarget,
  type CLIError,
  DEFAULT_CLI_CONFIG
} from "../types/cli.ts";
import { DEFAULT_VOICE } from "../constants.ts";

interface ParseResult {
  readonly _: string[];
  readonly text?: string;
  readonly file?: string;
  readonly voice?: string;
  readonly ["list-voices"]?: boolean;
  readonly rate?: string;
  readonly volume?: string;
  readonly pitch?: string;
  readonly ["words-in-cue"]?: number;
  readonly ["write-media"]?: string;
  readonly ["write-subtitles"]?: string;
  readonly proxy?: string;
  readonly [key: string]: unknown;
}

/**
 * CLI处理器实现类
 */
export class EdgeTTSCliProcessor implements CLIProcessor {
  /**
   * 解析命令行参数
   */
  async parseArgs(args: string[]): Promise<CLIArgs> {
    const parsed = parse(args, {
      string: ["text", "file", "voice", "rate", "volume", "pitch", "write-media", "write-subtitles", "proxy"],
      boolean: ["list-voices"],
      default: {
        ...DEFAULT_CLI_CONFIG,
        listVoices: false,
        wordsInCue: 10
      },
      alias: {
        t: "text",
        f: "file",
        v: "voice",
        l: "list-voices",
      },
    }) as ParseResult;

    // 验证必需参数
    if (!parsed["list-voices"] && !parsed.text && !parsed.file) {
      throw this.createError(
        "INVALID_ARGS",
        "Must provide either --text, --file or --list-voices"
      );
    }

    // 验证文件路径
    if (parsed.file && parsed.file !== "-") {
      if (!await exists(parsed.file)) {
        throw this.createError(
          "FILE_NOT_FOUND",
          `Input file not found: ${parsed.file}`
        );
      }
    }

    return {
      text: parsed.text,
      file: parsed.file,
      voice: parsed.voice || DEFAULT_VOICE,
      listVoices: Boolean(parsed["list-voices"]),
      rate: parsed.rate || "+0%",
      volume: parsed.volume || "+0%",
      pitch: parsed.pitch || "+0Hz",
      wordsInCue: Number(parsed["words-in-cue"]) || 10,
      writeMedia: parsed["write-media"],
      writeSubtitles: parsed["write-subtitles"],
      proxy: parsed.proxy,
    };
  }

  /**
   * 读取输入内容
   */
  async readInput(source: InputSource): Promise<string> {
    try {
      switch (source.type) {
        case "text":
          return source.content;
        case "file":
          return await Deno.readTextFile(source.path);
        case "stdin": {
          const buffer = new Uint8Array(1024);
          let result = "";
          const decoder = new TextDecoder();
          
          while (true) {
            const readResult = await Deno.stdin.read(buffer);
            if (readResult === null) break;
            result += decoder.decode(buffer.subarray(0, readResult));
          }
          return result;
        }
        default:
          throw this.createError("IO_ERROR", "Invalid input source");
      }
    } catch (error) {
      if (error instanceof Error) {
        throw this.createError("IO_ERROR", `Failed to read input: ${error.message}`);
      }
      throw this.createError("IO_ERROR", "Failed to read input: Unknown error");
    }
  }

  /**
   * 写入输出内容
   */
  async writeOutput(
    data: Uint8Array | string,
    target: OutputTarget
  ): Promise<void> {
    try {
      switch (target.type) {
        case "file":
          if (data instanceof Uint8Array) {
            await Deno.writeFile(target.path, data);
          } else {
            await Deno.writeTextFile(target.path, data);
          }
          break;
        case "stdout":
          if (data instanceof Uint8Array) {
            await Deno.stdout.write(data);
          } else {
            await Deno.stdout.write(new TextEncoder().encode(data));
          }
          break;
        case "stderr":
          await Deno.stderr.write(new TextEncoder().encode(data.toString()));
          break;
        default:
          throw this.createError("IO_ERROR", "Invalid output target");
      }
    } catch (error) {
      if (error instanceof Error) {
        throw this.createError("IO_ERROR", `Failed to write output: ${error.message}`);
      }
      throw this.createError("IO_ERROR", "Failed to write output: Unknown error");
    }
  }

  /**
   * 处理错误
   */
  handleError(error: CLIError): void {
    console.error(`Error [${error.type}]: ${error.message}`);
    if (error.details) {
      console.error("Details:", error.details);
    }
    Deno.exit(1);
  }

  /**
   * 创建标准化错误对象
   */
  createError(type: CLIError["type"], message: string, details?: unknown): CLIError {
    return { type, message, details };
  }

  /**
   * 检查是否为TTY终端
   */
  isTTY(): boolean {
    return Deno.stdin.isTerminal() && Deno.stdout.isTerminal();
  }

  /**
   * 显示交互式提示
   */
  async showPrompt(message: string): Promise<boolean> {
    await this.writeOutput(message, { type: "stderr" });
    if (this.isTTY()) {
      const input = await this.readInput({ type: "stdin" });
      return input.trim() === "";
    }
    return true;
  }

  /**
   * 检查文件是否存在
   */
  async checkFileExists(path: string): Promise<boolean> {
    return await exists(path);
  }

  /**
   * 格式化时间戳
   */
  formatTimeStamp(ms: number): string {
    const s = Math.floor(ms / 1000);
    const m = Math.floor(s / 60);
    const h = Math.floor(m / 60);
    return `${h.toString().padStart(2, "0")}:${(m % 60).toString().padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")},${(ms % 1000).toString().padStart(3, "0")}`;
  }
}