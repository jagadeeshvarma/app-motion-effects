# Validation and limits

## Skill version 2.0.0 baseline

Before publication, the skill was evaluated against eight contrasting decision scenarios: repeated business work, consumer learning, consequential transactions, creative manipulation, constrained native/offline use, incomplete brand guidance, a narrowly scoped change and unavailable/licence-restricted examples. These were decision reviews, not eight implemented applications. A separate host-versus-target instruction-scope review was also performed.

Two isolated synthetic Chrome fixtures were implemented and checked: nine business-workflow check groups, plus seventeen core creative-canvas checks and three pointer-ownership checks. Resting before/after desktop screenshots were byte-identical. Drafts, focus, existing visual tokens and local timing were preserved. Actual playback was captured; the MP4s in this repository come from those runs.

Codex discovery was verified in the author’s environment. Claude Code installation files were checked; no Claude model run was performed. This does not establish behaviour for every agent or version.

## Public repository checks

The current gallery contains ten interactions: content loading, an indeterminate loader, slow connection, connection recovery, file upload, saving, filtering, notifications, a side panel and tabs. A shared original simulator implements them without application service calls. The earlier standalone save/canvas fixtures remain as historical baselines with their own regression tests.

The page has a full-viewport workbench, desktop left navigation, a large After preview, optional Before/Compare modes and a compact mobile selector. The hero uses the same saving primitive. The visual contract retains the paper/green tokens and system typography, with no decorative eyebrow labels or arrow links.

Thirty-three browser tests cover the current workbench and retained fixtures: actual animation sampling, row geometry, cancellation, honest retries, draft and error preservation, paused progress, keyboard modal/tab behaviour, notification dwell/fading, five responsive widths, reduced motion, full prompt equality and a real clipboard round trip. Clipboard-denial coverage checks the selected-text fallback and honest feedback. Results are in [GitHub Actions](https://github.com/jagadeeshvarma/app-motion-effects/actions).

Timer-focused checks use Playwright’s virtual clock after observing the corresponding state. Playback, screenshots and recordings use real browser time. Screenshots establish appearance; played interactions establish motion. Mobile widths are web previews, not native device certification.

The full-repo invocation prompt has one canonical text file. `scripts/sync-prompt.mjs` writes it into both the README’s native copyable code block and the page’s read-only textarea. The public clipboard button copies the complete value, not a summary. GitHub README JavaScript buttons are not used.

Original CSS, SVG, native Web Animations and native dialog semantics are sufficient; no new runtime dependency or animation engine was added. References: [Clipboard writeText](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText), [native dialog](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog), [tabs pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/). No external implementation or asset was copied.

Run `npm test` for verification, `npm run screenshots` for actual renders and `node scripts/record.mjs` for loading/saving playback when Playwright’s optional recording helper is installed. Required CI must pass before merging; Pages reruns checks before deployment. Version 2.1.0 adds the audited skill guidance. Its comparative failures and unverified platforms remain explicit; see the maintainer evaluation below.

## Explicit limits

- Synthetic local operations only; no messages, payments or real account changes.
- Browser widths and touch emulation do not establish native platform support.
- No native hardware, screen-reader session, sustained frame-rate/battery benchmark or WCAG certification.
- No guarantee of identical agent decisions or integration with every client.
- The reference catalogue is a research shortlist, not a complete or perpetual licence/maintenance audit.
- Before versions intentionally retain baseline limitations for comparison. They are not recommended production snippets.
- Automated checks are bounded regression evidence, not proof that all visual or interaction defects are absent.

## Maintainer evaluation

The [maintainer audit](audit/SKILL_AUDIT.md) preserves this earlier validation as the baseline and separates structural checks, authored website tests, comparative agent-generated outputs and native runtime evidence. See its explicit result states and limitations before interpreting support claims. The dependency-free installed package excludes audit logs and evaluation projects.
