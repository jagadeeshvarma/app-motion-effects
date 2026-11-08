// Keep the exact same portable prompt in the website and GitHub's copyable code block.
import { readFileSync, writeFileSync } from "node:fs";
const root = new URL("../", import.meta.url);
const prompt = readFileSync(new URL("docs/full-repo-prompt.txt", root), "utf8");
const examples = (await import(new URL("docs/examples.js", root))).examples;
const escape = (value) =>
  value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
const htmlPath = new URL("docs/index.html", root);
let html = readFileSync(htmlPath, "utf8");
const nav = examples
  .map(
    (item) =>
      `<button type="button" data-example="${item.id}" aria-pressed="${item.id === "loading"}">${item.name}</button>`,
  )
  .join("\n");
const options = examples
  .map((item) => `<option value="${item.id}">${item.name}</option>`)
  .join("\n");
html = html.replace(
  /<!-- EXAMPLE_NAV -->|(?<=<nav id="example-nav" aria-label="Choose an example">)[\s\S]*?(?=<\/nav>)/,
  nav,
);
html = html.replace(
  /<!-- EXAMPLE_OPTIONS -->|(?<=<select id="example-select">)[\s\S]*?(?=<\/select>)/,
  options,
);
html = html.replace(
  /(?<=<textarea id="full-prompt" readonly spellcheck="false">)[\s\S]*?(?=<\/textarea>)/,
  escape(prompt),
);
// Handles the formatted HTML as well as the initial source.
if (!html.includes(escape(prompt)))
  html = html.replace(
    /(<textarea\b[^>]*id="full-prompt"[^>]*>)[\s\S]*?(<\/textarea>)/,
    "$1" + escape(prompt) + "$2",
  );
for (const [id, value] of [
  ["example-title", examples[0].name],
  ["example-description", examples[0].description],
  ["demo-hint", examples[0].hint],
  ["benefit", examples[0].benefit],
]) {
  const expression = new RegExp(
    '(<(?:p|h2)\\b[^>]*id="' + id + '"[^>]*>)[\\s\\S]*?(<\\/(?:p|h2)>)',
  );
  html = html.replace(
    expression,
    (_, start, end) => start + escape(value) + end,
  );
}
writeFileSync(htmlPath, html);
const readmePath = new URL("README.md", root);
let readme = readFileSync(readmePath, "utf8");
const section = `<!-- FULL_REPO_PROMPT_START -->\n## Full-repository audit and implementation\n\nInstall the skill, then paste this into your coding agent to audit the complete active product and implement every justified improvement. Use GitHub’s code-block copy control, or the **Copy full prompt** button on the [examples page](https://jagadeeshvarma.github.io/app-motion-effects/#full-repo-prompt).\n\n\`\`\`text\n${prompt}\`\`\`\n<!-- FULL_REPO_PROMPT_END -->`;
if (readme.includes("<!-- FULL_REPO_PROMPT_START -->"))
  readme = readme.replace(
    /<!-- FULL_REPO_PROMPT_START -->[\s\S]*?<!-- FULL_REPO_PROMPT_END -->/,
    section,
  );
else
  readme = readme.replace("## How it works", section + "\n\n## How it works");
writeFileSync(readmePath, readme);
console.log("Synced the full-repo prompt and ten example names.");
