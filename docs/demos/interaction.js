import { resolveExample } from "../examples.js";

// Original local fixtures. These operations never call an application service.
const params = new URLSearchParams(location.search);
const kind = resolveExample(params.get("example")).id;
const enhanced = params.get("variant") !== "before";
const hero = params.has("hero");
const media = matchMedia("(prefers-reduced-motion: reduce)");
const root = document.documentElement;
const card = document.querySelector("#demo");
const content = document.querySelector("#content");
const actions = document.querySelector("#actions");
const status = document.querySelector("#status");
const notice = document.querySelector("#notice");
const heading = document.querySelector("#heading");
const dialog = document.querySelector("#details");
const toast = document.querySelector("#toast");
if (kind !== "panel") dialog.remove();
if (kind !== "toast") toast.remove();
let reviewReduced = false;
let generation = 0;
let timers = [];
let state = "ready";
const animations = new Set();
root.classList.toggle("enhanced", enhanced);
document.body.dataset.example = kind;
document.body.classList.toggle("hero-mode", hero);

const check =
  '<svg class="check" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg>';
const spinner =
  '<svg class="spinner" viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="15"/></svg>';
const fileIcon =
  '<svg viewBox="0 0 36 44" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M7 2h14l9 9v31H7zM21 2v10h9M12 21h13M12 27h13M12 33h8"/></svg>';
