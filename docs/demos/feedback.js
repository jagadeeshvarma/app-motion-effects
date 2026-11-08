// Original, entirely local state simulations. No network throttling or uploads.
const query = new URLSearchParams(location.search);
const scenario = ["loading", "slow", "offline", "upload"].includes(
  query.get("scenario"),
)
  ? query.get("scenario")
  : "loading";
const improved = query.get("variant") !== "before";
document.body.dataset.scenario = scenario;
const content = document.querySelector("#content");
const actions = document.querySelector("#actions");
const notice = document.querySelector("#notice");
const status = document.querySelector("#status");
let generation = 0,
  timers = [],
  phase = "ready",
  bytes = 0,
  paused = false,
  connected = true;
const totalBytes = 5000000;
const projects = [
  ["S", "Studio website", "Updated just now"],
  ["A", "Annual report", "Ready for review"],
  ["P", "Product launch", "Three files"],
];
function announce(message) {
  status.textContent = message;
  parent.postMessage(
    {
      type: "app-motion-state",
      scenario,
      variant: improved ? "after" : "before",
      phase,
      message,
    },
    location.origin,
  );
}
function clearWork() {
  generation++;
  for (const timer of timers) clearTimeout(timer);
  timers = [];
  content.removeAttribute("aria-busy");
}
function later(callback, delay) {
  const id = generation;
  timers.push(
    setTimeout(() => {
      if (id === generation) callback();
    }, delay),
  );
}
function showNotice(title, message) {
  notice.replaceChildren();
  const strong = document.createElement("strong");
  strong.textContent = title;
  notice.append(strong, document.createTextNode(message));
  notice.hidden = false;
}
function hideNotice() {
  notice.hidden = true;
  notice.replaceChildren();
}
function button(label, handler) {
  const el = document.createElement("button");
  el.type = "button";
  el.textContent = label;
  el.addEventListener("click", handler);
  actions.append(el);
  return el;
}
// If an action disappears while focused, offer a useful next action in its place.
function clearActions(restartLabel, restart) {
  const hadFocus = actions.contains(document.activeElement);
  actions.replaceChildren();
  if (hadFocus && restartLabel) button(restartLabel, restart).focus();
  return hadFocus;
}
function renderProjects(reveal = false) {
  content.innerHTML =
    '<ul aria-label="Projects">' +
    projects
      .map(
        ([icon, title, detail]) =>
          `<li class="project"><span class="project-icon" aria-hidden="true">${icon}</span><div><strong>${title}</strong><span>${detail}</span></div></li>`,
      )
      .join("") +
    "</ul>";
  if (reveal && improved) content.firstElementChild.classList.add("reveal");
}
function skeleton() {
  content.innerHTML =
    '<ul class="skeleton" aria-hidden="true">' +
    Array.from(
      { length: 3 },
      () =>
        '<li class="project"><div class="project-icon"></div><div class="skeleton-lines"><div class="skeleton-line"></div><div class="skeleton-line"></div></div></li>',
    ).join("") +
    "</ul>";
}
function cancel() {
  clearWork();
  phase = "cancelled";
  hideNotice();
  renderProjects();
  clearActions("Load again", load);
  announce("Cancelled. Your projects are unchanged.");
}
function completeLoad() {
  content.removeAttribute("aria-busy");
  phase = "complete";
  hideNotice();
  renderProjects(true);
  clearActions("Reload projects", load);
  announce("Three projects loaded.");
}
function load() {
  clearWork();
  phase = "loading";
  const hadFocus = clearActions();
  hideNotice();
  content.setAttribute("aria-busy", "true");
  if (improved) {
    skeleton();
    const cancelButton = button("Cancel", cancel);
    if (hadFocus) cancelButton.focus();
  } else content.innerHTML = "";
  announce("Loading projects…");
  if (scenario === "slow" && improved)
    later(() => {
      phase = "waiting";
      showNotice(
        "The connection is taking longer.",
        "Your request is still running. You can wait or cancel.",
      );
      announce("Still loading. You can wait or cancel.");
    }, 1300);
  later(completeLoad, scenario === "slow" ? 6000 : 2400);
}
function disconnect() {
  clearWork();
  connected = false;
  phase = "offline";
  hideNotice();
  const hadFocus = clearActions();
  if (improved) {
    renderProjects();
    showNotice(
      "Connection lost.",
      "Your last loaded projects are still visible. Your note is still here.",
    );
  } else content.innerHTML = '<p class="empty">Unable to load projects.</p>';
  const retryButton = button("Try again", retry);
  if (hadFocus) retryButton.focus();
  announce(
    improved
      ? "Offline. Your projects and note are preserved."
      : "Unable to load projects.",
  );
}
function retry() {
  if (phase === "retrying") return;
  if (connected) {
    restore();
    return;
  }
  clearWork();
  phase = "retrying";
  content.setAttribute("aria-busy", "true");
  const retryButton = actions.querySelector("button");
  retryButton.setAttribute("aria-disabled", "true");
  announce("Checking the connection…");
  later(() => {
    disconnect();
  }, 700);
}
function restore() {
  clearWork();
  connected = true;
  phase = "reconnecting";
  hideNotice();
  actions.replaceChildren();
  content.setAttribute("aria-busy", "true");
  if (!improved) content.innerHTML = "";
  announce("Connection restored. Updating projects…");
  later(() => {
    completeLoad();
    announce("Back online. Projects updated. Your note is unchanged.");
  }, 1000);
}
const fileIcon =
  '<svg width="20" height="22" viewBox="0 0 20 22" fill="none" stroke="currentColor" aria-hidden="true"><path d="M4 1h8l5 5v15H4zM12 1v6h5M7 12h7M7 16h5"/></svg>';
