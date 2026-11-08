# Final web output snapshots

These synthetic interfaces are unchanged runtime files from the final candidate evaluation, including failures. They are evidence, not recommended production components. Each file is bound to the original output SHA in `manifest.json`. No output was repaired. Tests, review notes, installed skills, caches and private transcripts remain outside these snapshots.

Serve a selected app root with Python 3, for example:

```sh
python3 -m http.server 8000 --directory evals/outputs-final/A/public
```

Use the manifest for other app roots; I uses `I/packages/warehouse/public`. All operations are local synthetic demonstrations. See `docs/audit/results.json` and the final manual review for failed checks and limits. The installed skill and stable maintenance release exclude this directory.
