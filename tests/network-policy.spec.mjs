import { test, expect } from "@playwright/test";
import { examples } from "../docs/examples.js";

test("all ten example replays stay within static assets", async ({
  page,
  baseURL,
}) => {
  test.setTimeout(90000);
  const unexpected = [];
  const staticPaths = new Set([
    "",
    "index.html",
    "app.js",
    "examples.js",
    "styles.css",
    "favicon.svg",
    "demos/interaction.html",
    "demos/interaction.css",
    "demos/interaction.js",
  ]);
  const prefix = new URL(baseURL).pathname.replace(/\/?$/, "/");
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (
      url.origin !== new URL(baseURL).origin ||
      !staticPaths.has(url.pathname.slice(prefix.length)) ||
      !["document", "script", "stylesheet", "image", "media", "other"].includes(
        request.resourceType(),
      )
    )
      unexpected.push({ url: url.pathname, type: request.resourceType() });
  });
  await page.clock.install();
  for (const example of examples) {
    await page.goto(`./?example=${example.id}#playground`);
    await expect(page.frameLocator("#after").locator("#demo")).toBeVisible();
    await page.locator("#replay").click();
    await page.clock.runFor(12000);
  }
  expect(unexpected).toEqual([]);
});

test("demo CSP blocks a synthetic beacon before it reaches the server", async ({
  page,
}) => {
  const requests = [];
  page.on("request", (r) => {
    if (r.url().includes("__audit_beacon__")) requests.push(r.url());
  });
  await page.goto("./demos/interaction.html?example=save&variant=after");
  const violation = await page.evaluate(async () => {
    return new Promise((resolve) => {
      const timer = setTimeout(() => resolve("no violation"), 2000);
      document.addEventListener(
        "securitypolicyviolation",
        (e) => {
          clearTimeout(timer);
          resolve(e.effectiveDirective);
        },
        { once: true },
      );
      navigator.sendBeacon("/__audit_beacon__", "SYNTHETIC_ONLY");
    });
  });
  expect(violation).toBe("connect-src");
  expect(requests).toEqual([]);
});

test("demo CSP rejects a remote asset without contacting it", async ({
  page,
}) => {
  let reachedNetwork = false;
  await page.route("https://example.invalid/**", async (route) => {
    reachedNetwork = true;
    await route.abort();
  });
  await page.goto("./demos/interaction.html?example=save&variant=after");
  const violation = await page.evaluate(
    () =>
      new Promise((resolve) => {
        const timer = setTimeout(() => resolve("no violation"), 2000);
        document.addEventListener(
          "securitypolicyviolation",
          (e) => {
            clearTimeout(timer);
            resolve(e.effectiveDirective);
          },
          { once: true },
        );
        const img = new Image();
        img.src = "https://example.invalid/synthetic-canary.png";
        document.body.append(img);
      }),
  );
  expect(violation).toBe("img-src");
  expect(reachedNetwork).toBe(false);
});
