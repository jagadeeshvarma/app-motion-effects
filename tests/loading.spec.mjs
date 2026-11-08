import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { examples } from "../docs/examples.js";
const afterOf = (page) => page.frameLocator("#after");
async function open(page, id = "loading") {
  await page.goto(`./?example=${id}#playground`);
  await expect(page.locator("#replay")).toBeEnabled();
  await expect(afterOf(page).locator("#demo")).toBeVisible();
}
async function compare(page) {
  await page
    .getByRole("group", { name: "Preview mode" })
    .getByRole("button", { name: "Compare", exact: true })
    .click();
}

test("hero explains the skill and examples open a full-viewport workspace", async ({
  page,
}) => {
  await page.goto("./");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Better motion.Still your app.",
  );
  await expect(
    page.getByRole("link", { name: "Download skill", exact: true }),
  ).toHaveAttribute(
    "href",
    /releases\/download\/v2.0.0\/app-motion-effects-2.0.0.zip$/,
  );
  await page
    .getByRole("link", { name: "See the examples", exact: true })
    .click();
  const viewport = page.viewportSize(),
    box = await page.locator("#playground").boundingBox();
  expect(Math.abs(box.y)).toBeLessThan(2);
  expect(box.height).toBe(viewport.height);
  const pane = await page.locator("#after").boundingBox();
  expect(pane.width).toBeGreaterThan(viewport.width * 0.65);
  expect(pane.height).toBeGreaterThan(viewport.height * 0.48);
  await expect(
    page
      .getByRole("navigation", { name: "Choose an example" })
      .getByRole("button"),
  ).toHaveCount(10);
  expect(await page.locator("body").innerText()).not.toMatch(/[↗→↓]/);
});

test("loading shows real intermediate animation without moving project rows", async ({
  page,
}) => {
  await open(page);
  await compare(page);
  const after = afterOf(page),
    before = page.frameLocator("#before");
  const original = await after.locator("#content").boundingBox();
  await page.locator("#replay").click();
  await expect(after.locator(".skeleton")).toBeVisible();
  await expect(before.locator(".project")).toHaveCount(0);
  const first = await after
    .locator(".skeleton")
    .evaluate((el) => getComputedStyle(el).opacity);
  await page.waitForTimeout(160);
  expect(
    await after
      .locator(".skeleton")
      .evaluate((el) => getComputedStyle(el).opacity),
  ).not.toBe(first);
  await expect(
    after.getByRole("list", { name: "Projects", exact: true }),
  ).toBeVisible();
  const final = await after.locator("#content").boundingBox();
  expect(final.height).toBe(original.height);
  expect(Math.abs(final.y - original.y)).toBeLessThan(2);
});

test("indeterminate loading rotates and cancellation prevents late success", async ({
  page,
}) => {
  await open(page, "loader");
  const after = afterOf(page);
  await page.locator("#replay").click();
  await expect(after.locator(".spinner")).toBeVisible();
  const first = await after
    .locator(".spinner")
    .evaluate((el) => getComputedStyle(el).transform);
  await page.waitForTimeout(120);
  expect(
    await after
      .locator(".spinner")
      .evaluate((el) => getComputedStyle(el).transform),
  ).not.toBe(first);
  await expect(after.getByRole("progressbar")).toHaveCount(0);
  await after.getByRole("button", { name: "Cancel", exact: true }).click();
  await page.waitForTimeout(3900);
  await expect(after.locator("#status")).toHaveText("Preparation cancelled.");
  await expect(
    after.getByText("Your preview is ready", { exact: true }),
  ).toHaveCount(0);
});

test("slow loading explains the delay, supports cancellation and retains keyboard focus", async ({
  page,
}) => {
  await page.clock.install();
  await open(page, "slow");
  const after = afterOf(page);
  await page.locator("#replay").click();
  await expect(after.locator("#status")).toHaveText("Loading projects…");
  await page.clock.runFor(1400);
  await expect(after.locator("#notice")).toContainText(
    "This is taking longer.",
  );
  await after.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(
    after.getByRole("button", { name: "Load again", exact: true }),
  ).toBeFocused();
  await page.clock.runFor(7000);
  await expect(after.locator("#status")).toHaveText(
    "Cancelled. Your projects are unchanged.",
  );
});

