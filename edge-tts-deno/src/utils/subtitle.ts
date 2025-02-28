import {
  type SubtitleCue,
  type SubtitleTimestamp,
  type SubtitleConfig,
  type SubtitleGenerator,
  SubtitleFormat,
  DEFAULT_SUBTITLE_CONFIG,
} from "../types/subtitle.ts";

/**
 * 字幕生成器工厂
 */
export class SubtitleGeneratorFactory {
  static create(config: Partial<SubtitleConfig> = {}): SubtitleGenerator {
    const format = config.format || DEFAULT_SUBTITLE_CONFIG.format;
    switch (format) {
      case SubtitleFormat.SRT:
        return new SRTGenerator(config);
      case SubtitleFormat.VTT:
        return new VTTGenerator(config);
      case SubtitleFormat.TEXT:
        return new TextGenerator(config);
      default:
        throw new Error(`Unsupported subtitle format: ${format}`);
    }
  }
}

/**
 * 基础字幕生成器
 */
abstract class BaseSubtitleGenerator implements SubtitleGenerator {
  protected cues: SubtitleCue[] = [];
  protected config: Required<SubtitleConfig>;
  protected currentIndex = 1;

  constructor(config: Partial<SubtitleConfig> = {}) {
    this.config = {
      ...DEFAULT_SUBTITLE_CONFIG,
      ...config,
    };
  }

  /**
   * 格式化时间戳
   */
  protected abstract formatTimestamp(timestamp: SubtitleTimestamp): string;

  /**
   * 格式化字幕片段
   */
  protected abstract formatCue(cue: SubtitleCue): string;

  /**
   * 添加字幕片段
   */
  addCue(text: string, timestamp: SubtitleTimestamp): void {
    // 验证持续时间
    const duration = Math.min(
      Math.max(timestamp.duration, this.config.minDuration),
      this.config.maxDuration
    );

    // 应用时间偏移
    const adjustedTimestamp: SubtitleTimestamp = {
      start: timestamp.start + this.config.timeOffset,
      duration,
      end: timestamp.start + duration + this.config.timeOffset,
    };

    // 创建字幕片段
    this.cues.push({
      index: this.currentIndex++,
      timestamp: adjustedTimestamp,
      text,
    });
  }

  /**
   * 获取所有字幕片段
   */
  getCues(): SubtitleCue[] {
    return [...this.cues];
  }

  /**
   * 生成字幕内容
   */
  generate(): string {
    return this.cues
      .sort((a, b) => a.timestamp.start - b.timestamp.start)
      .map(cue => this.formatCue(cue))
      .join("\n\n");
  }

  /**
   * 重置生成器状态
   */
  reset(): void {
    this.cues = [];
    this.currentIndex = 1;
  }
}

/**
 * SRT格式字幕生成器
 */
class SRTGenerator extends BaseSubtitleGenerator {
  protected override formatTimestamp(timestamp: SubtitleTimestamp): string {
    const format = (ms: number) => {
      const totalSeconds = Math.floor(ms / 1000);
      const hours = Math.floor(totalSeconds / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);
      const seconds = totalSeconds % 60;
      const milliseconds = ms % 1000;

      return `${hours.toString().padStart(2, "0")}:${
        minutes.toString().padStart(2, "0")}:${
        seconds.toString().padStart(2, "0")},${
        milliseconds.toString().padStart(3, "0")}`;
    };

    return `${format(timestamp.start)} --> ${format(timestamp.end)}`;
  }

  protected override formatCue(cue: SubtitleCue): string {
    return `${cue.index}\n${this.formatTimestamp(cue.timestamp)}\n${cue.text}`;
  }
}

/**
 * WebVTT格式字幕生成器
 */
class VTTGenerator extends BaseSubtitleGenerator {
  protected override formatTimestamp(timestamp: SubtitleTimestamp): string {
    const format = (ms: number) => {
      const totalSeconds = Math.floor(ms / 1000);
      const hours = Math.floor(totalSeconds / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);
      const seconds = totalSeconds % 60;
      const milliseconds = ms % 1000;

      return `${hours.toString().padStart(2, "0")}:${
        minutes.toString().padStart(2, "0")}:${
        seconds.toString().padStart(2, "0")}.${
        milliseconds.toString().padStart(3, "0")}`;
    };

    return `${format(timestamp.start)} --> ${format(timestamp.end)}`;
  }

  protected override formatCue(cue: SubtitleCue): string {
    return `${this.formatTimestamp(cue.timestamp)}\n${cue.text}`;
  }

  override generate(): string {
    return `WEBVTT\n\n${super.generate()}`;
  }
}

/**
 * 纯文本格式字幕生成器
 */
class TextGenerator extends BaseSubtitleGenerator {
  protected override formatTimestamp(_timestamp: SubtitleTimestamp): string {
    return "";
  }

  protected override formatCue(cue: SubtitleCue): string {
    return cue.text;
  }

  override generate(): string {
    return this.cues
      .sort((a, b) => a.timestamp.start - b.timestamp.start)
      .map(cue => cue.text)
      .join("\n");
  }
}

export {
  type SubtitleConfig,
  type SubtitleCue,
  type SubtitleGenerator,
  type SubtitleTimestamp,
  SubtitleFormat,
};