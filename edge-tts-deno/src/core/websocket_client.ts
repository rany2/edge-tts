import { WebSocket } from "../../deps.ts";
import {
  TTSConfig,
  TTSChunk,
  WordBoundary,
  CommunicateState,
  WebSocketEvent,
  WebSocketErrorEvent,
} from "../types/config.ts";
import {
  WSS_URL,
  WSS_HEADERS,
  SEC_MS_GEC_VERSION,
  DEFAULT_VOICE,
} from "../constants.ts";
import {
  WebSocketError,
  NoAudioReceived,
  UnexpectedResponse,
  UnknownResponse,
} from "../errors/tts_error.ts";
import { DRM } from "../utils/drm.ts";
import { SSMLGenerator } from "../utils/ssml.ts";
import {
  splitTextByByteLength,
  getCurrentDateString,
  parseHeadersAndData,
  removeIncompatibleCharacters,
  findPattern,
  DELIMITER,
} from "../utils/helpers.ts";
import { ReconnectManager } from "../utils/reconnect.ts";
import type { ReconnectConfig, ReconnectHandler } from "../types/reconnect.ts";
import {
  SubtitleGeneratorFactory,
  type SubtitleConfig,
  type SubtitleGenerator,
  SubtitleFormat,
} from "../utils/subtitle.ts";

/**
 * WebSocket客户端配置
 */
interface WebSocketClientConfig {
  connectTimeout?: number;
  receiveTimeout?: number;
  proxy?: string;
  reconnect?: ReconnectConfig;
  subtitle?: SubtitleConfig;
}

/**
 * WebSocket TTS客户端
 */
export class WebSocketClient implements ReconnectHandler {
  private state: CommunicateState;
  private texts: Generator<Uint8Array, void, unknown>;
  private config: TTSConfig;
  private ws: WebSocket | null = null;
  private clientConfig: Required<Omit<WebSocketClientConfig, "subtitle">>;
  private reconnectManager: ReconnectManager;
  private subtitleGenerator: SubtitleGenerator | null = null;

  constructor(
    text: string,
    voice: string = DEFAULT_VOICE,
    rate = "+0%",
    volume = "+0%",
    pitch = "+0Hz",
    config: WebSocketClientConfig = {},
  ) {
    // 验证并存储TTS配置
    this.config = { voice, rate, volume, pitch };

    // 客户端配置
    this.clientConfig = {
      connectTimeout: config.connectTimeout ?? 10000,
      receiveTimeout: config.receiveTimeout ?? 60000,
      proxy: config.proxy ?? "",
      reconnect: config.reconnect ?? {
        maxRetries: 3,
        initialDelay: 1000,
        maxDelay: 10000,
        backoffFactor: 2,
      },
    };

    // 初始化重连管理器
    this.reconnectManager = new ReconnectManager(this.clientConfig.reconnect);
    this.reconnectManager.setHandler(this);

    // 初始化字幕生成器
    if (config.subtitle) {
      this.subtitleGenerator = SubtitleGeneratorFactory.create(config.subtitle);
    }

    // 初始化状态
    this.state = {
      partialText: new Uint8Array(),
      offsetCompensation: 0,
      lastDurationOffset: 0,
      streamWasCalled: false,
    };

    // 分割文本
    const cleanText = removeIncompatibleCharacters(text);
    this.texts = splitTextByByteLength(
      cleanText,
      SSMLGenerator.calculateMaxMessageSize(this.config),
    );
  }

  /**
   * 实现ReconnectHandler接口
   */
  onEvent(event: { type: string; attempt?: number; delay?: number }): void {
    if (event.type === "attempt") {
      console.log(`Reconnecting... Attempt ${event.attempt} (delay: ${event.delay}ms)`);
    }
  }

  onError(error: Error): void {
    console.error("Reconnection error:", error);
  }

  onSuccess(): void {
    console.log("Successfully reconnected");
  }

  /**
   * 获取生成的字幕内容
   */
  getSubtitles(): string {
    if (!this.subtitleGenerator) {
      throw new Error("No subtitle generator configured");
    }
    return this.subtitleGenerator.generate();
  }

