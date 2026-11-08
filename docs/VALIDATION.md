# Validation and limits

## Skill version 2.0.0 baseline

Before publication, the skill was evaluated against eight contrasting decision scenarios: repeated business work, consumer learning, consequential transactions, creative manipulation, constrained native/offline use, incomplete brand guidance, a narrowly scoped change and unavailable/licence-restricted examples. These were decision reviews, not eight implemented applications. A separate host-versus-target instruction-scope review was also performed.

Two isolated synthetic Chrome fixtures were implemented and checked: nine business-workflow check groups, plus seventeen core creative-canvas checks and three pointer-ownership checks. Resting before/after desktop screenshots were byte-identical. Drafts, focus, existing visual tokens and local timing were preserved. Actual playback was captured; the MP4s in this repository come from those runs.

Codex discovery was verified in the author’s environment. Claude Code installation files were checked; no Claude model run was performed. This does not establish behaviour for every agent or version.

## Public repository checks

The public demos add parent-only, same-origin review hooks for replay and reduced-motion comparison. Their current automated checks are in `tests/`, with results visible in [GitHub Actions](https://github.com/jagadeeshvarma/app-motion-effects/actions). Checks cover structure/local links, draft truthfulness, persistent failures and recovery, keyboard precision, interrupted reset, reduced motion, review-control draft preservation and responsive overflow.

The deploy workflow reruns checks before publishing the static site. Run `npm test` to reproduce locally. Rendered gallery screenshots are included in `media/`. Browser screenshots establish appearance; playback sampling and interactions establish motion behaviour.

## Explicit limits

- Synthetic local operations only; no messages, payments or real account changes.
- Browser widths and touch emulation do not establish native platform support.
- No native hardware, screen-reader session, sustained frame-rate/battery benchmark or WCAG certification.
- No guarantee of identical agent decisions or integration with every client.
- The reference catalogue is a research shortlist, not a complete or perpetual licence/maintenance audit.
- Before versions intentionally retain baseline limitations for comparison. They are not recommended production snippets.
- Automated checks are bounded regression evidence, not proof that all visual or interaction defects are absent.
