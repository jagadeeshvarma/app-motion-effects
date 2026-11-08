# GA02: submitted-tree and static-transport containment

Date: 2026-11-08. This is an explicit, opt-in grading-infrastructure amendment. It changes neither tasks nor frozen UI assertions/thresholds, repairs no evaluated output and does not rewrite existing grades or results. Active batches retain their original defaults. Record GA02 results separately and apply the same selected grading version uniformly to all compared conditions.

## Confirmed defect

The frozen web server checks lexical paths, then follows links through `stat`/`readFile`. A disposable synthetic B copy with a `public/linked.txt` link to a synthetic file outside the static root served that content as same-origin data. The canary appeared in the browser-error assertion detail. Python legacy file enumeration likewise treats linked files as files and may read/hash them before browser grading. No real secret was read. [Recorded synthetic proof](../docs/audit/ga02-synthetic-proof.json).

## Corrected opt-in path

- `containment.py` rejects submitted symlinks, broken links and special files using metadata only, before legacy content enumeration/read/hash. It covers the complete submitted tree, including ordinarily ignored directories. Optional prior workspaces are checked too.
- `graders/grade_with_containment.py` runs the registered, unchanged legacy grader and records infrastructure hashes. Only its exact Node web transport invocation is redirected.
- `graders/safe-web-preload.mjs` wraps the Node HTTP server factory before the frozen web module loads. The existing test source and all assertions run unchanged.
- `graders/safe-static-server.mjs` checks the static tree before serving and checks every request's components with `lstat` plus canonical realpath containment before invoking the original static listener. Rejected requests return a generic 403; link contents are not returned.
- Companion, runner and regrade wiring select this path only with `--safe-grading`; runner use also requires `--trusted-input-grading`. Existing GA01/default runs are not silently relabelled.

A confirmed submitted symlink/special-file violation produces **FAIL**, with frozen UI checks explicitly **NOT RUN** because content grading was stopped before reads. Missing files/tools or an OSError preventing preflight produce **BLOCKED**, rather than an artifact pass. Violation metadata is retained, so an observed output failure cannot disappear into infrastructure counts. Containment is a host-side infrastructure boundary, not a new animation quality criterion or an operating-system read sandbox. Source integrity and applicable artifact acceptance still require their existing checks.

Direct transport verification, without a model call:

```sh
python3 -m unittest discover -s evals/tests -p test_containment.py -v
python3 evals/graders/grade_with_containment.py --legacy-grader evals/graders/grade.py --scenario B --workspace ./synthetic-B-output
```

Ten focused synthetic regressions cover ordinary trees, inside/outside/broken/ancestor links, ignored subtrees, FIFO rejection without opening, preflight before legacy execution, unchanged legacy assertion outcomes, exact transport redirection and same-origin HTTP link blocking. An unchanged previously reviewed B output also passed its seven original checks through the corrected transport. A–L freeze validation remained passing. No evaluated model calls were made by this amendment work.
