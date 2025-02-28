/**
 * 字幕时间戳
 */
export interface SubtitleTimestamp {
  /** 开始时间（毫秒） */
  start: number;
  /** 持续时间（毫秒） */
  duration: number;
  /** 结束时间（毫秒） */
  end: number;
}

/**
 * 字幕片段
 */
export interface SubtitleCue {
  /** 序号 */
  index: number;
  /** 时间戳 */
  timestamp: SubtitleTimestamp;
  /** 文本内容 */
  text: string;
}

/**
 * 字幕格式
 */
export enum SubtitleFormat {
  /** SRT格式 */
  SRT = "srt",
  /** WebVTT格式 */
  VTT = "vtt",
  /** 纯文本格式 */
  TEXT = "txt",
}

/**
 * 字幕生成配置
 */
export interface SubtitleConfig {
  /** 字幕格式 */
  format: SubtitleFormat;
  /** 每个字幕片段的最大词数 */
  wordsPerCue: number;
  /** 最小字幕持续时间（毫秒） */
  minDuration: number;
  /** 最大字幕持续时间（毫秒） */
  maxDuration: number;
  /** 字幕时间偏移（毫秒） */
  timeOffset: number;
}

/**
 * 字幕生成器接口
 */
export interface SubtitleGenerator {
  /** 添加字幕片段 */
  addCue(text: string, timestamp: SubtitleTimestamp): void;
  
  /** 获取所有字幕片段 */
  getCues(): SubtitleCue[];
  
  /** 生成字幕内容 */
  generate(): string;
  
  /** 重置生成器状态 */
  reset(): void;
}

/**
 * 默认字幕配置
 */
export const DEFAULT_SUBTITLE_CONFIG: SubtitleConfig = {
  format: SubtitleFormat.SRT,
  wordsPerCue: 10,
  minDuration: 1000,  // 1秒
  maxDuration: 5000,  // 5秒
  timeOffset: 0,
};