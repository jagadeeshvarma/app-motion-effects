import { chromium } from "@playwright/test";
import { resolve } from "node:path";
import { examples } from "../docs/examples.js";
const browser = await chromium.launch(
  process.env.PLAYWRIGHT_CHANNEL
    ? { channel: process.env.PLAYWRIGHT_CHANNEL }
    : {},
);
const base = process.env.PREVIEW_URL || "http://127.0.0.1:4173/";
async function pageAt(url, width = 1440, height = 1000) {
  const page = await browser.newPage({
    viewport: { width, height },
    deviceScaleFactor: 1,
  });
  await page.goto(new URL(url, base).href, { waitUntil: "networkidle" });
  return page;
}
try {
  const hero = await pageAt("./");
  await hero
    .frameLocator("#hero-preview")
    .getByRole("button", { name: "Saved", exact: true })
    .waitFor();
  await hero.screenshot({ path: resolve("docs/media/site-desktop.png") });
  await hero.close();
  for (const item of examples) {
    const page = await pageAt(`?example=${item.id}#playground`);
    await page.locator("#replay").waitFor();
    await page.getByRole("button", { name: item.action, exact: true }).click();
    const after = page.frameLocator("#after");
    if (["loading", "slow"].includes(item.id))
      await after.locator(".skeleton").waitFor();
    if (item.id === "slow")
      await after.locator("#notice").waitFor({ state: "visible" });
    if (item.id === "loader") await after.locator(".spinner").waitFor();
    if (item.id === "offline")
      await after
        .getByRole("button", { name: "Try again", exact: true })
        .waitFor();
    if (item.id === "upload") {
      await after.getByRole("progressbar").locator("span").waitFor();
      await page.waitForTimeout(600);
      await after.getByRole("button", { name: "Pause", exact: true }).click();
    }
    if (item.id === "save")
      await after.getByRole("button", { name: "Saved", exact: true }).waitFor();
    if (item.id === "filter")
      await after
        .locator("#status")
        .filter({ hasText: "2 projects shown." })
        .waitFor();
    if (item.id === "toast")
      await after.locator("#toast").waitFor({ state: "visible" });
    if (item.id === "panel")
      await after.getByRole("dialog").waitFor({ state: "visible" });
    if (item.id === "tabs")
      await after.getByRole("tab", { name: "Activity", exact: true }).waitFor();
    if (!["loading", "loader", "slow"].includes(item.id))
      await after.locator("body").evaluate(async (el) => {
        await Promise.all(
          el
            .getAnimations({ subtree: true })
            .filter((a) => a.effect.getTiming().iterations !== Infinity)
            .map((a) => a.finished.catch(() => {})),
        );
      });
    const filename =
      {
        loading: "playground-desktop",
        slow: "slow-connection",
        offline: "offline-recovery",
        upload: "upload-progress",
      }[item.id] || item.id;
    await page.screenshot({ path: resolve(`docs/media/${filename}.png`) });
    await page.close();
  }
  const mobileHero = await pageAt("./", 390, 844);
  await mobileHero
    .frameLocator("#hero-preview")
    .getByRole("button", { name: "Saved", exact: true })
    .waitFor();
  await mobileHero.screenshot({ path: resolve("docs/media/site-mobile.png") });
  await mobileHero.close();
  const mobile = await pageAt("?example=save#playground", 390, 844);
  await mobile
    .getByRole("button", { name: "Play save example", exact: true })
    .click();
  await mobile
    .frameLocator("#after")
    .getByRole("button", { name: "Saved", exact: true })
    .waitFor();
  await mobile.screenshot({
    path: resolve("docs/media/playground-mobile.png"),
  });
  await mobile.close();
  const prompt = await pageAt("#full-repo-prompt");
  await prompt.screenshot({ path: resolve("docs/media/full-repo-prompt.png") });
  await prompt.close();
  console.log(
    "Captured the rendered hero, ten examples, mobile views and full-repo prompt.",
  );
} finally {
  await browser.close();
}
