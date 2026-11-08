const examples = {
  studio: {
    title: "Keep precision. Explain the return.",
    benefit:
      "Dragging stays immediate. Reset takes 180 ms, follows a clear path and can be interrupted. No bounce. No added decoration.",
    instructions:
      "Drag the object, or focus it and use arrow keys. Shift + arrow moves one unit. Type a caption and reset: your draft stays.",
    before: "Immediate reset",
    after: "Interruptible continuity",
    replay: "Compare reset",
    name: "Creative canvas",
    fit: "Creative work needs direct control. A short return path preserves spatial continuity without slowing manipulation.",
    preserved:
      "Paper palette, typography, canvas geometry, input labels and caption state. Existing pointer and keyboard workflows remain.",
    mechanism:
      "Original SVG + requestAnimationFrame implementation. No animation engine needed. Reduced motion resets immediately.",
  },
  dispatch: {
    title: "Make save feedback quiet and truthful.",
    benefit:
      "A subtle opacity pulse signals pending work. Feedback distinguishes a saved snapshot from newer unsaved edits. Errors stay until recovery.",
    instructions:
      "Edit a note and save. Keep typing during the save, or enable “Simulate next save failure” inside a preview and try again.",
    before: "Basic save status",
    after: "State-aware feedback",
    replay: "Compare save",
    name: "Business workflow",
    fit: "Repeated business work needs clear status without distraction. Feedback stays next to the action; drafts and focus remain stable.",
    preserved:
      "Neutral palette, compact controls, typography, field labels, existing layout and local save timing. No navigation changes.",
    mechanism:
      "Original CSS opacity keyframes + existing form state. No new dependencies. Reduced motion keeps readable static status.",
  },
};
let active = "studio";
const frames = [
  document.querySelector("#before"),
  document.querySelector("#after"),
];
const reduce = document.querySelector("#reduce");
const status = document.querySelector("#review-status");
function send(action) {
  for (const frame of frames)
    frame.contentWindow.postMessage(
      { type: "app-motion-demo", action, reduced: reduce.checked },
      location.origin,
    );
}
// Keep example content visible without nested scrolling or clipped form controls.
function fitFrames() {
  const heights = frames.map((frame) => {
    const main = frame.contentDocument?.querySelector("main");
    return main
      ? Math.ceil(
          main.getBoundingClientRect().bottom +
            frame.contentWindow.scrollY +
            32,
        )
      : 550;
  });
  const height = Math.max(...heights);
  for (const frame of frames)
    if (frame.style.height !== `${height}px`)
      frame.style.height = `${height}px`;
}
function initializeFrame(frame) {
  frame.reviewObserver?.disconnect();
  const main = frame.contentDocument.querySelector("main");
  frame.reviewObserver = new ResizeObserver(fitFrames);
  if (main) frame.reviewObserver.observe(main);
  fitFrames();
  send("settings");
}
for (const frame of frames) {
  frame.addEventListener("load", () => initializeFrame(frame));
  if (
    frame.contentDocument?.readyState === "complete" &&
    frame.contentDocument.querySelector("main")
  )
    initializeFrame(frame);
}
for (const button of document.querySelectorAll("[data-example]")) {
  button.addEventListener("click", () => {
    if (active === button.dataset.example) return;
    active = button.dataset.example;
    const e = examples[active];
    for (const item of document.querySelectorAll("[data-example]"))
      item.setAttribute("aria-pressed", String(item === button));
    for (const [id, key] of [
      ["example-title", "title"],
      ["example-benefit", "benefit"],
      ["instructions", "instructions"],
      ["before-label", "before"],
      ["after-label", "after"],
      ["fit", "fit"],
      ["preserved", "preserved"],
      ["mechanism", "mechanism"],
    ])
      document.getElementById(id).textContent = e[key];
    document.querySelector("#replay").textContent = e.replay + " ↗";
    for (const [i, variant] of ["before", "after"].entries()) {
      frames[i].title = `${e.name} ${variant} improvement`;
      frames[i].src = `demos/${active}-${variant}.html`;
      document.querySelector(`#${variant}-source`).href =
        `https://github.com/jagadeeshvarma/app-motion-effects/blob/main/docs/demos/${active}-${variant}.html`;
    }
    status.textContent = `${e.name} loaded. Both previews restarted. System reduced-motion preferences remain respected.`;
  });
}
document.querySelector("#replay").addEventListener("click", () => {
  send("replay");
  status.textContent =
    active === "studio"
      ? "Comparing the same reset: immediate before, a short continuous return after."
      : "Saving both synthetic notes. Nothing is sent to a server.";
});
reduce.addEventListener("change", () => {
  send("settings");
  status.textContent = reduce.checked
    ? "Reduced motion enabled. Current drafts are preserved."
    : "Example motion enabled unless your system requests reduced motion. Current drafts are preserved.";
});
document.querySelector("#mobile").addEventListener("change", (event) => {
  document
    .querySelector("#comparison")
    .classList.toggle("narrow", event.target.checked);
  status.textContent = event.target.checked
    ? "Narrow previews enabled. This is a browser layout preview, not a native device."
    : "Full-width previews enabled. Current drafts are preserved.";
});
