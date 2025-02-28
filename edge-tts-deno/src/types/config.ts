/**
 * TTS配置接口
 */
export interface TTSConfig {
  voice: string;
  rate: string;
  volume: string;
  pitch: string;
}

/**
 * 通信状态接口
 */
export interface CommunicateState {
  partialText: Uint8Array;
  offsetCompensation: number;
  lastDurationOffset: number;
  streamWasCalled: boolean;
}

/**
 * WebSocket消息类型
 */
export interface WebSocketEvent {
  data: string | ArrayBuffer;
  type: string;
  target: WebSocket;
}

/**
 * WebSocket错误事件
 */
export interface WebSocketErrorEvent {
  error: Error;
  message: string;
  type: string;
  target: WebSocket;
}

/**
 * 音频块类型
 */
export interface AudioChunk {
  type: "audio";
  data: Uint8Array;
}

/**
 * 词边界类型
 */
export interface WordBoundary {
  type: "WordBoundary";
  offset: number;
  duration: number;
  text: string;
}

/**
 * TTS输出块类型
 */
export type TTSChunk = AudioChunk | WordBoundary;

/**
 * WebSocket客户端配置
 */
export interface WebSocketClientConfig {
  /** 连接超时时间(ms) */
  connectTimeout?: number;
  /** 接收超时时间(ms) */
  receiveTimeout?: number;
  /** 代理设置 */
  proxy?: string;
  /** 重连配置 */
  reconnect?: {
    /** 是否启用重连 */
    enabled: boolean;
    /** 最大重试次数 */
    maxRetries?: number;
    /** 初始重试延迟(ms) */
    initialDelay?: number;
    /** 最大重试延迟(ms) */
    maxDelay?: number;
    /** 重试延迟增长因子 */
    factor?: number;
    /** 是否启用抖动 */
    jitter?: boolean;
  };
}

/**
 * 默认WebSocket客户端配置
 */
export const DEFAULT_CLIENT_CONFIG: Required<WebSocketClientConfig> = {
  connectTimeout: 10000,
  receiveTimeout: 60000,
  proxy: "",
  reconnect: {
    enabled: true,
    maxRetries: 3,
    initialDelay: 1000,
    maxDelay: 10000,
    factor: 2,
    jitter: true,
  },
};