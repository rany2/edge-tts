import type {
  ReconnectConfig,
  ReconnectState,
  ReconnectResult,
  ReconnectEvent,
  ReconnectHandler,
} from "../types/reconnect.ts";

/**
 * 重连管理器
 */
export class ReconnectManager {
  private config: ReconnectConfig;
  private state: ReconnectState;
  private handler?: ReconnectHandler;

  constructor(config: Partial<ReconnectConfig> = {}) {
    this.config = {
      maxRetries: config.maxRetries ?? 3,
      initialDelay: config.initialDelay ?? 1000,
      maxDelay: config.maxDelay ?? 10000,
      backoffFactor: config.backoffFactor ?? 2,
    };

    this.state = {
      attempts: 0,
      lastAttempt: 0,
      currentDelay: this.config.initialDelay,
      isRetrying: false,
    };
  }

  /**
   * 设置事件处理器
   */
  setHandler(handler: ReconnectHandler) {
    this.handler = handler;
  }

  /**
   * 计算下一次重试延迟
   */
  private calculateDelay(): number {
    const delay = this.state.currentDelay * this.config.backoffFactor;
    return Math.min(delay, this.config.maxDelay);
  }

  /**
   * 执行重连操作
   */
  async execute(operation: () => Promise<void>): Promise<ReconnectResult> {
    const startTime = Date.now();
    this.state.attempts = 0;
    this.state.currentDelay = this.config.initialDelay;

    while (this.state.attempts < this.config.maxRetries) {
      try {
        this.state.isRetrying = true;
        this.state.lastAttempt = Date.now();
        
        // 通知尝试事件
        this.handler?.onEvent({
          type: "attempt",
          attempt: this.state.attempts + 1,
          delay: this.state.currentDelay,
        });

        await operation();

        // 操作成功
        const result: ReconnectResult = {
          success: true,
          attempts: this.state.attempts + 1,
          totalTime: Date.now() - startTime,
        };

        this.handler?.onEvent({ type: "success", result });
        this.handler?.onSuccess();
        return result;

      } catch (error) {
        this.state.attempts++;
        
        // 处理错误
        if (error instanceof Error) {
          this.handler?.onError(error);
        }

        // 检查是否还有重试机会
        if (this.state.attempts >= this.config.maxRetries) {
          const result: ReconnectResult = {
            success: false,
            attempts: this.state.attempts,
            totalTime: Date.now() - startTime,
            error: error instanceof Error ? error : new Error(String(error)),
          };
          
          this.handler?.onEvent({ type: "failure", result });
          return result;
        }

        // 等待下一次重试
        await new Promise(resolve => setTimeout(resolve, this.state.currentDelay));
        this.state.currentDelay = this.calculateDelay();
      }
    }

    // 达到最大重试次数
    const result: ReconnectResult = {
      success: false,
      attempts: this.state.attempts,
      totalTime: Date.now() - startTime,
      error: new Error("Max retries exceeded"),
    };

    this.handler?.onEvent({ 
      type: "abort", 
      reason: "Max retries exceeded" 
    });
    
    return result;
  }

  /**
   * 重置状态
   */
  reset(): void {
    this.state = {
      attempts: 0,
      lastAttempt: 0,
      currentDelay: this.config.initialDelay,
      isRetrying: false,
    };
  }

  /**
   * 获取当前状态
   */
  getState(): Readonly<ReconnectState> {
    return { ...this.state };
  }

  /**
   * 获取配置
   */
  getConfig(): Readonly<ReconnectConfig> {
    return { ...this.config };
  }
}

// 重新导出类型
export type {
  ReconnectConfig,
  ReconnectState,
  ReconnectResult,
  ReconnectEvent,
  ReconnectHandler,
} from "../types/reconnect.ts";