test("connection loss retains content and the note, with honest retry and recovery", async ({
  page,
}) => {
  await open(page, "offline");
  await compare(page);
  const after = afterOf(page),
    note = after.getByLabel("Project note");
  await note.fill("Keep my draft");
  await page.locator("#replay").click();
  await expect(after.locator(".project")).toHaveCount(3);
  await expect(page.frameLocator("#before").locator(".project")).toHaveCount(0);
  await after.getByRole("button", { name: "Try again" }).click();
  await expect(after.locator("#status")).toContainText("Offline.");
  await expect(note).toHaveValue("Keep my draft");
  await page.getByRole("button", { name: "Restore connection" }).click();
  await expect(after.locator("#status")).toContainText("Back online.");
  await expect(note).toHaveValue("Keep my draft");
});

test("upload progress freezes while paused, resumes to completion and rejects cancelled work", async ({
  page,
}) => {
  await page.clock.install();
  await open(page, "upload");
  const after = afterOf(page);
  await page.locator("#replay").click();
  await expect(after.locator("#status")).toHaveText("Uploading the demo file…");
  await page.clock.runFor(700);
  const progress = after.getByRole("progressbar", { name: "Upload progress" });
  expect(Number(await progress.getAttribute("aria-valuenow"))).toBeGreaterThan(
    0,
  );
  await after.getByRole("button", { name: "Pause", exact: true }).click();
  const paused = await progress.getAttribute("aria-valuenow");
  await page.clock.runFor(1500);
  await expect(progress).toHaveAttribute("aria-valuenow", paused);
  await after.getByRole("button", { name: "Resume", exact: true }).click();
  await page.clock.runFor(4000);
  await expect(progress).toHaveAttribute("aria-valuenow", "100");
  await expect(after.locator("#status")).toContainText("Upload complete.");
  await page.locator("#replay").click();
  await expect(after.locator("#status")).toHaveText("Uploading the demo file…");
  await page.clock.runFor(300);
  await after.getByRole("button", { name: "Cancel", exact: true }).click();
  const cancelled = await progress.getAttribute("aria-valuenow");
  await page.clock.runFor(6000);
  await expect(progress).toHaveAttribute("aria-valuenow", cancelled);
  await expect(after.locator("#status")).toHaveText(
    "Upload cancelled. Nothing was uploaded.",
  );
});

test("saving has a stable control, visible pending animation and confirmed check", async ({
  page,
}) => {
  await open(page, "save");
  const after = afterOf(page),
    input = after.getByLabel("Project title"),
    button = after.locator("#save");
  await input.fill("Spring website");
  const original = await button.boundingBox();
  await input.press("Enter");
  await expect(button).toHaveAttribute("aria-disabled", "true");
  await expect(button.locator(".spinner")).toBeVisible();
  await expect(button).toHaveText("Saved");
  await expect(button.locator(".check")).toBeVisible();
  await expect(after.locator("#save-summary")).toHaveText(
    "Your project title is saved.",
  );
  await expect(input).toHaveValue("Spring website");
  expect(
    Math.abs((await button.boundingBox()).width - original.width),
  ).toBeLessThan(2);
});

test("save drafts and errors survive mode changes, editing and retries", async ({
  page,
}) => {
  await open(page, "save");
  const after = afterOf(page),
    field = after.getByLabel("Project title");
  await field.fill("Snapshot A");
  await after
    .getByRole("button", { name: "Save changes", exact: true })
    .click();
  await field.fill("New draft B");
  await expect(after.locator("#save-summary")).toHaveText(
    "Earlier title saved. New edits are not saved.",
  );
  await expect(field).toBeFocused();
  await page.getByRole("button", { name: "Before", exact: true }).click();
  await page.getByRole("button", { name: "After", exact: true }).click();
  await expect(field).toHaveValue("New draft B");
  await after.getByLabel("Fail next save").check();
  await after
    .getByRole("button", { name: "Save changes", exact: true })
    .click();
  await expect(after.locator("#save-summary")).toContainText("Could not save.");
  await field.fill("Retry draft C");
  await expect(after.locator("#save-summary")).toContainText("Could not save.");
  await after.getByRole("button", { name: "Try again", exact: true }).click();
  await expect(
    after.getByRole("button", { name: "Saved", exact: true }),
  ).toBeVisible();
  await expect(field).toHaveValue("Retry draft C");
});

