# Validation and limits

## Skill version 2.0.0 baseline

Before publication, the skill was evaluated against eight contrasting decision scenarios: repeated business work, consumer learning, consequential transactions, creative manipulation, constrained native/offline use, incomplete brand guidance, a narrowly scoped change and unavailable/licence-restricted examples. These were decision reviews, not eight implemented applications. A separate host-versus-target instruction-scope review was also performed.

Two isolated synthetic Chrome fixtures were implemented and checked: nine business-workflow check groups, plus seventeen core creative-canvas checks and three pointer-ownership checks. Resting before/after desktop screenshots were byte-identical. Drafts, focus, existing visual tokens and local timing were preserved. Actual playback was captured; the MP4s in this repository come from those runs.

Codex discovery was verified in the author’s environment. Claude Code installation files were checked; no Claude model run was performed. This does not establish behaviour for every agent or version.

## Public repository checks

The public gallery now presents six scenarios: loading, slow connection, connection loss/recovery, upload progress, save feedback and direct manipulation. A shared original state simulator implements the first four without network calls. It uses parent-only, same-origin messages for review controls. Existing save and canvas fixtures retain their own visual systems.

Current automated checks are in `tests/`, with results visible in [GitHub Actions](https://github.com/jagadeeshvarma/app-motion-effects/actions). Seventeen browser tests cover actual loading-animation sampling and stable row geometry, cancellation and stale callbacks, honest offline retries and preserved drafts, paused/resumed/cancelled uploads, repeated starts, reduced motion, keyboard focus recovery, touch manipulation, mobile version switching and all six scenarios at 320, 390, 768 and 1440 pixels.

Timer-focused tests use Playwright's virtual clock after observing the corresponding start state. Playback sampling, screenshots and recordings use real browser time. Captures establish appearance; interaction assertions and playback establish behaviour. The original v2.0.0 two-fixture baseline above remains distinct from these public-gallery additions.

The review shell preserves the existing neutral/green tokens and system typography. The revised layout removes decorative eyebrow labels and uses direct example names, plain explanations and a mobile Before/After switch. Run `npm test` to reproduce the checks. Generate renders with `npm run screenshots`; `node scripts/record.mjs` records the loading sequence when Playwright's optional FFmpeg helper is installed.

Source selection: original CSS/JS rather than an additional engine is sufficient for these small examples. Technical references: [reduced motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion), [progress semantics](https://www.w3.org/WAI/ARIA/apg/practices/range-related-properties/). No external implementation or asset was copied.

The Pages workflow reruns the checks before publishing. Required CI must pass before a pull request merges into main. No branch-protection bypass is used. Skill instructions and the v2.0.0 downloadable skill package are unchanged by the gallery update.

## Explicit limits

- Synthetic local operations only; no messages, payments or real account changes.
- Browser widths and touch emulation do not establish native platform support.
- No native hardware, screen-reader session, sustained frame-rate/battery benchmark or WCAG certification.
- No guarantee of identical agent decisions or integration with every client.
- The reference catalogue is a research shortlist, not a complete or perpetual licence/maintenance audit.
- Before versions intentionally retain baseline limitations for comparison. They are not recommended production snippets.
- Automated checks are bounded regression evidence, not proof that all visual or interaction defects are absent.
