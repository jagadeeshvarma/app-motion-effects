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
    .getByRole("list", { name: "Projects" })
    .waitFor();
  await page.screenshot({
    path: resolve("docs/media/site-desktop.png"),
    fullPage: false,
  });
  await page
    .getByRole("button", { name: "Load projects", exact: true })
    .click();
  await page.frameLocator("#after").locator(".skeleton").waitFor();
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
  await mobile.close();
  for (const [scenario, name] of [
    ["slow", "slow-connection"],
    ["offline", "offline-recovery"],
    ["upload", "upload-progress"],
  ]) {
    const review = await browser.newPage({
      viewport: { width: 1280, height: 1000 },
      deviceScaleFactor: 1,
    });
    const base = process.env.PREVIEW_URL || "http://127.0.0.1:4173/";
    await review.goto(base + "?example=" + scenario, {
      waitUntil: "networkidle",
    });
    const after = review.frameLocator("#after");
    if (scenario === "offline")
      await after
        .getByLabel("Project note")
        .fill("Keep my draft while reconnecting.");
    await review.locator("#replay").click();
    if (scenario === "slow")
      await after.locator("#notice").waitFor({ state: "visible" });
    if (scenario === "offline")
      await after.getByRole("button", { name: "Try again" }).waitFor();
    if (scenario === "upload") {
      await after.getByRole("button", { name: "Pause", exact: true }).waitFor();
      await review.waitForTimeout(600);
      await after.getByRole("button", { name: "Pause", exact: true }).click();
    }
    await review
      .locator("#playground")
      .screenshot({ path: resolve(`docs/media/${name}.png`) });
    await review.close();
  }
  console.log(
    "Captured actual rendered desktop, mobile and playground screenshots.",
  );
} finally {
  await browser.close();
}
