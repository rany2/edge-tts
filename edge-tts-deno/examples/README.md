# Edge TTS Deno 示例代码

本目录包含了Edge TTS Deno的各种使用示例。每个示例都展示了不同的功能和使用场景。

## 示例列表

### 基础示例

- `simple_tts.ts`: 最简单的TTS转换示例
- `basic_tts.ts`: 带有基本配置的TTS示例
- `streaming_tts.ts`: 演示如何使用流式转换

### 进阶示例

- `advanced_streaming.ts`: 展示自动重连和错误恢复功能
- `subtitle_generation.ts`: 演示多种字幕格式生成功能
- `multilingual_tts.ts`: 多语言支持示例

## 测试示例

- `test_subtitle.ts`: 字幕生成的单元测试示例
  - SRT格式测试
  - WebVTT格式测试
  - 纯文本格式测试

## 运行示例

### 基本用法

```bash
# 运行基础示例
deno run --allow-net examples/simple_tts.ts

# 运行带字幕的示例
deno run --allow-net --allow-write examples/subtitle_generation.ts

# 运行高级流处理示例
deno run --allow-net --allow-write examples/advanced_streaming.ts
```

### 运行测试

```bash
# 运行所有测试
deno test --allow-net examples/test_subtitle.ts

# 运行特定测试

```

## 权限说明

示例程序需要以下权限：

- `--allow-net`: 访问TTS服务（所有示例都需要）
- `--allow-write`: 保存音频和字幕文件（部分示例需要）
- `--allow-read`: 从文件读取输入文本（部分示例需要）

## 配置示例

### 字幕生成配置

```typescript
{
  subtitle: {
    format: SubtitleFormat.SRT,    // 字幕格式：SRT, VTT, TEXT
    wordsPerCue: 5,               // 每个字幕片段的词数
    minDuration: 1000,            // 最小持续时间（毫秒）
    maxDuration: 5000,            // 最大持续时间（毫秒）
    timeOffset: 0,                // 时间偏移（毫秒）
  }
}
```

### 重连配置

```typescript
{
  reconnect: {
    maxRetries: 3,                // 最大重试次数
    initialDelay: 1000,           // 初始延迟（毫秒）
    maxDelay: 5000,               // 最大延迟（毫秒）
    backoffFactor: 2,             // 延迟增长因子
  }
}
```

## 注意事项

1. 运行示例前请确保已安装最新版本的Deno
2. 示例代码主要用于演示目的，生产环境使用时请根据实际需求调整配置
3. 运行测试时可能需要稳定的网络连接
4. 部分示例会在当前目录生成输出文件
5. 字幕生成功能支持多种格式，可以根据需要选择合适的格式

## 反馈和贡献

- 如果发现问题，请提交Issue
- 欢迎提交Pull Request改进示例
- 如需更多示例，请在Issue中提出建议