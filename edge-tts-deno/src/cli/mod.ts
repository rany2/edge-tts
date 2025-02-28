/**
 * @file CLI模块入口
 */

export { EdgeTTSCliProcessor } from "./processor.ts";
export { main } from "./main.ts";
export type {
  CLIArgs,
  CLIProcessor,
  InputSource,
  OutputTarget,
  CLIError,
} from "../types/cli.ts";

/**
 * CLI运行入口
 */
if (import.meta.main) {
  const { main } = await import("./main.ts");
  await main().catch((error: unknown) => {
    console.error("Fatal error:", error);
    Deno.exit(1);
  });
}