test("filtering animates surviving rows and rapid changes keep the correct collection", async ({
  page,
}) => {
  await open(page, "filter");
  const after = afterOf(page);
  await after.getByRole("button", { name: "Complete", exact: true }).click();
  await expect(after.locator(".project:visible")).toHaveCount(2);
  expect(
    await after
      .locator(".project:visible")
      .evaluateAll((rows) =>
        rows.some((row) =>
          row
            .getAnimations()
            .some((animation) => animation.playState === "running"),
        ),
      ),
  ).toBe(true);
  await after.getByRole("button", { name: "All", exact: true }).click();
  await after.getByRole("button", { name: "In progress", exact: true }).click();
  await expect(after.locator(".project:visible")).toHaveCount(3);
  await expect(
    after.getByRole("button", { name: "In progress", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
});

test("notification stays while focused, then fades and dismisses without covering its action", async ({
  page,
}) => {
  await page.clock.install();
  await open(page, "toast");
  const after = afterOf(page);
  await page.locator("#replay").click();
  const toast = after.locator("#toast");
  await expect(toast).toBeVisible();
  const close = after.getByRole("button", { name: "Dismiss notification" });
  await close.focus();
  await page.clock.runFor(5000);
  await expect(toast).toBeVisible();
  const notificationBox = await toast.boundingBox(),
    buttonBox = await after
      .getByRole("button", { name: "Save project", exact: true })
      .boundingBox();
  expect(notificationBox.y + notificationBox.height).toBeLessThan(buttonBox.y);
  await after
    .getByRole("button", { name: "Save project", exact: true })
    .focus();
  await page.clock.runFor(4500);
  await expect(toast).toBeHidden();
});

test("side panel animates, supports Escape and keeps its note and focus", async ({
  page,
}) => {
  await open(page, "panel");
  const after = afterOf(page);
  await page.locator("#replay").click();
  await expect(after.getByRole("dialog")).toBeVisible();
  await expect(
    after.getByRole("button", { name: "Close details" }),
  ).toBeFocused();
  await after.getByLabel("Project note").fill("Keep this detail");
  await after.getByLabel("Project note").press("Escape");
  await expect(after.getByRole("dialog")).toBeHidden();
  await expect(
    after.getByRole("button", { name: "Open details", exact: true }),
  ).toBeFocused();
  await after
    .getByRole("button", { name: "Open details", exact: true })
    .click();
  await expect(after.getByLabel("Project note")).toHaveValue(
    "Keep this detail",
  );
});

test("tabs have keyboard selection, a moving indicator and preserved input", async ({
  page,
}) => {
  await open(page, "tabs");
  const after = afterOf(page);
  await after.getByLabel("Project note").fill("My tab draft");
  const overview = after.getByRole("tab", { name: "Overview", exact: true });
  await overview.focus();
  await page.keyboard.press("ArrowRight");
  await expect(
    after.getByRole("tab", { name: "Activity", exact: true }),
  ).toBeFocused();
  await expect(
    after.getByRole("tab", { name: "Activity", exact: true }),
  ).toHaveAttribute("aria-selected", "true");
  await page.keyboard.press("ArrowLeft");
  await expect(after.getByLabel("Project note")).toHaveValue("My tab draft");
});

for (const width of [320, 390, 768, 1440, 1920])
  test(`all ten examples fit the ${width}px workbench`, async ({ page }) => {
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.setViewportSize({ width, height: width < 701 ? 844 : 1000 });
    await open(page);
    for (const item of examples) {
      if (width < 701)
        await page
          .getByRole("combobox", { name: "Choose an example", exact: true })
          .selectOption(item.id);
      else
        await page
          .getByRole("navigation", { name: "Choose an example" })
          .getByRole("button", { name: item.name, exact: true })
          .click();
      await expect(page.locator("#replay")).toBeEnabled();
      await expect(page.locator("#example-title")).toHaveText(item.name);
      const stage = await page.locator("#stage").boundingBox();
      expect(stage.height).toBeGreaterThan(width < 701 ? 240 : 400);
      expect(stage.y + stage.height).toBeLessThanOrEqual(
        page.viewportSize().height + 1,
      );
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      expect(
        await page
          .locator("#after")
          .evaluate(
            (frame) =>
              frame.contentDocument.documentElement.scrollWidth <=
              frame.contentWindow.innerWidth,
          ),
      ).toBe(true);
      // Every idle demo and its controls remain reachable inside the full-screen stage.
      await expect(afterOf(page).locator("#demo")).toBeVisible();
    }
    expect(errors).toEqual([]);
  });

test("system and review reduced motion stop decorative animation without blocking results", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await open(page, "loader");
  const after = afterOf(page);
  await page.locator("#replay").click();
  await expect(after.locator(".spinner")).toBeVisible();
  expect(
    await after
      .locator(".spinner")
      .evaluate((el) => getComputedStyle(el).animationName),
  ).toBe("none");
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.getByLabel("Reduce motion", { exact: true }).check();
  await expect
    .poll(() =>
      after
        .locator(".spinner")
        .evaluate((el) => getComputedStyle(el).animationName),
    )
    .toBe("none");
  await expect(after.locator("#status")).toHaveText("Preview ready.", {
    timeout: 6000,
  });
});

test("full prompt is identical in the page, README and a real clipboard copy", async ({
  page,
  context,
}) => {
  const expected = readFileSync(
    new URL("../docs/full-repo-prompt.txt", import.meta.url),
    "utf8",
  );
  const readme = readFileSync(new URL("../README.md", import.meta.url), "utf8");
  expect(readme).toContain("```text\n" + expected + "```");
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.goto("./#full-repo-prompt");
  await expect(
    page.getByLabel("Full-repository audit and implementation prompt"),
  ).toHaveValue(expected);
  await page
    .getByRole("button", { name: "Copy full prompt", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Copied", exact: true }),
  ).toBeVisible();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(
    expected,
  );
  await expect(page.locator("#copy-status")).toContainText(
    "Full prompt copied.",
  );
});

test("blocked clipboard selects the prompt and reports the manual fallback honestly", async ({
  page,
}) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "clipboard", {
      value: {
        writeText: async () => {
          throw new Error("Denied");
        },
      },
    });
  });
  await page.goto("./#full-repo-prompt");
  await page
    .getByRole("button", { name: "Copy full prompt", exact: true })
    .click();
  await expect(page.locator("#copy-status")).toContainText(
    "Automatic copy is unavailable.",
  );
  const selection = await page.locator("#full-prompt").evaluate((el) => ({
    start: el.selectionStart,
    end: el.selectionEnd,
    length: el.value.length,
  }));
  expect(selection.start).toBe(0);
  expect(selection.end).toBe(selection.length);
});

