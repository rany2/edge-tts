/**
 * Edge TTS Deno - Microsoft Edge TTS服务的Deno实现
 */

// 核心功能导出
export { WebSocketClient } from "@src/core/websocket_client.ts";

// 类型定义导出
export type {
  TTSConfig,
  TTSChunk,
  WordBoundary,
  AudioChunk,
} from "@src/types/config.ts";

// CLI相关导出
export {
  EdgeTTSCliProcessor,
  main as cliMain,
} from "@src/cli/mod.ts";
export type {
  CLIArgs,
  CLIProcessor,
  InputSource,
  OutputTarget,
  CLIError,
} from "@src/types/cli.ts";

// 字幕相关导出
export { SubtitleFormat } from "@src/types/subtitle.ts";
export type {
  SubtitleConfig,
  SubtitleCue,
  SubtitleTimestamp,
  SubtitleGenerator,
} from "@src/types/subtitle.ts";

// 常量导出
export {
  DEFAULT_VOICE,
  AUDIO_FORMATS,
  type AudioFormat,
} from "@src/constants.ts";

// 错误类型导出
export {
  TTSError,
  WebSocketError,
  NoAudioReceived,
  UnexpectedResponse,
  UnknownResponse,
  ConfigError,
  DRMError,
} from "@src/errors/tts_error.ts";

// 工具函数导出
export {
  SSMLGenerator,
} from "@src/utils/ssml.ts";

// 版本信息
export const VERSION = "0.1.0";

// CLI运行入口
if (import.meta.main) {
  const { main } = await import("@src/cli/main.ts");
  await main().catch((error: unknown) => {
    console.error("Fatal error:", error);
    Deno.exit(1);
  });
}