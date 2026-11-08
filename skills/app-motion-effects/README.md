# App Motion & Effects

Portable Agent Skills package for implementing and verifying app animations, transitions, microinteractions, graphics/effects and appropriate sensory feedback without replacing the app's design rules.

Version 2.0.0 makes product/customer context and a strict visual contract the basis for effect selection. It preserves suitable existing patterns, adapts mechanisms into the app's actual components/state/tokens and checks contextual fit as well as playback. It does not require novelty or a new visual direction.

Version 2.0.1 is a maintenance release for package containment, local-reference validation and installation checks. The runtime workflow is unchanged from 2.0.0.

## Use

Codex:

```text
Use $app-motion-effects to improve meaningful animations, transitions and effects in this app. Preserve its design rules. Build and verify a working preview; do not deploy.
```

Claude Code:

```text
/app-motion-effects Improve meaningful animations, transitions and effects in this app. Preserve its design rules. Build and verify a working preview; do not deploy.
```

Focused request, either agent:

```text
Use the app-motion-effects skill to improve only the save interaction in this form. Preserve layout, headings and field labels. Verify real pending, success, error and reduced-motion behaviour. Do not deploy.
```

The skill supports focused changes, broad passes, audit-only work and isolated mockups. Invoking it does not grant deployment or other external-action permission. Existing explicit authorisation still applies within its scope.

## Install or share

Copy the entire `app-motion-effects` folder, including supporting files, to the intended discovery location. Do not overwrite an existing same-named skill without reviewing it. Avoid multiple independently installed versions in the same agent's discovery paths.

| Client | Personal location | Project location | Invocation |
| --- | --- | --- | --- |
| Codex | `~/.agents/skills/app-motion-effects/` | `.agents/skills/app-motion-effects/` | `$app-motion-effects` |
| Claude Code | `~/.claude/skills/app-motion-effects/` | `.claude/skills/app-motion-effects/` | `/app-motion-effects` |
| Other Agent Skills clients | Client's documented skill directory | Client's documented project skill directory | Client-specific |

These locations and commands follow the [official OpenAI documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) and [Claude Code documentation](https://code.claude.com/docs/en/skills). Codex supports symlinked skill directories. Personal Claude Code files apply to local Code projects; they do not automatically install into Claude account/cloud/Cowork skill settings. Consult that surface's own import instructions for the portable ZIP.

Open a new session or use the client's supported refresh/list mechanism. Confirm the skill appears; installation of files alone does not prove runtime selection. Client versions and managed settings can affect discovery.

For an agent without native skill support, provide this instruction:

```text
Read /path/to/app-motion-effects/SKILL.md and use it for this task. Resolve supporting reference paths relative to that directory. Follow my project's instructions and the actual task scope. Do not assume tools or permissions that are unavailable.
```

The common entrypoint uses standard YAML `name`, `description` and optional version `metadata`. `agents/openai.yaml` is optional Codex presentation metadata; other agents can ignore it. There are no required scripts, paid accounts, MCP servers or runtime dependencies in this skill. Browser/build/profiling capabilities depend on the receiving environment; unavailable verification must be stated rather than invented.

## Package contents

- `SKILL.md`: scope-aware implementation workflow and completion criteria.
- `references/adaptation.md`: evidence-led customer/task context, visual contract, motion direction and adaptation/fit review.
- `references/taxonomy.md`: 63 category IDs with technical vocabulary.
- `references/sources.md`: 31 source/use-case groups with direct links and selection guidance.
- `references/verification.md`: playback, state preservation, accessibility and performance checks.
- `assets/review-template.md`: adaptable coverage, improvement, source and evidence tables.
- `agents/openai.yaml`: optional Codex display metadata.

The catalogue is a research shortlist, not a package bundle or licence grant for third-party work. Source, asset and runtime terms must be checked for each adoption. The skill contains no private application branding, credentials or customer data. Its instructions remain portable; app-specific conventions belong in the target repository.

Format reference: [Agent Skills specification](https://agentskills.io/specification). Discovery guidance checked 8 November 2026. No claim is made that every client or every motion category has been exercised by this package's structural validation.