  /**
   * 建立WebSocket连接
   */
  private async connect(): Promise<void> {
    await this.reconnectManager.execute(async () => {
      // 如果已经连接，先关闭
      if (this.ws) {
        try {
          this.ws.close();
        } catch {
          // 忽略关闭错误
        }
        this.ws = null;
      }

      // 创建新的WebSocket连接
      const wsUrl = new URL(WSS_URL);
      const connectionId = crypto.randomUUID().replace(/-/g, "");
      const sec_ms_gec = DRM.generateSecMsGec();

      wsUrl.searchParams.set("Sec-MS-GEC", sec_ms_gec);
      wsUrl.searchParams.set("Sec-MS-GEC-Version", SEC_MS_GEC_VERSION);
      wsUrl.searchParams.set("ConnectionId", connectionId);

      const headers = {
        ...WSS_HEADERS,
        "Sec-WebSocket-Extensions": "permessage-deflate",
        "Sec-WebSocket-Protocol": "synthesize",
      };

      this.ws = new WebSocket(wsUrl.toString(), {
        headers: headers,
      });

      // 等待连接建立
      await new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new WebSocketError("Connection timeout"));
        }, this.clientConfig.connectTimeout);

        this.ws!.onopen = () => {
          clearTimeout(timeout);
          resolve();
        };

