# Playback and behaviour verification

Use checks relevant to the actual change. A focused change does not require unrelated application-wide testing. For broad passes, track representative patterns and every distinct major journey/role boundary.

## Establish the baseline

- Record the actual entry route, role, state, framework/runtime version and viewport/device. An auth gate is not feature coverage.
- Capture current behaviour and identify the expected result before implementation. Do not invent a before state retrospectively.
- Identify existing business responses, pending/retry semantics, request identity, focus and scroll ownership.
- For expensive work, compare representative interaction timing, frame pacing and asset/bundle cost before and after.

## Observe the interaction

- Trigger the actual event. Check start, intermediate, final and exit states, not just a resting screenshot.
- Confirm success/error/progress cues match actual responses. Do not substitute a timed success cue for a failed request.
- Check repeated taps, rapid state changes, reversed gestures, cancellation, retargeting, back navigation and component removal.
- Confirm the final state remains correct with animation disabled. Business behaviour must not depend on an animation finishing.

## Verify product and brand fit

- Trace the treatment to an evidenced customer/task need and the app-specific motion direction. Label assumptions and unknowns; do not accept fabricated personas or industry stereotypes as evidence.
- Compare actual before/after renders against the visual contract: assets, colours, typography, spacing/geometry, icons, hierarchy, copy/navigation and existing interaction patterns. Token reuse alone does not prove composition matches the brand.
- Review normal, pending, disabled, error and reduced-motion states for the same contract. Do not let an internet example's default styling reappear in less-visible states.
- Perform the removal test: identify concrete information, continuity or permitted experience lost without the effect. If the benefit is weak, remove/simplify it or retain the existing pattern.
- Check proportionality to task frequency, consequences of mistakes, input/device context and resources. Assess role/journey variation within one coherent system, not disconnected presets.
- Verify adopted code was adapted to actual state, primitives, tokens and platform/access behaviour. Cosmetic recolouring and renamed classes do not establish app-specific integration. Retaining a suitable library is valid; unjustified rewrites are not required.
- Confirm focused requests did not grow into brand redesign or unrelated audits, and project context was not persisted into global skill instructions or another app.

## Preserve application state

- Open a form, enter a draft and switch viewport/orientation or reveal the keyboard. Confirm values, input node/state where relevant, focus and selection survive.
- Resize with a nested dialog, dropdown or leave-confirmation open. Verify valid stacking, focus, Escape/back behaviour and safe popup repositioning or collapse.
- Switch the selected record during a pending or uncertain action. Confirm old errors and recovery keys do not leak into the new record.
- Confirm optimistic updates reconcile or roll back and explicit retries preserve idempotency. Animate existing state; do not invent a new business retry policy.
- Confirm filters, sorting, insertion and removal preserve sensible item identity, scroll and keyboard focus.

## Inputs, appearance and access

- Exercise relevant mouse, keyboard and touch paths, including non-hover operation and visible focus.
- Check screen-reader names, live announcements and reading/focus order where affected. Prevent duplicate announcements from overlapping old/new views.
- Review normal and reduced motion, approved themes, long/localised text and supported role/permission states. Do not add a theme selector to test a product that deliberately has none.
- Include relevant loading, empty, pending, disabled, success, error, interrupted and recovered states.
- Check narrow supported widths, desktop/tablet and relevant native devices. Inspect clipping, overlap, unwanted scrolling, text distortion, stacking, scroll jumps and invisible hit targets.
- Respect system accessibility settings. Do not make animation, colour, sound or haptics the sole essential signal. Avoid flashing and unnecessary disorientation.

## Performance and lifecycle

- Profile representative interactions on available target hardware/runtime. Report conditions; do not infer native performance from a desktop web preview.
- Examine dropped frames/frame pacing, main/UI-thread work, layout/paint, re-renders, memory/GPU resources, startup/route costs, asset/dependency size and sustained battery work where measurable.
- Check background/offscreen behaviour, mount/unmount cleanup and repeated navigation for accumulating timers, observers, listeners, render loops or GPU resources.
- Prefer efficient properties where suitable. Measure rather than treating all transforms as free or all layout animation as unacceptable.
- Lazy-load specialist rendering where justified and provide an honest fallback when unavailable.

## Evidence and gates

- Run applicable target-app build/type/lint/content/accessibility/tests. Resolve their documented scope and instruction hierarchy; do not classify a checker from the skill's host project as a target gate merely because it is available. Add focused tests only for meaningful risks. Preserve existing assertions.
- Record actual commands and outcomes, with pre-existing failures separated. Never equate compilation or zero console errors with complete visual verification.
- Capture appearance screenshots plus playback recordings for important animations where tools support them. No recording tool: provide a runnable replay and exact interaction steps, with the limitation stated.
- Keep secrets, real personal data and protected credentials out of screenshots, recordings and traces. Use permitted synthetic environments for mutating tests.
- Label fixture states, stubbed actions, real test-service actions, blocked routes and unverified native/provider behaviour accurately.
- Do not claim WCAG conformance, a sustained frame rate, provider delivery or production release from narrower evidence.

## Release, only when authorised

Follow the app's normal process and verify the exact reviewed source/build. Keep unrelated changes and review-only fixtures/controls out of production. Preserve required credits. Retain the established rollback path and verify the real live URL or released native version. Distinguish local preview, staged build, test distribution, store submission and actual production release.
