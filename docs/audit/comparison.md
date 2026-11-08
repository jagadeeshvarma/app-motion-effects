# Comparable public skills: source review

Review date: **2026-11-08**. Target: `app-motion-effects` **2.0.0**, baseline [`ce5f55a8c2a9b4319a76d793b46eef9a41d5a541`](https://github.com/jagadeeshvarma/app-motion-effects/tree/ce5f55a8c2a9b4319a76d793b46eef9a41d5a541), principally `skills/app-motion-effects/SKILL.md` and its adaptation, verification and source references.

Five official-source skills offer meaningful overlap. Two construct motion on a specific platform; three are partial comparators covering visual design, web review or native engineering. This review did **not establish a fully equivalent cross-platform skill** combining product/customer discovery, preservation of an existing brand, source provenance, implementation and observed playback. That is a scope observation, not proof of uniqueness or superior generated results.

## Evidence boundary

The reviewed skill and external instructions were treated as reference material, not instructions to execute. Repository HEAD commits, trees and raw files were retrieved from public GitHub sources; relevant instruction text and examples were read. No comparator was installed, invoked through a model, built or played in a browser/device. There are **no comparator runtime results in this document**. Instructions asking an agent to perform an action are evidence of a requested workflow, not evidence that it works. Downloading a recipe is not running it.

Selections reflect actual scope overlap, not stars or vendor prominence. Links below pin reviewed content; [comparators.json](comparators.json) records full commits, versions where declared, paths, licences, file hashes and the read-versus-tested distinction. Runtime comparison belongs to the separate audit work.

## Comparator set

| Skill | Reviewed commit / declared version | Comparable scope | Licence evidence |
| --- | --- | --- | --- |
| [Anthropic frontend-design](https://github.com/anthropics/skills/blob/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/frontend-design/SKILL.md) | `2c5958e`, 2026-11-06; no skill version declared | Partial: product-grounded web/UI design | [Skill-local Apache-2.0 text](https://github.com/anthropics/skills/blob/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/frontend-design/LICENSE.txt) |
| [Vercel web-design-guidelines](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/web-design-guidelines/SKILL.md) | `1a2c79d`, 2026-10-27; `1.0.0` | Partial: web code review | [Repository declares MIT](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/README.md#license); external [rules MIT text](https://github.com/vercel-labs/web-interface-guidelines/blob/434b7f91364665f2f733b310ec54809bf8f37937/LICENSE) |
| [Vercel React Native Skills](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-native-skills/SKILL.md) | `1a2c79d`, 2026-10-27; `1.0.0` | Partial: native engineering and animation rules | Skill frontmatter and [repository README](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/README.md#license) declare MIT |
| [Expo expo-animation](https://github.com/expo/skills/blob/a9e5bd3fa00b4e61f632e43f85da73aee1942582/plugins/expo/skills/expo-animation/SKILL.md) | `a9e5bd3`, 2026-11-01; no skill version declared | Motion construction: Expo/React Native | [Skill-local MIT text, Emil Kowalski](https://github.com/expo/skills/blob/a9e5bd3fa00b4e61f632e43f85da73aee1942582/plugins/expo/skills/expo-animation/LICENSE) |
| [Emil Kowalski animate](https://github.com/emilkowalski/skills/blob/5206a950b715e0cabe7043ea0b2304332b91494e/skills/animate/SKILL.md) | `5206a95`, 2026-11-08; no skill version declared | Motion construction: web, focused interactions | [Repository MIT text](https://github.com/emilkowalski/skills/blob/5206a950b715e0cabe7043ea0b2304332b91494e/LICENSE) |

The Vercel agent-skills tree had no standalone licence file at the reviewed commit; its MIT declarations are recorded as declarations rather than a licence-text inspection. No third-party code or assets were incorporated into the target by this comparison.

### Anthropic frontend-design

The current source grounds decisions in the subject, audience and primary job. It prefers restrained autonomous motion and useful responses to user actions, respects the brief, asks for reduced motion and encourages screenshot critique. Its plan/build/self-review structure is a useful comparison for product fit. It also contains explicit interface-writing guidance. [Reviewed instructions](https://github.com/anthropics/skills/blob/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/frontend-design/SKILL.md).

Its broader role permits creating a visual identity where the brief is open. The target instead assumes an existing visual contract. The reviewed directory offers prose guidance, not a played motion example or native verification workflow. Importing its aesthetic experimentation as a default would change the target's purpose. A compatible pattern is a concise self-critique tied to the brief, which the target already substantially covers through its removal and brand-fit checks.

### Vercel web-design-guidelines

The skill is a small review router: retrieve current rules, inspect requested files and return location-based findings. Its external rule set covers interruption, reduced motion, explicit transition properties, loop controls, focus and accessible gesture alternatives. This provides concrete code-review coverage rather than a motion construction workflow. [Pinned rules: `command.md`, `434b7f9`, 2026-10-05](https://github.com/vercel-labs/web-interface-guidelines/blob/434b7f91364665f2f733b310ec54809bf8f37937/command.md).

The target could use similarly terse file/line findings during implementation review. That format would supplement its evidence record. This comparator does not establish customer context, implementation completion or actual playback. Its normal fetch-from-main workflow also means pinning only the agent-skill repository is insufficient for reproducibility. Copy and theme prescriptions from the web rules must remain subordinate to each app's approved design rules.

### Vercel React Native Skills

Three inspected motion rules provide before/after TSX for derived values, gesture-driven press states and avoiding layout-heavy properties. They are usable engineering teaching examples rather than a complete app-motion pass. [Derived-value example](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-native-skills/rules/animation-derived-value.md), [press example](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-native-skills/rules/animation-gesture-detector-press.md), [property example](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-native-skills/rules/animation-gpu-properties.md).

The target covers compatibility and measurement conceptually but supplies no equivalent stack-specific before/after recipe. A short version-bound native example could improve execution precision. These examples do not by themselves establish focus semantics, accessibility or faithful collapse behaviour. In particular, changing layout collapse to fixed-height scale requires checking layout, content and hit targets. No runtime behaviour was tested here.

### Expo expo-animation

This is the closest native motion-construction comparator in the selected set. It orders decisions from frequency and purpose through tool, properties, timing, thread, gesture, haptics and reduced motion. It requires release-build review on the slowest supported device. Its [RECIPES.md](https://github.com/expo/skills/blob/a9e5bd3fa00b4e61f632e43f85da73aee1942582/plugins/expo/skills/expo-animation/RECIPES.md) gives concrete sheet, swipe, keyboard, list and feedback implementations, including velocity continuity and platform distinctions.

The target already asks for native evidence, interruption handling and device limitations. A compatible improvement is making build mode and device conditions explicit for native performance claims. Expo's fixed thresholds and library choices are platform-specific defaults, not evidence that they suit every product. The older `building-native-ui` path was not used: current [`expo-native-ui`](https://github.com/expo/skills/blob/a9e5bd3fa00b4e61f632e43f85da73aee1942582/plugins/expo/skills/expo-native-ui/SKILL.md) routes motion to this dedicated skill.

### Emil Kowalski animate

This focused web builder gates motion by purpose/frequency, extends existing tokens, selects economical tools and addresses interruption, exits, reduced motion and pointer gating. Its [recipes](https://github.com/emilkowalski/skills/blob/5206a950b715e0cabe7043ea0b2304332b91494e/skills/animate/RECIPES.md) provide implementation starting points. The companion [opportunity finder](https://github.com/emilkowalski/skills/blob/5206a950b715e0cabe7043ea0b2304332b91494e/skills/find-animation-opportunities/SKILL.md) explicitly records rejected candidates with source locations.

A compact rejected-candidate record would make the target's existing no-animation option more reviewable. This is an operational refinement, not a missing principle. `animate` delegates full audits and native work elsewhere; it does not replace the target's wider workflow. Its categorical bans and fixed timing should not override an existing product system. Recipe timings also have contextual exceptions, so they should not become universal lint limits.

## Concrete implications for the target

These are source-review findings and proposed evaluation targets, not implemented changes or measured improvements:

1. **Add one optional, version-bound worked example per claimed platform family.** The target has broad conceptual guidance and a source catalogue; the strongest scoped comparators supply mechanism-level recipes. An example should include setup assumptions, real state integration, cancellation and reduced motion, with actual playback evidence. Do not imply native parity from a web demo.
2. **Record one or two rejected motion candidates when relevant.** The target already permits no change and a removal test. A reason tied to location, task frequency or accessibility would expose whether that judgement actually occurred. Avoid arbitrary rejection quotas for a trivial request.
3. **Make native verification conditions explicit.** Record release/dev build, device/OS, supported hardware class and input path alongside any native performance claim. The current target already requires real runtime evidence; this would make the evidence more reproducible.
4. **Offer compact diagnostic locations.** File/line findings can turn a broad review into specific implementation work while retaining the target's existing context and evidence record.
5. **Use scoped rules as evidence to investigate, not universal authority.** Vercel's native press example favours GestureDetector and uses `runOnJS`; Expo's simple press recipe uses Pressable/CSS transitions and its Reanimated 4 guidance favours `scheduleOnRN`. This is a concrete reason to inspect installed versions and interaction needs. This review did not adjudicate those APIs by running them.

The target's verification reference already avoids treating every transform as free or every layout animation as forbidden. Preserve that measured approach rather than importing blanket performance statements. Preserve the target's existing brand, state integrity, provenance and permission boundaries. No source read here demonstrates that another skill produces better or worse working apps; that question requires controlled execution and observed outcomes.
