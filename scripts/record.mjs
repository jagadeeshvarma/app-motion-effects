// Record real browser playback. ffmpeg conversion is a separate media step.
import { chromium } from "@playwright/test";
import { mkdir, copyFile } from "node:fs/promises";
const browser = await chromium.launch(
  process.env.PLAYWRIGHT_CHANNEL
    ? { channel: process.env.PLAYWRIGHT_CHANNEL }
    : {},
);
const base = process.env.PREVIEW_URL || "http://127.0.0.1:4173/";
try {
  await mkdir("dist/recordings", { recursive: true });
  for (const kind of ["loading", "save"]) {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
      recordVideo: {
        dir: "dist/recordings",
        size: { width: 1440, height: 1000 },
      },
    });
    const page = await context.newPage();
    await page.goto(new URL(`?example=${kind}#playground`, base).href, {
      waitUntil: "networkidle",
    });
    await page.getByRole("button", { name: "Compare", exact: true }).click();
    await page.locator("#replay").click();
    const after = page.frameLocator("#after");
    if (kind === "loading")
      await after
        .getByRole("list", { name: "Projects", exact: true })
        .waitFor();
    else
      await after.getByRole("button", { name: "Saved", exact: true }).waitFor();
    await page.waitForTimeout(1000);
    const video = page.video();
    await context.close();
    await copyFile(await video.path(), `dist/recordings/${kind}.webm`);
  }
  console.log(
    "Recorded actual loading and saving comparisons in dist/recordings.",
  );
} finally {
  await browser.close();
}
