/**
 * @file CLI相关类型定义
 */

import { type AudioFormat, DEFAULT_VOICE } from '../constants.ts';

/**
 * CLI命令行参数接口
 */
export interface CLIArgs {
  /** 直接输入的文本 */
  text?: string;
  
  /** 输入文件路径 */
  file?: string;
  
  /** 语音选择 */
  voice: string;
  
  /** 是否列出可用语音 */
  listVoices: boolean;
  
  /** 语速控制 (默认 +0%) */
  rate: string;
  
  /** 音量控制 (默认 +0%) */
  volume: string;
  
  /** 音调控制 (默认 +0Hz) */
  pitch: string;
  
  /** 每个字幕片段的词数 */
  wordsInCue: number;
  
  /** 音频输出路径 */
  writeMedia?: string;
  
  /** 字幕输出路径 */
  writeSubtitles?: string;
  
  /** 代理服务器 */
  proxy?: string;
}

/**
 * CLI默认配置
 */
export const DEFAULT_CLI_CONFIG: Partial<CLIArgs> = {
  voice: DEFAULT_VOICE,
  rate: "+0%",
  volume: "+0%",
  pitch: "+0Hz",
  wordsInCue: 10,
  listVoices: false,
};

/**
 * CLI错误类型
 */
export type CLIErrorType =
  | "INVALID_ARGS"      // 无效参数
  | "FILE_NOT_FOUND"    // 文件未找到
  | "PERMISSION_DENIED" // 权限不足
  | "IO_ERROR"         // IO错误
  | "TTS_ERROR";       // TTS服务错误

/**
 * CLI错误接口
 */
export interface CLIError {
  type: CLIErrorType;
  message: string;
  details?: unknown;
}

/**
 * 输入源类型
 */
export type InputSource = 
  | { type: "text"; content: string }
  | { type: "file"; path: string }
  | { type: "stdin" };

/**
 * 输出目标类型
 */
export type OutputTarget =
  | { type: "file"; path: string }
  | { type: "stdout" }
  | { type: "stderr" };

/**
 * CLI处理器接口
 */
export interface CLIProcessor {
  parseArgs(args: string[]): Promise<CLIArgs>;
  readInput(source: InputSource): Promise<string>;
  writeOutput(data: Uint8Array | string, target: OutputTarget): Promise<void>;
  handleError(error: CLIError): void;
}