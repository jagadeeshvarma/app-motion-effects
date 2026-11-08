# Runner audit and operation

`run.py` creates a fresh fixture workspace for each case/condition/trial. It uses the pinned model/reasoning and a maximum 240-second model timeout. Graders, manifests, other tasks and condition labels stay outside that workspace. This is context separation, not a claim that workspace-write provides read isolation from every host path. Output directories are private audit artifacts and may contain local paths, synthetic canaries and raw transcripts; publish only reviewed summaries.

No-skill, original-v2 and improved conditions share explicit configuration. Default activation remains the original `$app-motion-effects` host invocation for the two skill conditions; task text is otherwise identical. `--activation implicit` omits that invocation and is a separate experiment. Negative/ambiguous `--trigger-kind` tasks are routing probes; primary functional graders are intentionally not applied. Report routing observations separately.

## Checks without model calls

```sh
python3 -m unittest discover -s evals/tests -p 'test_*.py' -v
python3 evals/run.py --help
python3 evals/run.py --cases A --conditions no-skill --output /path/to/new-audit --dry-run
```

Unit tests use fake local CLI scripts and no model or network calls. Discovery uses only initialize/skills/list, with no thread or turn creation. Per-run registry checks fail closed if unexpected skills or discovery errors appear. They establish skill catalogue availability, not that the model read the skill. Installed app-server does not support exec's `--ignore-user-config` option; that configuration difference is disclosed in registry and invocation records. Full configuration equality is not asserted. Actual no-skill/skill probes observed 0/1 enabled skills respectively in the tested host environment.

## Prepared native environment

**Current checkpoint:** model-environment v6 readiness passes, but generated native grading remains under an explicit admission hold. The stricter profile denies the outside/source canaries as required, yet actual Flutter bootstrap is unverified because hardware-query permission and external Flutter-tool package roots remain unresolved. A protected fresh-toolchain-per-grade transport/anchor is not established. No native trial 3 model calls or generated widget grading may start. Earlier blocked proofs and invalid cohorts remain evidence, not passing native capability. The command below describes the gated future procedure, not present admission.

Native trial 1 used the host environment and is provisional. Trial 2 is invalid as a comparison cohort: C encountered sibling SDK-cache write denial; D failed setup after the old seed path was withdrawn and made no model calls. Do not repair or merge those records into final-native evidence. Prepared trial 3 requires a fresh matching proof and uses unique per-run public-only SDK/cache clones with serial C/D tasks. The exact nine reviewed environment variables, including ZDOTDIR and ANALYZER_STATE_LOCATION_OVERRIDE, are propagated through `shell_environment_policy.set`; HOME/CODEX_HOME are preserved. Any future authoritative grader must use a protected fresh trusted toolchain rather than reusing a model-mutable SDK/cache. Native sources and evaluated outputs are never repaired by setup.

```sh
python3 evals/run.py --cases CD --conditions no-skill,original-v2.0.0,improved \
  --candidate /path/to/frozen-skill --trial 3 --jobs 1 \
  --native-seed /path/to/public-seed --native-readiness /path/to/readiness-proof.json \
  --trusted-input-grading --safe-grading --native-grading-readiness /path/to/grading-proof.json \
  --output /path/to/private-results
```

The readiness proof must match the exact seed-manifest/profile/helper hashes. It must use the actual default system temporary parent, app cwd and `/bin/zsh -lc`, and demonstrate that whole-parent TMPDIR covers SDK/pub-cache/config/analyzer-state writes, the owned ZDOTDIR adapter preserves bare Flutter selection after login startup, locks remain unchanged, and version/offline dependency/analyze/test commands work. Loopback bind and explicit denial of a disallowed synthetic host remain required. Earlier private-tmp proofs were masked by inherited `/tmp` permissions and cannot establish default-temp ownership; they are rejected. The adapter is certified for the tested macOS/zsh host only, not a portable-shell guarantee. A missing, blocked or mismatched proof prevents model calls. The reviewed native-only profile uses an active network proxy, limited mode and exact localhost/127.0.0.1/::1 domain rules. The owner separately authorized `allow_local_binding=true` after false still blocked Flutter socket binding. General web permissions remain unchanged. Native exec uses command-line `default_permissions`, ignores user config and omits legacy `-s`/sandbox keys. The standalone capability proof is not evidence of a model run's effective runtime until the run itself is observed. Managed requirements still apply.