const projects = [
  {
    id: "studio",
    letter: "S",
    title: "Studio website",
    detail: "Design review on Friday",
    status: "In progress",
  },
  {
    id: "annual",
    letter: "A",
    title: "Annual report",
    detail: "Ready for the next chapter",
    status: "Complete",
  },
  {
    id: "product",
    letter: "P",
    title: "Product launch",
    detail: "Three files to review",
    status: "In progress",
  },
];
function reduced() {
  return reviewReduced || media.matches;
}
function motion(node, frames, options = {}) {
  if (!enhanced || reduced()) return null;
  const animation = node.animate(frames, {
    duration: 240,
    easing: "cubic-bezier(.2,.7,.2,1)",
    ...options,
  });
  animations.add(animation);
  animation.finished.then(
    () => animations.delete(animation),
    () => animations.delete(animation),
  );
  return animation;
}
function finishMotion() {
  for (const animation of animations) {
    try {
      animation.finish();
    } catch {
      animation.cancel();
    }
  }
}
media.addEventListener("change", () => {
  if (reduced()) finishMotion();
});
function announce(message, next = state) {
  state = next;
  root.dataset.state = state;
  status.textContent = message;
  status.dataset.state = state;
  parent.postMessage(
    {
      type: "motion-demo-state",
      kind,
      variant: enhanced ? "after" : "before",
      state,
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
  const token = generation;
  timers.push(
    setTimeout(() => {
      if (token === generation) callback();
    }, delay),
  );
}
function clearActions() {
  const hadFocus = actions.contains(document.activeElement);
  actions.replaceChildren();
  return hadFocus;
}
function button(label, callback, primary = false) {
  const el = document.createElement("button");
  el.type = "button";
  el.className = "control" + (primary ? " primary" : "");
  el.textContent = label;
  el.addEventListener("click", callback);
  actions.append(el);
  return el;
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
function projectMarkup(project) {
  return `<li class="project" data-project="${project.id}"><span class="project-icon" aria-hidden="true">${project.letter}</span><div><strong>${project.title}</strong><p>${project.detail}</p></div><span class="project-state">${project.status}</span></li>`;
}
function renderProjects(reveal = false) {
  content.innerHTML =
    '<div class="content-space"><ul class="project-list" aria-label="Projects">' +
    projects.map(projectMarkup).join("") +
    "</ul></div>";
  if (reveal)
    motion(
      content.firstElementChild,
      [
        { opacity: 0, transform: "translateY(7px)" },
        { opacity: 1, transform: "none" },
      ],
      { duration: 260 },
    );
}
function renderSkeleton() {
  content.innerHTML =
    '<div class="content-space"><ul class="project-list skeleton" aria-hidden="true">' +
    Array.from(
      { length: 3 },
      () =>
        '<li class="project"><span class="project-icon"></span><div class="skeleton-lines"><div class="skeleton-line"></div><div class="skeleton-line"></div></div></li>',
    ).join("") +
    "</ul></div>";
}
function restartAction(label, callback, hadFocus) {
  if (hadFocus) button(label, callback).focus();
}
function completeLoad() {
  content.removeAttribute("aria-busy");
  hideNotice();
  renderProjects(true);
  const focused = clearActions();
  restartAction("Load again", load, focused);
  announce("Three projects loaded.", "complete");
}
function cancelLoad() {
  clearWork();
  hideNotice();
  renderProjects();
  const focused = clearActions();
  restartAction("Load again", load, focused);
  announce("Cancelled. Your projects are unchanged.", "cancelled");
}
function load() {
  clearWork();
  hideNotice();
  const focused = clearActions();
  content.setAttribute("aria-busy", "true");
  if (enhanced) {
    renderSkeleton();
    const cancel = button("Cancel", cancelLoad);
    if (focused) cancel.focus();
  } else content.innerHTML = '<div class="content-space"></div>';
  announce("Loading projects…", "loading");
  if (kind === "slow" && enhanced)
    later(() => {
      showNotice(
        "This is taking longer.",
        "Your request is still running. You can wait or cancel.",
      );
      announce("Still loading. You can wait or cancel.", "waiting");
    }, 1300);
  later(completeLoad, kind === "slow" ? 6000 : 2400);
}

// Unknown-duration work is intentionally indeterminate.
function loaderReady() {
  content.innerHTML = `<div class="loader-stage"><div class="loader-rest">${fileIcon}</div><h2>Prepare a project preview</h2><p>The original file stays right here.</p></div>`;
  button("Prepare preview", startLoader, true);
}
function startLoader() {
  clearWork();
  clearActions();
  content.innerHTML = `<div class="loader-stage">${enhanced ? spinner : ""}<h2>Preparing your preview</h2><p>This usually takes a few seconds.</p></div>`;
  content.setAttribute("aria-busy", "true");
  if (enhanced)
    button("Cancel", () => {
      clearWork();
      content.replaceChildren();
      clearActions();
      loaderReady();
      announce("Preparation cancelled.", "cancelled");
    });
  announce("Preparing your preview…", "loading");
  later(() => {
    content.removeAttribute("aria-busy");
    content.innerHTML = `<div class="loader-stage"><div class="loader-rest">${check}</div><h2>Your preview is ready</h2><p>Studio website · three pages</p></div>`;
    const focused = clearActions();
    restartAction("Prepare again", startLoader, focused);
    motion(content.firstElementChild, [
      { opacity: 0, transform: "translateY(8px)" },
      { opacity: 1, transform: "none" },
    ]);
    announce("Preview ready.", "complete");
  }, 3800);
}

// Connection recovery preserves a separately mounted input.
let connected = true;
function createNote() {
  const field = document.createElement("div");
  field.id = "note-field";
  field.innerHTML =
    '<label for="project-note">Project note</label><input id="project-note" type="text" value="Send the draft for review.">';
  const row = document.createElement("div");
  row.className = "connection-edit";
  card.insertBefore(row, status);
  row.append(field, actions);
}
function disconnect() {
  clearWork();
  connected = false;
  document.querySelector("#context").textContent = "Offline";
  hideNotice();
  const focused = clearActions();
  if (enhanced) {
    renderProjects();
    showNotice("Connection lost.", "Your projects and note are still here.");
  } else
    content.innerHTML =
      '<div class="content-space"><p>Unable to load projects.</p></div>';
  const retry = button("Try again", retryConnection);
  if (focused) retry.focus();
  announce(
    enhanced ? "Offline. Your work is preserved." : "Unable to load projects.",
    "offline",
  );
}
function retryConnection() {
  if (state === "retrying") return;
  if (connected) {
    restoreConnection();
    return;
  }
  clearWork();
  const retry = actions.querySelector("button");
  retry?.setAttribute("aria-disabled", "true");
  announce("Checking the connection…", "retrying");
  later(disconnect, 650);
}
function restoreConnection() {
  clearWork();
  connected = true;
  document.querySelector("#context").textContent = "Reconnecting";
  hideNotice();
  clearActions();
  if (!enhanced) content.innerHTML = '<div class="content-space"></div>';
  content.setAttribute("aria-busy", "true");
  announce("Connection restored. Updating projects…", "reconnecting");
  later(() => {
    content.removeAttribute("aria-busy");
    renderProjects(true);
    document.querySelector("#context").textContent = "Online";
    announce("Back online. Your note is unchanged.", "complete");
  }, 1000);
}

// Progress represents completed synthetic chunks, never an invented real upload.
let bytes = 0,
  paused = false;
const totalBytes = 5000000;
function renderFile() {
  content.innerHTML = `<div class="file"><div class="file-top">${fileIcon}<div><strong>Brand assets.zip</strong><p>5 MB · demonstration file</p></div></div>${enhanced ? '<div class="progress" role="progressbar" aria-label="Upload progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span></span></div><div class="progress-copy"><span id="bytes">0 MB of 5 MB</span><span id="percentage">0%</span></div>' : ""}</div>`;
}
function updateProgress() {
  if (!enhanced) return;
  const value = Math.round((bytes / totalBytes) * 100),
    progress = content.querySelector('[role="progressbar"]');
  progress.setAttribute("aria-valuenow", String(value));
  progress.setAttribute(
    "aria-valuetext",
    `${(bytes / 1000000).toFixed(1)} MB of 5 MB`,
  );
  progress.firstElementChild.style.width = value + "%";
  content.querySelector("#bytes").textContent =
    `${(bytes / 1000000).toFixed(1)} MB of 5 MB`;
  content.querySelector("#percentage").textContent = value + "%";
}
function uploadTick() {
  if (paused || state !== "uploading") return;
  bytes = Math.min(totalBytes, bytes + 400000);
  updateProgress();
  if (bytes === totalBytes) {
    content.removeAttribute("aria-busy");
    const focused = clearActions();
    restartAction("Upload again", startUpload, focused);
    if (enhanced) {
      const complete = document.createElement("div");
      complete.className = "upload-done";
      complete.innerHTML = check + "<span>Upload complete</span>";
      content.append(complete);
    }
    announce("Upload complete. The demo file is ready.", "complete");
    return;
  }
  later(uploadTick, 260);
}
function startUpload() {
  clearWork();
  clearActions();
  hideNotice();
  bytes = 0;
  paused = false;
  renderFile();
  content.setAttribute("aria-busy", "true");
  if (enhanced) {
    const pause = button("Pause", () => {
      clearWork();
      paused = !paused;
      pause.textContent = paused ? "Resume" : "Pause";
      announce(
        paused
          ? "Upload paused. Resume when you are ready."
          : "Uploading the demo file…",
        paused ? "paused" : "uploading",
      );
      if (!paused) {
        content.setAttribute("aria-busy", "true");
        later(uploadTick, 260);
      }
    });
    button("Cancel", () => {
      clearWork();
      paused = false;
      const focused = clearActions();
      restartAction("Start again", startUpload, focused);
      announce("Upload cancelled. Nothing was uploaded.", "cancelled");
    });
  }
  announce("Uploading the demo file…", "uploading");
  later(uploadTick, 260);
}

// Saving demonstrates a complete, visible control transition and accurate draft state.
let savedTitle = "Studio website",
  pendingSave = false,
  submittedTitle = "";
function setupSave() {
  heading.textContent = "Project settings";
  content.innerHTML =
    '<form id="save-form"><label for="project-title">Project title</label><input id="project-title" type="text" value="Studio website" maxlength="100"><div class="save-summary" id="save-summary">Make a change, then save it.</div><div class="save-actions"><button type="submit" id="save" class="control primary">Save changes</button><label class="failure-control"><input type="checkbox" id="fail-save">Fail next save</label></div></form>';
  status.classList.add("visually-hidden");
  const field = content.querySelector("#project-title");
  content.querySelector("#save-form").addEventListener("submit", (event) => {
    event.preventDefault();
    saveTitle();
  });
  field.addEventListener("input", () => {
    if (!pendingSave) {
      if (state === "error") return;
      content.querySelector("#save").textContent = "Save changes";
      setSaveSummary(
        field.value === savedTitle ? "No unsaved changes." : "Unsaved changes.",
        "draft",
      );
    } else
      setSaveSummary(
        "Saving the earlier title. New edits are still a draft.",
        "pending",
      );
  });
}
function setSaveSummary(message, phase) {
  const summary = content.querySelector("#save-summary");
  summary.textContent = message;
  summary.dataset.state = phase;
}
function saveTitle() {
  if (pendingSave) return;
  clearWork();
  const field = content.querySelector("#project-title"),
    save = content.querySelector("#save"),
    fail = content.querySelector("#fail-save");
  submittedTitle = field.value;
  const willFail = fail.checked;
  fail.checked = false;
  pendingSave = true;
  save.style.minWidth = Math.ceil(save.getBoundingClientRect().width) + "px";
  save.setAttribute("aria-disabled", "true");
  save.innerHTML = (enhanced ? spinner : "") + "Saving";
  setSaveSummary("Saving your project title…", "pending");
  announce("Saving your project title…", "saving");
  later(() => {
    pendingSave = false;
    save.removeAttribute("aria-disabled");
    if (willFail) {
      save.textContent = "Try again";
      setSaveSummary("Could not save. Your changes are still here.", "error");
      announce("Could not save. Try again.", "error");
      return;
    }
    savedTitle = submittedTitle;
    const hasDraft = field.value !== savedTitle;
    save.innerHTML = enhanced && !hasDraft ? check + "Saved" : "Save changes";
    setSaveSummary(
      hasDraft
        ? "Earlier title saved. New edits are not saved."
        : "Your project title is saved.",
      hasDraft ? "draft" : "saved",
    );
    announce(
      hasDraft
        ? "Earlier title saved. New edits are not saved."
        : "Project title saved.",
      hasDraft ? "draft" : "saved",
    );
    if (enhanced)
      motion(content.querySelector("#save-summary"), [
        { opacity: 0.25, transform: "translateY(3px)" },
        { opacity: 1, transform: "none" },
      ]);
  }, 1500);
}
function playSave() {
  if (pendingSave) return;
  const field = content.querySelector("#project-title");
  field.value =
    field.value === "Studio website"
      ? "Studio website · Spring"
      : "Studio website";
  saveTitle();
}

// FLIP preserves DOM identity and animates only the changed positions.
const filterProjects = [
  ...projects,
  {
    id: "journal",
    letter: "J",
    title: "Design journal",
    detail: "Notes from the studio",
    status: "Complete",
  },
  {
    id: "identity",
    letter: "I",
    title: "Brand identity",
    detail: "A new direction",
    status: "In progress",
  },
];
let filterChoice = "All";
function setupFilter() {
  heading.textContent = "Recent projects";
  content.innerHTML =
    '<div class="filter-controls" role="group" aria-label="Project status">' +
    ["All", "In progress", "Complete"]
      .map(
        (label) =>
          `<button type="button" aria-pressed="${label === "All"}" data-filter="${label}">${label}</button>`,
      )
      .join("") +
    '</div><ul class="project-list filter-list" aria-label="Projects">' +
    filterProjects.map(projectMarkup).join("") +
    "</ul>";
  for (const control of content.querySelectorAll("[data-filter]"))
    control.addEventListener("click", () => filterList(control.dataset.filter));
}
function filterList(choice) {
  const list = content.querySelector(".filter-list"),
    rows = [...list.children],
    old = new Map(
      rows
        .filter((row) => !row.hidden)
        .map((row) => [row, row.getBoundingClientRect()]),
    );
  for (const animation of [...animations]) animation.cancel();
  for (const control of content.querySelectorAll("[data-filter]"))
    control.setAttribute(
      "aria-pressed",
      String(control.dataset.filter === choice),
    );
  filterChoice = choice;
  for (const row of rows) {
    const data = filterProjects.find(
      (project) => project.id === row.dataset.project,
    );
    row.hidden = choice !== "All" && data.status !== choice;
  }
  for (const row of rows.filter((item) => !item.hidden)) {
    const box = row.getBoundingClientRect(),
      previous = old.get(row);
    if (previous) {
      const y = previous.top - box.top;
      if (Math.abs(y) > 1)
        motion(
          row,
          [{ transform: `translateY(${y}px)` }, { transform: "none" }],
          { duration: 320 },
        );
    } else
      motion(
        row,
        [
          { opacity: 0, transform: "translateY(10px)" },
          { opacity: 1, transform: "none" },
        ],
        { duration: 260 },
      );
  }
  announce(
    `${rows.filter((row) => !row.hidden).length} projects shown.`,
    "filtered",
  );
}

// One toast is reused; dismissal is paused while the user interacts with it.
let toastTimer,
  toastRemaining = 0,
  toastStarted = 0,
  toastAnimation,
  toastVersion = 0;
function pauseToast() {
  if (toast.hidden || !toastTimer) return;
  clearTimeout(toastTimer);
  toastTimer = null;
  toastRemaining = Math.max(
    0,
    toastRemaining - (performance.now() - toastStarted),
  );
}
function resumeToast() {
  if (
    toast.hidden ||
    toast.matches(":hover") ||
    toast.contains(document.activeElement)
  )
    return;
  clearTimeout(toastTimer);
  toastStarted = performance.now();
  toastTimer = setTimeout(hideToast, toastRemaining);
}
function showToast() {
  toastVersion++;
  clearTimeout(toastTimer);
  toastAnimation?.cancel();
  toast.querySelector(".toast-icon").innerHTML = check;
  toast.hidden = false;
  toastRemaining = 4000;
  toastAnimation = motion(
    toast,
    [
      { opacity: 0, transform: "translateY(-12px)" },
      { opacity: 1, transform: "none" },
    ],
    { duration: 260 },
  );
  resumeToast();
  announce("Project saved. A confirmation is visible.", "notified");
}
async function hideToast() {
  const token = ++toastVersion,
    restoreFocus = toast.contains(document.activeElement);
  clearTimeout(toastTimer);
  toastAnimation?.cancel();
  const animation = motion(
    toast,
    [
      { opacity: 1, transform: "none" },
      { opacity: 0, transform: "translateY(-5px)" },
    ],
    { duration: 420 },
  );
  if (animation) {
    try {
      await animation.finished;
    } catch {
      return;
    }
  }
  if (token !== toastVersion) return;
  toast.hidden = true;
  if (restoreFocus) content.querySelector("#notify")?.focus();
  announce("Confirmation dismissed.", "dismissed");
}
function setupToast() {
  heading.textContent = "Project overview";
  content.innerHTML = `<div class="notification-preview">${fileIcon}<h2>Studio website</h2><p>Everything in its place.</p><button type="button" class="control primary" id="notify">Save project</button></div>`;
  content.querySelector("#notify").addEventListener("click", showToast);
  toast.addEventListener("pointerenter", pauseToast);
  toast.addEventListener("pointerleave", resumeToast);
  toast.addEventListener("focusin", pauseToast);
  toast.addEventListener("focusout", () => queueMicrotask(resumeToast));
  document.querySelector("#close-toast").addEventListener("click", hideToast);
}

// Native dialog semantics supply modal focus and Escape handling.
let panelVersion = 0,
  panelAnimation;
function openPanel() {
  if (dialog.open && state !== "closing") {
    document.querySelector("#close-panel").focus();
    return;
  }
  const from = dialog.open
    ? getComputedStyle(dialog).transform
    : "translateX(100%)";
  dialog.classList.remove("closing");
  panelVersion++;
  panelAnimation?.cancel();
  if (!dialog.open) dialog.showModal();
  document.querySelector("#close-panel").focus();
  panelAnimation = motion(
    dialog,
    [
      { transform: from, opacity: 0.8 },
      { transform: "translateX(0)", opacity: 1 },
    ],
    { duration: 300 },
  );
  announce("Project details opened.", "open");
}
async function closePanel() {
  if (state === "closing") return;
  const from = getComputedStyle(dialog).transform;
  dialog.classList.add("closing");
  announce("Closing project details.", "closing");
  const token = ++panelVersion;
  panelAnimation?.cancel();
  const animation = motion(
    dialog,
    [
      { transform: from, opacity: 1 },
      { transform: "translateX(100%)", opacity: 0.8 },
    ],
    { duration: 240 },
  );
  panelAnimation = animation;
  if (animation) {
    try {
      await animation.finished;
    } catch {
      return;
    }
  }
  if (token !== panelVersion) return;
  dialog.close();
  content.querySelector("#open-panel").focus();
  announce("Project details closed.", "closed");
}
function setupPanel() {
  heading.textContent = "Project overview";
  content.innerHTML =
    '<ul class="project-list" aria-label="Projects">' +
    projectMarkup(projects[0]) +
    '</ul><div class="task-actions"><button type="button" id="open-panel" class="control primary">Open details</button></div>';
  content.querySelector("#open-panel").addEventListener("click", openPanel);
  document.querySelector("#close-panel").addEventListener("click", closePanel);
  dialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closePanel();
  });
  dialog.addEventListener("click", (event) => {
    if (
      event.target === dialog &&
      event.clientX < dialog.getBoundingClientRect().left
    )
      closePanel();
  });
}

let selectedTab = 0;
let tabObserver;
function setupTabs() {
  heading.textContent = "Studio website";
  content.innerHTML =
    '<div class="tabs" role="tablist" aria-label="Project views">' +
    ["Overview", "Activity", "Files"]
      .map(
        (label, i) =>
          `<button type="button" role="tab" id="tab-${i}" aria-controls="view-${i}" aria-selected="${i === 0}" tabindex="${i === 0 ? 0 : -1}">${label}</button>`,
      )
      .join("") +
    '<span class="tab-indicator" aria-hidden="true"></span></div><section class="tab-body" role="tabpanel" id="view-0" aria-labelledby="tab-0"><h2>A considered beginning.</h2><p>A small website for a design studio. The next milestone is the first design review.</p><label for="tab-note">Project note</label><input id="tab-note" type="text" value="Keep the navigation simple."></section><section class="tab-body" role="tabpanel" id="view-1" aria-labelledby="tab-1" hidden><ul class="activity"><li>First design shared<span>Today, 10:30</span></li><li>Project brief approved<span>Yesterday, 14:00</span></li><li>Workspace created<span>Monday, 09:15</span></li></ul></section><section class="tab-body" role="tabpanel" id="view-2" aria-labelledby="tab-2" hidden><ul class="project-list" aria-label="Project files">' +
    projectMarkup({
      id: "brief",
      letter: "B",
      title: "Project brief.pdf",
      detail: "1.2 MB",
      status: "Approved",
    }) +
    projectMarkup({
      id: "design",
      letter: "D",
      title: "First design.fig",
      detail: "4.8 MB",
      status: "For review",
    }) +
    "</ul></section>";
  for (const [i, tab] of [
    ...content.querySelectorAll('[role="tab"]'),
  ].entries()) {
    tab.addEventListener("click", () => selectTab(i));
    tab.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight") next = (i + 1) % 3;
      if (event.key === "ArrowLeft") next = (i + 2) % 3;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = 2;
      if (next !== undefined) {
        event.preventDefault();
        selectTab(next);
        content.querySelector(`#tab-${next}`).focus();
      }
    });
  }
  tabObserver = new ResizeObserver(updateIndicator);
  tabObserver.observe(content.querySelector(".tabs"));
  requestAnimationFrame(updateIndicator);
}
function updateIndicator() {
  const tab = content.querySelector(`#tab-${selectedTab}`),
    indicator = content.querySelector(".tab-indicator");
  if (!tab || !indicator) return;
  indicator.style.left = tab.offsetLeft + "px";
  indicator.style.width = tab.offsetWidth + "px";
}
function selectTab(index) {
  if (index === selectedTab) return;
  for (const animation of [...animations]) animation.cancel();
  selectedTab = index;
  for (const [i, tab] of [
    ...content.querySelectorAll('[role="tab"]'),
  ].entries()) {
    tab.setAttribute("aria-selected", String(i === index));
    tab.tabIndex = i === index ? 0 : -1;
    content.querySelector(`#view-${i}`).hidden = i !== index;
  }
  updateIndicator();
  motion(
    content.querySelector(`#view-${index}`),
    [
      { opacity: 0, transform: "translateY(8px)" },
      { opacity: 1, transform: "none" },
    ],
    { duration: 260 },
  );
  announce(
    ["Overview", "Activity", "Files"][index] + " view selected.",
    "selected",
  );
}

