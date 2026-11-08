# GA03: safe defaults and historical-entry quarantine

New run, regrade and companion entrypoints always enable trusted-input verification and GA02 containment. Existing compatibility flags are accepted, but there is no disabling or unsafe bypass flag. Native admission remains held. Original result/grade files and evaluated outputs are not rewritten.

The two historical Python graders are now authenticated compressed assertion data. Their decompressed bytes match the preserved original freeze hashes exactly. Direct `grade.py` execution returns BLOCKED without reading a submitted tree or executing assertions. Only the containment loader executes the registered archive after preflight, using the original virtual filename so fixture and transport paths retain their original semantics. The loader verifies container hash, source hash and the original preserved freeze manifest before execution. No assertion or threshold is edited.

`historical_assertions/index.json` records both archive/source hashes and their original freeze provenance. Original freeze files remain unchanged; superseding manifests record the wrappers, archive containers and loader. Compressed archives are historical evidence, not runnable entrypoints. Reconstructing and executing arbitrary code manually is outside the supported harness; no such bypass is provided.

Use `evals/run.py` for new work and `evals/regrade.py` for existing retained outputs. The companion requires an external trusted before manifest. Frozen JavaScript assertion files are internal historical transport inputs, never recommended direct serving/grading entrypoints. Their supported route uses the contained preload.

Regression checks cover direct-entry quarantine, archive provenance, guarded default routing and retained-source integrity. Safe defaults are a new-run policy change and do not retroactively rename or overwrite old raw results.