function renderFile() {
  content.innerHTML = `<div class="file"><strong>${fileIcon}Project files.zip</strong><p>5 MB · demonstration file</p>${improved ? '<div id="progress" role="progressbar" aria-label="Upload progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span></span></div><p id="bytes">0 MB of 5 MB</p>' : ""}</div>`;
}
function updateProgress() {
  if (!improved) return;
  const percentage = Math.round((bytes / totalBytes) * 100);
  const progress = document.querySelector("#progress");
  progress.setAttribute("aria-valuenow", String(percentage));
  progress.setAttribute(
    "aria-valuetext",
    `${(bytes / 1000000).toFixed(1)} MB of 5 MB`,
  );
  progress.firstElementChild.style.width = percentage + "%";
  document.querySelector("#bytes").textContent =
    `${(bytes / 1000000).toFixed(1)} MB of 5 MB`;
}
function tickUpload() {
  if (paused || phase !== "uploading") return;
  bytes = Math.min(totalBytes, bytes + 400000);
  updateProgress();
  if (bytes === totalBytes) {
    phase = "complete";
    content.removeAttribute("aria-busy");
    clearActions("Upload again", startUpload);
    if (improved) {
      const done = document.createElement("p");
      done.className = "done";
      done.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="m7 12 3 3 7-7"/></svg>Upload complete';
      content.append(done);
    }
    announce("Upload complete. The demo file is ready.");
    return;
  }
  later(tickUpload, 260);
}
function startUpload() {
  clearWork();
  phase = "uploading";
  bytes = 0;
  paused = false;
  hideNotice();
  actions.replaceChildren();
  renderFile();
  content.setAttribute("aria-busy", "true");
  if (improved) {
    const pauseButton = button("Pause", () => {
      clearWork();
      paused = !paused;
      pauseButton.textContent = paused ? "Resume" : "Pause";
      if (paused) {
        phase = "paused";
        content.removeAttribute("aria-busy");
        announce("Upload paused. Resume when you are ready.");
      } else {
        phase = "uploading";
        content.setAttribute("aria-busy", "true");
        announce("Uploading the demo file…");
        later(tickUpload, 260);
      }
    });
    button("Cancel", () => {
      clearWork();
      phase = "cancelled";
      paused = false;
      clearActions("Start again", startUpload);
      announce("Upload cancelled. Nothing was uploaded.");
    });
  }
  announce("Uploading the demo file…");
  later(tickUpload, 260);
}
if (scenario === "upload") {
  document.querySelector("#heading").textContent = "File upload";
  renderFile();
} else renderProjects();
if (scenario === "offline")
  document.querySelector("#note-field").hidden = false;
window.addEventListener("message", (event) => {
  if (
    event.source !== parent ||
    event.origin !== location.origin ||
    event.data?.type !== "app-motion-demo"
  )
    return;
  document.documentElement.dataset.reviewReduced = String(
    Boolean(event.data.reduced),
  );
  if (event.data.action === "replay") {
    if (scenario === "upload") startUpload();
    else if (scenario === "offline") disconnect();
    else load();
  }
  if (event.data.action === "reconnect" && scenario === "offline") restore();
});
window.addEventListener("pagehide", clearWork);
