/**
 * TTS错误类
 * 参考原edge_tts/exceptions.py
 */

/** 基础TTS错误 */
export class TTSError extends Error {
  constructor(
    message: string,
    public code: string = "TTS_ERROR",
    public status: number = 500,
  ) {
    super(message);
    this.name = "TTSError";
  }
}

/** WebSocket错误 */
export class WebSocketError extends TTSError {
  constructor(message: string) {
    super(message, "WEBSOCKET_ERROR", 500);
    this.name = "WebSocketError";
  }
}

/** 未收到音频错误 */
export class NoAudioReceived extends TTSError {
  constructor() {
    super(
      "No audio was received. Please verify that your parameters are correct.",
      "NO_AUDIO_RECEIVED",
      400,
    );
    this.name = "NoAudioReceived";
  }
}

/** 意外响应错误 */
export class UnexpectedResponse extends TTSError {
  constructor(message: string) {
    super(message, "UNEXPECTED_RESPONSE", 500);
    this.name = "UnexpectedResponse";
  }
}

/** 未知响应错误 */
export class UnknownResponse extends TTSError {
  constructor(message: string) {
    super(message, "UNKNOWN_RESPONSE", 500);
    this.name = "UnknownResponse";
  }
}

/** 配置错误 */
export class ConfigError extends TTSError {
  constructor(message: string) {
    super(message, "CONFIG_ERROR", 400);
    this.name = "ConfigError";
  }
}

/** DRM错误 */
export class DRMError extends TTSError {
  constructor(message: string) {
    super(message, "DRM_ERROR", 403);
    this.name = "DRMError";
  }
}