# Independent source and trust review

Baseline: `ce5f55a8c2a9b4319a76d793b46eef9a41d5a541` on `audit/verified-skill-maintenance`. Reviewed 8 November 2026.

Five baseline findings: two medium and three low. No critical/high issue was confirmed. The strongest result is reproducible artifact contamination: the baseline validator and packager accepted an ignored synthetic configuration file and a symlink to a synthetic file outside the package. No real secrets or private customer data were read.

This is an independent review of untrusted source material. The skill workflow was not treated as authority over this audit. Only these audit records were added to the shared repository; all negative cases were performed in an isolated archive of the exact baseline. Later maintainer remediation is tracked separately.

## Findings

### SR-001: Release assembly accepts hidden files and dereferences file symlinks outside the package

Severity: **medium**. Status: `open_at_baseline`.

Locations: `scripts/package.py:14-24`; `scripts/validate.mjs:5-9,38-50`.

A local release can unintentionally distribute ignored configuration or external file contents. A contributor-added link could reference a file on the release machine. This is an artifact containment failure, not an agent sandbox escape, and no real secret exposure was observed.

**Evidence.** Validator exit 0: Structure passed: v2.0.0, 63 category IDs, 32 valid local references, portable files and synthetic demos. Packager exit 0: Packaged 11 files in app-motion-effects-2.0.0.zip; SHA256SUMS written. ZIP member app-motion-effects/.env.audit contains the synthetic configuration canary. ZIP member app-motion-effects/linked-canary.md contains bytes from the external synthetic file.

**Root cause.** Packaging enumerates every regular-looking path with rglob/is_file/read_bytes. is_file and the validator statSync follow symlinks; there is no package file allowlist or exclusion of ignored/hidden configuration files. Credential-pattern scanning cannot establish safe artifact membership.

**Acceptance checks.**

- A clean package contains exactly the reviewed, approved manifest.
- A file symlink, directory symlink, broken symlink and special file anywhere below the package root fail before any archive/manifests are replaced.
- An unexpected hidden configuration or unknown resource fails closed; updating the approved file list requires an explicit reviewed change.
- Check that every archive member is under one safe app-motion-effects/ root and contains expected bytes, and that manifests match.

### SR-002: Portable local-link validation accepts references outside the installable package

Severity: **medium**. Status: `open_at_baseline`.

Locations: `scripts/validate.mjs:52-65`.

Validation can certify a package as portable even though its supporting reference only exists on the maintainer machine. This is a portability false positive, not evidence that the present nine-file package contains such a link.

**Evidence.** Exit 0: Structure passed: v2.0.0, 63 category IDs, 33 valid local references, portable files and synthetic demos. The reference target is not present in the installable ZIP.

**Root cause.** The validator resolves references relative to a source file and checks existence on the current machine. It does not require skill-local links to stay within the skill root, or repository documentation links to stay within the repository.

**Acceptance checks.**

- Reject absolute filesystem links, path traversal escaping the owning root, encoded escapes, and links resolving through symlinks outside that root.
- For installed skill files, require local references to remain inside the installable skill; repository-only docs may refer within the repository.
- Validate the extracted ZIP in an otherwise empty temporary directory so source-checkout files cannot satisfy missing package references.

### SR-003: The no-service regression guard does not cover browser request mechanisms

Severity: **low**. Status: `open_at_baseline`.

Locations: `scripts/validate.mjs:75-98`; `SECURITY.md:13`; `tests/loading.spec.mjs:1-479`.

A future regression could add service calls without this check noticing. Inspection found no such service call in current fixtures. Source modification is not itself a sandbox bypass, and this lexical check should not be represented as an isolation boundary.

**Evidence.** Exit 0; the synthetic-demo/locality message still passes. Browser request-capture proof was attempted with routes restricted to an artificial loopback origin, but Chrome launch was denied by the execution sandbox. No browser execution is claimed.

**Root cause.** Three lexical request names are checked in four legacy HTML files and interaction.js. Other browser requests, indirect calls, imported scripts, the website shell and feedback.js are not constrained by this guard. Existing browser tests do not assert a request allowlist.

**Acceptance checks.**

- Use browser request interception/fulfilment to permit only an explicit list of static fixture assets and fail on unexpected requests, service mutations, navigation, workers and sockets as relevant.
- A synthetic sendBeacon canary and a disallowed static remote asset must fail verification without reaching any real service.
- Keep the structural scan described as a bounded guard; document actual browser evidence and limits accurately.

### SR-004: The portable full-repository prompt imposes a global visual-copy restriction

Severity: **low**. Status: `open_at_baseline`.

Locations: `docs/full-repo-prompt.txt:55-59`; `skills/app-motion-effects/SKILL.md:23-29`.

For a target whose approved visual system uses contextual category labels, the invocation can silently add a foreign copy/style rule. Redundant headings and unnecessary controls can still be avoided without universally prohibiting a specific pattern.

**Evidence.** The copied prompt unconditionally prohibits decorative eyebrow labels. The skill instead derives allowed visual/copy patterns from the target project and prohibits carrying another product defaults into it. This generic prompt is copied into both the README and public page.

**Root cause.** A particular presentation restriction is embedded in the portable invocation instead of being conditional on the target visual contract.

