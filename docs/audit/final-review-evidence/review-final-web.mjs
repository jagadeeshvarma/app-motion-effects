/** Independent six-item corpus evidence collection, no output repairs/model calls. */
import { chromium } from "@playwright/test";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { createServer } from "node:http";
import { join, extname } from "node:path";
import { parseArgs } from "node:util";
import {
  assertSafeStaticRequest,
  preflightStaticRoot,
} from "../../../evals/graders/safe-static-server.mjs";
const { values } = parseArgs({
  options: {
    "input-map": { type: "string" },
    "output-base": { type: "string" },
  },
});
if (!values["input-map"] || !values["output-base"])
  throw Error("Require --input-map and --output-base");
const mapping = JSON.parse(await readFile(values["input-map"], "utf8"));
const dest = values["output-base"];
await mkdir(dest, { recursive: true });
const browser = await chromium.launch({ channel: "chrome", headless: true });
const report = {
  browser: await browser.version(),
  method:
    "Independent final candidate review, explicitly not condition-blinded",
  outputs: [],
};
const pause = (ms) => new Promise((r) => setTimeout(r, ms));
for (const entry of mapping) {
  const root = await preflightStaticRoot(join(entry.source, entry.app_root));
  const server = createServer(async (req, res) => {
    try {
      const file = await assertSafeStaticRequest(root, req.url);
      res.setHeader(
        "Content-Type",
        { ".html": "text/html", ".js": "text/javascript", ".css": "text/css" }[
          extname(file)
        ] || "text/plain",
      );
      res.end(await readFile(file));
    } catch {
      res.statusCode = 403;
      res.end("Not available");
    }
  });
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  const origin = `http://127.0.0.1:${server.address().port}`;
  const output = { id: entry.id, scenario: entry.scenario, cases: [] };
  report.outputs.push(output);
  for (const [size, viewport] of Object.entries({
    desktop: { width: 1280, height: 900 },
    mobile: { width: 320, height: 720 },
  }))
    for (const colorScheme of ["light", "dark"])
      for (const reducedMotion of ["no-preference", "reduce"]) {
        const context = await browser.newContext({
          viewport,
          colorScheme,
          reducedMotion,
          hasTouch: size === "mobile",
          recordVideo:
            size === "desktop" &&
            colorScheme === "light" &&
            reducedMotion === "no-preference"
              ? { dir: dest, size: viewport }
              : undefined,
        });
        const page = await context.newPage();
        page.setDefaultTimeout(2500);
        const row = {
          size,
          colorScheme,
          reducedMotion,
          checks: [],
          errors: [],
          externalRequests: [],
        };
        output.cases.push(row);
        page.on("pageerror", (error) => row.errors.push(error.message));
        await context.route("**/*", (route) => {
          const url = route.request().url();
          if (
            !url.startsWith(origin + "/") &&
            !url.startsWith("data:") &&
            !url.startsWith("blob:")
          ) {
            row.externalRequests.push(url);
            return route.abort();
          }
          return route.continue();
        });
        const observe = async (name, fn) => {
          try {
            row.checks.push({ name, result: await fn() });
          } catch (error) {
            row.checks.push({ name, error: error.message });
          }
        };
        try {
          await page.goto(origin);
          await page.evaluate(() => {
            window.__reviewSamples = [];
            window.__reviewSampler = setInterval(() => {
              for (const a of document.getAnimations()) {
                if (window.__reviewSamples.length > 1500) break;
                const el = a.effect?.target;
                if (!el) continue;
                const s = getComputedStyle(el);
                window.__reviewSamples.push({
                  target: el.id || el.tagName,
                  time: a.currentTime,
                  progress: a.effect.getComputedTiming().progress,
                  duration: a.effect.getTiming().duration,
                  opacity: s.opacity,
                  transform: s.transform,
                  color: s.color,
                  background: s.backgroundColor,
                });
              }
            }, 8);
          });
          const sampleShot = async () => {
            if (
              reducedMotion === "no-preference" &&
              ((size === "desktop" && colorScheme === "light") ||
                (size === "mobile" && colorScheme === "dark"))
            )
              await page.screenshot({
                path: join(
                  dest,
                  `${entry.id}-${size}-${colorScheme}-central.png`,
                ),
                fullPage: true,
              });
          };
          const value = (id) => page.locator(id).inputValue();
          const text = (id) => page.locator(id).textContent();
          const stat = () => page.evaluate(() => ({ ...window.__repoStats }));
          const click = (selector) => page.locator(selector).click();
          const wait = (ms) => page.waitForTimeout(ms);
          const s = entry.scenario;
          if (s === "A") {
            await observe("empty-note-focus", async () => {
              await click("#save");
              return {
                feedback: await text("#feedback"),
                focus: await page.evaluate(() => document.activeElement.id),
              };
            });
            await page.locator("#draft").fill("Retained failure note");
            await page.locator("#fail-next").check();
            await click("#save");
            row.pending = {
              feedback: await text("#feedback"),
              stats: await stat(),
            };
            await page.locator("#save").evaluate((e) => {
              e.click();
              e.click();
            });
            await wait(380);
            row.failure = {
              draft: await value("#draft"),
              feedback: await text("#feedback"),
              stats: await stat(),
              notes: await text("#notes"),
            };
            await page.locator("#fail-next").uncheck();
            await click("#save");
            await wait(340);
            await sampleShot();
            row.saved = {
              feedback: await text("#feedback"),
              notes: await text("#notes"),
              stats: await stat(),
            };
            row.motionBeforeReload = await page.evaluate(
              () => window.__reviewSamples,
            );
            await page.reload();
            row.reload = await text("#notes");
            await page.locator("#draft").fill("Submitted note");
            await click("#save");
            await page.locator("#draft").fill("Newer draft");
            await wait(370);
            row.newerDraft = {
              value: await value("#draft"),
              feedback: await text("#feedback"),
            };
            await page.locator("#draft").fill("Reentered note");
            await click("#save");
            await page.locator("#draft").fill("Different text");
            await page.locator("#draft").fill("Reentered note");
            await wait(370);
            row.reenteredDraft = {
              value: await value("#draft"),
              feedback: await text("#feedback"),
            };
          } else if (s === "B") {
            await page.evaluate(
              () => (window.__draftNode = document.querySelector("#draft")),
            );
            await page.locator("#draft").fill("Lamp draft retained");
            await page.locator("#priority").check();
            await page
              .locator("#draft")
              .evaluate((e) => e.setSelectionRange(3, 8));
            await page.locator("[data-record=two]").focus();
            await page.keyboard.press("Enter");
            await wait(35);
            await sampleShot();
            await page.locator("#draft").fill("Chair draft retained");
            await page.locator("#priority").uncheck();
            for (let n = 0; n < 8; n++) {
              await page
                .locator(`[data-record=${n % 2 ? "two" : "one"}]`)
                .focus();
              await page.keyboard.press("Enter");
            }
            row.chair = {
              draft: await value("#draft"),
              priority: await page.locator("#priority").isChecked(),
            };
            await click("[data-record=one]");
            row.lamp = await page
              .locator("#draft")
              .evaluate((e) => ({
                draft: e.value,
                start: e.selectionStart,
                end: e.selectionEnd,
                identity: e === window.__draftNode,
                priority: document.querySelector("#priority").checked,
              }));
          } else if (s === "E") {
            await page.locator("#open").focus();
            await page.keyboard.press("Enter");
            await wait(35);
            await sampleShot();
            row.dialog = await page
              .locator("#editor")
              .evaluate((e) => ({
                tag: e.tagName,
                role: e.getAttribute("role"),
                label: e.getAttribute("aria-label"),
                labelledby: e.getAttribute("aria-labelledby"),
                focus: e.contains(document.activeElement),
                active: document.activeElement.id,
              }));
            row.tabContained = true;
            for (let n = 0; n < 8; n++) {
              await page.keyboard.press("Tab");
              row.tabContained &&= await page
                .locator("#editor")
                .evaluate((e) => e.contains(document.activeElement));
            }
            await page.locator("#count").fill("9");
            await click("#confirm");
            await wait(300);
            row.confirmed = {
              feedback: await text("#feedback"),
              visible: await page.locator("#editor").isVisible(),
              focus: await page.evaluate(() => document.activeElement.id),
            };
            await click("#open");
            await page.keyboard.press("Escape");
            await wait(300);
            row.escaped = {
              visible: await page.locator("#editor").isVisible(),
              focus: await page.evaluate(() => document.activeElement.id),
            };
            for (let n = 0; n < 2; n++) {
              await click("#open");
              await click("#cancel");
              await wait(reducedMotion === "reduce" ? 30 : 180);
            }
            row.repeatedClosed = !(await page.locator("#editor").isVisible());
          } else if (s === "F") {
            row.rejections = [];
            for (const permission of ["viewer", "expired"]) {
              await page.locator("#permission").selectOption(permission);
              await page.locator("#address").fill("Draft " + permission);
              await click("#save");
              const pending = await text("#feedback");
              await page.locator("#save").evaluate((e) => {
                e.click();
                e.click();
              });
              await wait(370);
              const error = await text("#feedback");
              await wait(720);
              row.rejections.push({
                permission,
                pending,
                error,
                persistent: (await text("#feedback")) === error,
                draft: await value("#address"),
                stats: await stat(),
              });
            }
            await page.locator("#permission").selectOption("editor");
            await click("#save");
            await wait(335);
            await sampleShot();
            row.retry = {
              feedback: await text("#feedback"),
              stats: await stat(),
            };
            await page.locator("#address").fill("Submitted address");
            await click("#save");
            await page.locator("#address").fill("Newer unsaved address");
            await wait(370);
            row.newerDraft = {
              draft: await value("#address"),
              feedback: await text("#feedback"),
            };
          } else if (s === "G" || s === "K") {
            const input = s === "G" ? "#message" : "#handover",
              open = s === "G" ? "#preview" : "#show",
              close = s === "G" ? "#close" : "#hide",
              panel = s === "G" ? "#preview-panel" : "#handover-panel",
              content = s === "G" ? "#message-content" : "#handover-content";
            const payload =
              '<img src=x onerror="window.__reviewInjected=true">Literal note';
            await page.locator(input).fill(payload);
            await click(open);
            await wait(35);
            await sampleShot();
            row.literal = {
              content: await text(content),
              childMarkup: await page
                .locator(content + " img," + content + " script")
                .count(),
              injected: await page.evaluate(() =>
                Boolean(window.__reviewInjected),
              ),
            };
            await page.locator(close).focus();
            await page.keyboard.press("Enter");
            await wait(25);
            await page.locator(open).evaluate((e) => e.click());
            await wait(280);
            row.reversed = {
              visible: await page.locator(panel).isVisible(),
              draft: await value(input),
              content: await text(content),
            };
            await page.locator(close).focus();
            if (s === "G") await page.keyboard.press("Escape");
            else await page.keyboard.press("Enter");
            await wait(280);
            row.closed = {
              visible: await page.locator(panel).isVisible(),
              focus: await page.evaluate(() => document.activeElement.id),
            };
            await click(open);
            await wait(20);
          } else if (s === "H") {
            await page.locator("#refresh").focus();
            await page.keyboard.press("Enter");
            await wait(25);
            await sampleShot();
            row.refresh = {
              feedback: await text("#feedback"),
              duration: await page
                .locator("#refresh")
                .evaluate((e) => getComputedStyle(e).transitionDuration),
            };
            await wait(180);
            await click("#refresh");
            await wait(180);
          } else if (s === "I") {
            await page.locator("#search").fill("A");
            await wait(20);
            row.initialAAnimations = await page.evaluate(
              () => document.getAnimations().length,
            );
            row.initialAVisible = await page
              .locator("#shelves li:visible")
              .allTextContents();
            await page.locator("#search").fill("");
            await wait(160);
            await page.locator("#search").fill("B");
            await wait(35);
            await sampleShot();
            for (const term of ["A", "missing", "B", ""])
              await page.locator("#search").fill(term);
            row.filter = {
              visible: await page
                .locator("#shelves li:visible")
                .allTextContents(),
              feedback: await text("#feedback"),
              focus: await page.evaluate(() => document.activeElement.id),
            };
          } else if (s === "J" || s === "L") {
            const list = s === "J" ? "#kits" : "#parcels";
            await page.locator("#filter").selectOption("ready");
            await wait(35);
            await sampleShot();
            row.ready = {
              visible: await page
                .locator(list + " li:visible")
                .allTextContents(),
              feedback: await text("#feedback"),
            };
            for (const option of ["all", "ready", "all", "ready"])
              await page.locator("#filter").selectOption(option);
            row.latest = {
              visible: await page
                .locator(list + " li:visible")
                .allTextContents(),
              feedback: await text("#feedback"),
              focus: await page.evaluate(() => document.activeElement.id),
              changes: await page.evaluate(() => window.__filterStats?.changes),
            };
          }
          row.samples = await page.evaluate(() => window.__reviewSamples || []);
          row.layout = await page.evaluate(() => ({
            width: innerWidth,
            scrollWidth: document.documentElement.scrollWidth,
            bg: getComputedStyle(document.body).backgroundColor,
            color: getComputedStyle(document.body).color,
          }));
          if (reducedMotion === "no-preference") {
            if (s === "B") await click("[data-record=two]");
            else if (s === "I") await page.locator("#search").fill("B");
            else if (s === "J" || s === "L")
              await page.locator("#filter").selectOption("all");
            else if (s === "H") await click("#refresh");
            else if (s === "E") await click("#open");
            else if (s === "G" || s === "K")
              await page
                .locator(s === "G" ? "#close" : "#hide")
                .evaluate((e) => e.click());
            else if (s === "F") {
              await click("#save");
            } else if (s === "A") {
              await page.locator("#draft").fill("Live preference");
              await click("#save");
            }
            await page.emulateMedia({ reducedMotion: "reduce" });
            await wait(45);
            row.liveReducedActive = await page.evaluate(
              () =>
                document
                  .getAnimations()
                  .filter((a) => a.playState === "running").length,
            );
          }
        } catch (error) {
          row.flowError = error.message;
        }
        const video = page.video();
        await context.close();
        if (video) {
          const filename = `${entry.id}-desktop-playback.webm`;
          await video.saveAs(join(dest, filename));
          await video.delete();
          row.video = filename;
        }
      }
  await new Promise((resolve) => server.close(resolve));
  await writeFile(
    join(dest, `${entry.id}-observations.json`),
    JSON.stringify(output, null, 2),
  );
  console.log(
    JSON.stringify({
      id: entry.id,
      scenario: entry.scenario,
      cases: output.cases.length,
      errors: output.cases
        .filter((c) => c.flowError || c.errors.length)
        .map((c) => ({
          size: c.size,
          theme: c.colorScheme,
          motion: c.reducedMotion,
          error: c.flowError || c.errors,
        })),
    }),
  );
}
await browser.close();
await writeFile(
  join(dest, "all-observations.json"),
  JSON.stringify(report, null, 2),
);
