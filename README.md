<div align="center">

# App Motion & Effects

### Motion that belongs in your app.

A product-aware skill for coding agents that designs, implements and verifies meaningful animations, transitions and effects **within your existing brand and visual system**.

[**Try the live playground →**](https://jagadeeshvarma.github.io/app-motion-effects/) · [Install](#quick-start) · [Read the skill](skills/app-motion-effects/SKILL.md) · [Contribute](CONTRIBUTING.md)

[![Checks](https://github.com/jagadeeshvarma/app-motion-effects/actions/workflows/checks.yml/badge.svg)](https://github.com/jagadeeshvarma/app-motion-effects/actions/workflows/checks.yml)
[![Pages](https://github.com/jagadeeshvarma/app-motion-effects/actions/workflows/pages.yml/badge.svg)](https://github.com/jagadeeshvarma/app-motion-effects/actions/workflows/pages.yml)

**Codex · Claude Code · compatible Agent Skills clients**<br>
MIT licensed · 63 technical categories · 31 source groups · No skill runtime dependencies

</div>

[![Interactive before/after playground](docs/media/playground-desktop.png)](https://jagadeeshvarma.github.io/app-motion-effects/)

## What it does

An operations console, a learning app and a creative canvas need different movement. This skill starts with the customer’s task, the consequences of mistakes and the app’s existing design rules. It then selects and implements an appropriate mechanism, verifies actual playback and checks that the original workflow still works.

- **Fit first.** Frequency, precision, accessibility, device constraints and customer context shape each decision. No invented personas or mandatory “signature” effects.
- **Strict brand fidelity.** Existing tokens, typography, geometry, copy conventions and interaction patterns form an explicit visual contract.
- **Deliberate adaptation.** Research useful mechanisms, reuse suitable libraries or examples, and integrate them with the app’s real components and state. Original code is welcome when it serves the job better.
- **Behaviour survives.** Preserve drafts, focus, permissions and business logic. Handle interrupted, repeated, loading and failed actions.
- **Evidence over claims.** Render and play the result. Test reduced motion, keyboard and relevant touch behaviour. State what remains unverified.
- **Scope stays yours.** Focused fix, app-wide pass, audit or isolated mockup. Invoking a skill does not grant permission to deploy, purchase or mutate accounts.

Sometimes the right decision is to keep the existing interaction or add no animation.

## See it in action

[**Open the interactive playground**](https://jagadeeshvarma.github.io/app-motion-effects/) and switch between the two examples. Compare before/after, replay a shared action, narrow the previews and enable reduced motion. The gallery controls are separate from the example interfaces.

| Example | What changes | What remains |
| --- | --- | --- |
| **Creative canvas** | A 180 ms, interruptible return to the original position. Direct dragging stays immediate. | Paper palette, typography, object geometry, keyboard precision and the caption draft. |
| **Business workflow** | Subtle pending feedback, stable save control, truthful snapshot/draft status and persistent failure recovery. | Compact layout, neutral palette, labels, save timing and existing form state. |

**Try this:** move the canvas object and select Reset. Interrupt its return with an arrow key. Then switch to Business workflow, save a note and keep typing during the save. Enable a simulated failure and retry.

[![Recorded canvas reset playback](docs/media/studio-playback.gif)](https://jagadeeshvarma.github.io/app-motion-effects/#playground)

*Actual recorded fixture playback. [Canvas MP4](docs/media/studio-playback.mp4) · [Save feedback MP4](docs/media/dispatch-playback.mp4). The live examples also work without video playback.*

Both examples use synthetic content and original HTML/CSS/JS/SVG. No backend, analytics, external fonts or paid assets. They illustrate two bounded interactions; they are not a promise that every category, native platform or agent has been tested. [Evidence and limits](docs/VALIDATION.md).

## Quick start

### 1. Get the source

```sh
git clone https://github.com/jagadeeshvarma/app-motion-effects.git
cd app-motion-effects
```

Prefer a portable ZIP? [Download the latest release](https://github.com/jagadeeshvarma/app-motion-effects/releases/latest). Release assets include SHA-256 integrity records.

The installable skill is **`skills/app-motion-effects/`**. Copy the whole folder, including references and licence. Review an existing same-named installation first; the commands below intentionally stop rather than replace it.

### 2. Install for your agent

**Codex — personal installation**

```sh
mkdir -p ~/.agents/skills
test ! -e ~/.agents/skills/app-motion-effects && \
  cp -R skills/app-motion-effects ~/.agents/skills/app-motion-effects
```

**Claude Code — personal installation**

```sh
mkdir -p ~/.claude/skills
test ! -e ~/.claude/skills/app-motion-effects && \
  cp -R skills/app-motion-effects ~/.claude/skills/app-motion-effects
```

For project-local use, copy the folder into the **target app’s** `.agents/skills/` (Codex) or `.claude/skills/` (Claude Code). Do not install the same skill independently into overlapping discovery locations. Refresh or start a new agent session and confirm discovery.

These locations follow [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) and [Claude Code skill documentation](https://code.claude.com/docs/en/skills). Client versions and managed settings may affect availability. Local Claude Code installation does not automatically install into Claude cloud or Cowork.

**Another coding agent?** Use its documented Agent Skills directory, or give it the entrypoint directly:

```text
Read /path/to/app-motion-effects/skills/app-motion-effects/SKILL.md
and use it for this task. Resolve references relative to that skill folder.
Follow the target repository’s instructions and the authorised task scope.
```

The package uses the [Agent Skills format](https://agentskills.io/specification). `agents/openai.yaml` is optional Codex presentation metadata. No plugin, MCP server, animation library or paid account is required to install it. Tools needed to build and verify an actual app depend on that app and your agent environment.

### 3. Ask for a concrete outcome

**Codex**

```text
Use $app-motion-effects to improve meaningful animations, transitions
and effects in this app. First understand our customers, workflows and
existing visual system. Preserve our branding and business behaviour.
Build and verify an isolated interactive preview. Do not deploy.
```

**Claude Code**

```text
/app-motion-effects Improve meaningful animations, transitions and
effects in this app. Understand our customers and existing visual
system first. Build and verify an isolated preview. Do not deploy.
```

**Focused change, any agent**

```text
Use the app-motion-effects skill to improve only the save interaction
in this form. Preserve its layout, headings, field labels and design
tokens. Verify pending, success, error, edits during save, focus and
reduced-motion behaviour. Do not deploy.
```

## How it works

| Step | The agent’s decision |
| --- | --- |
| Understand | Verify product purpose, customer jobs, roles, task frequency, consequences, devices and constraints. Separate facts from assumptions. |
| Preserve | Establish a visual contract from current instructions, approved assets and conservative shipped patterns. |
| Choose | Define purpose, intensity, rhythm, timing, easing, interruption and reduced-motion treatment before browsing effects. |
| Research | Compare at most two serious candidates for a need. Prefer existing tools; inspect current source, compatibility and terms. |
| Build | Adapt mechanisms to actual components, tokens, state and input. Remove demo styling and unnecessary dependencies. |
| Verify | Play, interrupt, resize and exercise states. Check draft/focus preservation, accessibility, performance and contextual fit. |
| Deliver | Provide a reviewable preview, source credits and honest evidence. Respect the user’s release boundary. |

The removal test asks: **what useful information, continuity or permitted experience disappears if this effect is removed?** Cosmetic recolouring alone is insufficient adaptation.

## Coverage and sources

The [63-category taxonomy](skills/app-motion-effects/references/taxonomy.md) covers interface and navigation motion; layout/presence and shared elements; input and gesture feedback; loading/status/data transitions; SVG, typography, particles, 3D and shaders; timing, easing, physics, timelines, state machines and orchestration; plus appropriate haptics, audio, sensors and multimodal feedback.

It is a coverage reference, not a requirement to add every effect.

The [source catalogue](skills/app-motion-effects/references/sources.md) groups resources by mechanism and platform. Examples include:

| Need | Starting points |
| --- | --- |
| Web layout, presence and shared elements | [Motion](https://motion.dev/docs), [View Transitions](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API) |
| DOM/SVG timelines and choreography | [Anime.js](https://animejs.com/documentation/), [GSAP](https://gsap.com/docs/v3/) |
| Springs, gestures and manipulation | [React Spring](https://www.react-spring.dev/docs/getting-started), [use-gesture](https://use-gesture.netlify.app/docs/) |
| UI components and interaction patterns | [shadcn/ui](https://ui.shadcn.com/docs/components), [Radix](https://www.radix-ui.com/primitives/docs/guides/animation), [React Bits](https://reactbits.dev/), [Magic UI](https://magicui.design/) |
| Native motion and graphics | [Reanimated](https://docs.swmansion.com/react-native-reanimated/), [React Native Skia](https://wcandillon.github.io/react-native-skia/) |
| Interactive vectors and animation assets | [Rive](https://rive.app/docs/getting-started/introduction), [LottieFiles](https://lottiefiles.com/) |
| Charts, 3D, sensory feedback and other frameworks | [Full catalogue →](skills/app-motion-effects/references/sources.md) |

The agent can research beyond this list or author a better-fitting implementation. Links are references, not endorsements, compatibility guarantees or licence grants. External code, assets, editors and runtimes may have different commercial and attribution terms. Web support does not imply native support.

## Develop and contribute

The skill is dependency-free text. The optional website is static; development-only browser tests use Node.js 22+ and Python 3.

```sh
npm ci
npx playwright install chromium
npm test
npm run serve             # http://localhost:4173
npm run package           # dist/ ZIP + SHA-256 manifests
```

The checks validate package structure, local links, portability and interactive example behaviour. Pull requests run the same checks. The Pages workflow validates before publishing. [Contributing guide](CONTRIBUTING.md) · [Code of conduct](CODE_OF_CONDUCT.md) · [Security policy](SECURITY.md).

Useful contributions include a reproducible interaction bug, a well-scoped adaptation improvement, verified platform guidance or a source/licence correction. Explain the customer task and show observed evidence. Keep project-specific brand rules and private data out of this reusable skill.

## Repository map

```text
skills/app-motion-effects/   Installable skill, references and review template
docs/                       Static playground, original demos and rendered media
tests/                      Browser checks for meaningful interaction risks
scripts/                    Portable structure checks and release packaging
.github/                    CI, Pages and contribution templates
```

## Licence and provenance

Original skill text, examples, screenshots and recordings are released under the [MIT licence](LICENSE), copyright Jagadeesh Varma. Keep the licence notice when redistributing. External resources retain their own terms; linking to them does not relicense them. No third-party component source or animation assets are bundled. [Provenance and third-party notices](THIRD_PARTY_NOTICES.md).

Maintained by [Jagadeesh Varma](https://github.com/jagadeeshvarma). Agent-assisted development; human review and application-specific verification remain necessary. No guarantee of identical decisions across agents or complete accessibility conformance.
