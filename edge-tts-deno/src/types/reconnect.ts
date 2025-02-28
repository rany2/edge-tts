/**
 * 重连配置接口
 */
export interface ReconnectConfig {
  /** 最大重试次数 */
  maxRetries: number;
  
  /** 初始重试延迟（毫秒） */
  initialDelay: number;
  
  /** 最大重试延迟（毫秒） */
  maxDelay: number;
  
  /** 延迟增长因子 */
  backoffFactor: number;
}

/**
 * 重连状态接口
 */
export interface ReconnectState {
  /** 当前重试次数 */
  attempts: number;
  
  /** 上次尝试时间 */
  lastAttempt: number;
  
  /** 当前延迟时间 */
  currentDelay: number;
  
  /** 是否正在重试 */
  isRetrying: boolean;
}

/**
 * 重连结果接口
 */
export interface ReconnectResult {
  /** 是否成功 */
  success: boolean;
  
  /** 重试次数 */
  attempts: number;
  
  /** 总耗时（毫秒） */
  totalTime: number;
  
  /** 错误信息（如果失败） */
  error?: Error;
}

/**
 * 重连事件类型
 */
export type ReconnectEvent = 
  | { type: "attempt"; attempt: number; delay: number }
  | { type: "success"; result: ReconnectResult }
  | { type: "failure"; result: ReconnectResult }
  | { type: "abort"; reason: string };

/**
 * 重连处理器接口
 */
export interface ReconnectHandler {
  /** 处理重连事件 */
  onEvent(event: ReconnectEvent): void;
  
  /** 处理重连错误 */
  onError(error: Error): void;
  
  /** 重连成功回调 */
  onSuccess(): void;
}