        this.ws!.onerror = (event: WebSocketErrorEvent) => {
          clearTimeout(timeout);
          reject(new WebSocketError(`Connection failed: ${event.message}`));
        };
      });
    });
  }

  /**
   * 关闭WebSocket连接
   */
  private async disconnect(): Promise<void> {
    if (this.ws) {
      try {
        this.ws.close();
      } catch {
        // 忽略关闭错误
      }
      this.ws = null;
    }
  }

  /**
   * 发送配置命令
   */
  private async sendConfigCommand(): Promise<void> {
    if (!this.ws) throw new WebSocketError("Not connected");

    const command = {
      context: {
        synthesis: {
          audio: {
            metadataoptions: {
              sentenceBoundaryEnabled: false,
              wordBoundaryEnabled: true,
            },
            outputFormat: "audio-24khz-48kbitrate-mono-mp3",
          },
        },
      },
    };

    const headers = [
      `X-Timestamp:${getCurrentDateString()}`,
      "Content-Type:application/json; charset=utf-8",
      "Path:speech.config",
      "",
      JSON.stringify(command),
      "",
    ].join("\r\n");

    this.ws.send(headers);
  }

  /**
   * 发送SSML请求
   */
  private async sendSSMLRequest(): Promise<void> {
    if (!this.ws) throw new WebSocketError("Not connected");

    const ssml = SSMLGenerator.generate(this.config, this.state.partialText);
    const headers = SSMLGenerator.generateRequestHeaders(
      crypto.randomUUID().replace(/-/g, ""),
      getCurrentDateString(),
      ssml,
    );

    this.ws.send(headers);
  }

  /**
   * 处理WordBoundary元数据
   */
  private handleWordBoundary(metadata: WordBoundary): void {
    if (this.subtitleGenerator && metadata.text) {
      this.subtitleGenerator.addCue(metadata.text, {
        start: metadata.offset,
        duration: metadata.duration,
        end: metadata.offset + metadata.duration,
      });
    }
  }

  /**
   * 解析元数据
   */
  private parseMetadata(data: string): WordBoundary {
    const metadata = JSON.parse(data).Metadata;
    for (const meta of metadata) {
      if (meta.Type === "WordBoundary") {
        return {
          type: "WordBoundary",
          offset: meta.Data.Offset + this.state.offsetCompensation,
          duration: meta.Data.Duration,
          text: meta.Data.text.Text,
        };
      }
      if (meta.Type === "SessionEnd") continue;
      throw new UnknownResponse(`Unknown metadata type: ${meta.Type}`);
    }
    throw new UnexpectedResponse("No WordBoundary metadata found");
  }

  /**
   * 处理WebSocket消息流
   */
  private async *streamWebSocket(): AsyncGenerator<string | ArrayBuffer, void, unknown> {
    if (!this.ws) throw new WebSocketError("Not connected");

    const ws = this.ws;
    const messageQueue: Array<string | ArrayBuffer> = [];
    let error: Error | null = null;
    let done = false;

    // 设置消息处理器
    ws.onmessage = (event: WebSocketEvent) => {
      messageQueue.push(event.data);
    };

    ws.onerror = (event: WebSocketErrorEvent) => {
      error = new WebSocketError(`WebSocket error: ${event.message}`);
    };

    ws.onclose = () => {
      done = true;
    };

    // 接收消息循环
    while (!done && !error) {
      if (messageQueue.length > 0) {
        yield messageQueue.shift()!;
      } else {
        await new Promise(resolve => setTimeout(resolve, 10));
      }
    }

    if (error) throw error;
  }

  /**
   * 处理单个文本块的流式传输
   */
  private async *streamChunk(): AsyncGenerator<TTSChunk, void, unknown> {
    let audioReceived = false;

    await this.sendConfigCommand();
    await this.sendSSMLRequest();

    for await (const message of this.streamWebSocket()) {
      if (typeof message === "string") {
        const data = new TextEncoder().encode(message);
        const headerEnd = findPattern(data, DELIMITER);
        if (headerEnd === -1) {
          throw new UnexpectedResponse("Invalid message format: no header delimiter found");
        }

        const [headers, content] = parseHeadersAndData(data, headerEnd);

        const path = headers["Path"];
        if (path === "audio.metadata") {
          const metadata = this.parseMetadata(new TextDecoder().decode(content));
          this.handleWordBoundary(metadata);
          yield metadata;
          this.state.lastDurationOffset = metadata.offset + metadata.duration;
        } else if (path === "turn.end") {
          this.state.offsetCompensation = this.state.lastDurationOffset + 8_750_000;
          break;
        } else if (!["response", "turn.start"].includes(path)) {
          throw new UnknownResponse("Unknown path received");
        }
      } else {
        const view = new Uint8Array(message);
        if (view.length < 2) {
          throw new UnexpectedResponse("Binary message too short");
        }

        const headerLength = (view[0] << 8) | view[1];
        if (headerLength > view.length) {
          throw new UnexpectedResponse("Header length greater than message length");
        }

        const [headers, content] = parseHeadersAndData(view, headerLength);

        if (headers["Path"] !== "audio") {
          throw new UnexpectedResponse("Unexpected binary message path");
        }

        const contentType = headers["Content-Type"];
        if (!["audio/mpeg", undefined].includes(contentType)) {
          throw new UnexpectedResponse("Unexpected Content-Type");
        }

        if (!contentType && content.length > 0) {
          throw new UnexpectedResponse("Binary message with no Content-Type but with data");
        }

        if (content.length === 0 && contentType) {
          throw new UnexpectedResponse("Empty audio data received");
        }

        audioReceived = true;
        yield { type: "audio", data: content };
      }
    }

    if (!audioReceived) {
      throw new NoAudioReceived();
    }
  }

  /**
   * 流式获取音频和元数据
   */
  async *stream(): AsyncGenerator<TTSChunk, void, unknown> {
    if (this.state.streamWasCalled) {
      throw new Error("Stream can only be called once");
    }
    this.state.streamWasCalled = true;

    try {
      for (const text of this.texts) {
        this.state.partialText = text;
        await this.connect();

        try {
          for await (const chunk of this.streamChunk()) {
            yield chunk;
          }
        } catch (error: unknown) {
          if (
            error instanceof Error &&
            "status" in error &&
            (error as { status: number }).status === 403
          ) {
            DRM.handleClientResponseError(error as Error & { status?: number });
            await this.connect();
            for await (const chunk of this.streamChunk()) {
              yield chunk;
            }
          } else {
            throw error;
          }
        } finally {
          await this.disconnect();
        }
      }
    } finally {
      await this.disconnect();
    }
  }
}
