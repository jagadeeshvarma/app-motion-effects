# Maintainer audit

Status: **audit evaluated; original capability acceptance FAIL;2.1.0 merged, published and verified live under owner authorisation with known limitations**. The subsequent owner instruction is recorded in [release authorisation](release-authorization-2.1.0.json). Required GitHub CI remains enforced. Frozen assertions and measured FAIL/BLOCKED outcomes are unchanged. Independently verified maintenance 2.0.1 was merged, published and verified live separately; publication state is recorded in `release-verification.json`. Baseline source: `ce5f55a8c2a9b4319a76d793b46eef9a41d5a541`, released skill `v2.0.0`. The preceding website update was completed separately in PR #7 and verified live before this audit began.

## Scope and contract

This is a product-aware motion, transition, microinteraction and feedback skill for existing applications. It is not a general backend or application generator. Web and native mobile remain goals; desktop guidance remains available. The audit does not grant future users' agents new release or account permissions.

The [capability contract](CAPABILITY_CONTRACT.md), [frozen acceptance criteria](acceptance.json), [inventory](inventory.json) and [baseline](baseline.json) define scope and gates. Repository branding rules were checked for applicability: SITA application branding is not the independent open-source skill website's brand. Existing application repositories and user changes were left outside this branch.

All 54 maintained text files at baseline were independently source-reviewed. The 25 binary files are original synthetic screenshots/recordings; their provenance, formats and representative rendered playback were assessed rather than treating them as executable source. Generated dependencies, caches, packages and browser traces are excluded from the runtime package. The package contains no downloaded third-party implementation or private fixture data.

## Confirmed findings and changes

| Finding | Baseline problem | Implemented response |
| --- | --- | --- |
| SR-001, medium | Packaging accepted hidden files and dereferenced file symlinks | Explicit reviewed file manifest, unsafe-tree rejection, staged output and 27 isolated package regressions |
| SR-002, medium | Local references could resolve outside the installable skill | Skill/repository containment, real-path checks and extraction/portability tests |
| SR-003, low | Lexical service-call guard missed other browser request mechanisms | Local-only CSP, exact static request allowlist, synthetic beacon and remote-asset checks |
| SR-004, low | Portable invocation imposed this website's copy preference on other apps | Derive headings/label rules from the target visual contract; retain this site's own design |
| SR-005, low | Manual Pages source lacked a main-only guard | Explicit build/deploy main-ref guards; saved environment already restricts deployment to main |
| ME-001 | No executed three-condition skill benchmark | Frozen realistic fixtures, fresh agent contexts and independent rendered review |
| ME-002 | Native implementation checks were too general | Progressive shared/native stack guidance, including distinct iOS/Android reduced-motion APIs |
| ME-003 | Trust guidance needed operational detail | Preserve text rendering, inspect source commands, constrain demo traffic and retain host permissions |

The added verification footer link introduced a320px Linux font-metric overflow (SR-006), caught by hosted CI after local Chrome passed. The footer now wraps within its container; a wider-font regression supplements the existing responsive checks.

No critical/high defect was confirmed by the source review. This is a bounded result, not a complete-security claim. Detailed baseline reproductions are in the [independent source review](source-review.md); current status, root cause, impact and acceptance tests are in [findings.json](findings.json).

The skill remains dependency-free, with the same name, invocation and installation paths. Detailed native/trust guidance is loaded only when relevant. Existing taxonomy and source groups are retained. The installable archive excludes this audit and all evaluation fixtures.

## Comparison and evaluation method

Five scoped comparators were inspected at pinned revisions: Anthropic frontend-design, Vercel web-design-guidelines and react-native-skills, Expo expo-animation and Emil Kowalski animate. They are partial comparators with different purposes; source inspection does not establish relative runtime quality. Exact locations, dates, versions and licences: [comparison](comparison.md), [machine record](comparators.json). No universal ranking is supported.

The [evaluation corpus](../../evals/README.md) contains small realistic web/Flutter tasks. Graders stay outside model workspaces. Three conditions use the same advertised model, reasoning setting, task, tools and time budget: no skill, released v2.0.0 and frozen candidate. Skill-enabled conditions use normal project-local discovery and explicit invocation. Automatic selection is a separate check. SDK/browser/tool availability, task completion, executable correctness and independent visual judgement are separate results.

The Codex registry was queried directly: no-skill has zero enabled skills; the documented project-local path has exactly the intended skill. A directory copy or enabled-but-undiscovered path was not counted as successful discovery. Global installed skills/configuration were not replaced.

G–L descriptions were inadvertently exposed while inspecting runner metadata. They are explicitly **validation cases, not untouched held out**. Two unseen supplemental cases M/N were authored only after candidate freeze. Original freeze manifests are retained, including a pre-run native fake-time grader amendment. See [methodology amendments](methodology-amendments.json). Acceptance thresholds were not lowered.

Native pilot tasks exposed SDK writes denied by the model sandbox and shared self-chosen temporary SDK paths. Those runs are provisional infrastructure evidence, not clean comparative native scores. Per-run SDK/cache isolation and serialized reruns are required. Generated outputs are never manually repaired to make a score pass.

A browser test can establish a rendered web assertion; it cannot establish native support. Widget tests, native builds, iOS simulator playback, Android emulator playback, hardware accessibility and store release are recorded separately. Claude Code is installed but unauthenticated, so its agent-runtime evaluation is blocked. No equivalent execution claim is made for other Markdown-reading agents.

## Release boundary

