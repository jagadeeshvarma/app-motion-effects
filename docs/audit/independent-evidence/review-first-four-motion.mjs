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
    "Usage: node docs/audit/independent-evidence/review-first-four-motion.mjs --input-base http://127.0.0.1:8000/ --output-base ./review-evidence [--outputs 0123abcd:B] [--label additional]",
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
const browser = await chromium.launch({ channel: "chrome", headless: true });
let data = {};
for (const [id, task] of Object.entries(ids)) {
  data[id] = [];
  for (const reducedMotion of ["no-preference", "reduce"]) {
    const ctx = await browser.newContext({
      viewport: { width: 390, height: 844 },
      colorScheme: "dark",
      reducedMotion,
    });
    const page = await ctx.newPage();
    await page.goto(new URL(`${id}/public/`, inputBase).href);
    await page.evaluate(() => {
      window.__samples = [];
      window.__timer = setInterval(() => {
        for (const a of document.getAnimations()) {
          const t = a.effect.target;
          window.__samples.push({
            time: performance.now(),
            target: t.id || t.tagName,
            progress: a.effect.getComputedTiming().progress,
            opacity: getComputedStyle(t).opacity,
            transform: getComputedStyle(t).transform,
            duration: a.effect.getTiming().duration,
          });
        }
      }, 8);
    });
    if (task === "B") await page.locator('[data-record="two"]').click();
    else {
      await page.locator("#draft").fill("Motion sample");
      await page.locator("#fail-next").check();
      await page.locator("#save").click();
      await page.waitForTimeout(350);
      await page.screenshot({
        path: `${dest}/${id}-mobile-dark-${reducedMotion}-error.png`,
      });
      await page.locator("#fail-next").uncheck();
      await page.locator("#save").click();
    }
    await page.waitForTimeout(600);
    const row = {
      reducedMotion,
      samples: await page.evaluate(() => window.__samples),
      feedback: await page.locator("#feedback").textContent(),
    };
    if (reducedMotion === "no-preference") {
      if (task === "B") await page.locator('[data-record="one"]').click();
      else {
        await page.locator("#draft").fill("Live setting");
        await page.locator("#save").click();
        await page.waitForTimeout(325);
      }
      await page.emulateMedia({ reducedMotion: "reduce" });
      await page.waitForTimeout(40);
      row.liveReducedAfter40ms = await page.evaluate(() => ({
        matches: matchMedia("(prefers-reduced-motion:reduce)").matches,
        active: document.getAnimations().length,
      }));
    }
    data[id].push(row);
    await ctx.close();
  }
}
await browser.close();
await fs.writeFile(
  path.join(
    dest,
    label === "first-four"
      ? "motion-followup.json"
      : `motion-followup-${label}.json`,
  ),
  JSON.stringify(data, null, 2),
);
console.log(
  JSON.stringify(
    Object.fromEntries(
      Object.entries(data).map(([id, rows]) => [
        id,
        rows.map((r) => ({
          ...r,
          samples: {
            count: r.samples.length,
            targets: [...new Set(r.samples.map((s) => s.target))],
            opacities: [...new Set(r.samples.map((s) => s.opacity))].slice(
              0,
              5,
            ),
            transforms: [...new Set(r.samples.map((s) => s.transform))].slice(
              0,
              5,
            ),
          },
        })),
      ]),
    ),
    null,
    2,
  ),
);
