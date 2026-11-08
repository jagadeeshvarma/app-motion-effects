const examples = {
  loading: {
    title: "A clearer wait.",
    benefit:
      "A blank area gives no clue what is coming. A skeleton holds the layout while the same content loads.",
    instructions:
      "Click Load projects. Both sides take 2.4 seconds. Watch the right side keep its shape, then reveal the content.",
    before: "An empty wait",
    after: "A layout that stays in place",
    replay: "Load projects",
    name: "Loading content",
    notice:
      "The wait is not shorter. It is easier to understand, and the project rows do not jump when the content arrives.",
    mechanism:
      "CSS skeleton pulse and a 180 ms reveal. Reduced motion keeps a static skeleton. No animation library.",
  },
  slow: {
    title: "When the connection is slow.",
    benefit:
      "Silence can look like a broken page. A delayed message explains what is happening and gives you a way out.",
    instructions:
      "Click Start a slow load. Both sides take six seconds. After 1.3 seconds, the improved version explains the wait. Try Cancel, or let it finish.",
    before: "No explanation",
    after: "Reassurance and a way out",
    replay: "Start a slow load",
    name: "Slow connection",
    notice:
      "The message appears only when the wait becomes unusually long. Cancelling stops the simulated request; a late response cannot overwrite the screen.",
    mechanism:
      "The same skeleton, a delayed status message and cancellation tied to request identity. No made-up percentage for an unknown wait.",
  },
  offline: {
    title: "Losing the connection should not hide your work.",
    benefit:
      "Keep the last loaded content visible, explain the problem and preserve the note while reconnecting.",
    instructions:
      "Type a note on the right, then click Lose connection. Try again while offline, or use Restore connection above to recover.",
    before: "An error replaces the projects",
    after: "Content and draft stay visible",
    replay: "Lose connection",
    name: "Lost connection",
    notice:
      "On the right, the last loaded projects stay visible and your note survives. Restore connection updates the projects without resetting the note.",
    mechanism:
      "Persistent inline status, cached fixture content and an explicit retry. A short reveal marks confirmed recovery; no fake online success.",
  },
  upload: {
    title: "Progress you can understand and control.",
    benefit:
      "Show how much has finished. Let someone pause or cancel instead of leaving them with an indefinite uploading message.",
    instructions:
      "Click Upload a demo file. On the right, watch progress advance, pause it, resume it and let it complete. Nothing is actually uploaded.",
    before: "An indefinite uploading message",
    after: "Progress, pause and confirmation",
    replay: "Upload a demo file",
    name: "Uploading a file",
    notice:
      "The progress follows known chunks in this simulation. Pause holds that value. Completion appears only after every chunk has finished.",
    mechanism:
      "An accessible progress bar, a short linear fill transition and a drawn completion check. Reduced motion keeps the accurate values without decorative movement.",
  },
  dispatch: {
    title: "Know which changes were saved.",
    benefit:
      "A save can finish while you are still typing. The status should explain exactly what is saved and what is still a draft.",
    instructions:
      "Edit a note and click Save both notes. Keep typing on the right while it saves. You can also simulate a failure and retry inside either preview.",
    before: "A generic saved message",
    after: "Accurate draft and save feedback",
    replay: "Save both notes",
    name: "Saving changes",
    notice:
      "On the right, editing during a save leaves a clear unsaved-changes message. Errors stay beside the action until a successful retry.",
    mechanism:
      "A quiet CSS opacity pulse, stable button width and state-aware copy. The form stays mounted, preserving drafts and focus.",
  },
  studio: {
    title: "Follow where an object goes.",
    benefit:
      "A short return path makes a reset easier to follow. Dragging still reacts immediately and the return can be interrupted.",
    instructions:
      "Click Reset both objects to move and reset the same object on each side. Or drag the object yourself, then click Reset object. Your caption stays.",
    before: "An instant jump",
    after: "A short continuous return",
    replay: "Reset both objects",
    name: "Moving an object",
    notice:
      "The object on the right returns in 180 ms. Grab it or press an arrow key during that return: it responds immediately, without waiting for playback.",
    mechanism:
      "Original SVG and requestAnimationFrame. No overshoot or new engine. Reduced motion returns immediately.",
  },
};
let active = "loading";
const frames = [
  document.querySelector("#before"),
  document.querySelector("#after"),
];
const reduce = document.querySelector("#reduce");
const status = document.querySelector("#review-status");
const replay = document.querySelector("#replay");
const reconnect = document.querySelector("#reconnect");
function send(action) {
  for (const frame of frames)
    if (frame.dataset.ready === "true")
      frame.contentWindow.postMessage(
        { type: "app-motion-demo", action, reduced: reduce.checked },
        location.origin,
      );
}
function fitFrames() {
  const heights = frames
    .filter((frame) => frame.offsetParent !== null)
    .map((frame) => {
      const main = frame.contentDocument?.querySelector("main");
      return main
        ? Math.ceil(
            main.getBoundingClientRect().bottom +
              frame.contentWindow.scrollY +
              24,
          )
        : 0;
    });
  const height = Math.max(
    { loading: 450, slow: 550, offline: 650, upload: 430 }[active] || 0,
    ...heights,
  );
  for (const frame of frames)
    if (frame.style.height !== `${height}px`)
      frame.style.height = `${height}px`;
}
function initializeFrame(frame) {
  frame.reviewObserver?.disconnect();
  const main = frame.contentDocument?.querySelector("main");
  if (!main || frame.contentDocument.URL !== frame.src) return;
  frame.dataset.ready = "true";
  frame.reviewObserver = new ResizeObserver(fitFrames);
  frame.reviewObserver.observe(main);
  fitFrames();
  frame.contentWindow.postMessage(
    { type: "app-motion-demo", action: "settings", reduced: reduce.checked },
    location.origin,
  );
  replay.disabled = !frames.every((item) => item.dataset.ready === "true");
}
for (const frame of frames) {
  frame.addEventListener("load", () => initializeFrame(frame));
  if (
    frame.contentDocument?.readyState === "complete" &&
    frame.contentDocument.querySelector("main")
  )
    initializeFrame(frame);
}
function chooseExample(key, updateHistory = true) {
  if (!examples[key]) key = "loading";
  if (key === active) return;
  active = key;
  const e = examples[active];
  replay.disabled = true;
  reconnect.hidden = active !== "offline";
  reconnect.disabled = true;
  for (const button of document.querySelectorAll("[data-example]"))
    button.setAttribute(
      "aria-pressed",
      String(button.dataset.example === active),
    );
  for (const [id, key] of [
    ["example-title", "title"],
    ["example-benefit", "benefit"],
    ["instructions", "instructions"],
    ["before-label", "before"],
    ["after-label", "after"],
    ["notice", "notice"],
    ["mechanism", "mechanism"],
  ])
    document.getElementById(id).textContent = e[key];
  replay.textContent = e.replay;
  for (const [i, variant] of ["before", "after"].entries()) {
    frames[i].dataset.ready = "false";
    frames[i].title = `${e.name} ${variant} improvement`;
    const shared = ["loading", "slow", "offline", "upload"].includes(active);
    frames[i].src = shared
      ? `demos/feedback.html?scenario=${active}&variant=${variant}`
      : `demos/${active}-${variant}.html`;
    document.querySelector(`#${variant}-source`).href =
      `https://github.com/jagadeeshvarma/app-motion-effects/blob/main/docs/demos/${shared ? "feedback.js" : `${active}-${variant}.html`}`;
  }
  status.textContent = "Ready. Start the example to compare both sides.";
  if (updateHistory) {
    const url = new URL(location.href);
    url.searchParams.set("example", active);
    history.pushState({ example: active }, "", url);
  }
}
for (const button of document.querySelectorAll("[data-example]")) {
  button.setAttribute("aria-label", examples[button.dataset.example].name);
  button.addEventListener("click", () => chooseExample(button.dataset.example));
}
replay.addEventListener("click", () => {
  send("replay");
  reconnect.disabled = false;
  status.textContent = {
    loading: "Loading both previews for 2.4 seconds…",
    slow: "Loading both previews for six seconds…",
    offline:
      "Both previews are now disconnected. Restore connection to recover.",
    upload: "Uploading a synthetic file in both previews…",
    studio:
      "Watch the object jump on the left and return smoothly on the right.",
    dispatch:
      "Saving both synthetic notes. Keep typing to test unsaved changes.",
  }[active];
});
reconnect.addEventListener("click", () => {
  send("reconnect");
  reconnect.disabled = true;
});
window.addEventListener("message", (event) => {
  if (
    event.origin !== location.origin ||
    event.source !== frames[1].contentWindow ||
    event.data?.type !== "app-motion-state" ||
    event.data.scenario !== active
  )
    return;
  status.textContent = event.data.message;
});
reduce.addEventListener("change", () => {
  send("settings");
  status.textContent = reduce.checked
    ? "Reduced motion enabled. Current work is preserved."
    : "Example motion enabled unless your system requests reduced motion.";
});
document.querySelector("#mobile").addEventListener("change", (event) => {
  document
    .querySelector("#comparison")
    .classList.toggle("narrow", event.target.checked);
  requestAnimationFrame(fitFrames);
});
for (const button of document.querySelectorAll("[data-panel]"))
  button.addEventListener("click", () => {
    document.querySelector("#comparison").dataset.mobilePanel =
      button.dataset.panel;
    for (const item of document.querySelectorAll("[data-panel]"))
      item.setAttribute("aria-pressed", String(item === button));
    requestAnimationFrame(fitFrames);
  });
window.addEventListener("resize", () => requestAnimationFrame(fitFrames));
window.addEventListener("popstate", () =>
  chooseExample(
    new URLSearchParams(location.search).get("example") || "loading",
    false,
  ),
);
chooseExample(
  new URLSearchParams(location.search).get("example") || "loading",
  false,
);