if (["loading", "slow", "offline"].includes(kind)) {
  renderProjects();
  if (kind === "offline") {
    createNote();
    document.querySelector("#context").textContent = "Online";
  }
}
if (kind === "loader") {
  heading.textContent = "Project preview";
  loaderReady();
}
if (kind === "upload") {
  heading.textContent = "File upload";
  renderFile();
}
if (kind === "save") setupSave();
if (kind === "filter") setupFilter();
if (kind === "toast") setupToast();
if (kind === "panel") setupPanel();
if (kind === "tabs") setupTabs();
function replay() {
  if (["loading", "slow"].includes(kind)) load();
  if (kind === "loader") startLoader();
  if (kind === "offline") disconnect();
  if (kind === "upload") startUpload();
  if (kind === "save") playSave();
  if (kind === "filter")
    filterList(filterChoice === "All" ? "Complete" : "All");
  if (kind === "toast") showToast();
  if (kind === "panel") openPanel();
  if (kind === "tabs") selectTab((selectedTab + 1) % 3);
}
window.addEventListener("message", (event) => {
  if (
    event.source !== parent ||
    event.origin !== location.origin ||
    event.data?.type !== "motion-demo"
  )
    return;
  reviewReduced = Boolean(event.data.reduced);
  root.dataset.reviewReduced = String(reviewReduced);
  status.setAttribute(
    "aria-live",
    event.data.active && !hero ? "polite" : "off",
  );
  toast.setAttribute("aria-live", event.data.active ? "polite" : "off");
  if (reduced()) finishMotion();
  if (event.data.action === "replay") replay();
  if (event.data.action === "restore" && kind === "offline")
    restoreConnection();
});
if (hero) {
  status.setAttribute("aria-live", "off");
  let touched = false;
  for (const type of ["input", "pointerdown", "keydown"])
    card.addEventListener(type, () => {
      touched = true;
    });
  later(() => {
    if (!touched) saveTitle();
  }, 900);
}
window.addEventListener("pagehide", (event) => {
  if (event.persisted) return;
  clearWork();
  clearTimeout(toastTimer);
  tabObserver?.disconnect();
  for (const animation of animations) animation.cancel();
});