The audit branch is isolated from protected main. Existing required CI, strict up-to-date checks and administrator enforcement remain enabled. Pages is restricted to main in both source and saved environment settings. No new paid service, domain or infrastructure is required.

The original audit policy required the frozen behavioural and native gates, independent review, matching documentation, package integrity and final-candidate verification. The owner subsequently authorised the2.1.0 release despite the documented capability limitations; this is an explicit one-off release decision, not a passed audit or weaker assertion. If they remain blocked, independently verified maintenance may be released separately with precise scope; incomplete capability work must remain identified as such. Rollback uses the previous immutable skill release and prior Pages commit through the normal checked workflow. No application production change is part of this audit.

## Measured result

The scored non-native comparison comprises ten original web tasks plus two unseen held-out tasks, one output per condition. Native rows remain separately blocked.

| Condition | Executable artifacts pass | Agent completes within 240 seconds |
| --- | ---: | ---: |
| No skill |10/12|11/12|
| Original 2.0.0 |9/12|8/12|
| Final 2.1 candidate |11/12|8/12|

A completed artifact check is not a completed agent task. Both candidate held-out artifacts passed but their agents timed out. Final I failed observable filter animation under both original and contained grading; manual scores cannot waive it. No overall superiority claim is supported.

B (draft/state preservation) and K (untrusted reference) were repeated to three trials per condition. All 18 selected repeated outputs passed; elapsed variation is retained, not used as a causal speed claim. Native D repetitions could not proceed through the strict grading gate. Full original/prototype/native-invalid records remain in [results](results.json), with selected comparison/variation in [comparison-results](comparison-results.json). Recorded original inputs all match the pinned tag ([integrity](original-input-verification.json)).

The final ten primary web outputs underwent 80 Chrome cases at desktop/320px, light/dark and normal/reduced motion. The six-item manual scores are9–12/12; eight pass. H/J fail the no-zero evidence-honesty rule after an explicit consistency amendment; the original scores/reports remain preserved. The full corpus is NOT PASSED because of I, manual evidence failures and native blockers. Earlier five-item/390px reviews are separate evidence. G/K wrapping and H intermediate contrast limitations were inherited; H/J claimed executed server failures were absent from the supplied complete command traces; their evidence-honesty scores are zero without inferring intent. See [final review](final-manual-review.md) and [actual captures](EVIDENCE.md). Held-out M/N runtime review also passed, but both manual gates FAIL: their notes claim a concrete failed server command absent from the retained transcripts. The frozen evidence-honesty dimension is zero; no intent is inferred. Both generation timeouts remain. See [held-out review](heldout-manual-review.md).

Six automatic routing probes observed target loading for both positive requests. Negative tasks stayed narrow with no body read observed; ambiguous diagnosis remained source-only; one companion-skill overlap used that companion without duplicate work. Trace absence is not proof of every hidden host action. [Routing evidence](activation-results.json).

## Native and host boundaries

Flutter 3.47/Dart 3.13, Xcode 26.6/iOS 26.5 simulator and an owned Android API 35 guest were available. Native builds and normal-main synthetic note/sync playback occurred. These exploratory controls/pilots are not a clean three-condition native benchmark. Real-time 300/400ms assertions were unreliable on the emulator; supplementary Completer-driven controls nonvacuously detected the known stale-callback defect without changing app source.

Model environment readiness eventually passed using nine owned-path variables, isolated zsh startup and loopback-only proxy. Strict generated-code grading still failed: host architecture discovery was denied and the copied SDK tooling referenced 101 package roots outside the owned clone, triggering blocked dependency resolution. A protected fresh grading toolchain is not established. Native admission therefore stops before new model calls. No home/general-temp/public-network grant or unsandboxed fallback was used to obtain a pass. [Native record](native-runtime.json), [strict blocker](native-grading-readiness.md).

All owned simulators/emulators, private adb ports and 16 recorded process groups were cleaned; 17 owned tool copies were removed while app sources/evidence and original SDK/personal data were preserved. No real device or user AVD was used. Claude Code runtime remains BLOCKED by absent authentication. Other clients/frameworks, physical-device accessibility, screen-reader audio, sustained FPS/battery and store release are NOT RUN.

## Maintenance versus capability release

2.0.1 contains the original nine runtime files and unchanged 2.0.0 workflow, apart from version/readme maintenance metadata. It carries only independently tested distribution/link/install/example-isolation/workflow and truthful-documentation fixes. The eleven-file2.1.0 release subsequently includes the native/trust guidance by explicit owner authorisation; it is separate from that maintenance patch. Evaluation snapshots are repository evidence and remain excluded from installable archives.

The maintenance gate requires 27 package, 2 installation and 33 browser checks plus formatting/structure, exact 9-file reproducible archives, protected CI and actual live verification. The audit branch additionally passes 53 infrastructure tests, 13 activation self-tests and native adapter regressions. Structural passes do not repair the failed capability gate.

To satisfy the original capability acceptance criteria (still unmet): repair and re-evaluate I through a browser-capable measured workflow; prevent unsupported reported checks and rerun the affected evidence-honesty gate; establish a trusted relocated SDK-tool cache and permitted architecture metadata adapter inside the strict grader; rerun C/D under all three conditions and the frozen/supplementary native protocols; authenticate Claude before claiming its runtime; rerun affected final-candidate gates. Retain the current failures and publish any new protocol/candidate version explicitly.

Commit/PR/release/live identifiers and actual final states are in [release verification](release-verification.json). No staged, pushed or merely built artifact is called live.
