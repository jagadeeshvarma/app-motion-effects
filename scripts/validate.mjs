import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { resolve, dirname, join } from "node:path";
import assert from "node:assert/strict";
const root = resolve(import.meta.dirname, "..");
function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
}
const skill = join(root, "skills/app-motion-effects");
const entry = readFileSync(join(skill, "SKILL.md"), "utf8");
assert.match(
  entry,
  /^---\nname: app-motion-effects\ndescription: .+\nmetadata:\n  version: "[\d.]+"\n---/,
);
const version = entry.match(/version: "([\d.]+)"/)[1];
assert.equal(
  JSON.parse(readFileSync(join(root, "package.json"))).version,
  version,
);
for (const path of [
  "LICENSE",
  "README.md",
  "CONTRIBUTING.md",
  "SECURITY.md",
  "CODE_OF_CONDUCT.md",
  "THIRD_PARTY_NOTICES.md",
  "docs/index.html",
  "skills/app-motion-effects/LICENSE",
])
  assert.ok(existsSync(join(root, path)), `Missing ${path}`);
// Resolve local links independently of the author's absolute filesystem paths.
const files = [
  join(root, "README.md"),
  join(root, "CONTRIBUTING.md"),
  join(root, "THIRD_PARTY_NOTICES.md"),
  ...walk(skill),
  ...walk(join(root, "docs")).filter((p) => /\.(?:md|html|css|js)$/.test(p)),
];
let links = 0;
for (const path of files) {
  const body = readFileSync(path, "utf8");
  assert.ok(
    !/(?:\/Users\/|\/private\/tmp\/|sk_live_|ghp_[a-zA-Z0-9]{20,}|github_pat_[a-zA-Z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)/.test(
      body,
    ),
    `Private path/credential in ${path}`,
  );
  const refs = path.endsWith(".md")
    ? [...body.matchAll(/\]\(([^\s)]+)(?:\s+"[^"]*")?\)/g)].map((m) => m[1])
    : path.endsWith(".html")
      ? [...body.matchAll(/(?:src|href|poster)="([^"]+)"/g)].map((m) => m[1])
      : [];
  for (const ref of refs) {
    if (/^(?:https?:|mailto:|data:|#)/.test(ref)) continue;
    assert.ok(
      existsSync(resolve(dirname(path), decodeURIComponent(ref.split("#")[0]))),
      `Broken local link ${ref} in ${path}`,
    );
    links++;
  }
}
const taxonomy = readFileSync(join(skill, "references/taxonomy.md"), "utf8");
const ids = new Set(
  taxonomy.match(
    /\b(?:A(?:0[1-9]|1\d|2[0-2])|B(?:0[1-9]|1\d|2[0-3])|C(?:0[1-9]|1[0-4])|D0[1-4])\b/g,
  ),
);
assert.equal(ids.size, 63, "Taxonomy coverage changed");
for (const name of ["studio", "dispatch"])
  for (const variant of ["before", "after"]) {
    const html = readFileSync(
      join(root, `docs/demos/${name}-${variant}.html`),
      "utf8",
    );
    assert.ok(
      !/\b(?:fetch|XMLHttpRequest|WebSocket)\s*\(/.test(html),
      "Synthetic example performs network actions",
    );
    assert.ok(
      !/<(?:script|link)[^>]+(?:src|href)="https?:/.test(html),
      "External runtime dependency in example",
    );
  }
console.log(
  `Structure passed: v${version}, ${ids.size} category IDs, ${links} valid local references, portable files and synthetic demos.`,
);
