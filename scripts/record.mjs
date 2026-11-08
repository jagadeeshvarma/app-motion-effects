// Record real browser playback; conversion to MP4/GIF is a separate media step.
import { chromium } from "@playwright/test";
import { mkdir, copyFile } from "node:fs/promises";
const browser = await chromium.launch(
  process.env.PLAYWRIGHT_CHANNEL
    ? { channel: process.env.PLAYWRIGHT_CHANNEL }
    : {},
);
try {
  await mkdir("dist/recordings", { recursive: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 1000 },
    recordVideo: {
      dir: "dist/recordings",
      size: { width: 1280, height: 1000 },
    },
  });
  const page = await context.newPage();
  await page.goto(
    (process.env.PREVIEW_URL || "http://127.0.0.1:4173/") + "#playground",
    { waitUntil: "networkidle" },
  );
  await page
    .frameLocator("#after")
    .getByRole("list", { name: "Projects" })
    .waitFor();
  await page
    .getByRole("button", { name: "Load projects", exact: true })
    .click();
  await page
    .frameLocator("#after")
    .getByRole("list", { name: "Projects" })
    .waitFor();
  await page.waitForTimeout(700);
  const video = page.video();
  await context.close();
  await copyFile(await video.path(), "dist/recordings/loading.webm");
  console.log(
    "Recorded real loading comparison in dist/recordings/loading.webm.",
  );
} finally {
  await browser.close();
}