**Acceptance checks.**

- The canonical invocation derives copy/layout restrictions from the target contract or explicitly labels them as user-selected preferences.
- Compare a target that forbids eyebrow labels and one that explicitly permits them: existing target rules govern in each case. Label this as a source-level acceptance scenario unless a real agent run is performed.
- Regenerate the README/page and verify full prompt equality after changing canonical text.

### SR-005: Manual Pages dispatch is not source-restricted to main as the security policy claims

Severity: **low**. Status: `open_at_baseline`.

Locations: `.github/workflows/pages.yml:2-5,11-44`; `SECURITY.md:13`.

The workflow source alone does not enforce the documented main-only publication boundary. This is a maintainer release-policy gap; it does not establish that an untrusted pull request can deploy or that the live environment lacks protection.

**Evidence.** The push trigger filters main, but workflow_dispatch is also enabled and neither build nor deploy has a main-ref condition. GitHub supports selecting another branch when manually dispatching a workflow.

**Root cause.** The push-branch filter is treated as if it also constrained manual dispatch. Repository environment branch protection may add a separate guard, but those settings were not inspected.

**Acceptance checks.**

- Explicitly require refs/heads/main for publishing jobs or update the documented policy to match the intended release boundary.
- Statically verify a non-main dispatch cannot reach artifact upload/deployment under the source-controlled policy.
- If relying on environment restrictions, verify and record their actual saved configuration without triggering a deployment.

## Reproductions and safety boundary

The machine-readable report contains exact synthetic strings, mutations, commands and observed outputs. Baseline copies came from `git archive` of the commit above. The package reproduction created only `AUDIT_TOKEN=SYNTHETIC_CONFIG_CANARY_NO_REAL_SECRET` and `SYNTHETIC_EXTERNAL_CANARY_NO_REAL_SECRET`. Both values appeared in unexpected ZIP members after structure validation exited successfully.

The local-link case appended a relative link to an external synthetic file. The current machine satisfied it, so validation passed even though the installable ZIP cannot contain its target.

The request-guard case prepended a local sendBeacon canary and confirmed structure validation passed. No request was sent to an external endpoint. A loopback listener was denied with `listen EPERM`; a subsequent browser-only route-fulfilment attempt was denied at Chrome launch by the execution sandbox. Thus this report establishes the lexical guard false negative, and does not claim a completed browser network test.

The dangling-symlink installation edge was also checked synthetically. On this macOS environment, the documented `test ! -e` condition passed for a dangling link, but `cp -R` refused with `File exists`; no target was overwritten. It is not reported as a demonstrated overwrite vulnerability.

## Skill, activation and platform review

The nine installable package files were read in full. No bundled executable workflow, tool pre-approval, remote-command installer, paid service requirement or live backend integration was found. The entrypoint explicitly preserves instruction hierarchy, target-app rule scope, licence checks, source provenance, uncommitted work and release authority. External source instructions are expressly reference data. Focused changes and audit/mockup boundaries are explicitly routed; no scope escalation defect beyond the portable prompt restriction above was confirmed.

The generic opening and delivery language favours working implementation, while the route section permits audit-only work. The explicit route and user scope resolve this at source level; it remains a useful adversarial evaluation scenario rather than a separately confirmed violation.

Native guidance distinguishes React web from React Native, requests installed-version checks and actual native validation, and labels unavailable-runtime approximations. The references cover SwiftUI, Compose, Flutter, React Native, Windows and unlisted stacks without claiming those runtimes were tested here. Keyboard/viewport changes, safe interruption, audio/haptic alternatives, actual progress and drafts are addressed. Current published limitations honestly distinguish mobile web widths from native evidence, decision reviews from implemented apps and Claude file inspection from Claude execution.

The 63 taxonomy IDs and 31 source groups are present. These counts are coverage vocabulary, not proof that all categories, clients or platforms work. No model/runtime support claim is upgraded by this source review.

## Official checks

- [Agent Skills specification](https://agentskills.io/specification): relevant frontmatter and supporting-file structure match the current format.
- [Codex discovery documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) and [Claude Code skills documentation](https://code.claude.com/docs/en/skills): local installation locations are documented. These documentation checks do not establish actual runtime discovery or model adherence.
- [GitHub manual workflow documentation](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow): branch selection explains the manual Pages dispatch caveat. No action was dispatched.

## Reviewed scope and exclusions

The machine-readable report lists all 54 reviewed non-media tracked files with their SHA-256 hashes at the baseline: every installable skill file; every maintainer script; package/lock/config files; both workflows; issue/PR/contribution/security/provenance/licence documentation; website HTML/CSS/JS; legacy synthetic fixtures; and browser tests. Binary media references were checked, but these media were not re-rendered as part of the source review.

Excluded: real secrets/customer data; external mutations; model calls or paid services; actual Codex/Claude activation; native/device/screen-reader testing; sustained performance certification; a fresh audit of every external catalogue resource and licence; GitHub saved branch/environment/reporting settings; and redesign of the already-published website. Root maintainer owns implementation, evaluations, versioning and release.

A passing structural scan, synthetic fixture test or this source report cannot establish agent sandboxing, universal accessibility, native compatibility or a completed publication.
