import { TTSConfig } from "../types/config.ts";
import { SSML_CONSTANTS } from "../constants.ts";
import { removeIncompatibleCharacters } from "./helpers.ts";

/**
 * SSML生成器类
 * 用于生成符合SSML规范的XML文档
 */
export class SSMLGenerator {
  /**
   * 生成SSML文档
   * 参考原communicate.py中的mkssml()
   * @param config TTS配置
   * @param text 要合成的文本
   */
  static generate(config: TTSConfig, text: string | Uint8Array): string {
    const escapedText = SSMLGenerator.escapeText(text);

    return `<speak version='${SSML_CONSTANTS.VERSION}' xmlns='${SSML_CONSTANTS.XMLNS}' xml:lang='${SSML_CONSTANTS.LANG}'>` +
      `<voice name='${config.voice}'>` +
      `<prosody pitch='${config.pitch}' rate='${config.rate}' volume='${config.volume}'>` +
      `${escapedText}` +
      `</prosody>` +
      `</voice>` +
      `</speak>`;
  }

  /**
   * 转义文本中的特殊字符
   * @param text 原始文本
   */
  private static escapeText(text: string | Uint8Array): string {
    // 首先确保文本是字符串
    const cleanText = removeIncompatibleCharacters(text);

    // XML特殊字符转义
    return cleanText
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&apos;");
  }

  /**
   * 生成SSML请求头
   * 参考原communicate.py中的ssml_headers_plus_data()
   * @param requestId 请求ID
   * @param timestamp 时间戳
   * @param ssml SSML文档
   */
  static generateRequestHeaders(
    requestId: string,
    timestamp: string,
    ssml: string,
  ): string {
    return [
      `X-RequestId:${requestId}`,
      "Content-Type:application/ssml+xml",
      `X-Timestamp:${timestamp}Z`, // Z是必需的，参考原代码注释
      "Path:ssml",
      "",
      ssml,
    ].join("\r\n");
  }

  /**
   * 计算最大消息大小
   * 参考原communicate.py中的calc_max_mesg_size()
   * @param config TTS配置
   */
  static calculateMaxMessageSize(config: TTSConfig): number {
    // WebSocket最大消息大小
    const WEBSOCKET_MAX_SIZE = 2 ** 16;

    // 计算开销
    const overhead = SSMLGenerator.generateRequestHeaders(
      "00000000000000000000000000000000",
      new Date().toISOString(),
      SSMLGenerator.generate(config, ""),
    ).length;

    // 添加50字节的误差余量
    return WEBSOCKET_MAX_SIZE - overhead - 50;
  }

  /**
   * 验证SSML文档
   * 使用基本的结构检查来验证SSML
   * @param ssml SSML文档
   */
  static validate(ssml: string): boolean {
    // 检查基本的XML结构
    const hasXmlDeclaration = ssml.includes("<?xml");
    const hasSpeak = ssml.includes("<speak");
    const hasVoice = ssml.includes("<voice");
    const hasProsody = ssml.includes("<prosody");
    
    // 检查标签闭合
    const hasClosingTags = ssml.includes("</speak>") &&
      ssml.includes("</voice>") &&
      ssml.includes("</prosody>");

    // 检查必需属性
    const hasRequiredAttributes = ssml.includes("version=") &&
      ssml.includes("xmlns=") &&
      ssml.includes("name=") &&
      ssml.includes("pitch=") &&
      ssml.includes("rate=") &&
      ssml.includes("volume=");

    return (!hasXmlDeclaration || ssml.indexOf("<?xml") === 0) &&
      hasSpeak &&
      hasVoice &&
      hasProsody &&
      hasClosingTags &&
      hasRequiredAttributes;
  }
}