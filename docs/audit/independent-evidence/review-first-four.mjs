import { chromium } from "@playwright/test";
import fs from "node:fs/promises";
import path from "node:path";
import { parseArgs } from "node:util";

const { values } = parseArgs({
  options: {
    "input-base": { type: "string" },
    "output-base": { type: "string" },
    outputs: { type: "string" },
    label: { type: "string" },
    help: { type: "boolean" },
  },
});
if (values.help) {
  console.log(
    "Usage: node docs/audit/independent-evidence/review-first-four.mjs --input-base http://127.0.0.1:8000/ --output-base ./review-evidence [--outputs 0123abcd:B] [--label additional]",
  );
  process.exit(0);
}
if (!values["input-base"] || !values["output-base"]) {
  throw new Error(
    "Both --input-base (served fixture URL) and --output-base (evidence directory) are required.",
  );
}
const inputBase = new URL(values["input-base"].replace(/\/?$/, "/"));
if (
  !["http:", "https:"].includes(inputBase.protocol) ||
  !["localhost", "127.0.0.1", "[::1]"].includes(inputBase.hostname)
) {
  throw new Error(
    "--input-base must point to a loopback HTTP(S) server serving synthetic review fixtures.",
  );
}
const dest = path.resolve(values["output-base"]);
await fs.mkdir(dest, { recursive: true });

const defaultIds = {
  "3fc0a8e6": "B",
  ca146e90: "A",
  "27d19673": "B",
  "759978a7": "A",
};
const entries = values.outputs?.split(",").map((entry) => entry.split(":"));
if (
  entries?.some(
    ([id, task, extra]) =>
      !/^[a-f0-9]{8}$/.test(id) ||
      !["A", "B"].includes(task) ||
      extra !== undefined,
  )
) {
  throw new Error(
    "--outputs must be comma-separated anonymous-id:task pairs, for example 0123abcd:B.",
  );
}
const ids = entries ? Object.fromEntries(entries) : defaultIds;
const label = values.label || "first-four";
if (!/^[a-z0-9-]+$/.test(label))
  throw new Error(
    "--label must contain only lowercase letters, numbers and hyphens.",
  );
// Do not let Playwright's editable auto-wait turn a pending-edit attempt into
// an edit after completion. Read-only controls receive real keyboard input.
async function attemptPendingEdit(page, text) {
  const field = page.locator("#draft");
  const blocked = await field.evaluate(
    (element) => element.readOnly || element.disabled,
  );
  if (blocked) {
    await field.focus();
    await page.keyboard.press("ControlOrMeta+A");
    await page.keyboard.insertText(text);
  } else {
    await field.fill(text);
  }
  return { blocked, valueAfterAttempt: await field.inputValue() };
}

