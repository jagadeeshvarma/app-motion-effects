import { chromium } from "@playwright/test";
import { resolve } from "node:path";
const browser = await chromium.launch(
  process.env.PLAYWRIGHT_CHANNEL
    ? { channel: process.env.PLAYWRIGHT_CHANNEL }
    : {},
);
try {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
    deviceScaleFactor: 1,
  });
  await page.goto(process.env.PREVIEW_URL || "http://127.0.0.1:4173", {
    waitUntil: "networkidle",
  });
  await page
    .locator("#after")
    .contentFrame()
    .getByLabel("Composition caption")
    .waitFor();
  await page.screenshot({
    path: resolve("docs/media/site-desktop.png"),
    fullPage: false,
  });
  await page
    .locator("#playground")
    .screenshot({ path: resolve("docs/media/playground-desktop.png") });
  // A fresh page avoids compositor remnants after a tall element capture.
  await page.close();
  const mobile = await browser.newPage({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 1,
  });
  await mobile.goto(process.env.PREVIEW_URL || "http://127.0.0.1:4173", {
    waitUntil: "networkidle",
  });
  await mobile.screenshot({
    path: resolve("docs/media/site-mobile.png"),
    fullPage: false,
  });
  await mobile.locator("#playground").scrollIntoViewIfNeeded();
  await mobile.screenshot({
    path: resolve("docs/media/playground-mobile.png"),
  });
  console.log(
    "Captured actual rendered desktop, mobile and playground screenshots.",
  );
} finally {
  await browser.close();
}
