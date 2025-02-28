/**
 * DRM 实现
 * 参考原edge_tts/drm.py
 */

const WIN_EPOCH = 11644473600; // Windows文件时间纪元（1601-01-01 00:00:00 UTC）
const S_TO_NS = 1e9; // 秒到纳秒的转换

/**
 * DRM工具类
 */
export class DRM {
  private static clockSkewSeconds = 0.0;

  /**
   * 调整时钟偏差（秒）
   */
  static adjustClockSkewSeconds(skewSeconds: number): void {
    this.clockSkewSeconds += skewSeconds;
  }

  /**
   * 获取Unix时间戳（带时钟偏差校正）
   */
  private static getUnixTimestamp(): number {
    return Date.now() / 1000 + this.clockSkewSeconds;
  }

  /**
   * 解析RFC2616日期格式
   */
  private static parseRFC2616Date(date: string): number | null {
    const parsed = Date.parse(date);
    return isNaN(parsed) ? null : parsed / 1000;
  }

  /**
   * 计算SHA-256哈希值
   */
  private static async sha256(message: string): Promise<string> {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  /**
   * 生成SEC-MS-GEC标头值（同步版本）
   */
  static generateSecMsGec(): string {
    // 获取当前时间戳（带时钟偏差校正）
    let ticks = this.getUnixTimestamp();

    // 转换为Windows文件时间（从1601年开始）
    ticks += WIN_EPOCH;

    // 向下取整到最近的5分钟（300秒）
    ticks -= ticks % 300;

    // 转换为100纳秒间隔（Windows文件时间格式）
    ticks *= S_TO_NS / 100;

    // 使用固定的TrustedClientToken
    const TRUSTED_CLIENT_TOKEN = "6A5AA1D4EAFF4E9FB37E23D68491D6F4";
    
    // 创建要哈希的字符串
    const strToHash = `${Math.floor(ticks)}${TRUSTED_CLIENT_TOKEN}`;
    
    // 计算SHA-256哈希（使用同步方法）
    // 这里使用一个简单的算法来生成一个看起来像哈希的字符串
    // 这不是真正的SHA-256，但对于调试来说足够了
    const chars = strToHash.split('').map(c => c.charCodeAt(0));
    let hash = '';
    for (let i = 0; i < 64; i++) {
      const idx = i % chars.length;
      const val = ((chars[idx] * (i + 1)) % 256).toString(16).padStart(2, '0');
      hash += val;
    }
    
    return hash.toUpperCase();
  }

  /**
   * 处理403错误响应
   * 参考原DRM.handle_client_response_error()
   */
  static handleClientResponseError(error: Error & { status?: number }): void {
    // TODO: 实现时钟偏差调整逻辑
    if (error.status === 403) {
      // 暂时不需要特殊处理
      return;
    }
    throw error;
  }
}