/**
 * 常量定义
 * 参考原edge_tts/constants.py
 */

/** 基础URL和令牌 */
const BASE_URL = "speech.platform.bing.com/consumer/speech/synthesize/readaloud";
const TRUSTED_CLIENT_TOKEN = "6A5AA1D4EAFF4E9FB37E23D68491D6F4";

/** Chrome版本 */
const CHROMIUM_FULL_VERSION = "130.0.2849.68";
const CHROMIUM_MAJOR_VERSION = CHROMIUM_FULL_VERSION.split(".")[0];

/** WebSocket服务URL */
export const WSS_URL = `wss://${BASE_URL}/edge/v1?TrustedClientToken=${TRUSTED_CLIENT_TOKEN}`;

/** SEC-MS-GEC版本 */
export const SEC_MS_GEC_VERSION = `1-${CHROMIUM_FULL_VERSION}`;

/** 基础请求头 */
const BASE_HEADERS = {
  "User-Agent": `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${CHROMIUM_MAJOR_VERSION}.0.0.0 Safari/537.36 Edg/${CHROMIUM_MAJOR_VERSION}.0.0.0`,
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Language": "en-US,en;q=0.9",
};

/** WebSocket请求头 */
export const WSS_HEADERS = {
  ...BASE_HEADERS,
  "Pragma": "no-cache",
  "Cache-Control": "no-cache",
  "Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
  "Sec-WebSocket-Protocol": "synthesize",
  "Accept": "*/*"
};

/** 默认语音 */
export const DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural";

/** 支持的音频格式 */
export const AUDIO_FORMATS = [
  "audio-24khz-48kbitrate-mono-mp3",
  "audio-24khz-16bit-mono-pcm",
  "riff-24khz-16bit-mono-pcm",
  "raw-24khz-16bit-mono-pcm",
  "raw-16khz-16bit-mono-pcm",
  "raw-8khz-8bit-mono-mulaw",
  "raw-8khz-8bit-mono-alaw",
] as const;

/** 协议类型 */
export type AudioFormat = typeof AUDIO_FORMATS[number];

/** 默认音频格式 */
export const DEFAULT_AUDIO_FORMAT: AudioFormat = "audio-24khz-48kbitrate-mono-mp3";

/** SSML相关常量 */
export const SSML_CONSTANTS = {
  /** XML命名空间 */
  XMLNS: "http://www.w3.org/2001/10/synthesis",
  
  /** 版本 */
  VERSION: "1.0",
  
  /** 默认语言 */
  LANG: "en-US",
} as const;