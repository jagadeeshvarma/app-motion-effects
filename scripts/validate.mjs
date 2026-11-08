import {
  readFileSync,
  readdirSync,
  lstatSync,
  realpathSync,
  existsSync,
} from "node:fs";
import { resolve, dirname, join, relative, isAbsolute, sep } from "node:path";
import assert from "node:assert/strict";
const root = resolve(import.meta.dirname, "..");
function walk(dir, allowedFiles, allowedDirectories) {
  const directory = lstatSync(dir);
  assert.ok(
    directory.isDirectory() && !directory.isSymbolicLink(),
    `Unsafe directory ${dir}`,
  );
  return readdirSync(dir)
    .sort()
    .flatMap((name) => {
      const p = join(dir, name);
      const info = lstatSync(p);
      assert.ok(!info.isSymbolicLink(), `Symlink is not allowed: ${p}`);
      assert.ok(
        info.isDirectory() || info.isFile(),
        `Special file is not allowed: ${p}`,
      );
      if (allowedFiles) {
        assert.ok(
          (info.isDirectory() ? allowedDirectories : allowedFiles).has(p),
          `Unexpected skill ${info.isDirectory() ? "directory" : "file"}: ${p}`,
        );
      }
      return info.isDirectory()
        ? walk(p, allowedFiles, allowedDirectories)
        : [p];
    });
}
const skill = join(root, "skills/app-motion-effects");
const manifest = JSON.parse(
  readFileSync(join(root, "scripts/skill-manifest.json"), "utf8"),
);
assert.equal(manifest.name, "app-motion-effects");
assert.ok(
  Array.isArray(manifest.files) && manifest.files.length > 0,
  "Empty skill manifest",
);
assert.equal(
  new Set(manifest.files).size,
  manifest.files.length,
  "Duplicate manifest path",
);
const allowedFiles = new Set();
const allowedDirectories = new Set();
for (const name of manifest.files) {
  assert.ok(
    typeof name === "string" &&
      name.length > 0 &&
      !/[\\:\0]/.test(name) &&
      !isAbsolute(name) &&
      name.split("/").every((part) => part && part !== "." && part !== ".."),
    `Unsafe manifest path: ${name}`,
  );
  const path = join(skill, name);
  allowedFiles.add(path);
  for (let parent = dirname(path); parent !== skill; parent = dirname(parent))
    allowedDirectories.add(parent);
}
assert.ok(
  !lstatSync(dirname(skill)).isSymbolicLink(),
  "The skills directory must not be a symlink",
);
const skillFiles = walk(skill, allowedFiles, allowedDirectories);
assert.deepEqual(
  new Set(skillFiles),
  allowedFiles,
  "Missing approved skill files",
);

function inside(scope, path) {
  const local = relative(scope, path);
  return local !== ".." && !local.startsWith(".." + sep) && !isAbsolute(local);
}
function localReferences(body, path) {
  const patterns = path.endsWith(".md")
    ? [
        /!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))/g,
        /^\s{0,3}\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))/gm,
        /(?:src|href|poster)\s*=\s*["']([^"']+)["']/gi,
      ]
    : path.endsWith(".html")
      ? [/(?:src|href|poster)\s*=\s*["']([^"']+)["']/gi]
      : path.endsWith(".css")
        ? [/url\(\s*["']?([^\s"')]+)["']?\s*\)/gi]
        : /\.m?js$/.test(path)
          ? [/(?:\bfrom\s*|\bimport\s*\(?\s*)["']([^"']+)["']/g]
          : [];
  return patterns.flatMap((pattern) =>
    [...body.matchAll(pattern)].map((match) => match[1] ?? match[2]),
  );
}
function validateReference(path, ref) {
  if (/^(?:https?:|mailto:|data:|#)/i.test(ref)) return false;
  const local = decodeURIComponent(ref.split(/[?#]/)[0]);
  assert.ok(
    local && !isAbsolute(local) && !/[\\:\0]/.test(local),
    `Unsafe local reference ${ref} in ${path}`,
  );
  const scope = inside(skill, path) ? skill : root;
  const target = resolve(dirname(path), local);
  assert.ok(
    inside(scope, target),
    `Local reference escapes its root: ${ref} in ${path}`,
  );
  assert.ok(existsSync(target), `Broken local link ${ref} in ${path}`);
  assert.ok(
    inside(scope, realpathSync(target)),
    `Local reference resolves outside its root: ${ref} in ${path}`,
  );
  for (
    let component = target;
    component !== scope;
    component = dirname(component)
  )
    assert.ok(
      !lstatSync(component).isSymbolicLink(),
      `Symlink reference ${ref} in ${path}`,
    );
  return true;
}
const entry = readFileSync(join(skill, "SKILL.md"), "utf8");
assert.match(
  entry,
  /^---\nname: app-motion-effects\ndescription: .+\nmetadata:\n  version: "[\d.]+"\n---/,
);
const description = entry.match(/^description: (.+)$/m)?.[1];
assert.ok(
  description && description.length <= 1024,
  "Skill description exceeds Agent Skills format limits",
);
assert.ok(
  entry.split("\n").length < 500,
  "Keep the runtime entrypoint concise; route detailed guidance into references",
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
  ...skillFiles,
  ...walk(join(root, "docs")).filter((p) =>
    /\.(?:md|txt|html|css|js)$/.test(p),
  ),
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
  for (const ref of localReferences(body, path))
    if (validateReference(path, ref)) links++;
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

const simulator = readFileSync(join(root, "docs/demos/interaction.js"), "utf8");
assert.ok(
  !/\b(?:fetch|XMLHttpRequest|WebSocket)\s*\(/.test(simulator),
  "The interaction simulator must stay local",
);
const canonical = readFileSync(join(root, "docs/full-repo-prompt.txt"), "utf8");
assert.ok(
  readFileSync(join(root, "README.md"), "utf8").includes(
    "```text\n" + canonical + "```",
  ),
  "README prompt differs from canonical text",
);