The exact values are exported by `native_profile_values()`; `native_profile_sha256()` computes their canonical hash. The native helper and seed/proof hashes are recorded. Do not expose helper environment values or absolute SDK/cache paths in public reports. Official [configuration reference](https://developers.openai.com/codex/config-reference/) documents environment overrides and skill rule precedence; [permissions guidance](https://learn.chatgpt.com/docs/permissions) describes profiles/proxy enforcement and legacy-setting precedence.

## Results, cleanup and resume

Agent process statuses are COMPLETED, INCOMPLETE, TIMED_OUT, EXIT_FAILED, LAUNCH_FAILED, CLEANUP_FAILED, REGISTRY_BLOCKED or SETUP_FAILED. COMPLETED requires exit 0 plus a completed-turn event and no error event. It is not an artifact pass. Grader acceptance and manual acceptance remain separate. Older runner PASS/BLOCKED statuses retain their original semantics and must not be silently relabelled as complete acceptance.

Setup/model/grader failures are saved per run instead of aborting the whole batch. Model and grader timings are separate from setup/registry/total time. Process groups are reaped after completion and timeout; permission-limited child-only fallbacks or denied cleanup are recorded. Workspaces remain for review. A process that creates an independent session is outside the guarantee of process-group cleanup; bounded pipe draining prevents it from hanging the runner indefinitely.

Tool metrics count unique observed items of the named JSON event types, including incomplete started items. They are not an estimate of hidden internal calls. Token totals sum only reported completed-turn usage; missing/interrupted-turn usage is unknown. Monetary cost remains null because per-run monetary telemetry is unavailable. Do not impute zero cost or missing tokens.

The plan records runner/discovery/skill/corpus/CLI/dependency fingerprints, activation mode, native environment proof, order and worker count. `--order-seed` gives a reproducible shuffled schedule; omitted retains the earlier ordered schedule and must not be described as randomized. Invocation records include a sanitized argument list and exact-argument/input hashes. An output-directory lock prevents two new runners writing the same output concurrently. The runner never overwrites existing outputs or silently spends quota to replace mismatched same-trial results: use a new trial/output when experiment fingerprints differ. Existing original-v2 snapshots are checked against the tag before reuse.

MA04 corrects corpus chronology: acceptance criteria predated instruction edits; final A–L freezing completed before comparative runs after edits had begun; the independent task author did not inspect the candidate. Tasks, assertions and acceptance thresholds are unchanged. Supplemental M/N remain separately frozen held-out cases.

## Verified host-input grading correction

GA01 corrects the post-run scope-accounting bug described in [GRADING_AMENDMENT_GA01.md](GRADING_AMENDMENT_GA01.md). Trusted-input verification is now mandatory by default for new runs; the compatibility flag is accepted but cannot disable it. `regrade.py` applies the same companion uniformly to original outputs into a new private directory. Only a byte-for-byte verified host-injected skill tree is excluded from H's generated-file calculation; unrelated `.agents` or UI changes remain in scope. Raw first grades and evaluated sources are preserved.

GA02 submitted-tree/transport containment is now mandatory by default for new runs, regrades and companion calls. The compatibility `--safe-grading` flag is accepted; no disabling flag exists. Old raw records remain unchanged. Legacy seven/eight-key native environment records may be read for historical regrading only; they do not satisfy current readiness and remain labelled invalid legacy cohorts.

Generated native Dart must not execute through the historical unsandboxed grader path. Native scheduling and companion grading now require a separate `--native-grading-readiness` proof and the contained transport. That grader proof must establish deny-root reads, minimal tool/runtime reads, only owned paths writable, no generic temporary-root access, exact loopback proxy rules, and denial of an outside-owned synthetic canary alongside an actual Flutter test. Model SDK readiness alone does not establish grading containment. Missing enforceability keeps native execution blocked. Historical frozen grader files remain archived evidence, not the supported entrypoint for untrusted native output.

Metrics retain legacy `tool_calls` semantics (completed command/MCP/search items) and separately record observed `file_change` items, failed/incomplete change events and explicit category labels. File-change items are not net changed-file counts and shell writes may emit none. Older raw metrics are not rewritten; derived totals may be recomputed uniformly from retained transcripts.

## Supported frontdoors

GA03 makes guarded grading the default and quarantines direct historical `grade.py` execution. Use `run.py` or `regrade.py`; the companion always performs trusted-input and containment checks. Exact old assertion bytes are stored as authenticated gzip data and executed only by the guarded loader after preflight. Archive/source/original-freeze hashes are recorded in `historical_assertions/index.json`. The original freeze manifests and raw results remain intact. See [GA03](GRADING_AMENDMENT_GA03.md). There is no supported unsafe bypass flag.
