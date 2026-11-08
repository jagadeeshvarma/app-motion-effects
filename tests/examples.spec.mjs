import { test, expect } from "@playwright/test";

test("save status is truthful for an older snapshot and preserves a newer draft", async ({
  page,
}) => {
  await page.goto("./demos/dispatch-after.html");
  const field = page.getByLabel("Handling note");
  await field.fill("Snapshot A");
  await page.getByRole("button", { name: "Save note" }).click();
  await expect(page.locator("form")).toHaveAttribute("aria-busy", "true");
  await field.fill("Newer draft B");
  await expect(page.locator("#feedback")).toHaveText(
    "Earlier note saved. New changes are not saved.",
  );
  await expect(field).toHaveValue("Newer draft B");
  await expect(field).toBeFocused();
  expect(await page.evaluate(() => window.demoSavedValue())).toBe("Snapshot A");
});

test("failure persists, repeated saves are guarded, and retry succeeds", async ({
  page,
}) => {
  await page.goto("./demos/dispatch-after.html");
  const button = page.getByRole("button", { name: "Save note" }),
    field = page.getByLabel("Handling note");
  await page.getByLabel("Simulate next save failure").check();
  await button.click();
  await page.evaluate(() => document.querySelector("form").requestSubmit());
  await expect(page.locator("#feedback")).toContainText("Save failed");
  await field.fill("Retry without losing my draft");
  await expect(page.locator("#feedback")).toContainText("Save failed");
  await button.click();
  await expect(page.locator("#feedback")).toHaveText("Handling note saved");
  await expect(field).toHaveValue("Retry without losing my draft");
});

test("canvas reset plays intermediate positions, is interruptible and retains caption", async ({
  page,
}) => {
  await page.goto("./demos/studio-after.html");
  await page.getByLabel("Composition caption").fill("Keep this caption");
  const art = page.locator("#art");
  await art.focus();
  for (let i = 0; i < 20; i++) await page.keyboard.press("ArrowRight");
  // Sample browser animation frames rather than relying on a screenshot or timer race.
  const positions = await page.evaluate(async () => {
    const art = document.querySelector("#art"),
      xs = [];
    document.querySelector("#reset").click();
    for (let i = 0; i < 18; i++) {
      await new Promise(requestAnimationFrame);
      xs.push(Number(art.getAttribute("x")));
    }
    return xs;
  });
  expect(positions.some((x) => x > 100 && x < 300)).toBe(true);
  await expect(art).toHaveAttribute("x", "100");
  await art.focus();
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("Shift+ArrowRight");
  await expect(art).toHaveAttribute("x", "111");
  const interrupted = await page.evaluate(async () => {
    document.querySelector("#reset").click();
    await new Promise(requestAnimationFrame);
    document
      .querySelector("#art")
      .dispatchEvent(
        new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }),
      );
    const x = window.demoPosition().x;
    await new Promise((resolve) => setTimeout(resolve, 240));
    return { x, after: window.demoPosition().x };
  });
  expect(interrupted.x).toBeGreaterThan(100);
  expect(interrupted.after).toBe(interrupted.x);
  await expect(page.getByLabel("Composition caption")).toHaveValue(
    "Keep this caption",
  );
});

test("system reduced motion keeps static feedback and immediate reset", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("./demos/studio-after.html");
  await page.locator("#art").focus();
  await page.keyboard.press("ArrowRight");
  expect(
    await page.evaluate(() => {
      document.querySelector("#reset").click();
      return window.demoPosition().x;
    }),
  ).toBe(100);
  await page.goto("./demos/dispatch-after.html");
  await page.getByRole("button", { name: "Save note" }).click();
  expect(
    await page
      .locator("#feedback")
      .evaluate((el) => getComputedStyle(el).animationName),
  ).toBe("none");
});

test("review controls preserve drafts and apply reduced motion to live frames", async ({
  page,
}) => {
  await page.goto("./");
  const after = page.frameLocator("#after");
  await after
    .getByLabel("Composition caption")
    .fill("Persistent gallery draft");
  await page.getByLabel("Reduce motion", { exact: true }).check();
  await page.getByLabel("Narrow preview").check();
  await expect(after.getByLabel("Composition caption")).toHaveValue(
    "Persistent gallery draft",
  );
  await after.locator("#art").focus();
  await page.keyboard.press("ArrowRight");
  expect(
    await page.locator("#after").evaluate((el) => {
      el.contentDocument.querySelector("#reset").click();
      return el.contentWindow.demoPosition().x;
    }),
  ).toBe(100);
  await page
    .getByRole("button", { name: "Business workflow", exact: true })
    .click();
  await expect(after.getByLabel("Handling note")).toBeVisible();
  await page.getByRole("button", { name: /Compare save/ }).click();
  await expect(after.locator("#feedback")).toHaveText("Handling note saved");
});

for (const width of [390, 768, 1440])
  test(`gallery and both examples fit ${width}px without horizontal overflow`, async ({
    page,
  }) => {
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.setViewportSize({ width, height: 900 });
    await page.goto("./");
    for (const name of ["Creative canvas", "Business workflow"]) {
      await page.getByRole("button", { name, exact: true }).click();
      await expect(page.frameLocator("#after").locator("main")).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      for (const id of ["before", "after"])
        expect(
          await page
            .locator(`#${id}`)
            .evaluate(
              (el) =>
                el.contentDocument.querySelector("main").getBoundingClientRect()
                  .bottom <= el.clientHeight,
            ),
        ).toBe(true);
      for (const id of ["before", "after"])
        expect(
          await page
            .locator(`#${id}`)
            .evaluate(
              (el) =>
                el.contentDocument.documentElement.scrollWidth <=
                el.contentWindow.innerWidth,
            ),
        ).toBe(true);
    }
    expect(errors).toEqual([]);
  });

test("touch dragging tracks the pointer, releases cleanly and preserves caption", async ({
  browser,
}) => {
  const context = await browser.newContext({
    hasTouch: true,
    viewport: { width: 390, height: 844 },
  });
  const page = await context.newPage();
  await page.goto("./demos/studio-after.html");
  const client = await context.newCDPSession(page);
  const bounds = await page.locator("#art").boundingBox();
  const x = bounds.x + bounds.width / 2,
    y = bounds.y + bounds.height / 2;
  await client.send("Input.dispatchTouchEvent", {
    type: "touchStart",
    touchPoints: [{ x, y }],
  });
  await client.send("Input.dispatchTouchEvent", {
    type: "touchMove",
    touchPoints: [{ x: x + 40, y: y + 20 }],
  });
  await expect
    .poll(() => page.evaluate(() => window.demoPosition().x))
    .toBeGreaterThan(100);
  await client.send("Input.dispatchTouchEvent", {
    type: "touchEnd",
    touchPoints: [],
  });
  await expect(page.locator("#art")).not.toHaveClass(/dragging/);
  await expect(page.getByLabel("Composition caption")).toHaveValue(
    "Evening study",
  );
  await context.close();
});
