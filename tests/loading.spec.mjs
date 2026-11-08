import { test, expect } from "@playwright/test";
const afterOf = (page) => page.frameLocator("#after");

test("loading visibly pulses, preserves row geometry and reveals the same projects", async ({
  page,
}) => {
  await page.goto("./");
  const after = afterOf(page),
    before = page.frameLocator("#before");
  await expect(after.getByRole("list", { name: "Projects" })).toBeVisible();
  const bounds = await after.locator("#content").boundingBox();
  await page
    .getByRole("button", { name: "Load projects", exact: true })
    .click();
  await expect(after.locator(".skeleton")).toBeVisible();
  await expect(before.locator(".project")).toHaveCount(0);
  const opacity1 = await after
    .locator(".skeleton")
    .evaluate((el) => getComputedStyle(el).opacity);
  await page.waitForTimeout(160);
  const opacity2 = await after
    .locator(".skeleton")
    .evaluate((el) => getComputedStyle(el).opacity);
  expect(opacity1).not.toBe(opacity2);
  expect((await after.locator("#content").boundingBox()).height).toBe(
    bounds.height,
  );
  await expect(after.getByRole("list", { name: "Projects" })).toBeVisible();
  await expect(before.locator(".project")).toHaveCount(3);
  expect((await after.locator("#content").boundingBox()).height).toBe(
    bounds.height,
  );
});

test("a slow connection explains the delay and cancellation rejects late completion", async ({
  page,
}) => {
  await page.clock.install();
  await page.goto("./?example=slow");
  const after = afterOf(page);
  await page
    .getByRole("button", { name: "Start a slow load", exact: true })
    .click();
  await expect(after.locator("#notice")).toBeHidden();
  await expect(after.locator("#status")).toHaveText("Loading projects…");
  await page.clock.runFor(1400);
  await expect(after.locator("#notice")).toContainText("taking longer");
  await expect(page.frameLocator("#before").locator("#notice")).toBeHidden();
  await after.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(after.getByRole("button", { name: "Load again" })).toBeFocused();
  await page.clock.runFor(7000);
  await expect(after.locator("#status")).toHaveText(
    "Cancelled. Your projects are unchanged.",
  );
  await expect(after.locator(".project")).toHaveCount(3);
});

test("offline retries stay honest and reconnection preserves a draft", async ({
  page,
}) => {
  await page.goto("./?example=offline");
  const after = afterOf(page),
    note = after.getByLabel("Project note");
  await note.fill("Keep my local draft");
  await page
    .getByRole("button", { name: "Lose connection", exact: true })
    .click();
  await expect(after.locator(".project")).toHaveCount(3);
  await expect(page.frameLocator("#before").locator(".project")).toHaveCount(0);
  await after.getByRole("button", { name: "Try again" }).click();
  await expect(after.locator("#status")).toContainText("Offline.");
  await expect(note).toHaveValue("Keep my local draft");
  await page.getByRole("button", { name: "Restore connection" }).click();
  await expect(after.locator("#status")).toContainText("Back online.");
  await expect(note).toHaveValue("Keep my local draft");
});

test("upload pause freezes progress, resume completes, and cancel rejects stale chunks", async ({
  page,
}) => {
  await page.clock.install();
  await page.goto("./?example=upload");
  const after = afterOf(page);
  await page
    .getByRole("button", { name: "Upload a demo file", exact: true })
    .click();
  await expect(after.locator("#status")).toHaveText("Uploading the demo file…");
  await page.clock.runFor(600);
  const progress = after.getByRole("progressbar", { name: "Upload progress" });
  expect(Number(await progress.getAttribute("aria-valuenow"))).toBeGreaterThan(
    0,
  );
  await after.getByRole("button", { name: "Pause", exact: true }).click();
  const value = await progress.getAttribute("aria-valuenow");
  await page.clock.runFor(1200);
  await expect(progress).toHaveAttribute("aria-valuenow", value);
  await after.getByRole("button", { name: "Resume", exact: true }).click();
  await page.clock.runFor(4000);
  await expect(progress).toHaveAttribute("aria-valuenow", "100");
  await expect(after.locator("#status")).toContainText("Upload complete.");
  await page
    .getByRole("button", { name: "Upload a demo file", exact: true })
    .click();
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

test("repeated starts replace work and changing scenarios cannot leak stale feedback", async ({
  page,
}) => {
  await page.clock.install();
  await page.goto("./?example=slow");
  const after = afterOf(page);
  await page
    .getByRole("button", { name: "Start a slow load", exact: true })
    .click();
  await expect(after.locator("#status")).toHaveText("Loading projects…");
  await page.clock.runFor(1400);
  await expect(after.locator("#notice")).toBeVisible();
  await page
    .getByRole("button", { name: "Start a slow load", exact: true })
    .click();
  await expect(after.locator("#notice")).toBeHidden();
  await page.clock.runFor(5100);
  await expect(after.locator(".skeleton")).toBeVisible();
  await page
    .getByRole("button", { name: "Loading content", exact: true })
    .click();
  await expect(after.locator(".project")).toHaveCount(3);
  await page.clock.runFor(7000);
  await expect(page.locator("#review-status")).toHaveText(
    "Ready. Start the example to compare both sides.",
  );
});

test("system and review reduced motion remove decorative loading movement", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("./");
  const after = afterOf(page);
  await page
    .getByRole("button", { name: "Load projects", exact: true })
    .click();
  await expect(after.locator(".skeleton")).toBeVisible();
  expect(
    await after
      .locator(".skeleton")
      .evaluate((el) => getComputedStyle(el).animationName),
  ).toBe("none");
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.getByLabel("Reduce motion", { exact: true }).check();
  await expect
    .poll(() =>
      after
        .locator(".skeleton")
        .evaluate((el) => getComputedStyle(el).animationName),
    )
    .toBe("none");
});

test("mobile opens the improved example and switches versions without restarting", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("./?example=offline");
  const after = afterOf(page);
  await after.getByLabel("Project note").fill("My mobile draft");
  await page
    .getByRole("button", { name: "Lose connection", exact: true })
    .click();
  const versions = page.getByRole("group", { name: "Preview version" });
  await versions.getByRole("button", { name: "Before", exact: true }).click();
  await expect(page.locator("#before")).toBeVisible();
  await versions.getByRole("button", { name: "After", exact: true }).click();
  await expect(after.getByLabel("Project note")).toHaveValue("My mobile draft");
  await expect(after.locator("#status")).toContainText("Offline.");
});
