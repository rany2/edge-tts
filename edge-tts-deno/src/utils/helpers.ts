/**
 * 辅助函数
 * 参考原edge_tts/util.py和communicate.py中的工具函数
 */

/**
 * 获取请求ID（UUID不带横线）
 * 参考原communicate.py中的connect_id()
 */
export function generateRequestId(): string {
  return crypto.randomUUID().replace(/-/g, "");
}

/**
 * 查找字节数组中的模式
 * @param data 要搜索的数据
 * @param pattern 要查找的模式
 * @returns 找到的位置，如果未找到返回-1
 */
export function findPattern(data: Uint8Array, pattern: Uint8Array): number {
  for (let i = 0; i <= data.length - pattern.length; i++) {
    let found = true;
    for (let j = 0; j < pattern.length; j++) {
      if (data[i + j] !== pattern[j]) {
        found = false;
        break;
      }
    }
    if (found) return i;
  }
  return -1;
}

/**
 * 将文本按字节长度分割
 * 参考原communicate.py中的split_text_by_byte_length()
 * @param text 要分割的文本
 * @param byteLength 每段最大字节长度
 */
export function* splitTextByByteLength(
  text: string | Uint8Array,
  byteLength: number,
): Generator<Uint8Array, void, unknown> {
  if (typeof text === "string") {
    text = new TextEncoder().encode(text);
  }

  if (byteLength <= 0) {
    throw new Error("byteLength must be greater than 0");
  }

  while (text.length > byteLength) {
    // 在byteLength位置之前找到最后一个空格
    let splitAt = byteLength;
    for (let i = byteLength; i >= 0; i--) {
      if (text[i] === 32) { // 32是空格的ASCII码
        splitAt = i;
        break;
      }
    }

    // 处理&符号
    let ampIndex = -1;
    for (let i = 0; i < splitAt; i++) {
      if (text[i] === 38) { // 38是&的ASCII码
        ampIndex = i;
      }
      if (text[i] === 59) { // 59是;的ASCII码
        ampIndex = -1;
      }
    }

    if (ampIndex !== -1) {
      splitAt = ampIndex;
    }

    // 如果没找到合适的分割点，就在byteLength处分割
    if (splitAt === 0) {
      splitAt = byteLength;
    }

    const chunk = text.slice(0, splitAt);
    if (chunk.length > 0) {
      yield chunk;
    }

    text = text.slice(splitAt);
  }

  if (text.length > 0) {
    yield text;
  }
}

/**
 * 生成当前时间的JavaScript风格日期字符串
 * 参考原communicate.py中的date_to_string()
 */
export function getCurrentDateString(): string {
  const date = new Date();
  return date.toUTCString().replace("GMT", "GMT+0000 (Coordinated Universal Time)");
}

/**
 * 解析头部和数据
 * 参考原communicate.py中的get_headers_and_data()
 */
export function parseHeadersAndData(
  data: Uint8Array,
  headerLength: number,
): [Record<string, string>, Uint8Array] {
  const decoder = new TextDecoder();
  const headerText = decoder.decode(data.slice(0, headerLength));
  const headers: Record<string, string> = {};

  headerText.split("\r\n").forEach((line) => {
    const [key, value] = line.split(":", 2);
    if (key && value) {
      headers[key.trim()] = value.trim();
    }
  });

  return [headers, data.slice(headerLength + 2)];
}

/**
 * 移除不兼容的字符
 * 参考原communicate.py中的remove_incompatible_characters()
 */
export function removeIncompatibleCharacters(input: string | Uint8Array): string {
  if (input instanceof Uint8Array) {
    input = new TextDecoder().decode(input);
  }

  return input.replace(/[--]/g, " ");
}

/**
 * 常用字节序列
 */
export const DELIMITER = new Uint8Array([13, 10, 13, 10]); // \r\n\r\n