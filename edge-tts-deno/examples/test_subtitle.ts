/**
 * 字幕生成测试
 */
import { assertEquals } from "std/assert";
import {
  WebSocketClient,
  SubtitleFormat,
} from "@/mod.ts";

/**
 * 验证SRT格式
 */
function assertSRTFormat(content: string) {
  const lines = content.split("\n");
  let index = 0;

  while (index < lines.length) {
    const line = lines[index].trim();
    if (line === "") {
      index++;
      continue;
    }

    // 验证序号
    assertEquals(isNaN(parseInt(line, 10)), false);
    index++;

    if (index >= lines.length) break;

    // 验证时间戳格式
    const timestamp = lines[index].trim();
    assertEquals(
      /^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$/.test(timestamp),
      true,
      `无效的时间戳格式: ${timestamp}`
    );
    index++;

    if (index >= lines.length) break;

    // 验证文本内容
    assertEquals(lines[index].trim().length > 0, true);
    index++;
  }
}

/**
 * 验证WebVTT格式
 */
function assertVTTFormat(content: string) {
  const lines = content.split("\n");
  // 验证WebVTT头
  assertEquals(lines[0].trim(), "WEBVTT");

  let index = 1;
  while (index < lines.length) {
    const line = lines[index].trim();
    if (line === "") {
      index++;
      continue;
    }

    // 验证时间戳格式
    assertEquals(
      /^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}$/.test(line),
      true,
      `无效的VTT时间戳格式: ${line}`
    );
    index++;

    if (index >= lines.length) break;

    // 验证文本内容
    assertEquals(lines[index].trim().length > 0, true);
    index++;
  }
}

/**
 * 验证纯文本格式
 */
function assertTextFormat(content: string) {
  // 验证是否为非空文本
  assertEquals(content.trim().length > 0, true);
  // 验证没有时间戳格式
  assertEquals(
    /\d{2}:\d{2}:\d{2}[,\.]\d{3}/.test(content),
    false,
    "纯文本不应包含时间戳"
  );
}

/**
 * 测试SRT格式生成
 */
Deno.test("SRT格式测试", async () => {
  const text = "这是一个测试文本。它将被转换为SRT格式字幕。";
  const client = new WebSocketClient(
    text,
    "zh-CN-XiaoxiaoNeural",
    "+0%",
    "+0%",
    "+0Hz",
    {
      subtitle: {
        format: SubtitleFormat.SRT,
        wordsPerCue: 3,
        minDuration: 1000,
        maxDuration: 3000,
        timeOffset: 0,
      },
    }
  );

  for await (const chunk of client.stream()) {
    if (chunk.type === "audio") {
      assertEquals(chunk.data instanceof Uint8Array, true);
    } else {
      assertEquals(chunk.type, "WordBoundary");
      assertEquals(typeof chunk.text, "string");
      assertEquals(typeof chunk.offset, "number");
      assertEquals(typeof chunk.duration, "number");
    }
  }

  const srt = client.getSubtitles();
  assertSRTFormat(srt);
});

/**
 * 测试WebVTT格式生成
 */
Deno.test("WebVTT格式测试", async () => {
  const text = "这是一个测试文本。它将被转换为VTT格式字幕。";
  const client = new WebSocketClient(
    text,
    "zh-CN-XiaoxiaoNeural",
    "+0%",
    "+0%",
    "+0Hz",
    {
      subtitle: {
        format: SubtitleFormat.VTT,
        wordsPerCue: 3,
        minDuration: 1000,
        maxDuration: 3000,
        timeOffset: 0,
      },
    }
  );

  for await (const _ of client.stream()) {
    // 等待流完成
  }

  const vtt = client.getSubtitles();
  assertVTTFormat(vtt);
});

/**
 * 测试纯文本格式生成
 */
Deno.test("TEXT格式测试", async () => {
  const text = "这是一个测试文本。它将被转换为纯文本格式。";
  const client = new WebSocketClient(
    text,
    "zh-CN-XiaoxiaoNeural",
    "+0%",
    "+0%",
    "+0Hz",
    {
      subtitle: {
        format: SubtitleFormat.TEXT,
        wordsPerCue: 3,
        minDuration: 1000,
        maxDuration: 3000,
        timeOffset: 0,
      },
    }
  );

  for await (const _ of client.stream()) {
    // 等待流完成
  }

  const txt = client.getSubtitles();
  assertTextFormat(txt);
});