const browser = await chromium.launch({ channel: "chrome", headless: true });
const results = {
  browser: await browser.version(),
  reviewedAt: new Date().toISOString(),
  outputs: {},
};
for (const [id, task] of Object.entries(ids)) {
  const output = { task, cases: [] };
  results.outputs[id] = output;
  for (const [size, viewport] of Object.entries({
    desktop: { width: 1280, height: 900 },
    mobile: { width: 390, height: 844 },
  })) {
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
        const errors = [];
        page.on("pageerror", (e) => errors.push(String(e)));
        await page.goto(new URL(`${id}/public/`, inputBase).href);
        const result = { size, colorScheme, reducedMotion, errors };
        output.cases.push(result);
        await page.evaluate(() => {
          window.__originalDraft = document.querySelector("#draft");
          window.__originalInspector = document.querySelector("#inspector");
          window.__motionSamples = [];
          const sample = () => {
            let active = document.getAnimations();
            if (active.length)
              window.__motionSamples.push({
                time: performance.now(),
                animations: active.map((a) => ({
                  target: a.effect.target.id || a.effect.target.tagName,
                  time: a.currentTime,
                  duration: a.effect.getTiming().duration,
                  keyframes: a.effect.getKeyframes(),
                  opacity: getComputedStyle(a.effect.target).opacity,
                  transform: getComputedStyle(a.effect.target).transform,
                })),
              });
          };
          window.__sampler = setInterval(sample, 16);
        });
        if (task === "B") {
          await page.locator("#draft").fill("Lamp draft retained");
          await page.locator("#priority").check();
          await page
            .locator("#draft")
            .evaluate((e) => e.setSelectionRange(3, 8));
          await page.locator('[data-record="two"]').focus();
          await page.keyboard.press("Enter");
          await page.waitForTimeout(45);
          await page.screenshot({
            path: `${dest}/${id}-${size}-${colorScheme}-${reducedMotion}-mid.png`,
          });
          result.midState = await page.evaluate(() => ({
            title: document.querySelector("#record-title").textContent,
            draft: document.querySelector("#draft").value,
            priority: document.querySelector("#priority").checked,
            focus: document.activeElement.outerHTML,
          }));
          await page.locator("#draft").fill("Chair draft retained");
          await page.locator("#priority").uncheck();
          for (let i = 0; i < 6; i++) {
            await page
              .locator(`[data-record="${i % 2 ? "two" : "one"}"]`)
              .focus();
            await page.keyboard.press("Enter");
          }
          await page.locator('[data-record="one"]').focus();
          await page.keyboard.press("Enter");
          result.returned = await page.evaluate(() => ({
            draft: document.querySelector("#draft").value,
            priority: document.querySelector("#priority").checked,
            start: document.querySelector("#draft").selectionStart,
            end: document.querySelector("#draft").selectionEnd,
            nodePreserved:
              document.querySelector("#draft") === window.__originalDraft,
            inspectorPreserved:
              document.querySelector("#inspector") ===
              window.__originalInspector,
            pressed: [...document.querySelectorAll("[data-record]")].map(
              (e) => [e.dataset.record, e.getAttribute("aria-pressed")],
            ),
          }));
          await page.waitForTimeout(300);
          await page.locator("#draft").focus();
          await page
            .locator("#draft")
            .evaluate((e) => e.setSelectionRange(2, 4));
          await page.locator('[data-record="one"]').evaluate((e) => e.click());
          result.reselect = await page.locator("#draft").evaluate((e) => ({
            start: e.selectionStart,
            end: e.selectionEnd,
            focus: document.activeElement === e,
          }));
        } else {
          await page.locator("#save").click();
          result.empty = await page.evaluate(() => ({
            feedback: document.querySelector("#feedback").textContent,
            focused: document.activeElement.id,
            stats: window.__repoStats,
          }));
          await page.locator("#draft").fill("First packing note");
          await page.locator("#fail-next").check();
          await page.locator("#save").click();
          result.pending = await page.evaluate(() => ({
            feedback: document.querySelector("#feedback").textContent,
            disabled: document.querySelector("#save").disabled,
            ariaDisabled: document
              .querySelector("#save")
              .getAttribute("aria-disabled"),
            draftReadOnly: document.querySelector("#draft").readOnly,
            focus: document.activeElement.id,
            stats: { ...window.__repoStats },
          }));
          await page.locator("#save").evaluate((e) => {
            e.click();
            e.click();
          });
          await page.waitForTimeout(370);
          result.failed = await page.evaluate(() => ({
            feedback: document.querySelector("#feedback").textContent,
            draft: document.querySelector("#draft").value,
            notes: document.querySelectorAll("#notes li").length,
            failSwitch: document.querySelector("#fail-next").checked,
            stats: { ...window.__repoStats },
          }));
          await page.locator("#fail-next").uncheck();
          await page.locator("#save").click();
          await page.waitForTimeout(350);
          await page.screenshot({
            path: `${dest}/${id}-${size}-${colorScheme}-${reducedMotion}-mid.png`,
          });
          result.saved = await page.evaluate(() => ({
            feedback: document.querySelector("#feedback").textContent,
            draft: document.querySelector("#draft").value,
            notes: [...document.querySelectorAll("#notes li")].map(
              (e) => e.textContent,
            ),
            stats: { ...window.__repoStats },
          }));
          await page.reload();
          result.reloadNotes = await page.locator("#notes").allTextContents();
          await page.locator("#draft").fill("Submitted packing note");
          await page.locator("#save").click();
          result.pendingEditAttempt = await attemptPendingEdit(
            page,
            "Newer unsaved draft",
          );
          await page.waitForTimeout(360);
          result.editedWhilePending = await page.evaluate(() => ({
            feedback: document.querySelector("#feedback").textContent,
            draft: document.querySelector("#draft").value,
          }));
          await page.locator("#draft").fill("Reentered text");
          await page.locator("#save").click();
          result.pendingRevertAttempts = [
            await attemptPendingEdit(page, "Different text"),
            await attemptPendingEdit(page, "Reentered text"),
          ];
          await page.waitForTimeout(360);
          result.revertedWhilePending = await page.evaluate(() => ({
            feedback: document.querySelector("#feedback").textContent,
            draft: document.querySelector("#draft").value,
          }));
        }
        result.render = await page.evaluate(() => ({
          width: innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          bg: getComputedStyle(document.body).backgroundColor,
          ink: getComputedStyle(document.body).color,
          labels: [...document.querySelectorAll("label")].map(
            (e) => e.textContent,
          ),
          animations: window.__motionSamples || [],
        }));
        await page.screenshot({
          path: `${dest}/${id}-${size}-${colorScheme}-${reducedMotion}-final.png`,
          fullPage: true,
        });
        if (reducedMotion === "no-preference") {
          if (task === "B") await page.locator('[data-record="two"]').click();
          else {
            await page.locator("#draft").fill("Setting toggle test");
            await page.locator("#save").click();
            await page.waitForTimeout(330);
          }
          await page.emulateMedia({ reducedMotion: "reduce" });
          result.liveReducedMotionActiveAnimations = await page.evaluate(
            () => document.getAnimations().length,
          );
        }
        const video = page.video();
        await context.close();
        if (video) {
          const filename = `${id}-desktop-playback.webm`;
          await video.saveAs(path.join(dest, filename));
          await video.delete();
          result.video = filename;
        }
      }
  }
}
await browser.close();
await fs.writeFile(
  `${dest}/observations-${label}.json`,
  JSON.stringify(results, null, 2),
);
console.log(
  JSON.stringify(
    Object.fromEntries(
      Object.entries(results.outputs).map(([id, x]) => [
        id,
        {
          task: x.task,
          cases: x.cases.length,
          errors: x.cases.flatMap((c) => c.errors),
          sample: x.cases[0],
        },
      ]),
    ),
    null,
    2,
  ),
);
