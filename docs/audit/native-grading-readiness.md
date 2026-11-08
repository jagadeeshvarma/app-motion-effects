# Native grading containment checkpoint

The separate generated-code grading gate is **BLOCKED** as of 2026-11-08. `evals/native_grading.py` exposes the fail-closed readiness API expected by the runner/companion. Its explicit admission hold prevents any native grading proof from being accepted at this checkpoint. No model calls or unsandboxed fallback were used.

The proposed policy uses root deny, minimal runtime reads, an exact owned parent, a narrower deny for retained source, no generic temporary-directory grant, and an active literal loopback-only network proxy. These controls follow the documented [permission-profile model](https://learn.chatgpt.com/docs/permissions). A separate passing model/SDK readiness proof does not establish this generated-code boundary.

Four retained private probes establish progress without passing the gate. The final instance denied synthetic outside-owned and retained-source reads/writes, allowed owned writes and loopback, and returned an explicit CONNECT 403 denial for a disallowed synthetic host. No real secret was read.

Actual Flutter testing did not pass. Narrow-profile diagnostics show that `uname` reports arm64 but `sysctl hw.optional.arm64` is denied. The pinned SDK's Flutter-tool package configuration also references 101 package roots outside the owned clone. Git revision and tool stamp/timestamp predicates are valid; generic xcrun cache warnings are not the primary blocker. Offline app flags do not cover every SDK-tool bootstrap action. Public network/home/general-temp access was not added to generated-code execution.

A future attempt needs a reviewed trusted-tool/cache correction and a protected, fresh toolchain/cache per grading run, preserving versions and frozen assertions. Reusing a model-writable SDK/cache is not sufficient. No protected trust anchor or such fresh-clone transport was created in this bounded pass. All probes remain blocked, and the current adapter has an explicit admission hold.

Four pure native-grading policy/transport tests pass alongside the ten GA02 tree/static-transport regressions. They verify fail-closed admission, the deny policy, unchanged Flutter arguments and environment handoff; they are not runtime proof. [Structured checkpoint](native-grading-readiness.json).
