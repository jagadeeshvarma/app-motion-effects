# Product-led adaptation

Use before choosing effects. Read only relevant sections for a focused request; use the complete process for broad passes. Produce enough evidence to make good decisions, not a lengthy report or fictional customer research.

## 1. Establish the context

Inspect repository product notes, onboarding/help copy, real screen behaviour, roles, analytics/research already available and recorded decisions. Use authorised connected sources when useful; do not transmit private project/customer information to external design or search services.

Capture a brief evidence-led profile:

| Dimension | Establish | Decision affected |
| --- | --- | --- |
| Product purpose | What task/outcome does this product support? What is the requested scope? | Whether an effect helps and what remains out of scope |
| Customers and roles | Who actually uses it? Separate operator, buyer, administrator and end-user where evidence supports this | Role-specific emphasis, information needs and trust |
| Jobs and workflows | Important tasks, sequence, repetition, time pressure, interruptions and error recovery | Rhythm, continuity and feedback placement |
| Frequency and consequence | Occasional discovery vs repeated operations; reversible vs consequential actions | Expressive intensity, dwell/duration and persistence of errors |
| Access and input | Supported accessibility needs, language/localisation, input methods, devices and skill with the task | Meaningful static alternatives, readable timing and non-hover operation |
| Environment and resources | Connectivity, field/desk use, device/runtime constraints and available performance evidence | Asset choice, rendering strategy, offline feedback and budgets |
| Existing strengths | Which familiar interactions and styles already work? | Retain, refine or add; no change is an acceptable outcome |

Label each decision-driving statement as verified (cite its source), inferred (state basis/confidence) or unknown. Do not infer demographics, preferences, disabilities or research results from an industry label. When evidence is thin, use the established interaction system and conservative inference. Ask only for an unknown that materially changes the design and cannot be resolved by inspection.

For a single button, a few sentences about its user/task, existing pattern, constraints and intended feedback can suffice. Do not audit the whole business before correcting a local interaction.

## 2. Establish the visual contract

Use current explicit user direction, applicable repository instructions, approved design assets/tokens and recorded decisions as authority, subject to the environment's instruction hierarchy. Use consistent shipped components and their actual renders to resolve unspecified details. Check freshness and provenance: old mockups, external demos and accidental shipped violations are not new approvals.

Record the relevant invariants and source locations:

- Approved logo/assets, palette/semantic colours and themes.
- Type family, scale, weight, density and text/copy conventions.
- Spacing, sizing, component geometry, radius, borders and elevation.
- Icon family/stroke/optical sizing and illustrations where permitted.
- Layout/navigation, interaction patterns and existing motion tokens.
- Accessibility, responsiveness, localisation and explicit forbidden patterns.

Distinguish immutable brand rules, established component behaviour and details that can be adapted within the system. A new interaction should use existing primitives and tokens; it must not quietly introduce a new brand system. If a required treatment has no safe in-system interpretation, ask a targeted question or propose a clearly marked alternative before implementation of that treatment. Continue unaffected authorised work.

Do not over-ask about routine choices already determined by the system. Do not fabricate a brand policy from your taste. Do not preserve a known violation merely because it appears on an old or currently shipped screen.

## 3. Derive the app's motion direction

State a short direction grounded in the profile and contract. Establish only details needed for this request:

- Purpose: continuity, acknowledgement, status comprehension, direct manipulation, instruction or permitted expression.
- Expressive intensity: restrained, moderately expressive or expressive, with evidence; not an industry preset.
- Rhythm: how repeated tasks, occasional exploration and consequential actions should feel.
- Hierarchy: which events deserve attention; which should be immediate, quiet or unchanged.
- Vocabulary: existing timing, easing/springs, distance/scale, sequencing and component patterns; extensions need a reason.
- Reduced-motion/static equivalents and platform-native conventions.
- Relevant asset/dependency/frame-time budgets from the project or measured baseline; label estimates instead of inventing targets.

Different journeys or roles can have different emphasis while retaining semantic consistency. The same kind of action should convey the same meaning across the app. Branding does not justify identical animation on every control, and customer fit does not justify incompatible per-screen systems.

Do not require signature animation everywhere. A conventional fade or immediate state change can be the best app-specific decision when justified. Distinctiveness comes from coherent fit, not unusual effects for their own sake. Do not promise universal perfection or legal exclusivity.

## 4. Adapt mechanisms into the actual app

Follow the chain: observed task/problem -> intended behaviour -> visual contract -> relevant mechanism -> inspected source -> app-specific integration -> rendered evidence.

Inspect at most two serious candidates for the improvement, including existing capabilities. Search the catalogue only after identifying the need. Compare behavioural fit, existing-system compatibility, accessibility, interruption, platform maturity, licences, performance and maintenance. Avoid arbitrary numerical scores presented as research.

For adopted code, identify:

| Layer | Required adaptation |
| --- | --- |
| Behaviour | Real trigger, correct pending/final/error states, actual user task and interruption rules |
| Application integration | Existing state, data lifecycle, record/request identity, navigation and shared component ownership |
| Visual expression | Existing tokens, geometry, type/icons, hierarchy, timing and responsive treatment |
| Platform/access | Real input methods, native/runtime support, focus/announcements and reduced motion |
| Maintenance | Strip demo data/styles and unrelated dependencies; keep provenance, notices and testable boundaries |

Adapt only where needed: a suitable library primitive need not be copied or forked. App-owned interaction components can depend on existing engines and accessible controls. Preserve derivative/source notices; rewriting names or recolouring does not make borrowed work original.

Prefer focused original code when it clearly improves the fit or cost. Explain the mechanism and tradeoff. Do not browse endlessly when an existing in-project solution is already strong, and do not claim superiority over an alternative you did not inspect.

## 5. Review fit before acceptance

For each meaningful change answer:

1. Which evidenced user/task need does this serve, and why this treatment for this app?
2. What matches the visual contract? Compare actual before/after renders and component states, not only source token names.
3. What would the user lose if the effect were removed? A permitted experience benefit can count when concrete; novelty alone cannot.
4. Is the effect proportionate to frequency, consequence, accessibility and performance constraints?
5. What was deliberately retained, omitted or simplified, and why?
6. What source/integration choices distinguish this from a cosmetically recoloured gallery component?

If the benefit is weak, remove/simplify it or retain the existing interaction. Do not respond by making the effect louder. Keep focused work focused. Verify actual behaviour with the companion verification guide.

## Context isolation

Keep this profile/direction with the target project's permitted review/design records, scaled to scope. Do not silently edit this global skill, accumulate customer data in personal memory, or carry one project's brand, personas or decisions into another. Adapt on each use; permanent skill changes require an explicit request to update the skill.
