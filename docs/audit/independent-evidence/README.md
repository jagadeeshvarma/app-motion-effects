# Independent review instrumentation

These scripts require the repository's existing `@playwright/test` dependency and Google Chrome. They inspect synthetic copies through a loopback server and write evidence to the chosen directory. They do not modify the served copies.

Arrange the four anonymous IDs as child directories, each containing its reviewed `public/` app. Serve that input directory, then run from the repository root:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory ./review-input
```

In another terminal:

```sh
node docs/audit/independent-evidence/review-first-four.mjs --input-base http://127.0.0.1:8000/ --output-base ./review-evidence
node docs/audit/independent-evidence/review-first-four-motion.mjs --input-base http://127.0.0.1:8000/ --output-base ./review-evidence
```

To inspect another provided anonymous output with the same frozen A/B scenarios, pass `--outputs 0123abcd:B` (or comma-separated `ID:A,ID:B` pairs) and a distinct `--label additional` to both scripts. These options select copies and output filenames; they do not change the interaction checks.

Use a fresh output directory to retain existing evidence. For a read-only pending textarea, the first script attempts actual keyboard input immediately and records the blocked state; it does not treat an edit auto-waited until after save completion as a concurrent edit.

The first script runs the full appearance/input matrix; the second captures focused playback and settled live reduced-motion checks. Run `--help` for their argument format. The Chrome channel is explicit; these scripts do not install a browser or packages.

The published `observations-first-four.json` preserves original measurements. Its four video fields were normalised from machine-local generated paths to the existing anonymous-ID playback files alongside it. Original raw files were retained outside the publication tree. This path sanitisation does not change scores, timings, observed states or outcomes.
