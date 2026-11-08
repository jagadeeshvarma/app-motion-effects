# Contributing

Thanks for helping make app motion more useful, accessible and appropriate to the product.

## Start with the problem

Open an issue for substantial direction changes; focused corrections can go straight to a pull request. Describe the actual customer task, constraints and observable failure. Use a small synthetic reproduction. Never include private app data, credentials, personal customer information or paid source you cannot redistribute.

This is a portable skill, not a generic redesign recipe. Keep product-specific context in the target app. Preserve existing branding, state, accessibility and task scope. A recommendation to keep the current interaction or add no motion is welcome.

## Local checks

Node.js 22+ and Python 3 are needed for repository checks; the installed skill needs neither.

```sh
npm ci
npx playwright install chromium
npm test
npm run package
```

For Linux browser setup, use `npx playwright install --with-deps chromium`. Preview with `npm run serve` and open http://localhost:4173. Test representative desktop/narrow layouts, keyboard input and reduced motion. Check actual playback for motion changes, including interruptions and repeated actions. Explain limitations honestly.

## Submit a pull request

1. Fork the repo and create a focused branch.
2. Change the relevant skill/reference or example. Avoid duplicating the taxonomy in the entrypoint.
3. Add focused tests for meaningful new risks; avoid tests that only match instruction wording.
4. Run the checks. Include the problem, resulting behaviour, actual validation and any source/licence information.
5. If the version changes, keep SKILL.md metadata and package.json in sync. Packaging derives its version from SKILL.md.

Provide before/after renders and replay steps for visual changes. Skill-decision changes benefit from contrasting context scenarios; label proposal reviews separately from executed app tests. Do not claim a native runtime or agent was tested unless it was.

Maintainers review and merge contributions. No CLA or mandatory purchase is required. By submitting a contribution, you agree to license it under this repository’s MIT licence and confirm you have the right to contribute it. Follow the [code of conduct](CODE_OF_CONDUCT.md).

## Updating the full-repository prompt

Edit `docs/full-repo-prompt.txt`, then run `npm run sync:prompt` and `npm run format`. This keeps the README code block and the page’s copyable prompt identical. GitHub supplies its own copy control for fenced code blocks; the static website implements the clipboard button and an honest manual fallback. Browser tests verify the full copied text.

## Skill behaviour and package changes

The reviewed runtime file list is `scripts/skill-manifest.json`. Add a resource there deliberately; unexpected files and symlinks fail packaging. `npm test` includes package containment and disposable installation regressions. Audit fixtures, logs and development scripts belong outside the installed skill.

Behavioural changes should include equal-budget fresh-context comparisons against the previous skill and an agent without it when practical. Keep graders outside the evaluated context, freeze criteria first, use synthetic data, and report blocked tools rather than counting them as passes. Web/mobile guidance, builds and actual native playback are different evidence levels. The reproducible corpus is documented in `evals/README.md`; running model evaluations uses authenticated quota and is intentionally not an ordinary contribution CI prerequisite.

For an existing local skill, review the diff and make a backup before replacement. Keep the backup outside discovery directories to avoid loading two versions. Confirm the intended version is discovered; restore the backup if verification fails. Do not overwrite unrelated local customisations.
