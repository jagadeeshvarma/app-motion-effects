# GA01: verified host inputs versus generated scope

This is a transparent post-run grading correction, discovered when validation H output `32df6d45ede9` failed the tiny-change assertion solely because the harness had installed the skill under `.agents/skills/app-motion-effects/`. Those input files were absent from the standalone fixture baseline and were therefore incorrectly counted as model-generated files. The original task, fixture, tiny scope threshold, raw first grades, result records and source outputs remain unchanged. Original frozen manifests remain intact.

The companion `graders/grade_with_trusted_inputs.py` first executes the original frozen grader unchanged. It requires a trusted harness `before_sha256` map supplied outside the evaluated workspace. An optional expected manifest SHA protects the caller's recorded manifest bytes. The companion verifies every file in the exact injected skill tree against that map, rejects missing, added or modified files and symlink substitution, and excludes only that fully verified tree from H's generated-change calculation. It does not ignore `.agents` generally. Unrelated files under `.agents`, unverified skill additions, changed injected skills and unrelated UI changes still fail. Every other legacy assertion and failure is retained, and the unamended legacy grade is embedded in the new record.

The new check also verifies injected inputs for every other scenario when this companion is selected. No tree is excluded in a no-skill run. Authentication of the before-map is the trusted harness/caller's responsibility; merely moving an agent-written map outside its workspace does not make it trusted. Future corrected runs record the before-map before model execution and retain its expected hash in the running harness state. Existing runs use their externally recorded original result JSON.

This correction must be applied uniformly, including failures and all three conditions. It must not be reported as the original preregistered raw result. Report both first and amended outcomes, with this reason. No evaluated output may be repaired before either grade.

## Future runs

Add `--trusted-input-grading` to `evals/run.py`. The option records a before-manifest outside the workspace before launching the model and selects the companion. Legacy default grading is deliberately unchanged for already-running batches. Activation-only tasks continue without primary functional grading. The runner experiment fingerprint includes the option and companion hash, preventing silent reuse across grading paths.

## Existing outputs

```sh
python3 evals/graders/grade_with_trusted_inputs.py --scenario H \
  --workspace /path/to/original-workspace --before-manifest /path/to/original-result.json \
  --expected-manifest-sha256 <recorded-file-sha256>

python3 evals/regrade.py --results /path/to/private-first-results \
  --output /path/to/new-private-regrades
```

The batch tool writes separate records and refuses overwrites. It preserves first-result/grade hashes and uses a recorded public native environment when available. It does not launch model calls or alter original workspaces. The original first grades remain authoritative evidence of what the first grader reported.

Regression coverage checks verified exclusion, changed/added/missing injected files, invented inputs in a no-skill condition, unrelated `.agents` additions, unrelated UI edits, manifest placement/hash validation, symlinks, retained other failures and opt-in runner integration. Synthetic tests make no model or browser calls. Targeted read-only browser regrading additionally checks H's two reported outputs and records original-result/grade/source hashes before and after.