test("switching modes or reducing motion preserves a live draft", async ({
  page,
}) => {
  await open(page, "offline");
  const after = afterOf(page);
  await after.getByLabel("Project note").fill("My current draft");
  await page.getByRole("button", { name: "Before", exact: true }).click();
  await page.getByRole("button", { name: "After", exact: true }).click();
  await page.getByLabel("Reduce motion", { exact: true }).check();
  await expect(after.getByLabel("Project note")).toHaveValue(
    "My current draft",
  );
});

for (const [width, height] of [
  [320, 844],
  [390, 844],
  [1280, 720],
])
  test(`connection recovery keeps the note and retry inside ${width}x${height}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height });
    await open(page, "offline");
    await page.locator("#replay").click();
    const after = afterOf(page);
    await expect(after.locator("#notice")).toBeVisible();
    for (const selector of ["#project-note", "#actions button"])
      expect(
        await after.locator(selector).evaluate((el) => {
          const box = el.getBoundingClientRect();
          return (
            box.top >= 0 && box.bottom <= innerHeight && box.right <= innerWidth
          );
        }),
      ).toBe(true);
    await after.getByLabel("Project note").fill("My recovery draft");
    await after.getByRole("button", { name: "Try again", exact: true }).click();
    await expect(after.locator("#status")).toContainText("Offline.");
    await expect(after.getByLabel("Project note")).toHaveValue(
      "My recovery draft",
    );
  });
