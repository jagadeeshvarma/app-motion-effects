import { examples, resolveExample } from "./examples.js";

const before = document.querySelector("#before");
const after = document.querySelector("#after");
const frames = [before, after];
const stage = document.querySelector("#stage");
const replay = document.querySelector("#replay");
const restore = document.querySelector("#restore");
const reduce = document.querySelector("#reduce");
const select = document.querySelector("#example-select");
const status = document.querySelector("#review-status");
const mobile = matchMedia("(max-width:700px)");
let current = null;
let mode = "after";
function send(action, only) {
  for (const frame of only ? [only] : frames) {
    if (frame.dataset.ready !== "true") continue;
    frame.contentWindow.postMessage(
      {
        type: "motion-demo",
        action,
        reduced: reduce.checked,
        active: frame === after ? mode !== "before" : mode === "before",
      },
      location.origin,
    );
  }
}
function setMode(value) {
  mode = mobile.matches && value === "compare" ? "after" : value;
  stage.dataset.mode = mode;
  for (const control of document.querySelectorAll("[data-mode]"))
    if (control.tagName === "BUTTON")
      control.setAttribute(
        "aria-pressed",
        String(control.dataset.mode === mode),
      );
  send("settings");
}
function chooseExample(value, push = true) {
  const entry = resolveExample(value);
  if (current?.id === entry.id) return;
  current = entry;
  replay.disabled = true;
  restore.hidden = current.id !== "offline";
  restore.disabled = true;
  select.value = current.id;
  document.querySelector("#example-title").textContent = current.name;
  document.querySelector("#example-description").textContent =
    current.description;
  document.querySelector("#demo-hint").textContent = current.hint;
  document.querySelector("#benefit").textContent = current.benefit;
  replay.textContent = current.action;
  for (const button of document.querySelectorAll("[data-example]"))
    button.setAttribute(
      "aria-pressed",
      String(button.dataset.example === current.id),
    );
  for (const [index, variant] of ["before", "after"].entries()) {
    const frame = frames[index];
    frame.dataset.ready = "false";
    frame.title = `${current.name}: ${variant === "after" ? "after" : "before"}`;
    const src = new URL(
      `demos/interaction.html?example=${current.id}&variant=${variant}`,
      location.href,
    ).href;
    if (frame.src !== src) frame.src = src;
    else if (frame.contentDocument?.readyState === "complete")
      initializeFrame(frame);
  }
  status.textContent = "Ready to play.";
  if (push) {
    const url = new URL(location.href);
    url.searchParams.set("example", current.id);
    history.pushState(null, "", url);
  }
}
function initializeFrame(frame) {
  if (
    !frame.contentDocument?.querySelector("#demo") ||
    frame.contentDocument.URL !== frame.src
  )
    return;
  frame.dataset.ready = "true";
  send("settings", frame);
  replay.disabled = !frames.every((item) => item.dataset.ready === "true");
}
for (const frame of frames) {
  frame.addEventListener("load", () => initializeFrame(frame));
}
for (const button of document.querySelectorAll("[data-example]"))
  button.addEventListener("click", () => chooseExample(button.dataset.example));
select.addEventListener("change", () => chooseExample(select.value));
for (const button of document.querySelectorAll("button[data-mode]"))
  button.addEventListener("click", () => setMode(button.dataset.mode));
reduce.addEventListener("change", () => send("settings"));
mobile.addEventListener("change", () => setMode(mode));
replay.addEventListener("click", () => {
  send("replay");
  if (current.id === "offline") restore.disabled = false;
});
restore.addEventListener("click", () => {
  send("restore");
  restore.disabled = true;
});
window.addEventListener("message", (event) => {
  if (
    event.origin !== location.origin ||
    event.source !== after.contentWindow ||
    event.data?.type !== "motion-demo-state" ||
    event.data.kind !== current?.id
  )
    return;
  status.textContent = event.data.message;
});
window.addEventListener("popstate", () =>
  chooseExample(new URLSearchParams(location.search).get("example"), false),
);
chooseExample(new URLSearchParams(location.search).get("example"), false);
// A linked example should open the workbench, not leave its first half below the hero.
if (new URLSearchParams(location.search).has("example") && !location.hash)
  document.querySelector("#playground").scrollIntoView();

const copy = document.querySelector("#copy-prompt");
const prompt = document.querySelector("#full-prompt");
const copyStatus = document.querySelector("#copy-status");
let copyTimer;
copy.addEventListener("click", async () => {
  clearTimeout(copyTimer);
  try {
    if (!navigator.clipboard?.writeText)
      throw new Error("Clipboard unavailable");
    await navigator.clipboard.writeText(prompt.value);
    copy.textContent = "Copied";
    copyStatus.textContent =
      "Full prompt copied. Paste it into your coding agent after installing the skill.";
    copyTimer = setTimeout(() => {
      copy.textContent = "Copy full prompt";
    }, 3000);
  } catch {
    prompt.focus();
    prompt.select();
    copy.textContent = "Copy full prompt";
    copyStatus.textContent =
      "Automatic copy is unavailable. The full prompt is selected; press Command+C or Ctrl+C.";
  }
});
window.addEventListener("pagehide", () => clearTimeout(copyTimer));
